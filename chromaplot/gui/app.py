from __future__ import annotations

import sys
from pathlib import Path

from PyQt5.QtCore import QTimer, QCoreApplication
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from .main_window import MainWindow
from .welcome_dialog import WelcomeDialog
from .update_dialog import UpdateDialog

from chromaplot.core.update_checker import check_for_update


def maybe_check_for_updates(parent=None) -> None:
    update = check_for_update()
    if update is None:
        return

    dialog = UpdateDialog(update, parent=parent)
    dialog.exec_()

def main() -> None:
    app = QApplication(sys.argv)

    def resource_path(filename: str) -> str:
        if hasattr(sys, "_MEIPASS"):
            return str(Path(sys._MEIPASS) / filename)

        return str(
            Path(__file__).resolve().parent.parent / "resources" / filename
        )

    app.setWindowIcon(QIcon(resource_path("cp_thumbnail.png")))

    update_check_done = False

    while True:
        welcome = WelcomeDialog()

        if not update_check_done:
            update_check_done = True
            QTimer.singleShot(
                500,
                lambda: maybe_check_for_updates(welcome)
            )

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