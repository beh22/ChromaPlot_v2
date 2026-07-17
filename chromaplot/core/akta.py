from __future__ import annotations

import csv
import hashlib
import re
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from typing import Any
import numpy as np

from .models import Curve, DataSource, Dataset, Fraction, now_iso
from .styles import CurveStyle, default_curve_style


# -----------------------------------------------------------------------------
# Raw parsed representation
# -----------------------------------------------------------------------------

@dataclass
class AktaRawData:
    """
    Intermediate representation of an AKTA export file.

    This is intentionally close to the original file structure. It is then
    converted into ChromaPlot's generic Dataset/Curve model.
    """

    columns: dict[str, dict[str, list[Any]]]
    source_path: str
    title_header_line: int
    unit_header_line: int
    metadata: dict[str, Any] = field(default_factory=dict)


# -----------------------------------------------------------------------------
# File reading and parsing helpers
# -----------------------------------------------------------------------------

ENCODINGS_TO_TRY = (
    "utf-8-sig",
    "utf-16",
    "utf-16-le",
    "utf-16-be",
    "cp1252",
    "latin-1",
)


UNIT_TOKENS = {
    "ml",
    "mau",
    "ms/cm",
    "%",
    "%b",
    "mpa",
    "ml/min",
    "°c",
    "(fractions)",
    "(set marks)",
    "fraction",
    "logbook",
}


TITLE_KEYWORDS = (
    "uv",
    "cond",
    "conductivity",
    "flow",
    "pressure",
    "temp",
    "temperature",
    "fraction",
    "logbook",
    "ph",
)


KNOWN_TEXT_CURVES = (
    "fraction",
    "fractions",
    "logbook",
    "set marks",
)


AUXILIARY_CURVE_MARKERS = (
    "cut_temp",
    "basem",
    "temp@",
)


GRADIENT_KEYWORDS = (
    "gradient concentration",
    "conc b",
    "conc",
)


def read_text_lines(path: str | Path) -> tuple[list[str], str]:
    """
    Read an exported chromatography file using a robust sequence of encodings.

    Returns
    -------
    lines
        Text lines from the file.
    encoding
        Encoding that successfully decoded the file, or a fallback label.
    """
    path = Path(path)

    for encoding in ENCODINGS_TO_TRY:
        try:
            with path.open("r", encoding=encoding) as handle:
                lines = handle.readlines()
            if lines:
                return lines, encoding
        except Exception:
            continue

    with path.open("rb") as handle:
        raw = handle.read()
    return raw.decode("latin-1", errors="replace").splitlines(True), "latin-1-replace"


def file_sha256(path: str | Path) -> str:
    """Return SHA256 hash of a source file for traceability."""
    path = Path(path)
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def clean_field(value: str) -> str:
    """Strip whitespace and matching quotes from a field"""
    value = value.strip()
    if len(value) >= 2 and (
        (value[0] == value[-1] == '"') or (value[0] == value[-1] == "'")
    ):
        value = value[1:-1].strip()
    return value


def split_line(line: str) -> tuple[list[str], int, bool]:
    """
    Split one line from an AKTA export.

    AKTA exports are often tab-delimited, but some exports may be comma-based.
    The parser expects title/unit/data columns to appear in x/y pairs. If an odd
    number of columns is found, the final column is ignored and `colno_error` is
    set to True.
    """
    fields = line.split("\t")

    if len(fields) <= 1:
        reader = csv.reader(StringIO(line))
        fields = next(reader)

    colno = len(fields)
    colno_error = False

    if colno % 2 != 0:
        colno -= 1
        colno_error = True

    fields = [clean_field(field) for field in fields[:colno]]
    return fields, colno, colno_error


def is_header_titles(tokens: list[str]) -> bool:
    joined = " ".join(tokens).lower()
    return any(keyword in joined for keyword in TITLE_KEYWORDS)


def is_header_units(tokens: list[str]) -> bool:
    token_set = {token.lower() for token in tokens}
    return any(unit in token_set for unit in UNIT_TOKENS)


