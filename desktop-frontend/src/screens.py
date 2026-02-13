from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QEvent
import os

import src.app_state as app_state
from src.theme import apply_theme_to_screen
from src.theme_manager import theme_manager
from src.navigation import slide_to_index
from src.toast import show_toast
from src.api_client import login as api_login, register as api_register, ApiError


class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("ui/welcomescreen.ui", self)

        self.login.clicked.connect(self.gotologin)
        self.create.clicked.connect(self.gotocreate)

        if hasattr(self, "themeToggle"):
            self.themeToggle.clicked.connect(self.toggle_theme)
        
        # Connect to theme manager
        theme_manager.theme_changed.connect(self.on_theme_changed)
        
        # Apply initial theme
        self.on_theme_changed(theme_manager.current_theme)
        self.center_content()

    def gotologin(self):
        login_screen = app_state.screens["login"]
        login_screen.reset_state()
        slide_to_index(1, direction=1)

    def gotocreate(self):
        create_screen = app_state.screens["create"]
        create_screen.reset_state()
        slide_to_index(2, direction=1)

    def toggle_theme(self):
        """Toggle theme via theme manager."""
        theme_manager.toggle_theme()

    def on_theme_changed(self, theme):
        """Called when theme changes from theme manager."""
        apply_theme_to_screen(self, theme)
        self.update_theme_button(theme)
        self.center_content()

    def update_theme_button(self, theme):
        if not hasattr(self, "themeToggle"):
            return
            
        if theme == "light":
            icon_path = os.path.join("ui", "res", "moon.png")
        else:
            icon_path = os.path.join("ui", "res", "sun.png")
            
        if os.path.exists(icon_path):
            self.themeToggle.setIcon(QtGui.QIcon(icon_path))
            self.themeToggle.setIconSize(QtCore.QSize(32, 32))
            self.themeToggle.setText("")
        else:
            self.themeToggle.setText("Dark mode" if theme == "light" else "Light mode")

    def changeEvent(self, event):
        """Detect system theme changes."""
        if event.type() in (QEvent.PaletteChange, QEvent.ApplicationPaletteChange):
            theme_manager.on_system_theme_changed()
        super().changeEvent(event)

    def resizeEvent(self, event):
        self.center_content()
        self.position_theme_toggle()

        bg = self.findChild(QtWidgets.QWidget, "bgwidget")
        if bg:
            bg.setGeometry(self.rect())
        super().resizeEvent(event)

    def center_content(self):
        names = ["label", "label_2", "login", "create"]
        for name in names:
            w = getattr(self, name, None)
            if not w:
                continue
            geo = w.geometry()
            new_x = (self.width() - geo.width()) // 2
            geo.moveLeft(new_x)
            w.setGeometry(geo)

    def position_theme_toggle(self):
        btn = getattr(self, "themeToggle", None)
        if not btn:
            return
        geo = btn.geometry()
        margin_right = 40
        geo.moveLeft(self.width() - geo.width() - margin_right)
        btn.setGeometry(geo)


class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("ui/login.ui", self)

        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.login.clicked.connect(self.loginfunction)
        self.error.setWordWrap(True)

        if hasattr(self, "backToWelcome"):
            self.backToWelcome.clicked.connect(self.gotowelcome)

        if hasattr(self, "themeToggle"):
            self.themeToggle.clicked.connect(self.toggle_theme)
        
        # Connect to theme manager
        theme_manager.theme_changed.connect(self.on_theme_changed)
        
        # Apply initial theme
        self.on_theme_changed(theme_manager.current_theme)
        self.center_content()

    def gotowelcome(self):
        slide_to_index(0, direction=-1)

    def toggle_theme(self):
        """Toggle theme via theme manager."""
        theme_manager.toggle_theme()

    def on_theme_changed(self, theme):
        """Called when theme changes from theme manager."""
        apply_theme_to_screen(self, theme)
        self.update_theme_button(theme)
        self.center_content()

    def update_theme_button(self, theme):
        if not hasattr(self, "themeToggle"):
            return
            
        if theme == "light":
            icon_path = os.path.join("ui", "res", "moon.png")
        else:
            icon_path = os.path.join("ui", "res", "sun.png")

        if os.path.exists(icon_path):
            self.themeToggle.setIcon(QtGui.QIcon(icon_path))
            self.themeToggle.setIconSize(QtCore.QSize(32, 32))
            self.themeToggle.setText("")
        else:
            self.themeToggle.setText("Dark mode" if theme == "light" else "Light mode")

    def changeEvent(self, event):
        """Detect system theme changes."""
        if event.type() in (QEvent.PaletteChange, QEvent.ApplicationPaletteChange):
            theme_manager.on_system_theme_changed()
        super().changeEvent(event)
    
    def resizeEvent(self, event):
        self.center_content()
        self.position_theme_toggle()

        bg = self.findChild(QtWidgets.QWidget, "bgwidget")
        if bg:
            bg.setGeometry(self.rect())
        super().resizeEvent(event)

    def center_content(self):
        names = [
            "label", "label_2",
            "label_3", "emailfield",
            "label_4", "passwordfield",
            "error", "login", "backToWelcome"
        ]
        for name in names:
            w = getattr(self, name, None)
            if not w:
                continue
            geo = w.geometry()
            new_x = (self.width() - geo.width()) // 2
            geo.moveLeft(new_x)
            w.setGeometry(geo)

    def position_theme_toggle(self):
        btn = getattr(self, "themeToggle", None)
        if not btn:
            return
        geo = btn.geometry()
        margin_right = 40
        geo.moveLeft(self.width() - geo.width() - margin_right)
        btn.setGeometry(geo)

    def reset_state(self):
        self.emailfield.clear()
        self.passwordfield.clear()
        self.error.setText("")

    def loginfunction(self):
        user = self.emailfield.text().strip()
        password = self.passwordfield.text()

        if not user or not password:
            self.error.setText("Please input all fields.")
            return

        self.error.setText("")

        try:
            access, refresh = api_login(user, password)
        except ApiError as e:
            self.error.setText(str(e))
            return

        app_state.access_token = access
        app_state.refresh_token = refresh
        app_state.current_user = user

        # Sync component library now that we have a valid auth token
        canvas_screen = app_state.screens.get("canvas")
        if canvas_screen and hasattr(canvas_screen, "library"):
            canvas_screen.library.reload_components()

        print("Successfully logged in via backend.")
        show_toast("Logged in successfully!")
        slide_to_index(3, direction=1)


