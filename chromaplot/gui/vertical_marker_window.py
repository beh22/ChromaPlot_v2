from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtGui import QColor, QPainter, QPen

from chromaplot.core.models import Project
from chromaplot.core.plotting import vertical_marker_values

from .dialog_geometry import restore_dialog_geometry, save_dialog_geometry

class CurveStyleSample(QWidget):
    def __init__(self, curve, parent=None):
        super().__init__(parent)

        self.curve = curve

        self.setFixedSize(56, 24)
        self.setStyleSheet("background-color: white;")

    def paintEvent(self, event) -> None:
        painter = QPainter(self)

        painter.fillRect(self.rect(), QColor("white"))

        style = self.curve.style

        pen = QPen(QColor(style.color))

        pen.setWidthF(max(0.5, float(style.linewidth)))

        linestyle = str(style.linestyle)

        if linestyle == "--":
            pen.setStyle(Qt.DashLine)
        elif linestyle == ":":
            pen.setStyle(Qt.DotLine)
        elif linestyle == "-.":
            pen.setStyle(Qt.DashDotLine)
        else:
            pen.setStyle(Qt.SolidLine)

        painter.setPen(pen)

        y = self.height() // 2

        painter.drawLine(6, y, self.width() - 6, y)

        painter.end()


class VerticalMarkerWindow(QDialog):
    """A window showing the current vertical marker position and values"""

    position_changed = pyqtSignal(float)
    close_requested = pyqtSignal()
    appearance_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.project: Project | None = None
        self._updating_position = False

        self.setWindowTitle("Vertical Marker")
        self.setModal(False)

        self.selected_color = "#444444"

        self.position_spin = QDoubleSpinBox()
        self.position_spin.setDecimals(4)
        self.position_spin.setRange(-1e12, 1e12)
        self.position_spin.setSingleStep(0.1)
        self.position_spin.setKeyboardTracking(False)

        self.position_label = QLabel("Position")

        position_layout = QFormLayout()
        position_layout.addRow(self.position_label, self.position_spin)

        self.keyboard_hint = QLabel(
            "Use ← / → to move the marker when main window is focused; hold Shift for larger steps."
        )
        self.keyboard_hint.setStyleSheet("color: #666666; font-size: 12pt;")
        self.keyboard_hint.setAlignment(Qt.AlignCenter)
        self.keyboard_hint.setWordWrap(True)

        self.values_table = QTableWidget(0, 4)
        self.values_table.setHorizontalHeaderLabels(
            [
                "Dataset",
                "Curve",
                "",
                "Value",
            ]
        )

        self.values_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.values_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.values_table.setSelectionMode(QAbstractItemView.SingleSelection)

        self.values_table.verticalHeader().setVisible(False)

        header = self.values_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        self.values_table.setColumnWidth(2, 60)

        self.appearance_toggle = QToolButton()
        self.appearance_toggle.setText("Appearance")
        self.appearance_toggle.setCheckable(True)
        self.appearance_toggle.setChecked(False)
        self.appearance_toggle.setArrowType(Qt.RightArrow)
        self.appearance_toggle.setToolButtonStyle(
            Qt.ToolButtonTextBesideIcon
        )

        self.appearance_widget = QWidget()
        appearance_form = QFormLayout(self.appearance_widget)
        appearance_form.setContentsMargins(12, 0, 0, 0)

        color_row = QWidget()
        color_layout = QHBoxLayout(color_row)
        color_layout.setContentsMargins(0, 0, 0, 0)

        self.color_button = QPushButton("Choose colour...")
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(40, 20)

        color_layout.addWidget(self.color_button)
        color_layout.addWidget(self.color_preview)
        color_layout.addStretch()

        appearance_form.addRow("Colour", color_row)

        self.linewidth_spin = QDoubleSpinBox()
        self.linewidth_spin.setRange(0.1, 10.0)
        self.linewidth_spin.setDecimals(1)
        self.linewidth_spin.setSingleStep(0.1)
        self.linewidth_spin.setValue(1.0)

        appearance_form.addRow("Line width", self.linewidth_spin)

        self.linestyle_combo = QComboBox()
        self.linestyle_combo.addItem("Solid", "-")
        self.linestyle_combo.addItem("Dashed", "--")
        self.linestyle_combo.addItem("Dotted", ":")
        self.linestyle_combo.addItem("Dash-dot", "-.")

        appearance_form.addRow("Line style", self.linestyle_combo)

        self.alpha_spin = QDoubleSpinBox()
        self.alpha_spin.setRange(0.0, 1.0)
        self.alpha_spin.setDecimals(2)
        self.alpha_spin.setSingleStep(0.05)
        self.alpha_spin.setValue(1.0)

        appearance_form.addRow("Alpha", self.alpha_spin)

        self.include_export_check = QCheckBox("Include marker in exported figure")

        appearance_form.addRow("", self.include_export_check)

        self._set_color_preview(self.selected_color)

        self.reset_appearance_button = QPushButton("Reset appearance")

        appearance_form.addRow("", self.reset_appearance_button)

        # Start collapsed
        self.appearance_widget.setVisible(False)

        layout = QVBoxLayout(self)
        layout.addLayout(position_layout)
        layout.addWidget(self.keyboard_hint)
        layout.addWidget(self.values_table)
        layout.addWidget(self.appearance_toggle)
        layout.addWidget(self.appearance_widget)

        self.position_spin.valueChanged.connect(self._on_position_changed)

        self.appearance_toggle.toggled.connect(self._toggle_appearance)

        self.color_button.clicked.connect(self._choose_color)
        self.linewidth_spin.valueChanged.connect(self.appearance_changed.emit)
        self.linestyle_combo.currentIndexChanged.connect(self.appearance_changed.emit)
        self.alpha_spin.valueChanged.connect(self.appearance_changed.emit)
        self.include_export_check.toggled.connect(self.appearance_changed.emit)
        self.reset_appearance_button.clicked.connect(self._reset_appearance)

        self.resize(420, 300)

        restore_dialog_geometry(self, "vertical_marker")

    def set_project(self, project: Project) -> None:
        self.project = project
        self.refresh()

    def set_position(self, x: float) -> None:
        """
        Update the displayed marker position without emitting position_changed back to plot
        """

        self._updating_position = True

        try:
            self.position_spin.setValue(float(x))
        finally:
            self._updating_position = False

        self.refresh_values()

    def set_position_range(
            self,
            xmin: float,
            xmax: float,
    ) -> None:
        lower, upper = sorted((float(xmin), float(xmax)))

        self.position_spin.setRange(lower, upper)

        span = upper - lower

        if span > 0:
            self.position_spin.setSingleStep(span / 500.0)

    def refresh(self) -> None:
        if self.project is None:
            self.values_table.setRowCount(0)
            return

        marker = self.project.vertical_marker()

        if marker is None:
            self.values_table.setRowCount(0)
            return

        x_label = self.project.plot_settings.x_label.strip()

        if x_label:
            self.position_label.setText(x_label)
        else:
            self.position_label.setText("Position")

        try:
            x = float(marker.data["x"])
        except (KeyError, TypeError, ValueError):
            return

        self.set_position(x)
        self._load_marker_appearance(marker)

    def refresh_values(self) -> None:
        if self.project is None:
            self.values_table.setRowCount(0)
            return

        x = self.position_spin.value()

        values = vertical_marker_values(self.project, x)

        self.values_table.setRowCount(len(values))

        for row, (dataset, curve, value) in enumerate(values):
            dataset_item = QTableWidgetItem(dataset.name)
            curve_item = QTableWidgetItem(curve.name)

            if value is None:
                value_text = "—"
            else:
                value_text = f"{value:.6g}"

                if curve.y_unit:
                    value_text += f" {curve.y_unit}"

            value_item = QTableWidgetItem(value_text)
            value_item.setTextAlignment(
                Qt.AlignRight | Qt.AlignVCenter
            )

            self.values_table.setItem(row, 0, dataset_item)
            self.values_table.setItem(row, 1, curve_item)

            style_sample = CurveStyleSample(curve, self.values_table)
            self.values_table.setCellWidget(row, 2, style_sample)

            self.values_table.setItem(row, 3, value_item)

    def _on_position_changed(self, value: float) -> None:
        if self._updating_position:
            return

        self.position_changed.emit(float(value))

    def showEvent(self, event) -> None:
        super().showEvent(event)

        self._restore_geometry_and_collapse

    def _restore_geometry_and_collapse(self) -> None:
        restore_dialog_geometry(
            self,
            "vertical_marker",
        )

        self.appearance_toggle.setChecked(False)
        self.appearance_widget.setVisible(False)
        self.appearance_toggle.setArrowType(Qt.RightArrow)

        self.adjustSize()

    def hideEvent(self, event) -> None:
        save_dialog_geometry(
            self,
            "vertical_marker",
        )

        super().hideEvent(event)

    def closeEvent(self, event) -> None:
        save_dialog_geometry(
            self,
            "vertical_marker",
        )

        self.close_requested.emit()
        super().closeEvent(event)

    def _set_color_preview(self, color: str) -> None:
        self.color_preview.setStyleSheet(
            f"background-color: {color}; border: 1px solid #666666;"
        )

    def _choose_color(self) -> None:
        color = QColorDialog.getColor(parent=self)

        if not color.isValid():
            return

        self.selected_color = color.name()
        self._set_color_preview(self.selected_color)

        self.appearance_changed.emit()

    def _load_marker_appearance(
        self,
        marker,
    ) -> None:
        self.selected_color = str(
            marker.style.get(
                "color",
                "#444444",
            )
        )

        self._set_color_preview(
            self.selected_color
        )

        self.linewidth_spin.blockSignals(True)
        self.linestyle_combo.blockSignals(True)
        self.alpha_spin.blockSignals(True)
        self.include_export_check.blockSignals(True)

        try:
            self.linewidth_spin.setValue(float(marker.style.get("linewidth", 1.0)))

            linestyle = str(marker.style.get("linestyle","--"))

            index = self.linestyle_combo.findData(linestyle)

            if index >= 0:
                self.linestyle_combo.setCurrentIndex(index)

            self.alpha_spin.setValue(float(marker.style.get("alpha", 1.0)))

            self.include_export_check.setChecked(bool(marker.data.get("include_in_export", False)))

        finally:
            self.linewidth_spin.blockSignals(False)
            self.linestyle_combo.blockSignals(False)
            self.alpha_spin.blockSignals(False)
            self.include_export_check.blockSignals(False)

    def appearance_data(self) -> dict:
        return {
            "color": self.selected_color,
            "linewidth": float(self.linewidth_spin.value()),
            "linestyle": str(
                self.linestyle_combo.currentData()
            ),
            "alpha": float(self.alpha_spin.value()),
            "include_in_export": bool(
                self.include_export_check.isChecked()
            ),
        }

    def _toggle_appearance(self, expanded: bool) -> None:
        self.appearance_widget.setVisible(expanded)

        if expanded:
            self.appearance_toggle.setArrowType(Qt.DownArrow)
        else:
            self.appearance_toggle.setArrowType(Qt.RightArrow)

        # self.adjustSize()

    def _reset_appearance(self) -> None:
        self.selected_color = "#444444"
        self._set_color_preview(self.selected_color)

        self.linewidth_spin.setValue(1.0)

        index = self.linestyle_combo.findData("--")
        if index >= 0:
            self.linestyle_combo.setCurrentIndex(index)

        self.alpha_spin.setValue(1.0)

        self.include_export_check.setChecked(False)

        self.appearance_changed.emit()