def autodetect_headers(lines: list[str], max_scan_lines: int = 20) -> tuple[int, int]:
    """
    Find likely consecutive title/unit header lines.

    Returns a tuple `(title_header_line, unit_header_line)`.
    """
    max_index = min(max_scan_lines, max(0, len(lines) - 1))

    for idx in range(max_index):
        line1_tokens, _, _ = split_line(lines[idx])
        line2_tokens, _, _ = split_line(lines[idx + 1])

        if is_header_titles(line1_tokens) and is_header_units(line2_tokens):
            return idx, idx + 1

    # Fallback matching the old code behaviour.
    return 1, 2


def to_number_or_text(value: str) -> float | str | None:
    """Convert numeric fields to float, preserve text fields, ignore blanks."""
    if value == "":
        return None

    # Some exports may use comma decimal separators. Only convert if it looks
    # like a simple decimal number rather than a CSV/list-like field.
    candidate = value.replace(",", ".") if value.count(",") == 1 else value

    try:
        return float(candidate)
    except ValueError:
        return value


# -----------------------------------------------------------------------------
# Raw AKTA parsing
# -----------------------------------------------------------------------------

def parse_akta_lines(
    lines: list[str],
    source_path: str,
    title_header_line: int | None = None,
    unit_header_line: int | None = None,
) -> AktaRawData:
    """
    Parse text lines from an AKTA export into nested dictionaries.

    The output structure is:

    {
        "UV": {
            "ml": [...],
            "mAU": [...],
        },
        "Cond": {
            "ml": [...],
            "mS/cm": [...],
        },
    }
    """
    if title_header_line is None or unit_header_line is None:
        title_header_line, unit_header_line = autodetect_headers(lines)

    title_tokens, title_colno, title_col_error = split_line(lines[title_header_line])
    unit_tokens, unit_colno, unit_col_error = split_line(lines[unit_header_line])

    max_colno = min(title_colno, unit_colno)
    if max_colno % 2 != 0:
        max_colno -= 1

    curve_names: list[str] = []
    columns: dict[str, dict[str, list[Any]]] = {}

    for i in range(0, max_colno, 2):
        curve_name = title_tokens[i]
        if curve_name == "":
            curve_name = f"Curve {i // 2 + 1}"

        # Avoid silently overwriting duplicate curve names.
        original_curve_name = curve_name
        suffix = 2
        while curve_name in columns:
            curve_name = f"{original_curve_name} ({suffix})"
            suffix += 1

        x_key = unit_tokens[i]
        y_key = unit_tokens[i + 1]

        if x_key == "":
            x_key = "x"
        if y_key == "":
            y_key = "y"

        curve_names.append(curve_name)
        columns[curve_name] = {x_key: [], y_key: []}

    colno_errors = [title_col_error, unit_col_error]
    colno_checks = [title_colno, unit_colno]

    for line in lines[unit_header_line + 1 :]:
        tokens, colno, col_error = split_line(line)
        colno_errors.append(col_error)
        colno_checks.append(colno)

        max_data_colno = min(colno, 2 * len(curve_names), len(tokens))

        for i in range(0, max_data_colno, 2):
            if i + 1 >= len(tokens):
                break

            raw_x = tokens[i]
            raw_y = tokens[i + 1]

            if raw_x == "" and raw_y == "":
                continue

            curve_name = curve_names[i // 2]
            curve_keys = list(columns[curve_name].keys())
            x_key, y_key = curve_keys[0], curve_keys[1]

            x_value = to_number_or_text(raw_x)
            y_value = to_number_or_text(raw_y)

            if x_value is not None:
                columns[curve_name][x_key].append(x_value)
            if y_value is not None:
                columns[curve_name][y_key].append(y_value)

    # From AKdatafile in V1, unsure if still needed
    # if "UV" not in columns:
    #     uv_candidates = [key for key in columns if "uv" in key.lower()]
    #     if uv_candidates:
    #         columns["UV"] = columns[uv_candidates[0]]

    metadata = {
        "title_header_line": title_header_line,
        "unit_header_line": unit_header_line,
        "consistent_column_count": colno_checks.count(colno_checks[0]) == len(colno_checks),
        "odd_column_lines_detected": any(colno_errors),
        "column_counts": colno_checks,
    }

    return AktaRawData(
        columns=columns,
        source_path=str(source_path),
        title_header_line=title_header_line,
        unit_header_line=unit_header_line,
        metadata=metadata,
    )


def read_akta_file(
    path: str | Path,
    title_header_line: int | None = None,
    unit_header_line: int | None = None,
) -> AktaRawData:
    """Read and parse an AKTA file into `AktaRawData`."""
    path = Path(path)
    lines, encoding = read_text_lines(path)
    raw = parse_akta_lines(
        lines=lines,
        source_path=str(path),
        title_header_line=title_header_line,
        unit_header_line=unit_header_line,
    )
    raw.metadata["encoding"] = encoding
    raw.metadata["file_hash"] = file_sha256(path)
    return raw


# -----------------------------------------------------------------------------
# Conversion into ChromaPlot data model
# -----------------------------------------------------------------------------

def normalise_curve_name(name: str) -> str:
    """Return a display-friendly curve name."""
    cleaned = " ".join(name.strip().split())
    return cleaned or "Untitled curve"


def is_auxiliary_curve(name: str) -> bool:
    """
    Return True for AKTA-generated auxiliary trace

    Such as:
        UV_CUT_TEMP@100,BASEM
        UV 1_280_CUT_TEMP@100,BASEM

    These should still be imported for completeness, but should not be
    treated as primary UV traces or be visible by default
    """
    text = name.lower()
    return any(marker in text for marker in AUXILIARY_CURVE_MARKERS)


def infer_uv_channel(name: str) -> int | None:
    """
    Infer the UV channel number from an AKTA curve name

    E.g.
    UV                  -> 1
    UV 1_280            -> 1
    UV 2_254            -> 2
    UV 3_214            -> 3
    UV_CUT_TEMP...      -> 1, but should still be hidden by auxiliary detection
    """
    cleaned = name.strip().lower()

    if not cleaned.startswith("uv"):
        return None
    
    if cleaned == "uv":
        return 1
    
    match = re.match(r"^uv\s*(\d+)", cleaned)
    if match:
        return int(match.group(1))
    
    return 1


def infer_uv_wavelength(name: str) -> int | None:
    """
    Infer wavelength from an AKTA UV curve name where possible

    E.g.
    UV 1_280 -> 280
    UV 2_254 -> 254
    UV 3_214 -> 214
    """
    match = re.search(r"_(\d{3})(?:\D|$)", name)
    if match:
        return int(match.group(1))
    return None

def infer_curve_type(name: str, y_unit: str | None = None) -> str:
    """
    Infer broad curve type from name/unit.

    This is used for defaults only. It should not affect raw data import.
    """
    text = f"{name} {y_unit or ''}".lower()

    if is_auxiliary_curve(name):
        if "uv" in text or "mau" in text:
            return "uv_auxiliary"
        return "auxiliary"

    if "uv" in text or "mau" in text:
        return "uv"
    if "cond" in text or "ms/cm" in text:
        return "conductivity"
    if "flow" in text or "ml/min" in text:
        return "flow"
    if "pressure" in text or "mpa" in text:
        return "pressure"
    if "temp" in text or "°c" in text:
        return "temperature"
    if "ph" in text:
        return "ph"
    if (
        any(keyword in text for keyword in GRADIENT_KEYWORDS)
        and (y_unit or "").lower() in {"%", "%b"}
    ):
        return "gradient"
    if any(keyword in text for keyword in KNOWN_TEXT_CURVES):
        return "text"
    return "unknown"


def default_style_for_curve_type(curve_type: str, index: int) -> CurveStyle:
    """Choose initial style based on inferred curve type."""
    # These are only defaults. The user can configure all of them later.
    if curve_type == "uv":
        return CurveStyle(color="#1f77b4", linewidth=1.5, linestyle="-")
    if curve_type == "uv_auxiliary":
        return CurveStyle(color="#1f77b4", linewidth=1.0, linestyle=":", alpha=0.6)
    if curve_type == "conductivity":
        return CurveStyle(color="#2ca02c", linewidth=1.2, linestyle="--")
    if curve_type == "gradient":
        return CurveStyle(color="#ff7f0e", linewidth=1.0, linestyle="-.")
    if curve_type == "pressure":
        return CurveStyle(color="#d62728", linewidth=1.0, linestyle=":")
    if curve_type == "temperature":
        return CurveStyle(color="#9467bd", linewidth=1.0, linestyle="-.")
    if curve_type == "ph":
        return CurveStyle(color="#8c564b", linewidth=1.0, linestyle="--")
    if curve_type == "flow":
        return CurveStyle(color="#7f7f7f", linewidth=1.0, linestyle=":")

    return default_curve_style(index)


def choose_default_visible_curve(curves: list[Curve]) -> str | None:
    """
    Choose exactly one curve to show when a dataset is first imported

    Priority is:
    1. Plain "UV" if present and not auxiliary
    2. Primary UV channel, e.g. "UV 1_280"
    3. First non-auxiliary UV curve
    4. First plottable non-auxiliary curve of any type

    Returns the chosen curve ID, or None if there are no curves
    """
    if not curves:
        return None

    def curve_type(curve: Curve) -> str:
        return str(curve.metadata.get("curve_type", "unknown"))

    def is_auxiliary(curve: Curve) -> bool:
        return bool(curve.metadata.get("is_auxiliary", False))

    # 1. Exact plain UV is the best default when present
    for curve in curves:
        if (
            curve.name.strip().lower() == "uv"
            and curve_type(curve) == "uv"
            and not is_auxiliary(curve)
        ):
            return curve.id

    # 2. Primary UV channel, usually UV 1_280
    primary_uv_curves = [
        curve for curve in curves
        if curve_type(curve) == "uv"
        and not is_auxiliary(curve)
        and curve.metadata.get("uv_channel") == 1
    ]
    if primary_uv_curves:
        # Prefer 280 nm if several channel 1 traces exist
        for curve in primary_uv_curves:
            if curve.metadata.get("uv_wavelength") == 280:
                return curve.id
        return primary_uv_curves[0].id

    # 3. Any clean UV curve
    for curve in curves:
        if curve_type(curve) == "uv" and not is_auxiliary(curve):
            return curve.id

    # 4. Any clean plottable curve
    for curve in curves:
        if not is_auxiliary(curve):
            return curve.id

    return curves[0].id


def apply_default_visibility(dataset: Dataset) -> None:
    """Hide all curves except the single default curve for a new dataset"""
    chosen_curve_id = choose_default_visible_curve(dataset.curves)

    for curve in dataset.curves:
        curve.visible = curve.id == chosen_curve_id


def _split_xy_columns(curve_data: dict[str, list[Any]]) -> tuple[str, str, list[Any], list[Any]]:
    """
    Extract x/y keys and values from a parsed raw curve dictionary.

    AKTA curves are expected to contain two columns. This helper keeps the
    conversion code explicit and easy to test.
    """
    keys = list(curve_data.keys())
    if len(keys) < 2:
        raise ValueError(f"Expected at least two columns, found {len(keys)}")

    x_key, y_key = keys[0], keys[1]
    return x_key, y_key, curve_data[x_key], curve_data[y_key]


def _is_numeric_sequence(values: list[Any]) -> bool:
    """Return True if all values can be interpreted as numeric."""
    if not values:
        return False
    return all(isinstance(value, (int, float)) for value in values)


def clean_fraction_label(value: Any) -> str:
    if value is None:
        return ""
    
    if isinstance(value, float) and np.isnan(value):
        return ""
    
    if isinstance(value, (int, float)):
        if float(value).is_integer():
            return str(int(value))
        return str(value)
    
    label = str(value).strip()
    label = label.strip('"').strip("'").strip()
    label = label.removeprefix("T")
    return label.strip()


def _is_waste_label(label: str) -> bool:
    text = label.strip().lower()
    return "waste" in text or text in {"w", "waste"}


def extract_fractions_from_column(
        x_values: list[Any],
        y_values: list[Any],
) -> list[Fraction]:
    fractions: list[Fraction] = []

    for x, y in zip(x_values, y_values):
        if not isinstance(x, (int, float)):
            continue
        if y is None:
            continue

        raw_label = str(y).strip()
        display_label = clean_fraction_label(y)

        if not display_label:
            continue

        fractions.append(
            Fraction(
                start_volume=float(x),
                label=raw_label,
                display_label=display_label,
                kind="waste" if _is_waste_label(raw_label) else "fraction",
            )
        )

    for i, fraction in enumerate(fractions[:-1]):
        fraction.end_volume = fractions[i + 1].start_volume

    return fractions


def akta_to_dataset(raw: AktaRawData, dataset_name: str | None = None) -> Dataset:
    """
    Convert parsed AKTA raw data into a generic ChromaPlot Dataset.

    Non-numeric curves such as fraction/logbook entries are kept in dataset
    metadata for now rather than becoming plottable `Curve` objects.
    """
    source_path = Path(raw.source_path)

    dataset = Dataset(
        name=dataset_name or source_path.stem,
        source=DataSource(
            path=str(source_path),
            importer="akta",
            imported_at=now_iso(),
            file_hash=raw.metadata.get("file_hash"),
        ),
        metadata={
            "akta": raw.metadata,
            "non_numeric_columns": {},
        },
    )

    curve_index = 0

    for raw_name, curve_data in raw.columns.items():
        x_key, y_key, x_values, y_values = _split_xy_columns(curve_data)
        curve_name = normalise_curve_name(raw_name)
        curve_type = infer_curve_type(curve_name, y_key)
        is_auxiliary = is_auxiliary_curve(curve_name)
        uv_channel = infer_uv_channel(curve_name)
        uv_wavelength = infer_uv_wavelength(curve_name)

        # Skip aliases that point to an already imported object.
        # This matters because parse_akta_lines may add columns["UV"] as an alias.
        if any(existing.name == curve_name for existing in dataset.curves):
            continue

        if not (_is_numeric_sequence(x_values) and _is_numeric_sequence(y_values)):
            dataset.metadata["non_numeric_columns"][curve_name] = {
                "x_key": x_key,
                "y_key": y_key,
                "x_values": x_values,
                "y_values": y_values,
                "curve_type": curve_type,
                "is_auxiliary": is_auxiliary,
                "uv_channel": uv_channel,
                "uv_wavelength": uv_wavelength,
            }

            if curve_type == "text" and "fraction" in curve_name.lower():
                dataset.fractions = extract_fractions_from_column(x_values, y_values)

            continue

        min_len = min(len(x_values), len(y_values))
        if min_len == 0:
            continue

        if len(x_values) != len(y_values):
            # Keep a record but allow plotting using the common length.
            dataset.metadata.setdefault("length_mismatches", {})[curve_name] = {
                "x_length": len(x_values),
                "y_length": len(y_values),
                "used_length": min_len,
            }

        curve = Curve(
            name=curve_name,
            x=x_values[:min_len],
            y=y_values[:min_len],
            x_label="Volume" if x_key.lower() == "ml" else x_key,
            y_label=curve_name,
            x_unit=x_key,
            y_unit=y_key,
            # Assigned after all curves are imported so that exactly one curve
            # is visible initially
            visible=False,
            style=default_style_for_curve_type(curve_type, curve_index),
            metadata={
                "source_curve_name": raw_name,
                "curve_type": curve_type,
                "x_column": x_key,
                "y_column": y_key,
                "is_auxiliary": is_auxiliary,
                "uv_channel": uv_channel,
                "uv_wavelength": uv_wavelength,
            },
        )
        dataset.add_curve(curve)
        curve_index += 1

    apply_default_visibility(dataset)
    return dataset


def import_akta_dataset(
    path: str | Path,
    dataset_name: str | None = None,
    title_header_line: int | None = None,
    unit_header_line: int | None = None,
) -> Dataset:
    """Read an AKTA file and return a populated ChromaPlot Dataset."""
    raw = read_akta_file(
        path,
        title_header_line=title_header_line,
        unit_header_line=unit_header_line,
    )
    return akta_to_dataset(raw, dataset_name=dataset_name)
