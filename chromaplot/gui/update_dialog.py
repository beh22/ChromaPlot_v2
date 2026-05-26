from __future__ import annotations

import webbrowser
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QPlainTextEdit,
    QFrame,
    QScrollArea,
    QWidget,
)

from chromaplot.core.update_checker import UpdateInfo

def set_font(widget, point_size: int, bold: bool = False) -> None:
    font = widget.font()
    font.setPointSize(point_size)
    font.setBold(bold)
    widget.setFont(font)

def changelog_markdown_to_html(text: str) -> str:
    """Convert simple changelog markdown to HTML."""

    lines = text.splitlines()

    html_lines: list[str] = []
    in_list = False

    for line in lines:
        stripped = line.strip()

        if not stripped:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            continue

        if stripped.startswith("### "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False

            heading = stripped.removeprefix("### ").strip()

            html_lines.append(
                f"""
                <p style="
                    font-size:13pt;
                    font-weight:bold;
                    margin-top:10px;
                    margin-bottom:4px;
                    color:#f0f0f0;
                ">
                    {heading}
                </p>
                """
            )

        elif stripped.startswith("- "):
            if not in_list:
                html_lines.append(
                    "<ul style='margin-top:2px; margin-bottom:8px;'>"
                )
                in_list = True

            item = stripped.removeprefix("- ").strip()

            html_lines.append(
                f"<li style='margin-bottom:3px;'>{item}</li>"
            )

        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False

            html_lines.append(f"<p>{stripped}</p>")

    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)


class UpdateDialog(QDialog):
    """Dialog shown when a newer ChromaPlot version is available."""

    def __init__(self, update: UpdateInfo, parent=None):
        super().__init__(parent)

        self.update = update
        self.setWindowTitle("Update Available")

        self._build_ui()

        if sys.platform.startswith("win"):
            self.resize(800, 1000)
        else:
            self.resize(400, 720)

    def _make_command_box(self, text: str, height: int = 80) -> QPlainTextEdit:
        box = QPlainTextEdit()
        box.setReadOnly(True)
        box.setFixedHeight(height)
        box.setPlainText(text)

        command_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        command_font.setPointSize(11)
        box.setFont(command_font)

        box.setStyleSheet(
            """
            QPlainTextEdit {
                background-color: #2b2b2b;
                color: #f0f0f0;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 6px;
                selection-background-color: #666666;
            }

            QScrollBar:vertical {
                background: #3e3e3e;
                width: 10px;
            }

            QScrollBar::handle:vertical {
                background: #666666;
                border-radius: 4px;
                min-height: 20px;
            }
            """
        )

        return box

    def _build_ui(self) -> None:
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(22, 18, 22, 18)
        outer_layout.setSpacing(12)

        self.setStyleSheet(
            """
            QDialog {
                background-color: #3e3e3e;
            }

            QWidget#scrollContent {
                background-color: #3e3e3e;
            }

            QScrollArea {
                border: none;
                background-color: #3e3e3e;
            }

            QScrollArea > QWidget > QWidget {
                background-color: #3e3e3e;
            }

            QLabel {
                color: #f0f0f0;
            }

            QPushButton {
                background-color: #5a5a5a;
                color: #f0f0f0;
                border: 1px solid #777777;
                border-radius: 6px;
                padding: 6px 12px;
            }

            QPushButton:hover {
                background-color: #6a6a6a;
            }

            QPushButton:pressed {
                background-color: #4a4a4a;
            }
            """
        )

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        outer_layout.addWidget(scroll)

        content = QWidget()
        content.setObjectName("scrollContent")
        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        title = QLabel("A new version of ChromaPlot is available")
        title.setAlignment(Qt.AlignCenter)
        set_font(title, 20, bold=True)
        title.setWordWrap(True)
        layout.addWidget(title)

        version_label = QLabel(
            f"<b>Current version:</b> {self.update.current_version}<br>"
            f"<b>Latest version:</b> {self.update.latest_version}"
        )
        version_label.setTextFormat(Qt.RichText)
        version_label.setAlignment(Qt.AlignCenter)
        set_font(version_label, 13)
        version_label.setWordWrap(True)
        layout.addWidget(version_label)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        changes_title = QLabel("What's new")
        set_font(changes_title, 14, bold=True)
        layout.addWidget(changes_title)

        self.changelog_box = QTextEdit()
        self.changelog_box.setReadOnly(True)
        self.changelog_box.setFixedHeight(170)
        self.changelog_box.setStyleSheet(
            """
            QTextEdit {
                background-color: #2b2b2b;
                color: #f0f0f0;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 6px;
            }

            QScrollBar:vertical {
                background: #3e3e3e;
                width: 10px;
            }

            QScrollBar::handle:vertical {
                background: #666666;
                border-radius: 4px;
                min-height: 20px;
            }
            """
        )

        if self.update.changelog_text:
            changelog_html = changelog_markdown_to_html(
                self.update.changelog_text
            )
        else:
            changelog_html = (
                "<p>No changelog details were found for this version.</p>"
            )

        self.changelog_box.setHtml(changelog_html)
        layout.addWidget(self.changelog_box)

        source_title = QLabel("To update:")
        set_font(source_title, 14, bold=True)
        layout.addWidget(source_title)

        pipx_text = QLabel(
            "If you installed ChromaPlot with pipx, update with:"
        )
        set_font(pipx_text, 12)
        pipx_text.setWordWrap(True)
        layout.addWidget(pipx_text)

        self.pipx_github_command_box = self._make_command_box(
            "pipx upgrade chromaplot",
            height=60,
        )
        layout.addWidget(self.pipx_github_command_box)

        source_text = QLabel(
            "If you installed ChromaPlot from source, update with:"
        )
        set_font(source_text, 12)
        source_text.setWordWrap(True)
        layout.addWidget(source_text)

        self.source_command_box = self._make_command_box(
            "cd ChromaPlot_v2\n"
            "git pull\n"
            "pip install .",
            height=120,
        )
        layout.addWidget(self.source_command_box)

        layout.addStretch()

        button_layout = QHBoxLayout()

        self.later_button = QPushButton("Later")
        self.later_button.clicked.connect(self.reject)
        button_layout.addWidget(self.later_button)

        button_layout.addStretch()

        self.open_releases_button = QPushButton("Open GitHub Releases")
        self.open_releases_button.clicked.connect(self._open_releases)
        button_layout.addWidget(self.open_releases_button)

        outer_layout.addLayout(button_layout)

    def _open_releases(self) -> None:
        webbrowser.open(self.update.release_url)
        self.accept()