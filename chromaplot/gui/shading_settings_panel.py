from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QPushButton,
    QHBoxLayout,
    QLabel,
)

from chromaplot.core.models import Project


class ShadingSettingsPanel(QWidget):
    """Panel for managing shaded regions in the project."""

    edit_region_requested = pyqtSignal(str)
    remove_region_requested = pyqtSignal(str)
    visibility_changed = pyqtSignal(str, bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.project: Project | None = None

        self._build_ui()
        self._connect_signals()

    # ------------------------------------------------------------------
    # UI setup
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:

        layout = QVBoxLayout(self)

        self.info_label = QLabel(
            "Manage shaded regions across the project."
        )
        self.info_label.setWordWrap(True)

        layout.addWidget(self.info_label)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(1)
        self.tree.setHeaderLabels(["Shaded Regions"])

        layout.addWidget(self.tree)

        button_row = QHBoxLayout()

        self.edit_button = QPushButton("Edit")
        self.remove_button = QPushButton("Remove")

        button_row.addWidget(self.edit_button)
        button_row.addWidget(self.remove_button)

        layout.addLayout(button_row)

    def _connect_signals(self) -> None:

        self.remove_button.clicked.connect(
            self._emit_remove_selected
        )

        self.edit_button.clicked.connect(
            self._emit_edit_selected
        )

        self.tree.itemChanged.connect(
            self._on_item_changed
        )

    def set_project(self, project: Project | None) -> None:

        self.project = project
        self.refresh()

    def refresh(self) -> None:

        self.tree.clear()

        if self.project is None:
            return

        dataset_items: dict[str, QTreeWidgetItem] = {}
        curve_items: dict[tuple[str, str], QTreeWidgetItem] = {}

        for annotation in self.project.shaded_regions():

            dataset_name = annotation.data.get(
                "dataset_name",
                annotation.data.get("dataset_id", "Dataset")
            )

            curve_name = annotation.data.get(
                "curve_name",
                annotation.data.get("curve_id", "Curve")
            )

            label = annotation.data.get("label", "Region")

            # ----------------------------------------------------------
            # Dataset item
            # ----------------------------------------------------------

            if dataset_name not in dataset_items:

                dataset_item = QTreeWidgetItem([dataset_name])

                dataset_item.setFlags(
                    Qt.ItemIsEnabled
                )

                self.tree.addTopLevelItem(dataset_item)

                dataset_items[dataset_name] = dataset_item

            dataset_item = dataset_items[dataset_name]

            # ----------------------------------------------------------
            # Curve item
            # ----------------------------------------------------------

            curve_key = (dataset_name, curve_name)

            if curve_key not in curve_items:

                curve_item = QTreeWidgetItem([curve_name])

                curve_item.setFlags(
                    Qt.ItemIsEnabled
                )

                dataset_item.addChild(curve_item)

                curve_items[curve_key] = curve_item

            curve_item = curve_items[curve_key]

            # ----------------------------------------------------------
            # Region item
            # ----------------------------------------------------------

            region_item = QTreeWidgetItem([label])

            region_item.setData(
                0,
                Qt.UserRole,
                annotation.id,
            )

            region_item.setFlags(
                Qt.ItemIsEnabled
                | Qt.ItemIsSelectable
                | Qt.ItemIsUserCheckable
            )

            region_item.setCheckState(
                0,
                Qt.Checked if annotation.visible else Qt.Unchecked
            )

            curve_item.addChild(region_item)

        self.tree.expandAll()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def selected_annotation_id(self) -> str | None:
        item = self.tree.currentItem()
        if item is None:
            return None
        annotation_id = item.data(0, Qt.UserRole)

        if annotation_id is None:
            return None
        return str(annotation_id)

    # ------------------------------------------------------------------
    # Signal emitters
    # ------------------------------------------------------------------

    def _emit_remove_selected(self) -> None:
        annotation_id = self.selected_annotation_id()
        if annotation_id is None:
            return
        self.remove_region_requested.emit(annotation_id)

    def _emit_edit_selected(self) -> None:
        annotation_id = self.selected_annotation_id()
        if annotation_id is None:
            return
        self.edit_region_requested.emit(annotation_id)

    def _on_item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        annotation_id = item.data(0, Qt.UserRole)
        if annotation_id is None:
            return

        visible = item.checkState(0) == Qt.Checked
        self.visibility_changed.emit(
            str(annotation_id),
            visible,
        )