class CreateAccScreen(QDialog):
    def __init__(self):
        super(CreateAccScreen, self).__init__()
        loadUi("ui/createacc.ui", self)

        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmpasswordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.signup.clicked.connect(self.signupfunction)
        self.error.setWordWrap(True)
        self.backToLogin.clicked.connect(self.gotologin)

        if hasattr(self, "themeToggle"):
            self.themeToggle.clicked.connect(self.toggle_theme)
        
        # Connect to theme manager
        theme_manager.theme_changed.connect(self.on_theme_changed)
        
        # Apply initial theme
        self.on_theme_changed(theme_manager.current_theme)
        self.center_content()

    def gotologin(self):
        login_screen = app_state.screens["login"]
        login_screen.reset_state()
        slide_to_index(1, direction=1)

    def toggle_theme(self):
        """Toggle theme via theme manager."""
        theme_manager.toggle_theme()

    def on_theme_changed(self, theme):
        """Called when theme changes from theme manager."""
        apply_theme_to_screen(self, theme)
        self.update_theme_button(theme)
        self.center_content()

    def update_theme_button(self, theme):
        if not hasattr(self, "themeToggle"):
            return
            
        if theme == "light":
            icon_path = os.path.join("ui", "res", "moon.png")
        else:
            icon_path = os.path.join("ui", "res", "sun.png")

        if os.path.exists(icon_path):
            self.themeToggle.setIcon(QtGui.QIcon(icon_path))
            self.themeToggle.setIconSize(QtCore.QSize(32, 32))
            self.themeToggle.setText("")
        else:
            self.themeToggle.setText("Dark mode" if theme == "light" else "Light mode")

    def changeEvent(self, event):
        """Detect system theme changes."""
        if event.type() in (QEvent.PaletteChange, QEvent.ApplicationPaletteChange):
            theme_manager.on_system_theme_changed()
        super().changeEvent(event)
    
    def resizeEvent(self, event):
        self.center_content()
        self.position_theme_toggle()

        bg = self.findChild(QtWidgets.QWidget, "bgwidget")
        if bg:
            bg.setGeometry(self.rect())
        super().resizeEvent(event)

    def center_content(self):
        center_names = [
            "label", "label_2",
            "emailfield", "passwordfield", "confirmpasswordfield",
            "error", "signup", "backToLogin"
        ]

        base_x = None

        for name in center_names:
            w = getattr(self, name, None)
            if not w:
                continue
            geo = w.geometry()
            new_x = (self.width() - geo.width()) // 2
            geo.moveLeft(new_x)
            w.setGeometry(geo)

            if name == "emailfield":
                base_x = new_x
                field_width = geo.width()

        if base_x is None:
            email = getattr(self, "emailfield", None)
            if email:
                base_x = email.geometry().x()
                field_width = email.geometry().width()

        if base_x is not None:
            for name in ["label_3", "label_4", "label_5"]:
                lab = getattr(self, name, None)
                if not lab:
                    continue
                geo = lab.geometry()
                geo.moveLeft(base_x)
                geo.setWidth(field_width)
                lab.setGeometry(geo)

    def position_theme_toggle(self):
        btn = getattr(self, "themeToggle", None)
        if not btn:
            return
        geo = btn.geometry()
        margin_right = 40
        geo.moveLeft(self.width() - geo.width() - margin_right)
        btn.setGeometry(geo)

    def reset_state(self):
        self.emailfield.clear()
        self.passwordfield.clear()
        self.confirmpasswordfield.clear()
        self.error.setText("")

    def signupfunction(self):
        email = self.emailfield.text().strip()
        password = self.passwordfield.text()
        confirmpassword = self.confirmpasswordfield.text()

        if not email or not password or not confirmpassword:
            self.error.setText("Please fill in all inputs.")
            return

        if password != confirmpassword:
            self.error.setText("Passwords do not match.")
            return

        username = email
        self.error.setText("")

        try:
            api_register(username, email, password)
        except ApiError as e:
            self.error.setText(str(e))
            return

        show_toast("Account created successfully!")
        self.emailfield.clear()
        self.passwordfield.clear()
        self.confirmpasswordfield.clear()
        slide_to_index(0, direction=-1)