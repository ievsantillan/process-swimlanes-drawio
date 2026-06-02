"""draw.io XML emission for swimlane diagrams.

Public entry points:

    * `emit_swimlane(path, title, lanes, steps, edges, ...) -> None`
      Render and write a `.drawio` file. The most common entry point.

    * `render_swimlane_xml(title, lanes, steps, edges, ...) -> str`
      Render to an in-memory XML string. Useful for tests and custom IO.

Key design points:

    * **Zero runtime dependencies.** Uses only stdlib `xml.sax.saxutils` and
      `xml.etree.ElementTree` (latter for the post-emit validation pass).
    * **Dynamic legend.** The emitted legend only contains color kinds that
      actually appear in the supplied steps — unused palette entries are
      silently dropped so the legend stays tight.
    * **HTML-in-XML rendering.** Labels support `<br/>` line breaks and inline
      `<font>` styling, which draw.io un-escapes at render time. The renderer
      escapes labels with `{'"': '&quot;'}` so the embedded HTML survives the
      `value="..."` attribute.
    * **Validation pass.** After emit, the renderer round-trips the XML through
      `ET.fromstring` and raises on parse failure — so malformed output never
      reaches disk.
"""
from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from collections.abc import Iterable, Sequence
from xml.sax.saxutils import escape as xml_escape

from .colors import DEFAULT_PALETTE, Palette
from .geometry import Edge, EmitConfig, Lane, Step


def render_swimlane_xml(
    title: str,
    lanes: Sequence[Lane],
    steps: Sequence[Step],
    edges: Iterable[Edge],
    *,
    pool_width: int,
    palette: Palette | None = None,
    config: EmitConfig | None = None,
    validate: bool = True,
) -> str:
    """Render a swimlane diagram to a draw.io-compatible XML string.

    Args:
        title:      Diagram title (also pool label).
        lanes:      Lanes in display order (top → bottom).
        steps:      Steps. Each step's `lane` index must be valid for `lanes`.
        edges:      Edges. Each edge's source/target must match a step id.
        pool_width: Total pool width in pixels (including the lane title bar).
                    Pick a value at least `lane_title_width + max(step.x + step.w) + 20`.
        palette:    Color palette. Defaults to `DEFAULT_PALETTE`.
        config:     Layout overrides. Defaults to `EmitConfig()`.
        validate:   If True (default), re-parses the emitted XML via `ET.fromstring`
                    to catch malformed output before write.

    Returns:
        Complete draw.io XML as a UTF-8-ready string (no BOM, LF line endings).
    """
    palette = palette or DEFAULT_PALETTE
    config = config or EmitConfig()
    edges = list(edges)

    _validate_inputs(lanes, steps, edges, palette)

    # Compute layout
    pool_h = config.pool_title_height + lanes[-1].y - 30 + lanes[-1].height
    legend_kinds = [k for k in palette.colors.keys() if any(s.kind == k for s in steps)]
    legend_h = (
        config.legend_title_height
        + config.legend_row_height * len(legend_kinds)
        + config.legend_padding
    )
    legend_x = config.pool_origin_x + pool_width + config.legend_gap_from_pool
    legend_y = config.pool_origin_y
    page_w = legend_x + config.legend_box_width + 40
    page_h = max(pool_h, legend_h) + config.page_bottom_margin

    out: list[str] = []
    out.append('<mxfile host="app.diagrams.net" agent="process-swimlanes-drawio" version="24.7.7">')
    out.append(f'  <diagram id="diagram-{_slug(title)}" name="{xml_escape(title)}">')
    out.append(
        f'    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" '
        f'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{page_w}" '
        f'pageHeight="{page_h}" math="0" shadow="0">'
    )
    out.append('      <root>')
    out.append('        <mxCell id="0" />')
    out.append('        <mxCell id="1" parent="0" />')

    # Pool
    pool_style = (
        "swimlane;fontSize=15;fontStyle=1;html=1;startSize=30;horizontal=1;"
        "swimlaneFillColor=#ffffff;fillColor=#f5f5f5;strokeColor=#333333;"
    )
    out.append(
        f'        <mxCell id="pool" value="{xml_escape(title)}" style="{pool_style}" vertex="1" parent="1">'
    )
    out.append(
        f'          <mxGeometry x="{config.pool_origin_x}" y="{config.pool_origin_y}" '
        f'width="{pool_width}" height="{pool_h}" as="geometry"/>'
    )
    out.append('        </mxCell>')

    # Lanes
    for i, lane in enumerate(lanes):
        lane_style = (
            "swimlane;fontSize=12;fontStyle=1;html=1;startSize=200;horizontal=0;"
            "swimlaneFillColor=#fafafa;fillColor=#fafafa;strokeColor=#888888;"
        )
        out.append(
            f'        <mxCell id="lane_{i}" value="{xml_escape(lane.label)}" '
            f'style="{lane_style}" vertex="1" parent="pool">'
        )
        out.append(
            f'          <mxGeometry x="0" y="{lane.y}" width="{pool_width}" height="{lane.height}" as="geometry"/>'
        )
        out.append('        </mxCell>')

    # Steps
    for step in steps:
        fill, stroke = palette[step.kind]
        html_label = step.label.replace("\n", "<br/>")
        if step.refs:
            html_label += f"<br/><font style='font-size:9px;color:#666;'>{xml_escape(step.refs)}</font>"
        html_label = xml_escape(html_label, {'"': '&quot;'})
        step_style = (
            f"rounded=1;whiteSpace=wrap;html=1;fontSize=10;fillColor={fill};"
            f"strokeColor={stroke};verticalAlign=middle;align=center;"
        )
        out.append(
            f'        <mxCell id="{step.id}" value="{html_label}" '
            f'style="{step_style}" vertex="1" parent="lane_{step.lane}">'
        )
        out.append(
            f'          <mxGeometry x="{step.x + config.lane_title_width}" y="{step.y}" '
            f'width="{step.w}" height="{step.h}" as="geometry"/>'
        )
        out.append('        </mxCell>')

    # Edges
    for j, edge in enumerate(edges):
        e_style = (
            "endArrow=classic;html=1;rounded=0;exitX=1;exitY=0.5;exitDx=0;exitDy=0;"
            "entryX=0;entryY=0.5;entryDx=0;entryDy=0;strokeColor=#666666;" + edge.style_extra
        )
        out.append(
            f'        <mxCell id="e_{j}" value="{xml_escape(edge.label)}" '
            f'style="{e_style}" edge="1" parent="1" source="{edge.source}" target="{edge.target}">'
        )
        out.append('          <mxGeometry relative="1" as="geometry"/>')
        out.append('        </mxCell>')

    # Legend container + rows
    legend_container_style = (
        "rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#333333;"
        "verticalAlign=top;align=center;fontSize=14;fontStyle=1;"
    )
    out.append(
        f'        <mxCell id="legend_box" value="Legend" style="{legend_container_style}" '
        f'vertex="1" parent="1">'
    )
    out.append(
        f'          <mxGeometry x="{legend_x}" y="{legend_y}" width="{config.legend_box_width}" '
        f'height="{legend_h}" as="geometry"/>'
    )
    out.append('        </mxCell>')
    for k_idx, kind in enumerate(legend_kinds):
        fill, stroke = palette[kind]
        desc = palette.legend_text(kind)
        row_y = legend_y + config.legend_title_height + k_idx * config.legend_row_height + 4
        sw_style = f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};"
        out.append(
            f'        <mxCell id="legend_sw_{k_idx}" value="" style="{sw_style}" vertex="1" parent="1">'
        )
        out.append(
            f'          <mxGeometry x="{legend_x + 12}" y="{row_y}" width="36" height="20" as="geometry"/>'
        )
        out.append('        </mxCell>')
        txt_style = "text;html=1;align=left;verticalAlign=middle;fontSize=11;"
        out.append(
            f'        <mxCell id="legend_tx_{k_idx}" value="{xml_escape(desc)}" '
            f'style="{txt_style}" vertex="1" parent="1">'
        )
        out.append(
            f'          <mxGeometry x="{legend_x + 58}" y="{row_y - 2}" '
            f'width="{config.legend_box_width - 70}" height="24" as="geometry"/>'
        )
        out.append('        </mxCell>')

    out.append('      </root>')
    out.append('    </mxGraphModel>')
    out.append('  </diagram>')
    out.append('</mxfile>')

    xml = "\n".join(out)

    if validate:
        # Round-trip parse to catch malformed XML early.
        try:
            ET.fromstring(xml)
        except ET.ParseError as exc:
            raise ValueError(f"Emitted XML failed to parse: {exc}") from exc

    return xml


