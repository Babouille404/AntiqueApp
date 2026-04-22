import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from gui.login_page import LoginPage
from gui.main_window import MainWindow
from services.auth_service import AuthService


def main():
    app = QApplication(sys.argv)

    # Chargement du thème
    qss_path = Path(__file__).parent / "resources" / "styles.qss"
    if qss_path.exists():
        app.setStyleSheet(qss_path.read_text(encoding="utf-8"))

    auth = AuthService()
    login = LoginPage(auth)
    main_window = MainWindow(auth)

    def on_login_success(user):
        main_window.set_user(user)
        main_window.show()
        login.close()

    def on_logout():
        main_window.close()
        login.show()

    login.login_success.connect(on_login_success)
    main_window.logout_requested.connect(on_logout)

    login.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
