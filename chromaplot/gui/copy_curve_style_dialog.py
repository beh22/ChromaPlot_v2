from __future__ import annotations

from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QVBoxLayout,
)

from chromaplot.core.models import Project


class CopyCurveStyleDialog(QDialog):
    """Dialog for copying style properties from another curve"""

    def __init__(
        self,
        project: Project,
        destination_curve_id: str,
        parent=None,
    ):
        super().__init__(parent)

        self.project = project
        self.destination_curve_id = destination_curve_id

        self.setWindowTitle("Copy Curve Style")
        self.setMinimumWidth(350)

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        source_form = QFormLayout()

        self.source_combo = QComboBox()

        for dataset in self.project.datasets:
            for curve in dataset.curves:

                if curve.id == self.destination_curve_id:
                    continue

                self.source_combo.addItem(
                    f"{dataset.name} - {curve.name}",
                    curve.id,
                )

        source_form.addRow("Copy style from:", self.source_combo)
        layout.addLayout(source_form)

        properties_group = QGroupBox("Style properties")
        properties_layout = QVBoxLayout(properties_group)

        self.color_check = QCheckBox("Colour")
        self.linewidth_check = QCheckBox("Line width")
        self.linestyle_check = QCheckBox("Line style")
        self.alpha_check = QCheckBox("Opacity")

        self.property_checks = {
            "color": self.color_check,
            "linewidth": self.linewidth_check,
            "linestyle": self.linestyle_check,
            "alpha": self.alpha_check,
        }

        for checkbox in self.property_checks.values():
            checkbox.setChecked(True)
            properties_layout.addWidget(checkbox)

        layout.addWidget(properties_group)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
        )

        self.button_box.button(
            QDialogButtonBox.Ok
        ).setText("Apply")

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout.addWidget(self.button_box)

        if self.source_combo.count() == 0:
            self.source_combo.setEnabled(False)

            self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)

            layout.insertWidget(
                0,
                QLabel("No other curves are available")
            )

        for checkbox in self.property_checks.values():
            checkbox.toggled.connect(self._update_apply_button)

        self._update_apply_button()

    def source_curve_id(self) -> str | None:
        return self.source_combo.currentData()

    def selected_properties(self) -> list[str]:
        return [
            name
            for name, checkbox in self.property_checks.items()
            if checkbox.isChecked()
        ]

    def _update_apply_button(self):
        enabled = (
            self.source_combo.count() > 0
            and any(
                checkbox.isChecked()
                for checkbox in self.property_checks.values()
            )
        )

        self.button_box.button(QDialogButtonBox.Ok).setEnabled(enabled)

