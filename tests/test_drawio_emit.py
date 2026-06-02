"""Pytest tests for `process_swimlanes.drawio_emit` + validation."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from process_swimlanes import (
    DEFAULT_PALETTE,
    Edge,
    EmitConfig,
    Lane,
    Palette,
    Step,
    emit_swimlane,
    render_swimlane_xml,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def basic_lanes() -> list[Lane]:
    return [
        Lane(label="A", y=30,  height=100),
        Lane(label="B", y=130, height=100),
    ]


@pytest.fixture
def basic_steps() -> list[Step]:
    return [
        Step(id="s1", lane=0, x=10,  y=10, kind="macro",   label="One"),
        Step(id="s2", lane=1, x=200, y=10, kind="handkey", label="Two", refs="A-01"),
    ]


@pytest.fixture
def basic_edges() -> list[Edge]:
    return [Edge(source="s1", target="s2")]


# ---------------------------------------------------------------------------
# Happy-path emission
# ---------------------------------------------------------------------------


def test_render_produces_parseable_xml(basic_lanes, basic_steps, basic_edges):
    xml = render_swimlane_xml(
        title="Test", lanes=basic_lanes, steps=basic_steps, edges=basic_edges,
        pool_width=500,
    )
    root = ET.fromstring(xml)
    assert root.tag == "mxfile"
    diagram = root.find("diagram")
    assert diagram is not None
    assert diagram.get("name") == "Test"


def test_emitted_xml_contains_pool_and_lanes(basic_lanes, basic_steps, basic_edges):
    xml = render_swimlane_xml(
        title="Pool Check", lanes=basic_lanes, steps=basic_steps, edges=basic_edges,
        pool_width=500,
    )
    assert 'id="pool"' in xml
    assert 'id="lane_0"' in xml
    assert 'id="lane_1"' in xml


def test_emitted_xml_contains_all_steps(basic_lanes, basic_steps, basic_edges):
    xml = render_swimlane_xml(
        title="Steps Check", lanes=basic_lanes, steps=basic_steps, edges=basic_edges,
        pool_width=500,
    )
    assert 'id="s1"' in xml
    assert 'id="s2"' in xml
    assert "One" in xml
    assert "Two" in xml
    assert "A-01" in xml  # refs footnote


def test_emitted_xml_contains_all_edges(basic_lanes, basic_steps, basic_edges):
    xml = render_swimlane_xml(
        title="Edge Check", lanes=basic_lanes, steps=basic_steps, edges=basic_edges,
        pool_width=500,
    )
    assert 'id="e_0"' in xml
    assert 'source="s1"' in xml
    assert 'target="s2"' in xml


# ---------------------------------------------------------------------------
# Dynamic legend
# ---------------------------------------------------------------------------


def test_legend_only_includes_used_kinds(basic_lanes):
    # Only `macro` is used — legend should NOT contain handkey, missing, etc.
    steps = [Step(id="m1", lane=0, x=10, y=10, kind="macro", label="M")]
    xml = render_swimlane_xml(
        title="Single Kind", lanes=basic_lanes, steps=steps, edges=[],
        pool_width=400,
    )
    # Legend rendered as swatch + text cells (legend_sw_0, legend_tx_0)
    assert 'id="legend_sw_0"' in xml
    assert 'id="legend_sw_1"' not in xml  # only one kind → only one legend row
    assert DEFAULT_PALETTE.legend_text("macro") in xml


def test_legend_includes_all_kinds_when_present(basic_lanes):
    steps = [
        Step(id="a", lane=0, x=10,  y=10, kind="macro",   label="A"),
        Step(id="b", lane=0, x=200, y=10, kind="handkey", label="B"),
        Step(id="c", lane=1, x=10,  y=10, kind="live",    label="C"),
    ]
    xml = render_swimlane_xml(
        title="Three Kinds", lanes=basic_lanes, steps=steps, edges=[],
        pool_width=500,
    )
    # 3 distinct kinds → 3 legend rows
    assert 'id="legend_sw_0"' in xml
    assert 'id="legend_sw_1"' in xml
    assert 'id="legend_sw_2"' in xml
    assert 'id="legend_sw_3"' not in xml


# ---------------------------------------------------------------------------
# Validation: input rejection
# ---------------------------------------------------------------------------


def test_rejects_empty_lanes():
    with pytest.raises(ValueError, match="lanes"):
        render_swimlane_xml(title="X", lanes=[], steps=[], edges=[], pool_width=100)


def test_rejects_out_of_range_lane_index(basic_lanes):
    bad = [Step(id="s1", lane=5, x=10, y=10, kind="macro", label="oops")]
    with pytest.raises(ValueError, match="lane=5"):
        render_swimlane_xml(title="X", lanes=basic_lanes, steps=bad, edges=[],
                            pool_width=400)


def test_rejects_unknown_kind(basic_lanes):
    bad = [Step(id="s1", lane=0, x=10, y=10, kind="unicorn", label="oops")]
    with pytest.raises(ValueError, match="unicorn"):
        render_swimlane_xml(title="X", lanes=basic_lanes, steps=bad, edges=[],
                            pool_width=400)


def test_rejects_duplicate_step_id(basic_lanes):
    bad = [
        Step(id="s1", lane=0, x=10,  y=10, kind="macro", label="A"),
        Step(id="s1", lane=0, x=200, y=10, kind="macro", label="B"),
    ]
    with pytest.raises(ValueError, match="Duplicate step id"):
        render_swimlane_xml(title="X", lanes=basic_lanes, steps=bad, edges=[],
                            pool_width=400)


def test_rejects_dangling_edge(basic_lanes, basic_steps):
    bad_edges = [Edge(source="s1", target="ghost")]
    with pytest.raises(ValueError, match="ghost"):
        render_swimlane_xml(title="X", lanes=basic_lanes, steps=basic_steps,
                            edges=bad_edges, pool_width=400)


# ---------------------------------------------------------------------------
# Custom palette
# ---------------------------------------------------------------------------


def test_custom_palette_kinds_work(basic_lanes):
    palette = Palette(
        colors={"go": ("#d5e8d4", "#82b366"), "stop": ("#f8cecc", "#b85450")},
        legend_labels={"go": "GO!", "stop": "STOP!"},
    )
    steps = [
        Step(id="g", lane=0, x=10,  y=10, kind="go",   label="green"),
        Step(id="s", lane=1, x=200, y=10, kind="stop", label="red"),
    ]
    xml = render_swimlane_xml(
        title="Custom", lanes=basic_lanes, steps=steps, edges=[],
        pool_width=400, palette=palette,
    )
    assert "GO!" in xml
    assert "STOP!" in xml
    # Default palette kinds should NOT appear in legend
    assert DEFAULT_PALETTE.legend_text("macro") not in xml


def test_custom_palette_rejects_step_with_unknown_kind(basic_lanes):
    palette = Palette(colors={"only": ("#fff", "#000")})
    bad = [Step(id="s", lane=0, x=10, y=10, kind="missing", label="oops")]
    with pytest.raises(ValueError, match="missing"):
        render_swimlane_xml(title="X", lanes=basic_lanes, steps=bad, edges=[],
                            pool_width=400, palette=palette)


# ---------------------------------------------------------------------------
# File output
# ---------------------------------------------------------------------------


def test_emit_writes_file_and_creates_parent_dir(tmp_path: Path, basic_lanes, basic_steps, basic_edges):
    target = tmp_path / "deep" / "nested" / "out.drawio"
    emit_swimlane(
        out_path=str(target),
        title="File Out",
        lanes=basic_lanes,
        steps=basic_steps,
        edges=basic_edges,
        pool_width=500,
    )
    assert target.is_file()
    # Re-parse the written file
    root = ET.parse(target).getroot()
    assert root.tag == "mxfile"


def test_emit_file_is_valid_xml_endtoend(tmp_path: Path, basic_lanes, basic_steps, basic_edges):
    target = tmp_path / "endtoend.drawio"
    emit_swimlane(
        out_path=str(target),
        title="E2E",
        lanes=basic_lanes,
        steps=basic_steps,
        edges=basic_edges,
        pool_width=500,
    )
    # If ET.parse succeeds, the file is well-formed
    tree = ET.parse(target)
    diagrams = tree.findall(".//diagram")
    assert len(diagrams) == 1


# ---------------------------------------------------------------------------
# Examples smoke-test (NGSM port)
# ---------------------------------------------------------------------------


def test_example_minimal_runs(tmp_path: Path, monkeypatch):
    """Smoke-test the minimal example by running its emit logic."""
    # Reproduce minimal example inline to avoid import side effects
    lanes = [Lane("A", 30, 100), Lane("B", 130, 100)]
    steps = [
        Step("s1", 0, 10, 18, "macro",   "One"),
        Step("s2", 0, 240, 18, "live",   "Two"),
        Step("s3", 1, 470, 18, "handkey","Three"),
    ]
    edges = [Edge("s1", "s2"), Edge("s2", "s3")]
    target = tmp_path / "minimal.drawio"
    emit_swimlane(str(target), "Minimal Demo", lanes, steps, edges, pool_width=900)
    assert target.exists()
    assert ET.parse(target).getroot().tag == "mxfile"


# ---------------------------------------------------------------------------
# EmitConfig overrides
# ---------------------------------------------------------------------------


def test_custom_config_widths_apply(basic_lanes, basic_steps, basic_edges):
    config = EmitConfig(lane_title_width=300, step_default_w=120)
    xml = render_swimlane_xml(
        title="Config",
        lanes=basic_lanes, steps=basic_steps, edges=basic_edges,
        pool_width=600, config=config,
    )
    # Step s1 was at x=10; with custom lane_title_width=300, rendered x should be 310
    assert 'x="310"' in xml
