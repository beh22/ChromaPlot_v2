from __future__ import annotations

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QCheckBox,
    QPushButton,
    QColorDialog,
    QDoubleSpinBox,
    QComboBox,
    QLabel,
    QGroupBox,
    QScrollArea,
)

from chromaplot.core.models import Curve


class CurveSettingsPanel(QWidget):
    """Panel for editing the selected curve."""

    curve_changed = pyqtSignal(str)
    add_shaded_region_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.curve: Curve | None = None
        self.dataset_name: str | None = None
        self._updating = False

        self._build_ui()
        self._connect_signals()
        self.set_curve(None)

    # ------------------------------------------------------------------
    # UI setup
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QWidget()
        main_layout = QVBoxLayout(content)

        self.info_label = QLabel("Select a curve to edit its settings.")
        self.info_label.setWordWrap(True)
        main_layout.addWidget(self.info_label)

        self.curve_group = QGroupBox("Curve")
        curve_form = QFormLayout(self.curve_group)

        self.name_edit = QLineEdit()
        curve_form.addRow("Name", self.name_edit)

        self.visible_check = QCheckBox("Visible")
        curve_form.addRow("", self.visible_check)

        self.dataset_label = QLabel("-")
        curve_form.addRow("Dataset", self.dataset_label)

        self.curve_type_label = QLabel("-")
        curve_form.addRow("Type", self.curve_type_label)

        self.x_label = QLabel("-")
        curve_form.addRow("X", self.x_label)

        self.y_label = QLabel("-")
        curve_form.addRow("Y", self.y_label)

        main_layout.addWidget(self.curve_group)

        self.style_group = QGroupBox("Style")
        style_form = QFormLayout(self.style_group)

        self.color_button = QPushButton("Choose colour")
        self.color_preview = QLabel()
        self.color_preview.setFixedHeight(20)
        style_form.addRow("Colour", self.color_button)
        style_form.addRow("Preview", self.color_preview)

        self.linewidth_spin = QDoubleSpinBox()
        self.linewidth_spin.setRange(0.1, 20.0)
        self.linewidth_spin.setSingleStep(0.1)
        self.linewidth_spin.setDecimals(2)
        style_form.addRow("Line width", self.linewidth_spin)

        self.linestyle_combo = QComboBox()
        self.linestyle_combo.addItems(["-", "--", "-.", ":", "None"])
        style_form.addRow("Line style", self.linestyle_combo)

        self.alpha_spin = QDoubleSpinBox()
        self.alpha_spin.setRange(0.0, 1.0)
        self.alpha_spin.setSingleStep(0.05)
        self.alpha_spin.setDecimals(2)
        style_form.addRow("Alpha", self.alpha_spin)

        main_layout.addWidget(self.style_group)

        self.transform_group = QGroupBox("Display transform")
        transform_form = QFormLayout(self.transform_group)

        self.x_offset_spin = QDoubleSpinBox()
        self.x_offset_spin.setRange(-1_000_000.0, 1_000_000.0)
        self.x_offset_spin.setSingleStep(0.1)
        self.x_offset_spin.setDecimals(4)
        transform_form.addRow("X offset", self.x_offset_spin)

        self.y_offset_spin = QDoubleSpinBox()
        self.y_offset_spin.setRange(-1_000_000.0, 1_000_000.0)
        self.y_offset_spin.setSingleStep(0.1)
        self.y_offset_spin.setDecimals(4)
        transform_form.addRow("Y offset", self.y_offset_spin)

        self.x_scale_spin = QDoubleSpinBox()
        self.x_scale_spin.setRange(-1_000_000.0, 1_000_000.0)
        self.x_scale_spin.setSingleStep(0.1)
        self.x_scale_spin.setDecimals(4)
        transform_form.addRow("X scale", self.x_scale_spin)

        self.y_scale_spin = QDoubleSpinBox()
        self.y_scale_spin.setRange(-1_000_000.0, 1_000_000.0)
        self.y_scale_spin.setSingleStep(0.1)
        self.y_scale_spin.setDecimals(4)
        transform_form.addRow("Y scale", self.y_scale_spin)

        self.reset_transform_button = QPushButton("Reset transform")
        transform_form.addRow("", self.reset_transform_button)

        main_layout.addWidget(self.transform_group)

        self.shading_group = QGroupBox("Shading")
        shading_layout = QVBoxLayout(self.shading_group)

        self.add_shaded_region_button = QPushButton("Add shaded region...")
        shading_layout.addWidget(self.add_shaded_region_button)

        main_layout.addWidget(self.shading_group)

        main_layout.addStretch()

        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

    def _connect_signals(self) -> None:
        self.name_edit.editingFinished.connect(self._apply_name)
        self.visible_check.stateChanged.connect(self._apply_all)
        self.color_button.clicked.connect(self._choose_color)
        self.linewidth_spin.valueChanged.connect(self._apply_all)
        self.linestyle_combo.currentTextChanged.connect(self._apply_all)
        self.alpha_spin.valueChanged.connect(self._apply_all)
        self.x_offset_spin.valueChanged.connect(self._apply_all)
        self.y_offset_spin.valueChanged.connect(self._apply_all)
        self.x_scale_spin.valueChanged.connect(self._apply_all)
        self.y_scale_spin.valueChanged.connect(self._apply_all)
        self.reset_transform_button.clicked.connect(self._reset_transform)
        self.add_shaded_region_button.clicked.connect(self._request_add_shaded_region)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_curve(self,
                  curve: Curve | None,
                  dataset_name: str | None = None,
        ) -> None:
        """Load a curve into the panel, or disable the panel if None."""
        self.curve = curve
        self.dataset_name = dataset_name
        self._updating = True

        enabled = curve is not None
        self.curve_group.setEnabled(enabled)
        self.style_group.setEnabled(enabled)
        self.transform_group.setEnabled(enabled)
        self.shading_group.setEnabled(enabled)

        if curve is None:
            self.info_label.setText("Select a curve to edit its settings.")
            self.name_edit.setText("")
            self.visible_check.setChecked(False)
            self.curve_type_label.setText("-")
            self.x_label.setText("-")
            self.y_label.setText("-")
            self.dataset_label.setText("-")
            self._set_color_preview("#ffffff")
            self._updating = False
            return

        self.info_label.setText(f"Editing: {curve.name}")
        self.name_edit.setText(curve.name)
        self.visible_check.setChecked(curve.visible)
        self.curve_type_label.setText(str(curve.metadata.get("curve_type", "unknown")))
        self.x_label.setText(f"{curve.x_label} ({curve.x_unit})")
        self.y_label.setText(f"{curve.y_label} ({curve.y_unit})")
        self.dataset_label.setText(dataset_name or "-")
        self._set_color_preview(curve.style.color)
        self.linewidth_spin.setValue(curve.style.linewidth)
        self.linestyle_combo.setCurrentText(curve.style.linestyle)
        self.alpha_spin.setValue(curve.style.alpha)

        self.x_offset_spin.setValue(curve.transform.x_offset)
        self.y_offset_spin.setValue(curve.transform.y_offset)
        self.x_scale_spin.setValue(curve.transform.x_scale)
        self.y_scale_spin.setValue(curve.transform.y_scale)

        self._updating = False

    def refresh_visibility(self, curve_id: str, visible: bool) -> None:
        if self.curve is None or self.curve.id != curve_id:
            return
        
        self._updating = True

        try:
            self.visible_check.setChecked(visible)
        finally:
            self._updating = False

    # ------------------------------------------------------------------
    # Internal update methods
    # ------------------------------------------------------------------

    def _apply_name(self) -> None:
        if self._updating or self.curve is None:
            return

        name = self.name_edit.text().strip()
        if not name:
            self.name_edit.setText(self.curve.name)
            return

        self.curve.name = name
        self.info_label.setText(f"Editing: {self.curve.name}")
        self.curve_changed.emit(self.curve.id)

    def _apply_all(self) -> None:
        if self._updating or self.curve is None:
            return

        self.curve.visible = self.visible_check.isChecked()

        self.curve.style.linewidth = self.linewidth_spin.value()
        self.curve.style.linestyle = self.linestyle_combo.currentText()
        self.curve.style.alpha = self.alpha_spin.value()

        self.curve.transform.x_offset = self.x_offset_spin.value()
        self.curve.transform.y_offset = self.y_offset_spin.value()
        self.curve.transform.x_scale = self.x_scale_spin.value()
        self.curve.transform.y_scale = self.y_scale_spin.value()

        self.curve_changed.emit(self.curve.id)

    def _choose_color(self) -> None:
        if self._updating or self.curve is None:
            return

        color = QColorDialog.getColor(parent=self)
        if not color.isValid():
            return

        color_hex = color.name()
        self.curve.style.color = color_hex
        self._set_color_preview(color_hex)
        self.curve_changed.emit(self.curve.id)

    def _reset_transform(self) -> None:
        if self._updating or self.curve is None:
            return

        self.curve.reset_transform()
        self.set_curve(self.curve, self.dataset_name)
        self.curve_changed.emit(self.curve.id)

    def _set_color_preview(self, color: str) -> None:
        self.color_preview.setStyleSheet(
            f"background-color: {color}; border: 1px solid #666;"
        )

    def _request_add_shaded_region(self) -> None:
        if self.curve is not None:
            self.add_shaded_region_requested.emit(self.curve.id)
