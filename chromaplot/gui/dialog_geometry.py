from __future__ import annotations

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QDialog


def restore_dialog_geometry(dialog: QDialog, key: str) -> None:
    settings = QSettings("ChromaPlot", "ChromaPlot")

    geometry = settings.value(f"dialogs/{key}/geometry")

    if geometry is not None:
        dialog.restoreGeometry(geometry)


def save_dialog_geometry(dialog: QDialog, key: str) -> None:
    settings = QSettings("ChromaPlot", "ChromaPlot")

    settings.setValue(
        f"dialogs/{key}/geometry",
        dialog.saveGeometry(),
    )