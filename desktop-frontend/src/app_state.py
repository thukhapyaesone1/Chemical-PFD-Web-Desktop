from PyQt5.QtWidgets import QStackedWidget

widget: QStackedWidget = None  # will be set in main.py
current_theme: str = "light"   # "light" or "dark"

# Backend base URL
BACKEND_BASE_URL = "http://127.0.0.1:8000"   # change later for prod

# Auth
access_token = None
refresh_token = None
current_user = None

# Project loading
pending_project_id = None
pending_project_data = None

# project state
current_project_id = None
current_project_name = None
project_created = False
