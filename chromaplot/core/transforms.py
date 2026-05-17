from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

import numpy as np

@dataclass
class CurveTransform:
    """
    Display transform for a curve

    Data is never modified directly when transforming curves for display. Instead, transform is applied at plotting/export time
    """

    x_offset: float = 0.0
    y_offset: float = 0.0
    x_scale: float = 1.0
    y_scale: float = 1.0

    def apply(self, x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Return transformed copies of x and y"""
        x_out = (np.asarray(x, dtype=float) * self.x_scale) + self.x_offset
        y_out = (np.asarray(y, dtype=float) * self.y_scale) + self.y_offset
        return x_out, y_out

    def reset(self) -> None:
        self.x_offset: float = 0.0
        self.y_offset: float = 0.0
        self.x_scale: float = 1.0
        self.y_scale: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict [str, Any] | None) -> "CurveTransform":
        if data is None:
            return cls()
        return cls(
                x_offset=float(data.get("x_offset", 0.0)),
                y_offset=float(data.get("y_offset", 0.0)),
                x_scale=float(data.get("x_scale", 1.0)),
                y_scale=float(data.get("y_scale", 1.0)),
        )


def apply_transform(
        x: np.ndarray,
        y: np.ndarray,
        transform: CurveTransform | None,
) -> tuple[np.ndarray, np.ndarray]:
    """Apply a transform, or return numeric copies if transform is None"""
    if transform is None:
        return np.asarray(x, dtype=float).copy(), np.asarray(y, dtype=float).copy()
    return transform.apply(x, y)