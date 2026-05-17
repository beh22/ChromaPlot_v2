from __future__ import annotations

from pathlib import Path

from .akta import import_akta_dataset
from .models import Dataset


SUPPORTED_EXTENSIONS = {".csv", ".txt", ".asc", ".tsv"}


def detect_importer(path: str | Path) -> str:
    """
    Detect which importer should be used for a file.

    Initially this is deliberately simple. As ChromaPlot supports more formats,
    this function can inspect file contents rather than just extension.
    """
    suffix = Path(path).suffix.lower()

    if suffix in SUPPORTED_EXTENSIONS:
        return "akta"

    raise ValueError(f"Could not detect importer for file extension: {suffix}")


def import_dataset(path: str | Path, importer: str = "auto") -> Dataset:
    """Import one chromatography file as a ChromaPlot Dataset."""
    if importer == "auto":
        importer = detect_importer(path)

    if importer == "akta":
        return import_akta_dataset(path)

    raise ValueError(f"Unknown importer: {importer}")


def import_multiple(paths: list[str | Path], importer: str = "auto") -> list[Dataset]:
    """Import several chromatography files."""
    return [import_dataset(path, importer=importer) for path in paths]

