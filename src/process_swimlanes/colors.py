"""Color palettes for swimlane step types.

A `Palette` maps a step `kind` (string identifier) to a `(fill, stroke)` tuple of
draw.io-compatible color strings. The library ships with `DEFAULT_PALETTE` covering
8 common kinds suitable for business-process modernization diagrams.

You can subclass / extend by passing a custom `Palette` to `emit_swimlane()`.

Default palette rationale (drawn from the AER NGSM modernization PoC, where each
colour encodes a different process risk profile):

| Kind        | Fill      | Stroke    | Meaning                                          |
| ----------- | --------- | --------- | ------------------------------------------------ |
| `macro`     | `#dae8fc` | `#6c8ebf` | Automated / VBA macro / solver step (blue)       |
| `live`      | `#d5e8d4` | `#82b366` | Live workbook formula link (green)               |
| `received`  | `#d5e8d4` | `#82b366` | Newly received external file (green, = live)     |
| `handkey`   | `#ffe6cc` | `#d79b00` | Analyst hand-keyed value (orange)                |
| `missing`   | `#f8cecc` | `#b85450` | File not yet received / blocked (red)            |
| `stale`     | `#fff2cc` | `#d6b656` | Received but vintage-stale / suspect (yellow)    |
| `dead`      | `#e1d5e7` | `#9673a6` | Dead code / abandoned path (purple)              |
| `oos`       | `#f5f5f5` | `#999999` | Out-of-scope / publication / external (grey)     |

The dynamic legend rendered by `emit_swimlane()` only shows kinds that actually
appear in the supplied steps — so unused palette entries are silently dropped.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


# A palette entry: (fill_hex, stroke_hex)
PaletteEntry = tuple[str, str]


@dataclass(frozen=True)
class Palette:
    """Mapping of `kind` → `(fill, stroke)` plus optional human-readable legend descriptions.

    Use `Palette.default()` for the canonical 8-kind palette, or build your own:

        my_palette = Palette(
            colors={
                "go":   ("#d5e8d4", "#82b366"),
                "stop": ("#f8cecc", "#b85450"),
            },
            legend_labels={
                "go":   "Approved action",
                "stop": "Blocked action",
            },
        )
    """
    colors: Mapping[str, PaletteEntry]
    legend_labels: Mapping[str, str] = field(default_factory=dict)

    def __getitem__(self, kind: str) -> PaletteEntry:
        return self.colors[kind]

    def __contains__(self, kind: str) -> bool:
        return kind in self.colors

    def legend_text(self, kind: str) -> str:
        """Human-readable legend caption for a kind; falls back to the kind id."""
        return self.legend_labels.get(kind, kind)

    @classmethod
    def default(cls) -> "Palette":
        return DEFAULT_PALETTE


DEFAULT_PALETTE = Palette(
    colors={
        "macro":    ("#dae8fc", "#6c8ebf"),
        "live":     ("#d5e8d4", "#82b366"),
        "received": ("#d5e8d4", "#82b366"),
        "handkey":  ("#ffe6cc", "#d79b00"),
        "missing":  ("#f8cecc", "#b85450"),
        "stale":    ("#fff2cc", "#d6b656"),
        "dead":     ("#e1d5e7", "#9673a6"),
        "oos":      ("#f5f5f5", "#999999"),
    },
    legend_labels={
        "macro":    "Automated / macro / solver step",
        "live":     "Live workbook formula link",
        "received": "Recently received (was previously blocked)",
        "handkey":  "Analyst hand-keyed value",
        "missing":  "File not yet received / blocked",
        "stale":    "Received but vintage-stale / suspect",
        "dead":     "Dead code / abandoned path",
        "oos":      "Out-of-scope / publication / external",
    },
)
