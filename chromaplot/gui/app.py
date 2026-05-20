from __future__ import annotations

import sys

from PyQt5.QtWidgets import QApplication

from .main_window import MainWindow
from .welcome_dialog import WelcomeDialog


def main() -> None:
    app = QApplication(sys.argv)

    while True:
        welcome = WelcomeDialog()
        choice = welcome.exec_()

        if choice == WelcomeDialog.ImportData:
            window = MainWindow(show_empty=True)
            window.import_data_files()

            if window.project.datasets:
                window.show()
                sys.exit(app.exec_())
                
            continue

        if choice == WelcomeDialog.OpenProject:
            window = MainWindow(show_empty=True)
            window.open_project()

            if window.project.datasets:
                window.show()
                sys.exit(app.exec_())

            continue

        sys.exit(0)


if __name__ == "__main__":
    main()