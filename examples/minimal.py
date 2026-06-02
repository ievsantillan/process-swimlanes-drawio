"""Minimal 3-step demo: smallest useful swimlane diagram.

Renders a 2-lane / 3-step / 2-edge "Hello World" swimlane to demonstrate the
core API surface. Each step uses a different `kind` so the dynamic legend
shows three rows. Run:

    python examples/minimal.py

…then open `out/minimal.drawio` at https://app.diagrams.net/.
"""
from __future__ import annotations

from pathlib import Path

from process_swimlanes import Edge, Lane, Step, emit_swimlane


def main() -> None:
    lanes = [
        Lane(label="Engineering", y=30,  height=100),
        Lane(label="Operations",  y=130, height=100),
    ]
    steps = [
        Step(id="s1", lane=0, x=10,  y=18, kind="macro",
             label="Build artifact\n(CI)",          refs="A-01"),
        Step(id="s2", lane=0, x=240, y=18, kind="live",
             label="Run automated tests"),
        Step(id="s3", lane=1, x=470, y=18, kind="handkey",
             label="Deploy to prod\n(manual)",     refs="C-12"),
    ]
    edges = [
        Edge(source="s1", target="s2"),
        Edge(source="s2", target="s3"),
    ]

    out = Path(__file__).parent.parent / "out" / "minimal.drawio"
    emit_swimlane(
        out_path=str(out),
        title="Minimal Process — Demo",
        lanes=lanes,
        steps=steps,
        edges=edges,
        pool_width=900,
    )
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
