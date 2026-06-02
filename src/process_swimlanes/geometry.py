"""Geometry primitives for swimlane diagrams: Lane, Step, Edge, EmitConfig.

A swimlane diagram is composed of:

    * A horizontal **pool** containing N stacked **lanes** (each a horizontal band
      assigned to a single actor / role / system).
    * **Steps** placed at (lane, x, y) coordinates inside the pool. Each step has
      a `kind` that maps to a colour via the active `Palette`.
    * **Edges** connecting steps left-to-right (or with arbitrary entry/exit
      points if `style_extra` overrides them).

Coordinate system (draw.io):
    * Y increases downward.
    * Step (x, y) is relative to the lane's interior, with the LANE_TITLE_WIDTH
      offset applied automatically by `emit_swimlane()`.
    * Lane y/height fields are absolute within the pool (not stacking).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Lane:
    """A horizontal lane inside the pool.

    Attributes:
        label:  Lane title shown in the left-side title bar.
        y:      Y-offset of the lane within the pool (in pixels, relative to pool top).
        height: Height of the lane (in pixels). Steps live inside this band.
    """
    label: str
    y: int
    height: int


@dataclass(frozen=True)
class Step:
    """A single step (rounded rectangle) inside one lane.

    Attributes:
        id:    Unique step identifier (e.g. "v1_03"). Referenced by Edge.source/target.
        lane:  Zero-based index into the lanes list.
        x:     X-offset within the lane (relative to lane interior; the renderer
               adds LANE_TITLE_WIDTH automatically).
        y:     Y-offset within the lane.
        kind:  Palette key (e.g. "macro", "handkey", "missing"). Determines colour.
        label: Step text. Use "\\n" to insert line breaks (converted to <br/>).
        refs:  Optional small-grey footnote (e.g. ASSUMPTIONS.md IDs "A-DOM-13 · C-PROC-03").
        w:     Width override (default 170).
        h:     Height override (default 64).
    """
    id: str
    lane: int
    x: int
    y: int
    kind: str
    label: str
    refs: str = ""
    w: int = 170
    h: int = 64


@dataclass(frozen=True)
class Edge:
    """A directed connection between two steps.

    Attributes:
        source:      Source step.id
        target:      Target step.id
        label:       Optional edge label text.
        style_extra: Raw draw.io style fragment appended to the default. Use to
                     override entry/exit anchors, dash patterns, colour. Example:
                     `style_extra="dashed=1;strokeColor=#999999;"`
    """
    source: str
    target: str
    label: str = ""
    style_extra: str = ""


@dataclass(frozen=True)
class EmitConfig:
    """Layout / typographic constants for the renderer. Override to taste.

    Defaults are tuned for diagrams with ~24-44 steps and 7-9 lanes.
    """
    pool_origin_x: int = 40
    pool_origin_y: int = 40
    pool_title_height: int = 30
    lane_title_width: int = 200      # left-side bar showing lane labels
    step_default_w: int = 170
    step_default_h: int = 64
    legend_box_width: int = 300
    legend_title_height: int = 36
    legend_row_height: int = 30
    legend_padding: int = 16
    legend_gap_from_pool: int = 30   # horizontal gap pool→legend
    page_bottom_margin: int = 200
