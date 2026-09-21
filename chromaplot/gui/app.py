from __future__ import annotations

import sys
from pathlib import Path

from PyQt5.QtCore import QTimer, QCoreApplication
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon

import argparse

from .main_window import MainWindow
from .welcome_dialog import WelcomeDialog
from .update_dialog import UpdateDialog

from chromaplot.core.update_checker import check_for_update
from chromaplot import __version__

def maybe_check_for_updates(parent=None) -> None:
    update = check_for_update()
    if update is None:
        return

    dialog = UpdateDialog(update, parent=parent)
    dialog.exec_()


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="chromaplot",
        description=(
            "Create chromatography figures or open an existing "
            "ChromaPlot project."
        ),
    )

    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        help=(
            "ChromaPlot project (.chromaplot) or chromatography "
            "data files (.txt, .csv, .asc, .tsv)"
        ),
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"ChromaPlot {__version__}",
    )

    return parser.parse_args()

def main() -> None:
    args = parse_arguments()

    app = QApplication(sys.argv)

    def resource_path(filename: str) -> str:
        if hasattr(sys, "_MEIPASS"):
            return str(Path(sys._MEIPASS) / filename)

        return str(
            Path(__file__).resolve().parent.parent / "resources" / filename
        )

    app.setWindowIcon(QIcon(resource_path("cp_thumbnail.png")))

    if args.files:
        paths = args.files

        missing = [
            path
            for path in paths
            if not path.is_file()
        ]

        if missing:
            QMessageBox.critical(
                None,
                "Could not open file",
                "The following file(s) do not exist:\n\n"
                + "\n".join(str(path) for path in missing),
            )
            sys.exit(1)

        project_files = [
            path
            for path in paths
            if path.suffix.lower() == ".chromaplot"
        ]

        data_files = [
            path
            for path in paths
            if path.suffix.lower() != ".chromaplot"
        ]

        if project_files and data_files:
            QMessageBox.critical(
                None,
                "Invalid file combination",
                "A ChromaPlot project and chromatography data files "
                "cannot be opened together."
            )
            sys.exit(1)

        if len(project_files) > 1:
            QMessageBox.critical(
                None,
                "Invalid file combination",
                "Only one ChromaPlot project can be opened at a time."
            )
            sys.exit(1)

        window = MainWindow(show_empty=True)

        if project_files:
            try:
                window.open_project_path(project_files[0])

            except Exception as exc:
                QMessageBox.critical(
                    None,
                    "Open project failed",
                    str(exc),
                )
                sys.exit(1)

        else:
            imported, errors = window.import_data_paths(data_files)

            if errors:
                QMessageBox.warning(
                    window,
                    "Some files could not be imported",
                    "\n\n".join(errors),
                )

            if not imported:
                sys.exit(1)

        window.show()

        QTimer.singleShot(
            500, lambda: maybe_check_for_updates(window),
        )

        sys.exit(app.exec_())

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