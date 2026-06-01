from __future__ import annotations

from PyQt5.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from chromaplot.core.models import Dataset


class FractionSettingsDialog(QDialog):
    """Dialog for customising fraction label display."""

    def __init__(self, dataset: Dataset, parent=None):
        super().__init__(parent)

        self.dataset = dataset
        self.settings = dataset.fraction_label_settings

        self.setWindowTitle("Configure Fraction Labels")

        self._build_ui()
        self._load_settings()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.visible_check = QCheckBox("Show fraction labels")
        form.addRow(self.visible_check)

        self.hide_when_dataset_hidden_check = QCheckBox(
            "Hide fractions when no curves from this dataset are visible"
        )
        form.addRow(self.hide_when_dataset_hidden_check)

        self.show_boundaries_check = QCheckBox("Show boundary lines")
        form.addRow(self.show_boundaries_check)

        self.show_labels_check = QCheckBox("Show labels")
        form.addRow(self.show_labels_check)

        self.label_mode_combo = QComboBox()
        self.label_mode_combo.addItems(["original", "sequential"])
        form.addRow("Label mode", self.label_mode_combo)

        self.hide_waste_check = QCheckBox("Hide waste fractions")
        form.addRow(self.hide_waste_check)

        self.hide_first_fraction_check = QCheckBox("Hide first fraction")
        form.addRow(self.hide_first_fraction_check)

        self.line_color_button = QPushButton("Choose line colour...")
        self.line_color_button.clicked.connect(self._choose_line_color)
        form.addRow("Line colour", self.line_color_button)

        self.line_style_combo = QComboBox()
        self.line_style_combo.addItems(["-", "--", ":", "-."])
        form.addRow("Line style", self.line_style_combo)

        self.line_width_spin = QDoubleSpinBox()
        self.line_width_spin.setRange(0.1, 10.0)
        self.line_width_spin.setSingleStep(0.1)
        form.addRow("Line width", self.line_width_spin)

        self.line_alpha_spin = QDoubleSpinBox()
        self.line_alpha_spin.setRange(0.0, 1.0)
        self.line_alpha_spin.setSingleStep(0.05)
        form.addRow("Line alpha", self.line_alpha_spin)

        self.line_height_spin = QDoubleSpinBox()
        self.line_height_spin.setRange(0.01, 1.0)
        self.line_height_spin.setSingleStep(0.01)
        form.addRow("Line height", self.line_height_spin)

        self.label_color_button = QPushButton("Choose text colour...")
        self.label_color_button.clicked.connect(self._choose_label_color)
        form.addRow("Text colour", self.label_color_button)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(4, 40)
        form.addRow("Text font size", self.font_size_spin)

        self.label_alpha_spin = QDoubleSpinBox()
        self.label_alpha_spin.setRange(0.0, 1.0)
        self.label_alpha_spin.setSingleStep(0.05)
        form.addRow("Text alpha", self.label_alpha_spin)

        self.label_height_spin = QDoubleSpinBox()
        self.label_height_spin.setRange(0.0, 1.0)
        self.label_height_spin.setSingleStep(0.05)
        form.addRow("Text relative height", self.label_height_spin)

        self.rotation_spin = QDoubleSpinBox()
        self.rotation_spin.setRange(-90.0, 90.0)
        self.rotation_spin.setSingleStep(5.0)
        form.addRow("Text rotation", self.rotation_spin)

        layout.addLayout(form)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.buttons.accepted.connect(self._accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def _load_settings(self) -> None:
        s = self.settings

        self.visible_check.setChecked(s.visible)
        self.show_boundaries_check.setChecked(s.show_boundaries)
        self.show_labels_check.setChecked(s.show_labels)
        self.label_mode_combo.setCurrentText(s.label_mode)
        self.hide_waste_check.setChecked(s.hide_waste)
        self.hide_first_fraction_check.setChecked(s.hide_first_fraction)
        self.line_style_combo.setCurrentText(s.line_style)
        self.line_width_spin.setValue(s.line_width)
        self.line_alpha_spin.setValue(s.line_alpha)
        self.line_height_spin.setValue(s.line_height_fraction)
        self.font_size_spin.setValue(s.label_font_size)
        self.rotation_spin.setValue(s.label_rotation)
        self.label_alpha_spin.setValue(s.label_alpha)
        self.label_height_spin.setValue(s.label_height_fraction)
        self.hide_when_dataset_hidden_check.setChecked(
            s.hide_when_dataset_hidden
        )

    def _choose_line_color(self) -> None:
        color = QColorDialog.getColor(parent=self)
        if color.isValid():
            self.settings.line_color = color.name()

    def _choose_label_color(self) -> None:
        color = QColorDialog.getColor(parent=self)
        if color.isValid():
            self.settings.label_color = color.name()

    def _accept(self) -> None:
        s = self.settings

        s.visible = self.visible_check.isChecked()
        s.show_boundaries = self.show_boundaries_check.isChecked()
        s.show_labels = self.show_labels_check.isChecked()
        s.label_mode = self.label_mode_combo.currentText()
        s.hide_waste = self.hide_waste_check.isChecked()
        s.hide_first_fraction = self.hide_first_fraction_check.isChecked()
        s.line_style = self.line_style_combo.currentText()
        s.line_width = self.line_width_spin.value()
        s.line_alpha = self.line_alpha_spin.value()
        s.line_height_fraction = self.line_height_spin.value()
        s.label_font_size = self.font_size_spin.value()
        s.label_rotation = self.rotation_spin.value()
        s.label_alpha = self.label_alpha_spin.value()
        s.label_height_fraction = self.label_height_spin.value()
        s.hide_when_dataset_hidden = (
            self.hide_when_dataset_hidden_check.isChecked()
        )

        self.accept()