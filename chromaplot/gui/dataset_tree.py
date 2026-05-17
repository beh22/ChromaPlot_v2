from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem

from chromaplot.core.models import Project


class DatasetTreeWidget(QTreeWidget):
    """
    Tree view showing datasets and curves.

    Dataset items are top-level items. Curve items are children with checkboxes
    controlling curve visibility.
    """

    curve_visibility_changed = pyqtSignal(str, bool)
    curve_selected = pyqtSignal(str)
    dataset_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.project: Project | None = None
        self._updating = False

        self.setHeaderLabels(["Datasets / Curves"])
        self.itemChanged.connect(self._on_item_changed)
        self.itemSelectionChanged.connect(self._on_selection_changed)

    def set_project(self, project: Project) -> None:
        """Rebuild the tree from a Project object."""
        self.project = project
        self._updating = True
        self.clear()

        for dataset in project.datasets:
            dataset_item = QTreeWidgetItem([dataset.name])
            dataset_item.setData(0, Qt.UserRole, {"type": "dataset", "id": dataset.id})
            dataset_item.setFlags(dataset_item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.addTopLevelItem(dataset_item)

            for curve in dataset.curves:
                curve_item = QTreeWidgetItem([curve.name])
                curve_item.setData(0, Qt.UserRole, {"type": "curve", "id": curve.id})
                curve_item.setFlags(
                    curve_item.flags()
                    | Qt.ItemIsUserCheckable
                    | Qt.ItemIsSelectable
                    | Qt.ItemIsEnabled
                )
                curve_item.setCheckState(0, Qt.Checked if curve.visible else Qt.Unchecked)
                dataset_item.addChild(curve_item)

            dataset_item.setExpanded(True)

        self._updating = False

    def _on_item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        if self._updating:
            return

        item_data = item.data(0, Qt.UserRole)
        if not isinstance(item_data, dict):
            return

        if item_data.get("type") != "curve":
            return

        curve_id = item_data.get("id")
        visible = item.checkState(0) == Qt.Checked
        self.curve_visibility_changed.emit(curve_id, visible)

    def _on_selection_changed(self) -> None:
        items = self.selectedItems()
        if not items:
            return

        item_data = items[0].data(0, Qt.UserRole)
        if not isinstance(item_data, dict):
            return

        item_type = item_data.get("type")
        item_id = item_data.get("id")

        if item_type == "curve":
            self.curve_selected.emit(item_id)
        elif item_type == "dataset":
            self.dataset_selected.emit(item_id)