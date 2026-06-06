from __future__ import annotations

import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QKeySequence
from PyQt5.QtWidgets import (
    QAction,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QMenuBar,
)

from chromaplot import __version__

def set_font(widget, point_size: int, bold: bool = False) -> None:
    font = widget.font()
    font.setPointSize(point_size)
    font.setBold(bold)
    widget.setFont(font)

class WelcomeDialog(QDialog):
    """Startup welcome dialog for ChromaPlot."""

    ImportData = 1
    OpenProject = 2

    def __init__(self, parent=None, version: str = __version__):
        super().__init__(parent)

        self.version = version

        self.setWindowTitle(f"ChromaPlot {self.version}")
        self.setMinimumWidth(420)

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
        self._build_menu_bar()
        self.adjustSize()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        self.menu_bar = QMenuBar()
        layout.setMenuBar(self.menu_bar)

        layout.setContentsMargins(20, 10, 20, 10)
        # layout.setSpacing(10)

        logo_label = QLabel()
        logo_path = self.resource_path("cp_logo.png")
        logo_pixmap = QPixmap(logo_path)

        if not logo_pixmap.isNull():
            scaled_logo = logo_pixmap.scaled(
                440,
                140,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            logo_label.setPixmap(scaled_logo)
        else:
            logo_label.setText("ChromaPlot")
            set_font(logo_label, 24, bold=True)

        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        welcome_label = QLabel("Welcome to ChromaPlot")
        welcome_label.setAlignment(Qt.AlignCenter)
        set_font(welcome_label, 22, bold=True)
        layout.addWidget(welcome_label)

        version_label = QLabel(f"Version {self.version}")
        version_label.setAlignment(Qt.AlignCenter)
        set_font(version_label, 16, bold=True)
        layout.addWidget(version_label)

        layout.setSpacing(10)

        description = QLabel(
            "A tool for creating high-quality chromatogram figures from chromatography data files."
        )
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        set_font(description, 13)
        layout.addWidget(description)

        # layout.addSpacing(8)

        prompt = QLabel("Get started:")
        prompt.setAlignment(Qt.AlignCenter)
        set_font(prompt, 20, bold=True)
        layout.addWidget(prompt)

        button_layout = QHBoxLayout()
        button_layout.addSpacing(8)

        self.import_button = QPushButton("Import Data")
        self.import_button.setMinimumHeight(36)
        set_font(self.import_button, 13, bold=True)
        button_layout.addWidget(self.import_button)

        self.open_button = QPushButton("Open Project")
        self.open_button.setMinimumHeight(36)
        set_font(self.open_button, 13, bold=True)
        button_layout.addWidget(self.open_button)

        layout.addLayout(button_layout)

        layout.addSpacing(8)

        import_title = QLabel("Import Data")
        set_font(import_title, 13, bold=True)

        import_text = QLabel(
            "Start a new project by importing chromatography data files."
        )
        set_font(import_text, 10)
        import_text.setWordWrap(True)

        open_title = QLabel("Open Project")
        set_font(open_title, 13, bold=True)

        open_text = QLabel(
            "Continue working from a saved ChromaPlot project."
        )
        set_font(open_text, 10)
        open_text.setWordWrap(True)

        layout.addWidget(import_title)
        layout.addWidget(import_text)
        layout.addSpacing(6)
        layout.addWidget(open_title)
        layout.addWidget(open_text)

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
        set_font(links_label, 10)
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

    def _build_menu_bar(self) -> None:
        """Create menu bar and keyboard shortcuts."""

        file_menu = self.menu_bar.addMenu("File")

        self.import_action = QAction("Import Data", self)
        self.import_action.setShortcut("Ctrl+I")
        self.import_action.triggered.connect(self._on_import_clicked)
        file_menu.addAction(self.import_action)

        self.open_action = QAction("Open Project", self)
        self.open_action.setShortcuts(QKeySequence.Open)
        self.open_action.triggered.connect(self._on_open_clicked)
        file_menu.addAction(self.open_action)

        file_menu.addSeparator()

        self.close_action = QAction("Close Window", self)
        self.close_action.setShortcuts(QKeySequence.Close)
        self.close_action.triggered.connect(self.reject)
        file_menu.addAction(self.close_action)

        self.quit_action = QAction("Quit", self)
        self.quit_action.setShortcuts(QKeySequence.Quit)
        self.quit_action.triggered.connect(self.reject)
        file_menu.addAction(self.quit_action)