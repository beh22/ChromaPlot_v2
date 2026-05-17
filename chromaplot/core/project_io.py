from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import CURRENT_SCHEMA_VERSION, Project


class ProjectIOError(Exception):
    """Raised when a ChromaPlot project cannot be saved or loaded."""


# -----------------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------------

"""
Could potentially change to zip-based format in the future if we want to decrease
file size and support more complex projects, but for now a single JSON file is
simpler and more transparent.
"""

def save_project(project: Project, path: str | Path, *, indent: int | None = None) -> None:
    """
    Save a ChromaPlot Project to a `.chromaplot` JSON file.

    Raw curve data are stored directly in the project file, so the saved project
    can be reopened even if the original imported data files are moved or
    deleted.
    """
    path = normalise_project_path(path)
    data = project_to_dict(project)

    try:
        with path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=indent, separators=(",", ": "))
    except Exception as exc:
        raise ProjectIOError(f"Could not save project to '{path}': {exc}") from exc


# def save_project(project: Project, path: str | Path, *, indent: int = 2) -> None:
#     """
#     Save a ChromaPlot Project to a `.chromaplot` JSON file.

#     Raw curve data are stored directly in the project file, so the saved project
#     can be reopened even if the original imported data files are moved or
#     deleted.
#     """
#     path = normalise_project_path(path)
#     data = project_to_dict(project)

#     try:
#         with path.open("w", encoding="utf-8") as handle:
#             json.dump(data, handle, indent=indent)
#     except Exception as exc:
#         raise ProjectIOError(f"Could not save project to '{path}': {exc}") from exc


def load_project(path: str | Path) -> Project:
    """
    Load a ChromaPlot Project from a `.chromaplot` JSON file.
    """
    path = Path(path)

    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except Exception as exc:
        raise ProjectIOError(f"Could not read project file '{path}': {exc}") from exc

    try:
        data = migrate_project_dict(data)
        validate_project_dict(data)
        return project_from_dict(data)
    except Exception as exc:
        raise ProjectIOError(f"Could not load project from '{path}': {exc}") from exc


# -----------------------------------------------------------------------------
# Conversion helpers
# -----------------------------------------------------------------------------


def project_to_dict(project: Project) -> dict[str, Any]:
    """
    Convert a Project object into a JSON-safe dictionary.

    Most of the detailed serialisation is handled by the dataclass `to_dict()`
    methods in `models.py`.
    """
    return project.to_dict()



def project_from_dict(data: dict[str, Any]) -> Project:
    """
    Convert a dictionary loaded from JSON into a Project object.
    """
    return Project.from_dict(data)


# -----------------------------------------------------------------------------
# Validation and migration
# -----------------------------------------------------------------------------


def validate_project_dict(data: dict[str, Any]) -> None:
    """
    Perform lightweight validation of a project dictionary.

    This is deliberately not over-complicated. The dataclass `from_dict()`
    methods handle many defaults, while this function catches obviously invalid
    files early.
    """
    if not isinstance(data, dict):
        raise ValueError("Project file must contain a JSON object.")

    if "schema_version" not in data:
        raise ValueError("Project file is missing 'schema_version'.")

    schema_version = data["schema_version"]
    if not isinstance(schema_version, int):
        raise ValueError("Project 'schema_version' must be an integer.")

    if schema_version > CURRENT_SCHEMA_VERSION:
        raise ValueError(
            f"Project schema version {schema_version} is newer than this "
            f"version of ChromaPlot supports ({CURRENT_SCHEMA_VERSION})."
        )

    if "project" not in data:
        raise ValueError("Project file is missing top-level 'project' object.")

    project_data = data["project"]
    if not isinstance(project_data, dict):
        raise ValueError("Top-level 'project' entry must be an object.")

    datasets = project_data.get("datasets", [])
    if not isinstance(datasets, list):
        raise ValueError("Project 'datasets' entry must be a list.")

    annotations = project_data.get("annotations", [])
    if not isinstance(annotations, list):
        raise ValueError("Project 'annotations' entry must be a list.")



def migrate_project_dict(data: dict[str, Any]) -> dict[str, Any]:
    """
    Migrate older project dictionaries to the current schema.

    For schema version 1 this currently does nothing, but having the function in
    place means future format changes can be handled cleanly.
    """
    if not isinstance(data, dict):
        raise ValueError("Project data must be a dictionary.")

    schema_version = data.get("schema_version")

    # Allow early development files that may have been saved directly as the
    # inner project object. This can be removed once the format is stable.
    if schema_version is None and "datasets" in data:
        data = {
            "schema_version": CURRENT_SCHEMA_VERSION,
            "project": data,
        }
        schema_version = CURRENT_SCHEMA_VERSION

    if schema_version == CURRENT_SCHEMA_VERSION:
        return data

    raise ValueError(f"Unsupported project schema version: {schema_version}")


# -----------------------------------------------------------------------------
# Path helpers
# -----------------------------------------------------------------------------


def normalise_project_path(path: str | Path) -> Path:
    """
    Ensure project files use the `.chromaplot` extension.

    If the user supplies `example`, this returns `example.chromaplot`.
    If the user supplies `example.chromaplot`, it is left unchanged.
    """
    path = Path(path)

    if path.suffix != ".chromaplot":
        path = path.with_suffix(".chromaplot")

    return path


