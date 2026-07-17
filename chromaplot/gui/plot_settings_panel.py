from __future__ import annotations

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QCheckBox,
    QDoubleSpinBox,
    QSpinBox,
    QComboBox,
    QPushButton,
    QLabel,
    QGroupBox,
    QScrollArea,
    QFontComboBox,
    QHBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from chromaplot.core.models import PlotSettings

import math

MAX_MAJOR_TICKS = 50
MAX_MINOR_TICKS = 200


class PlotSettingsPanel(QWidget):
    """Panel for editing project-level plot settings."""

    plot_settings_changed = pyqtSignal()
    autoscale_requested = pyqtSignal()
    use_preview_size_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.settings: PlotSettings | None = None
        self._updating = False

        self._current_xlim: tuple[float, float] | None = None
        self._current_ylim: tuple[float, float] | None = None

        self._build_ui()
        self._connect_signals()
        self.set_plot_settings(None)

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

        self.info_label = QLabel("Plot settings apply to the full project.")
        self.info_label.setWordWrap(True)
        main_layout.addWidget(self.info_label)

        # -------------------------
        # Labels
        # -------------------------
        self.labels_group = QGroupBox("Labels")
        labels_form = QFormLayout(self.labels_group)

        self.title_edit = QLineEdit()
        labels_form.addRow("Title", self.title_edit)

        self.x_label_edit = QLineEdit()
        labels_form.addRow("X label", self.x_label_edit)

        self.y_label_edit = QLineEdit()
        labels_form.addRow("Y label", self.y_label_edit)

        main_layout.addWidget(self.labels_group)

        # -------------------------
        # Axis limits
        # -------------------------
        self.limits_group = QGroupBox("Axis limits")
        limits_form = QFormLayout(self.limits_group)

        self.use_xlim_check = QCheckBox("Use manual X limits")
        limits_form.addRow("", self.use_xlim_check)

        self.xmin_spin = self._make_limit_spinbox()
        self.xmax_spin = self._make_limit_spinbox()
        limits_form.addRow("X min", self.xmin_spin)
        limits_form.addRow("X max", self.xmax_spin)

        self.use_ylim_check = QCheckBox("Use manual Y limits")
        limits_form.addRow("", self.use_ylim_check)

        self.ymin_spin = self._make_limit_spinbox()
        self.ymax_spin = self._make_limit_spinbox()
        limits_form.addRow("Y min", self.ymin_spin)
        limits_form.addRow("Y max", self.ymax_spin)

        self.autoscale_button = QPushButton("Autoscale visible curves")
        limits_form.addRow("", self.autoscale_button)

        main_layout.addWidget(self.limits_group)

        # -------------------------
        # Figure size
        # -------------------------
        self.figure_group = QGroupBox("Export figure size")
        figure_form = QFormLayout(self.figure_group)

        self.figure_width_spin = QDoubleSpinBox()
        self.figure_width_spin.setRange(1.0, 50.0)
        self.figure_width_spin.setSingleStep(0.1)
        self.figure_width_spin.setDecimals(2)
        self.figure_width_spin.setSuffix(" in")
        figure_form.addRow("Width", self.figure_width_spin)

        self.figure_height_spin = QDoubleSpinBox()
        self.figure_height_spin.setRange(1.0, 50.0)
        self.figure_height_spin.setSingleStep(0.1)
        self.figure_height_spin.setDecimals(2)
        self.figure_height_spin.setSuffix(" in")
        figure_form.addRow("Height", self.figure_height_spin)

        self.current_preview_size_label = QLabel("Current preview: -")
        figure_form.addRow("", self.current_preview_size_label)

        self.use_preview_size_button = QPushButton("Use current preview size")
        figure_form.addRow("", self.use_preview_size_button)

        main_layout.addWidget(self.figure_group)

        # -------------------------
        # Legend / display
        # -------------------------
        self.display_group = QGroupBox("Display")
        display_form = QFormLayout(self.display_group)

        self.show_legend_check = QCheckBox("Show legend")
        display_form.addRow("", self.show_legend_check)

        self.legend_location_combo = QComboBox()
        self.legend_location_combo.addItems(
            [
                "best",
                "outside top",
                "upper right",
                "upper left",
                "lower left",
                "lower right",
                "right",
                "center left",
                "center right",
                "lower center",
                "upper center",
                "center",
            ]
        )
        display_form.addRow("Legend", self.legend_location_combo)

        self.legend_label_mode_combo = QComboBox()
        self.legend_label_mode_combo.addItems(
            ["auto", "curve", "dataset", "dataset_curve"]
        )
        display_form.addRow("Legend labels", self.legend_label_mode_combo)

        self.legend_bbox_widget = QWidget()
        bbox_form = QFormLayout(self.legend_bbox_widget)
        bbox_form.setContentsMargins(0, 0, 0, 0)

        self.legend_bbox_x_spin = QDoubleSpinBox()
        self.legend_bbox_x_spin.setRange(-5.0, 5.0)
        self.legend_bbox_x_spin.setSingleStep(0.01)
        self.legend_bbox_x_spin.setDecimals(3)
        bbox_form.addRow("Legend X", self.legend_bbox_x_spin)

        self.legend_bbox_y_spin = QDoubleSpinBox()
        self.legend_bbox_y_spin.setRange(-5.0, 5.0)
        self.legend_bbox_y_spin.setSingleStep(0.01)
        self.legend_bbox_y_spin.setDecimals(3)
        bbox_form.addRow("Legend Y", self.legend_bbox_y_spin)

        self.legend_columns_spin = QSpinBox()
        self.legend_columns_spin.setRange(1, 20)
        bbox_form.addRow("Legend columns", self.legend_columns_spin)

        display_form.addRow(self.legend_bbox_widget)

        self.grid_check = QCheckBox("Show grid")
        display_form.addRow("", self.grid_check)

        self.clean_plot_check = QCheckBox("Clean plot style")
        display_form.addRow("", self.clean_plot_check)

        main_layout.addWidget(self.display_group)

        # -------------------------
        # Fonts
        # -------------------------
        
        self.font_group = QGroupBox("Fonts")
        font_form = QFormLayout(self.font_group)

        self.font_family_combo = QFontComboBox()
        self.font_family_combo.setMaximumWidth(140)
        font_form.addRow("Font", self.font_family_combo)

        self.title_font_spin = self._make_font_spinbox()
        font_form.addRow("Title", self.title_font_spin)

        self.axis_font_spin = self._make_font_spinbox()
        font_form.addRow("Axis labels", self.axis_font_spin)

        self.tick_font_spin = self._make_font_spinbox()
        font_form.addRow("Tick labels", self.tick_font_spin)

        self.legend_font_spin = self._make_font_spinbox()
        font_form.addRow("Legend", self.legend_font_spin)

        main_layout.addWidget(self.font_group)

        # -------------------------
        # Ticks
        # -------------------------
        self.tick_group = QGroupBox("Ticks")
        tick_form = QFormLayout(self.tick_group)

        tick_visibility_widget = QWidget()
        tick_visibility_layout = QHBoxLayout(tick_visibility_widget)

        tick_visibility_layout.setContentsMargins(0, 0, 0, 0)
        tick_visibility_layout.setSpacing(12)
        tick_visibility_layout.setAlignment(Qt.AlignCenter)

        self.major_ticks_check = QCheckBox("Major")
        tick_visibility_layout.addWidget(self.major_ticks_check)

        self.minor_ticks_check = QCheckBox("Minor")
        tick_visibility_layout.addWidget(self.minor_ticks_check)

        tick_form.addRow(tick_visibility_widget)

        self.tick_direction_combo = QComboBox()
        self.tick_direction_combo.addItems(["out", "in", "inout"])
        tick_form.addRow("Direction", self.tick_direction_combo)

        (
            self.x_major_spacing_widget,
            self.x_major_spacing_spin,
            self.x_major_spacing_auto_button,
        ) = self._make_tick_spacing_control()
        tick_form.addRow("X major spacing", self.x_major_spacing_widget)

        (
            self.x_minor_spacing_widget,
            self.x_minor_spacing_spin,
            self.x_minor_spacing_auto_button,
        ) = self._make_tick_spacing_control()
        tick_form.addRow("X minor spacing", self.x_minor_spacing_widget)

        (
            self.y_major_spacing_widget,
            self.y_major_spacing_spin,
            self.y_major_spacing_auto_button,
        ) = self._make_tick_spacing_control()
        tick_form.addRow("Y major spacing", self.y_major_spacing_widget)

        (
            self.y_minor_spacing_widget,
            self.y_minor_spacing_spin,
            self.y_minor_spacing_auto_button,
        ) = self._make_tick_spacing_control()
        tick_form.addRow("Y minor spacing", self.y_minor_spacing_widget)

        self.reset_tick_spacing_button = QPushButton(
            "Reset all spacing to Auto"
        )
        tick_form.addRow("", self.reset_tick_spacing_button)

        self.major_tick_length_spin = QDoubleSpinBox()
        self.major_tick_length_spin.setRange(0.0, 50.0)
        self.major_tick_length_spin.setValue(6.0)
        tick_form.addRow("Major tick length", self.major_tick_length_spin)

        self.minor_tick_length_spin = QDoubleSpinBox()
        self.minor_tick_length_spin.setRange(0.0, 50.0)
        self.minor_tick_length_spin.setValue(3.0)
        tick_form.addRow("Minor tick length", self.minor_tick_length_spin)

        main_layout.addWidget(self.tick_group)

        # --------------------------
        # Misc
        # --------------------------

        self.misc_group = QGroupBox("Misc")
        misc_form = QFormLayout(self.misc_group)

        self.plot_xkcd_check = QCheckBox("Significantly improve plot")
        misc_form.addRow("", self.plot_xkcd_check)

        main_layout.addWidget(self.misc_group)

        main_layout.addStretch()

        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

    def _make_limit_spinbox(self) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(-1_000_000.0, 1_000_000.0)
        spin.setSingleStep(0.1)
        spin.setDecimals(4)
        return spin

    def _make_font_spinbox(self) -> QSpinBox:
        spin = QSpinBox()
        spin.setRange(1, 100)
        spin.setSingleStep(1)
        return spin
    
    def _make_tick_spacing_control(
        self,
    ) -> tuple[QWidget, QDoubleSpinBox, QPushButton]:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        spin = QDoubleSpinBox()
        spin.setRange(0.0, 1_000_000.0)
        spin.setDecimals(4)
        spin.setSpecialValueText("Auto")
        spin.setKeyboardTracking(False)
        spin.setSingleStep(1.0)
        

        auto_button = QPushButton("Auto")
        auto_button.setMaximumWidth(55)

        layout.addWidget(spin)
        layout.addWidget(auto_button)

        return widget, spin, auto_button

    def _connect_signals(self) -> None:
        self.title_edit.editingFinished.connect(self._apply_all)
        self.x_label_edit.editingFinished.connect(self._apply_all)
        self.y_label_edit.editingFinished.connect(self._apply_all)

        self.use_xlim_check.stateChanged.connect(self._apply_all)
        self.xmin_spin.valueChanged.connect(self._apply_all)
        self.xmax_spin.valueChanged.connect(self._apply_all)
        self.use_ylim_check.stateChanged.connect(self._apply_all)
        self.ymin_spin.valueChanged.connect(self._apply_all)
        self.ymax_spin.valueChanged.connect(self._apply_all)
        self.autoscale_button.clicked.connect(self.autoscale_requested.emit)

        self.figure_width_spin.valueChanged.connect(self._apply_all)
        self.figure_height_spin.valueChanged.connect(self._apply_all)

        self.use_preview_size_button.clicked.connect(self.use_preview_size_requested.emit)

        self.show_legend_check.stateChanged.connect(self._apply_all)
        self.legend_location_combo.currentTextChanged.connect(self._apply_all)
        self.legend_label_mode_combo.currentTextChanged.connect(self._apply_all)
        self.grid_check.stateChanged.connect(self._apply_all)
        self.clean_plot_check.stateChanged.connect(self._apply_all)

        self.legend_bbox_x_spin.valueChanged.connect(self._apply_all)
        self.legend_bbox_y_spin.valueChanged.connect(self._apply_all)
        self.legend_columns_spin.valueChanged.connect(self._apply_all)

        self.font_family_combo.currentFontChanged.connect(self._apply_all)

        self.title_font_spin.valueChanged.connect(self._apply_all)
        self.axis_font_spin.valueChanged.connect(self._apply_all)
        self.tick_font_spin.valueChanged.connect(self._apply_all)
        self.legend_font_spin.valueChanged.connect(self._apply_all)

        self.major_ticks_check.stateChanged.connect(self._apply_all)
        self.minor_ticks_check.stateChanged.connect(self._apply_all)
        self.tick_direction_combo.currentTextChanged.connect(self._apply_all)

        self.x_major_spacing_spin.valueChanged.connect(self._apply_all)
        self.x_minor_spacing_spin.valueChanged.connect(self._apply_all)
        self.y_major_spacing_spin.valueChanged.connect(self._apply_all)
        self.y_minor_spacing_spin.valueChanged.connect(self._apply_all)

        self.x_major_spacing_auto_button.clicked.connect(
            lambda: self._reset_tick_spacing(self.x_major_spacing_spin)
        )

        self.x_minor_spacing_auto_button.clicked.connect(
            lambda: self._reset_tick_spacing(self.x_minor_spacing_spin)
        )

        self.y_major_spacing_auto_button.clicked.connect(
            lambda: self._reset_tick_spacing(self.y_major_spacing_spin)
        )

        self.y_minor_spacing_auto_button.clicked.connect(
            lambda: self._reset_tick_spacing(self.y_minor_spacing_spin)
        )

        self.reset_tick_spacing_button.clicked.connect(
            self._reset_all_tick_spacing
        )

        self.major_tick_length_spin.valueChanged.connect(self._apply_all)
        self.minor_tick_length_spin.valueChanged.connect(self._apply_all)

        self.plot_xkcd_check.stateChanged.connect(self._apply_all)

    def set_current_preview_size(self, width: float, height: float) -> None:
        """Display the current on-screen preview size."""
        self.current_preview_size_label.setText(
            f"Current preview: {width:.2f} × {height:.2f} in"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_plot_settings(self, settings: PlotSettings | None) -> None:
        """Load plot settings into the panel."""
        self.settings = settings
        self._updating = True

        enabled = settings is not None
        self.setEnabled(enabled)

        if settings is None:
            self._updating = False
            return

        self.title_edit.setText(settings.title)
        self.x_label_edit.setText(settings.x_label)
        self.y_label_edit.setText(settings.y_label)

        self.use_xlim_check.setChecked(settings.xlim is not None)
        self.use_ylim_check.setChecked(settings.ylim is not None)

        if settings.xlim is not None:
            self.xmin_spin.setValue(settings.xlim[0])
            self.xmax_spin.setValue(settings.xlim[1])
        else:
            self.xmin_spin.setValue(0.0)
            self.xmax_spin.setValue(0.0)

        if settings.ylim is not None:
            self.ymin_spin.setValue(settings.ylim[0])
            self.ymax_spin.setValue(settings.ylim[1])
        else:
            self.ymin_spin.setValue(0.0)
            self.ymax_spin.setValue(0.0)

        self.xmin_spin.setEnabled(settings.xlim is not None)
        self.xmax_spin.setEnabled(settings.xlim is not None)
        self.ymin_spin.setEnabled(settings.ylim is not None)
        self.ymax_spin.setEnabled(settings.ylim is not None)

        self.figure_width_spin.setValue(settings.figure_width)
        self.figure_height_spin.setValue(settings.figure_height)

        self.show_legend_check.setChecked(settings.show_legend)
        self.legend_location_combo.setCurrentText(settings.legend_location)

        self.legend_label_mode_combo.setCurrentText(settings.legend_label_mode)

        self.legend_bbox_x_spin.setValue(settings.legend_bbox_x)
        self.legend_bbox_y_spin.setValue(settings.legend_bbox_y)
        self.legend_columns_spin.setValue(settings.legend_columns)
        self._update_legend_bbox_visibility()

        self.grid_check.setChecked(settings.grid)
        self.clean_plot_check.setChecked(settings.clean_plot)

        self.font_family_combo.setCurrentFont(QFont(settings.font_family))

        self.title_font_spin.setValue(settings.font_sizes.title)
        self.axis_font_spin.setValue(settings.font_sizes.axis_label)
        self.tick_font_spin.setValue(settings.font_sizes.tick_label)
        self.legend_font_spin.setValue(settings.font_sizes.legend)

        ticks = settings.tick_settings

        self.major_ticks_check.setChecked(ticks.major_ticks)
        self.minor_ticks_check.setChecked(ticks.minor_ticks)
        self.tick_direction_combo.setCurrentText(ticks.tick_direction)

        self.x_major_spacing_spin.setValue(ticks.x_major_spacing or 0.0)
        self.x_minor_spacing_spin.setValue(ticks.x_minor_spacing or 0.0)

        self.y_major_spacing_spin.setValue(ticks.y_major_spacing or 0.0)
        self.y_minor_spacing_spin.setValue(ticks.y_minor_spacing or 0.0)

        self.major_tick_length_spin.setValue(ticks.major_tick_length)
        self.minor_tick_length_spin.setValue(ticks.minor_tick_length)

        self.plot_xkcd_check.setChecked(settings.plot_xkcd)
        self._updating = False

    def set_current_axis_limits(
        self,
        xlim: tuple[float, float],
        ylim: tuple[float, float],
    ) -> None:
        self._current_xlim = (
            float(xlim[0]),
            float(xlim[1]),
        )
        self._current_ylim = (
            float(ylim[0]),
            float(ylim[1]),
        )

        self._update_tick_spacing_steps()

    # ------------------------------------------------------------------
    # Internal update methods
    # ------------------------------------------------------------------

    def _apply_all(self) -> None:
        if self._updating or self.settings is None:
            return

        self.settings.title = self.title_edit.text()
        self.settings.x_label = self.x_label_edit.text()
        self.settings.y_label = self.y_label_edit.text()

        self.xmin_spin.setEnabled(self.use_xlim_check.isChecked())
        self.xmax_spin.setEnabled(self.use_xlim_check.isChecked())
        self.ymin_spin.setEnabled(self.use_ylim_check.isChecked())
        self.ymax_spin.setEnabled(self.use_ylim_check.isChecked())

        if self.use_xlim_check.isChecked():
            xmin = self.xmin_spin.value()
            xmax = self.xmax_spin.value()
            if xmin != xmax:
                self.settings.xlim = (xmin, xmax)
        else:
            self.settings.xlim = None

        if self.use_ylim_check.isChecked():
            ymin = self.ymin_spin.value()
            ymax = self.ymax_spin.value()
            if ymin != ymax:
                self.settings.ylim = (ymin, ymax)
        else:
            self.settings.ylim = None

        self.settings.figure_width = self.figure_width_spin.value()
        self.settings.figure_height = self.figure_height_spin.value()

        self.settings.show_legend = self.show_legend_check.isChecked()
        self.settings.legend_location = self.legend_location_combo.currentText()
        self.settings.legend_label_mode = self.legend_label_mode_combo.currentText()
        self.settings.legend_bbox_x = self.legend_bbox_x_spin.value()
        self.settings.legend_bbox_y = self.legend_bbox_y_spin.value()
        self.settings.legend_columns = self.legend_columns_spin.value()
        self._update_legend_bbox_visibility()

        self.settings.grid = self.grid_check.isChecked()
        self.settings.clean_plot = self.clean_plot_check.isChecked()

        self.settings.font_family = self.font_family_combo.currentFont().family()

        self.settings.font_sizes.title = self.title_font_spin.value()
        self.settings.font_sizes.axis_label = self.axis_font_spin.value()
        self.settings.font_sizes.tick_label = self.tick_font_spin.value()
        self.settings.font_sizes.legend = self.legend_font_spin.value()

        ticks = self.settings.tick_settings

        ticks.major_ticks = self.major_ticks_check.isChecked()
        ticks.minor_ticks = self.minor_ticks_check.isChecked()
        ticks.tick_direction = self.tick_direction_combo.currentText()

        x_major_spacing = self._validated_tick_spacing(
            self.x_major_spacing_spin.value(),
            self._current_xlim,
            MAX_MAJOR_TICKS,
        )

        x_minor_spacing = self._validated_tick_spacing(
            self.x_minor_spacing_spin.value(),
            self._current_xlim,
            MAX_MINOR_TICKS,
        )

        y_major_spacing = self._validated_tick_spacing(
            self.y_major_spacing_spin.value(),
            self._current_ylim,
            MAX_MAJOR_TICKS,
        )

        y_minor_spacing = self._validated_tick_spacing(
            self.y_minor_spacing_spin.value(),
            self._current_ylim,
            MAX_MINOR_TICKS,
        )

        ticks.x_major_spacing = x_major_spacing
        ticks.x_minor_spacing = x_minor_spacing
        ticks.y_major_spacing = y_major_spacing
        ticks.y_minor_spacing = y_minor_spacing

        self._updating = True

        try:
            self.x_major_spacing_spin.setValue(x_major_spacing or 0.0)
            self.x_minor_spacing_spin.setValue(x_minor_spacing or 0.0)
            self.y_major_spacing_spin.setValue(y_major_spacing or 0.0)
            self.y_minor_spacing_spin.setValue(y_minor_spacing or 0.0)
        finally:
            self._updating = False

        ticks.major_tick_length = self.major_tick_length_spin.value()
        ticks.minor_tick_length = self.minor_tick_length_spin.value()

        self.settings.plot_xkcd = self.plot_xkcd_check.isChecked()

        self.plot_settings_changed.emit()


    def _update_legend_bbox_visibility(self) -> None:
        show_bbox_controls = self.legend_location_combo.currentText() == "outside top"
        self.legend_bbox_widget.setVisible(show_bbox_controls)

    def _reset_tick_spacing(self, spin: QDoubleSpinBox) -> None:
        spin.setValue(0.0)

    def _reset_all_tick_spacing(self) -> None:
        self._updating = True

        try:
            self.x_major_spacing_spin.setValue(0.0)
            self.x_minor_spacing_spin.setValue(0.0)
            self.y_major_spacing_spin.setValue(0.0)
            self.y_minor_spacing_spin.setValue(0.0)
        finally:
            self._updating = False

        self._apply_all()

    def _update_tick_spacing_steps(self) -> None:
        x_span = self._axis_span(self._current_xlim)
        y_span = self._axis_span(self._current_ylim)

        if x_span is not None:
            self.x_major_spacing_spin.setSingleStep(
                self._minimum_spacing(x_span, MAX_MAJOR_TICKS)
            )
            self.x_minor_spacing_spin.setSingleStep(
                self._minimum_spacing(x_span, MAX_MINOR_TICKS)
            )

        if y_span is not None:
            self.y_major_spacing_spin.setSingleStep(
                self._minimum_spacing(y_span, MAX_MAJOR_TICKS)
            )
            self.y_minor_spacing_spin.setSingleStep(
                self._minimum_spacing(y_span, MAX_MINOR_TICKS)
            )

    @staticmethod
    def _axis_span(
        limits: tuple[float, float] | None,
    ) -> float | None:
        if limits is None:
            return None

        span = abs(float(limits[1]) - float(limits[0]))

        if span <= 0:
            return None

        return span

    @staticmethod
    def _minimum_spacing(
        axis_span: float,
        maximum_ticks: int,
    ) -> float:
        raw_spacing = axis_span / maximum_ticks

        if raw_spacing <= 0:
            return 1.0
        
        exponent = math.floor(math.log10(raw_spacing))
        magnitude = 10 ** exponent
        normalised = raw_spacing / magnitude

        if normalised < 1:
            nice_value = 1
        elif normalised < 2:
            nice_value = 2
        elif normalised < 5:
            nice_value = 5
        else:
            nice_value = 10

        return nice_value * magnitude
    
    def _validated_tick_spacing(
        self,
        value: float,
        limits: tuple[float, float] | None,
        maximum_ticks: int,
    ) -> float | None:
        if value <= 0:
            return None

        span = self._axis_span(limits)

        if span is None:
            return value

        minimum = self._minimum_spacing(span, maximum_ticks)

        return max(value, minimum)