def emit_swimlane(
    out_path: str,
    title: str,
    lanes: Sequence[Lane],
    steps: Sequence[Step],
    edges: Iterable[Edge],
    *,
    pool_width: int,
    palette: Palette | None = None,
    config: EmitConfig | None = None,
    validate: bool = True,
) -> None:
    """Render and write a swimlane diagram to a `.drawio` file.

    Convenience wrapper around `render_swimlane_xml()` that handles file IO.
    See `render_swimlane_xml()` for parameter details.
    """
    xml = render_swimlane_xml(
        title=title,
        lanes=lanes,
        steps=steps,
        edges=edges,
        pool_width=pool_width,
        palette=palette,
        config=config,
        validate=validate,
    )
    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(xml)


# ---------------------------------------------------------------------------
# Validation helpers (private)
# ---------------------------------------------------------------------------


def _validate_inputs(
    lanes: Sequence[Lane],
    steps: Sequence[Step],
    edges: Sequence[Edge],
    palette: Palette,
) -> None:
    if not lanes:
        raise ValueError("`lanes` must not be empty.")
    n_lanes = len(lanes)

    step_ids: set[str] = set()
    for s in steps:
        if not (0 <= s.lane < n_lanes):
            raise ValueError(
                f"Step {s.id!r} has lane={s.lane}, must be in [0, {n_lanes})."
            )
        if s.kind not in palette:
            raise ValueError(
                f"Step {s.id!r} has kind={s.kind!r}, not present in palette "
                f"(known: {sorted(palette.colors.keys())})."
            )
        if s.id in step_ids:
            raise ValueError(f"Duplicate step id: {s.id!r}.")
        step_ids.add(s.id)

    for e in edges:
        if e.source not in step_ids:
            raise ValueError(f"Edge source {e.source!r} does not match any step id.")
        if e.target not in step_ids:
            raise ValueError(f"Edge target {e.target!r} does not match any step id.")


def _slug(text: str) -> str:
    """Tiny slugifier for diagram ids — keeps alphanumerics + dashes only."""
    return "".join(c if c.isalnum() else "-" for c in text.lower()).strip("-") or "diagram"
