from __future__ import annotations

import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)

from chromaplot import __version__

class WelcomeDialog(QDialog):
    """Startup welcome dialog for ChromaPlot."""

    ImportData = 1
    OpenProject = 2

    def __init__(self, parent=None, version: str = __version__):
        super().__init__(parent)

        self.version = version

        self.setWindowTitle(f"ChromaPlot {self.version}")
        self.setFixedSize(400, 530)

        self.setStyleSheet(
            """
            QDialog {
                background-color: #3e3e3e;
            }

            QLabel {
                color: #f0f0f0;
            }

            QPushButton {
                background-color: #555555;
                color: #f0f0f0;
                border: 1px solid #666666;
                border-radius: 8px;
                padding: 4px 8px;
            }

            QPushButton:hover {
                background-color: #666666;
            }

            QPushButton:pressed {
                background-color: #4a4a4a;
            }
            """
        )

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        # layout.setSpacing(10)

        logo_label = QLabel()
        logo_path = self.resource_path("cp_logo.png")
        logo_pixmap = QPixmap(logo_path)

        if not logo_pixmap.isNull():
            scaled_logo = logo_pixmap.scaled(
                380,
                150,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            logo_label.setPixmap(scaled_logo)
        else:
            logo_label.setText("ChromaPlot")
            logo_label.setFont(QFont("Helvetica", 36, QFont.Bold))

        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        # welcome_label = QLabel(f"Welcome to ChromaPlot \n(Version {self.version})")
        welcome_label = QLabel(
            "< p style='line-height:130%;'><b>Welcome to ChromaPlot</b><br><span style='font-size:18pt;'>Version "
            f"{self.version}</span></p>"
        )
        welcome_label.setTextFormat(Qt.RichText)
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setFont(QFont("Helvetica", 24, QFont.Bold))
        layout.addWidget(welcome_label)

        layout.setSpacing(10)

        description = QLabel(
            "<p style='line-height:130%;'>"
            "A tool for creating high-quality chromatogram figures from "
            "chromatography data files."
            "</p>"
        )
        description.setTextFormat(Qt.RichText)
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        description.setFont(QFont("Helvetica", 16))
        layout.addWidget(description)

        # layout.addSpacing(8)

        prompt = QLabel("<b><span style='font-size:20pt'>Get started:</span></b>")
        prompt.setAlignment(Qt.AlignCenter)
        layout.addWidget(prompt)

        button_layout = QHBoxLayout()
        # button_layout.setSpacing(10)

        self.import_button = QPushButton("Import Data")
        self.import_button.setMinimumHeight(36)
        self.import_button.setFont(QFont("Helvetica", 16, QFont.Bold))
        button_layout.addWidget(self.import_button)

        self.open_button = QPushButton("Open Project")
        self.open_button.setMinimumHeight(36)
        self.open_button.setFont(QFont("Helvetica", 16, QFont.Bold))
        button_layout.addWidget(self.open_button)

        layout.addLayout(button_layout)

        layout.addSpacing(8)

        info_label = QLabel(
            "<p style='line-height:135%;'>"
            "<b>Import Data:</b> Start a new project by importing chromatography "
            "data files.<br><br>"
            "<b>Open Project:</b> Continue working from a saved ChromaPlot project."
            "</p>"
        )
        info_label.setTextFormat(Qt.RichText)
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignJustify)
        info_label.setFont(QFont("Helvetica", 16))
        layout.addWidget(info_label)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        links_label = QLabel(
            'Please report issues on '
            '<a href="https://github.com/beh22/ChromaPlot_v2/">GitHub</a>.'
        )
        links_label.setOpenExternalLinks(True)
        links_label.setAlignment(Qt.AlignCenter)
        links_label.setFont(QFont("Helvetica", 12))
        layout.addWidget(links_label)

        # layout.addStretch()

        self.import_button.clicked.connect(self._on_import_clicked)
        self.open_button.clicked.connect(self._on_open_clicked)

    def _on_import_clicked(self) -> None:
        self.done(self.ImportData)

    def _on_open_clicked(self) -> None:
        self.done(self.OpenProject)

    def resource_path(self, filename: str) -> str:
        if hasattr(sys, "_MEIPASS"):
            return str(Path(sys._MEIPASS) / filename)

        return str(Path(__file__).resolve().parent.parent / "resources" / filename)



# from __future__ import annotations

# from PyQt5.QtCore import Qt, pyqtSignal
# from PyQt5.QtWidgets import (
#     QDialog,
#     QVBoxLayout,
#     QHBoxLayout,
#     QLabel,
#     QPushButton,
#     QFrame,
# )


# class WelcomeDialog(QDialog):
#     """Startup welcome dialog for ChromaPlot."""

#     ImportData = 1
#     OpenProject = 2

#     def __init__(self, parent=None):
#         super().__init__(parent)

#         self.setWindowTitle("Welcome to ChromaPlot")
#         self.setModal(True)
#         self.setMinimumWidth(560)

#         self._build_ui()

#     def _build_ui(self) -> None:
#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(24, 24, 24, 24)
#         layout.setSpacing(18)

#         title = QLabel("ChromaPlot")
#         title.setAlignment(Qt.AlignCenter)
#         title.setStyleSheet(
#             """
#             QLabel {
#                 font-size: 44px;
#                 font-weight: 700;
#                 color: #d99000;
#             }
#             """
#         )
#         layout.addWidget(title)

#         subtitle = QLabel("Welcome to ChromaPlot")
#         subtitle.setAlignment(Qt.AlignCenter)
#         subtitle.setStyleSheet("font-size: 22px; font-weight: 600;")
#         layout.addWidget(subtitle)

#         description = QLabel(
#             "Create high-quality chromatogram figures from chromatography data files. "
#             "Import datasets, overlay traces, customise curves, and save complete "
#             "projects for later editing."
#         )
#         description.setWordWrap(True)
#         description.setAlignment(Qt.AlignCenter)
#         description.setStyleSheet("font-size: 14px;")
#         layout.addWidget(description)

#         separator = QFrame()
#         separator.setFrameShape(QFrame.HLine)
#         separator.setFrameShadow(QFrame.Sunken)
#         layout.addWidget(separator)

#         prompt = QLabel("Get started:")
#         prompt.setAlignment(Qt.AlignCenter)
#         prompt.setStyleSheet("font-size: 16px; font-weight: 600;")
#         layout.addWidget(prompt)

#         button_layout = QHBoxLayout()
#         button_layout.setSpacing(16)

#         self.import_button = QPushButton("Import Data")
#         self.import_button.setMinimumHeight(42)
#         self.import_button.setStyleSheet("font-size: 15px; font-weight: 600;")
#         button_layout.addWidget(self.import_button)

#         self.open_button = QPushButton("Open Project")
#         self.open_button.setMinimumHeight(42)
#         self.open_button.setStyleSheet("font-size: 15px; font-weight: 600;")
#         button_layout.addWidget(self.open_button)

#         layout.addLayout(button_layout)

#         hint = QLabel(
#             "Tip: imported data and all styling options can be saved into a "
#             ".chromaplot project file."
#         )
#         hint.setWordWrap(True)
#         hint.setAlignment(Qt.AlignCenter)
#         hint.setStyleSheet("font-size: 12px; color: #888;")
#         layout.addWidget(hint)

#         self.import_button.clicked.connect(self._on_import_clicked)
#         self.open_button.clicked.connect(self._on_open_clicked)

#     def _on_import_clicked(self) -> None:
#         self.done(self.ImportData)

#     def _on_open_clicked(self) -> None:
#         self.done(self.OpenProject)