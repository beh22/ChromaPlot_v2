from __future__ import annotations

from pathlib import Path

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QLabel,
    QGroupBox,
    QScrollArea,
)

from chromaplot.core.models import Dataset

class DatasetSettingsPanel(QWidget):
    """Panel for inspecting/editing the selected dataset"""

    dataset_changed = pyqtSignal(str)
    dataset_remove_requested = pyqtSignal(str)
    show_all_curves_requested = pyqtSignal(str)
    hide_all_curves_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.dataset: Dataset | None = None
        self._updating = False

        self._build_ui()
        self._connect_signals()
        self.set_dataset(None)

    def _build_ui(self) -> None:
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content = QWidget()
        main_layout = QVBoxLayout(content)

        self.info_label = QLabel("Select a dataset to edit its settings.")
        self.info_label.setWordWrap(True)
        main_layout.addWidget(self.info_label)

        self.dataset_group = QGroupBox("Dataset")
        dataset_form = QFormLayout(self.dataset_group)

        self.name_edit = QLineEdit()
        dataset_form.addRow("Name", self.name_edit)

        self.source_file_label = QLabel("-")
        self.source_file_label.setWordWrap(True)
        dataset_form.addRow("Source file", self.source_file_label)

        self.source_path_label = QLabel("-")
        self.source_path_label.setWordWrap(True)
        dataset_form.addRow("Source path", self.source_path_label)

        self.importer_label = QLabel("-")
        dataset_form.addRow("Importer", self.importer_label)

        self.imported_at_label = QLabel("-")
        dataset_form.addRow("Imported", self.imported_at_label)

        self.curve_count_label = QLabel("-")
        dataset_form.addRow("Curves", self.curve_count_label)

        self.visible_curve_count_label = QLabel("-")
        dataset_form.addRow("Visible", self.visible_curve_count_label)

        main_layout.addWidget(self.dataset_group)

        self.actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout(self.actions_group)

        self.show_all_button = QPushButton("Show all curves")
        actions_layout.addWidget(self.show_all_button)

        self.hide_all_button = QPushButton("Hide all curves")
        actions_layout.addWidget(self.hide_all_button)

        self.remove_dataset_button = QPushButton("Remove dataset")
        actions_layout.addWidget(self.remove_dataset_button)

        main_layout.addWidget(self.actions_group)

        self.notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout(self.notes_group)

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Add notes about this dataset...")
        notes_layout.addWidget(self.notes_edit)

        main_layout.addWidget(self.notes_group)

        main_layout.addStretch()

        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

    def _connect_signals(self) -> None:
        self.name_edit.editingFinished.connect(self._apply_name)
        self.notes_edit.textChanged.connect(self._apply_notes)

        self.show_all_button.clicked.connect(self._request_show_all)
        self.hide_all_button.clicked.connect(self._request_hide_all)
        self.remove_dataset_button.clicked.connect(self._request_remove_dataset)

    def set_dataset(self, dataset: Dataset | None) -> None:
        self.dataset = dataset
        self._updating = True

        enabled = dataset is not None
        self.dataset_group.setEnabled(enabled)
        self.actions_group.setEnabled(enabled)
        self.notes_group.setEnabled(enabled)

        if dataset is None:
            self.info_label.setText("Select a dataset to edit its settings.")
            self.name_edit.setText("")
            self.source_file_label.setText("-")
            self.source_path_label.setText("-")
            self.importer_label.setText("-")
            self.imported_at_label.setText("-")
            self.curve_count_label.setText("-")
            self.visible_curve_count_label.setText("-")
            self.notes_edit.setPlainText("")
            self._updating = False
            return

        source_path = dataset.source.path if dataset.source else None
        source_file = Path(source_path).name if source_path else "-"

        n_curves = len(dataset.curves)
        n_visible = sum(1 for curve in dataset.curves if curve.visible)

        self.info_label.setText(f"Editing dataset: {dataset.name}")
        self.name_edit.setText(dataset.name)
        self.source_file_label.setText(source_file)
        self.source_path_label.setText(source_path or "-")
        self.importer_label.setText(dataset.source.importer if dataset.source else "-")
        self.imported_at_label.setText(dataset.source.imported_at if dataset.source else "-")
        self.curve_count_label.setText(str(n_curves))
        self.visible_curve_count_label.setText(str(n_visible))

        self.notes_edit.setPlainText(str(dataset.metadata.get("notes", "")))

        self._updating = False

    def _apply_name(self) -> None:
        if self._updating or self.dataset is None:
            return

        name = self.name_edit.text().strip()
        if not name:
            self.name_edit.setText(self.dataset.name)
            return

        self.dataset.name = name
        self.info_label.setText(f"Editing dataset: {self.dataset.name}")
        self.dataset_changed.emit(self.dataset.id)

    def _apply_notes(self) -> None:
        if self._updating or self.dataset is None:
            return

        self.dataset.metadata["notes"] = self.notes_edit.toPlainText()
        self.dataset_changed.emit(self.dataset.id)

    def _request_show_all(self) -> None:
        if self.dataset is not None:
            self.show_all_curves_requested.emit(self.dataset.id)

    def _request_hide_all(self) -> None:
        if self.dataset is not None:
            self.hide_all_curves_requested.emit(self.dataset.id)

    def _request_remove_dataset(self) -> None:
        if self.dataset is not None:
            self.dataset_remove_requested.emit(self.dataset.id)
