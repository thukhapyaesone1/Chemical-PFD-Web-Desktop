from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer
import src.app_state as app_state

class Toast(QWidget):
    def __init__(self, parent=None, message="", duration=2000):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.ToolTip |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.duration = duration

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 10, 16, 10)

        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                color: #F5F1E6;
                font: 11pt "Segoe UI";
            }
        """)
        layout.addWidget(self.label)

        container = QWidget()
        container.setLayout(layout)
        container.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 200);
                border-radius: 10px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)

        self.adjustSize()

        if parent is not None:
            pg = parent.geometry()
            x = pg.x() + (pg.width() - self.width()) // 2
            y = pg.y() + pg.height() - self.height() - 40
            self.move(x, y)

        QTimer.singleShot(self.duration, self.close)


def show_toast(message, duration=2500):
    """Show a toast on top of the main widget."""
    if app_state.widget is None:
        return

    toast = Toast(app_state.widget, message, duration=duration)

    if not hasattr(app_state.widget, "_toasts"):
        app_state.widget._toasts = []
    app_state.widget._toasts.append(toast)

    def cleanup():
        if toast in app_state.widget._toasts:
            app_state.widget._toasts.remove(toast)

    toast.destroyed.connect(lambda _: cleanup())
    toast.show()
