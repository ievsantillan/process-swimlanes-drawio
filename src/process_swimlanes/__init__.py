"""process-swimlanes-drawio — generate draw.io swimlane diagrams.

Public API:

    from process_swimlanes import (
        Lane, Step, Edge, Palette, EmitConfig,
        DEFAULT_PALETTE,
        emit_swimlane,
    )

Quick start:

    lanes = [
        Lane(label="Engineering", y=30,  height=100),
        Lane(label="Ops",         y=130, height=100),
    ]
    steps = [
        Step(id="s1", lane=0, x=10,  y=10, kind="macro",   label="Build artifact"),
        Step(id="s2", lane=1, x=200, y=10, kind="handkey", label="Deploy manually"),
    ]
    edges = [Edge(source="s1", target="s2")]
    emit_swimlane(
        out_path="my_process.drawio",
        title="My Process — v1 Sponsor",
        lanes=lanes, steps=steps, edges=edges,
        pool_width=600,
    )

See examples/ for the canonical pattern (sponsor v1 + deep-dive v2 sharing
the same lanes, with assumption-registry ID cross-references).
"""
from __future__ import annotations

from .colors import Palette, DEFAULT_PALETTE
from .geometry import Lane, Step, Edge, EmitConfig
from .drawio_emit import emit_swimlane, render_swimlane_xml

__version__ = "0.1.0"

__all__ = [
    "Lane",
    "Step",
    "Edge",
    "Palette",
    "EmitConfig",
    "DEFAULT_PALETTE",
    "emit_swimlane",
    "render_swimlane_xml",
    "__version__",
]
