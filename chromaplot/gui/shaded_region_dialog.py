from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from chromaplot.core.models import Curve, Dataset


class ShadedRegionDialog(QDialog):
    """Dialog for creating/editing shaded regions."""

    select_on_plot_requested = pyqtSignal()
    fraction_visibility_changed = pyqtSignal(bool)

    def __init__(
        self,
        dataset: Dataset,
        curve: Curve,
        parent=None,
    ):
        super().__init__(parent)

        self.dataset = dataset
        self.curve = curve

        self.selected_color = curve.style.color

        self.setWindowTitle("Add Shaded Region")
        self.setMinimumWidth(420)

        self._build_ui()
        self._connect_signals()
        self._update_mode_visibility()

    # ------------------------------------------------------------------
    # UI setup
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:

        layout = QVBoxLayout(self)

        # --------------------------------------------------------------
        # General
        # --------------------------------------------------------------

        general_group = QGroupBox("General")
        general_form = QFormLayout(general_group)

        self.label_edit = QLineEdit()
        self.label_edit.setText(f"{self.curve.name} region")
        general_form.addRow("Label", self.label_edit)

        self.curve_label = QLabel(self.curve.name)
        general_form.addRow("Curve", self.curve_label)

        layout.addWidget(general_group)

        # --------------------------------------------------------------
        # Region definition
        # --------------------------------------------------------------

        region_group = QGroupBox("Region")
        region_layout = QVBoxLayout(region_group)

        mode_form = QFormLayout()

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(
            [
                "Volumes",
                "Fractions",
            ]
        )
        mode_form.addRow("Mode", self.mode_combo)

        region_layout.addLayout(mode_form)

        # --------------------------------------------------------------
        # Volume mode
        # --------------------------------------------------------------

        self.volume_widget = QWidget()
        volume_form = QFormLayout(self.volume_widget)

        self.start_volume_spin = QDoubleSpinBox()
        self.start_volume_spin.setRange(-1_000_000.0, 1_000_000.0)
        self.start_volume_spin.setDecimals(3)
        self.start_volume_spin.setSingleStep(0.1)

        self.end_volume_spin = QDoubleSpinBox()
        self.end_volume_spin.setRange(-1_000_000.0, 1_000_000.0)
        self.end_volume_spin.setDecimals(3)
        self.end_volume_spin.setSingleStep(0.1)

        volume_form.addRow("Start volume", self.start_volume_spin)
        volume_form.addRow("End volume", self.end_volume_spin)

        self.select_on_plot_button = QPushButton("Select on plot...")
        volume_form.addRow("", self.select_on_plot_button)

        region_layout.addWidget(self.volume_widget)

        # --------------------------------------------------------------
        # Fraction mode
        # --------------------------------------------------------------

        self.fraction_widget = QWidget()
        fraction_form = QFormLayout(self.fraction_widget)

        fraction_labels = [
            fraction.display_label or fraction.label
            for fraction in self.dataset.fractions_for_shading()
        ]

        self.start_fraction_combo = QComboBox()
        self.start_fraction_combo.addItems(fraction_labels)

        self.end_fraction_combo = QComboBox()
        self.end_fraction_combo.addItems(fraction_labels)

        fraction_form.addRow("Start fraction", self.start_fraction_combo)
        fraction_form.addRow("End fraction", self.end_fraction_combo)

        self.show_fraction_labels_check = QCheckBox("Show fraction labels on plot")

        self.show_fraction_labels_check.setChecked(
            self.dataset.fraction_label_settings.visible
        )

        fraction_form.addRow("", self.show_fraction_labels_check)

        region_layout.addWidget(self.fraction_widget)

        layout.addWidget(region_group)

        # --------------------------------------------------------------
        # Appearance
        # --------------------------------------------------------------

        appearance_group = QGroupBox("Appearance")
        appearance_form = QFormLayout(appearance_group)

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

        self.alpha_spin = QDoubleSpinBox()
        self.alpha_spin.setRange(0.0, 1.0)
        self.alpha_spin.setSingleStep(0.05)
        self.alpha_spin.setDecimals(2)
        self.alpha_spin.setValue(0.25)

        appearance_form.addRow("Alpha", self.alpha_spin)

        layout.addWidget(appearance_group)

        # --------------------------------------------------------------
        # Buttons
        # --------------------------------------------------------------

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )

        layout.addWidget(self.buttons)

        self._set_color_preview(self.selected_color)

    # ------------------------------------------------------------------
    # Signal connections
    # ------------------------------------------------------------------

    def _connect_signals(self) -> None:

        self.mode_combo.currentTextChanged.connect(
            self._update_mode_visibility
        )

        self.color_button.clicked.connect(
            self._choose_color
        )

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.select_on_plot_button.clicked.connect(
            self.select_on_plot_requested.emit
        )

        self.show_fraction_labels_check.toggled.connect(
            self._request_fraction_visibility_change
        )

    # ------------------------------------------------------------------
    # UI updates
    # ------------------------------------------------------------------

    def _update_mode_visibility(self) -> None:

        use_fractions = self.mode_combo.currentText() == "Fractions"

        self.volume_widget.setVisible(not use_fractions)
        self.fraction_widget.setVisible(use_fractions)

    def _set_color_preview(self, color: str) -> None:

        self.color_preview.setStyleSheet(
            f"""
            background-color: {color};
            border: 1px solid #666666;
            """
        )

    # ------------------------------------------------------------------
    # Colour selection
    # ------------------------------------------------------------------

    def _choose_color(self) -> None:

        color = QColorDialog.getColor(parent=self)

        if not color.isValid():
            return

        self.selected_color = color.name()
        self._set_color_preview(self.selected_color)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def region_data(self) -> dict | None:

        mode = self.mode_combo.currentText()

        # --------------------------------------------------------------
        # Manual volumes
        # --------------------------------------------------------------

        if mode == "Volumes":

            x_start = self.start_volume_spin.value()
            x_end = self.end_volume_spin.value()

        # --------------------------------------------------------------
        # Fractions
        # --------------------------------------------------------------

        else:

            result = self.dataset.fraction_volume_range(
                self.start_fraction_combo.currentText(),
                self.end_fraction_combo.currentText(),
            )

            if result is None:
                return None

            x_start, x_end = result

        if x_start > x_end:
            x_start, x_end = x_end, x_start

        return {
            "label": self.label_edit.text().strip(),
            "x_start": x_start,
            "x_end": x_end,
            "curve_id": self.curve.id,
            "curve_name": self.curve.name,
            "dataset_id": self.dataset.id,
            "color": self.selected_color,
            "alpha": self.alpha_spin.value(),
        }
    
    def set_volume_range(self, x_start: float, x_end: float) -> None:
        self.mode_combo.setCurrentText("Volumes")
        self.start_volume_spin.setValue(x_start)
        self.end_volume_spin.setValue(x_end)

    def _request_fraction_visibility_change(self, visible: bool) -> None:
        self.dataset.fraction_label_settings.visible = visible
        self.fraction_visibility_changed.emit(visible)