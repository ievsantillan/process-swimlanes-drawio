# process-swimlanes-drawio

> **Generate draw.io swimlane diagrams (sponsor + deep-dive pattern) for business-process modernization. Python library + AI-agent skill.**

A small, **zero-dependency** Python library that emits clean `.drawio` XML for swimlane process diagrams. Built for the dual-audience pattern that works well during legacy-system modernization:

- **v1 — Sponsor view:** high-level, ≤30 steps, plain L→R flow. The diagram you show executives.
- **v2 — Deep-dive view:** same lanes, more steps, macro internals, dead-code branches, stale-vintage annotations. The diagram you walk SMEs through.

Both diagrams share lanes (actors / systems) and a colour palette that encodes process risk (manual / live / blocked / stale / dead). Steps optionally cross-reference an **assumption registry** by stable ID (e.g. `A-DOM-13 · C-PROC-03`) so a reader can drill from the diagram to the underlying assumption to the SME backlog.

## Why this exists

Built for the AER NGSM (Natural Gas Supply Model) modernization PoC, where the current state is a 21-workbook annual cycle with ~3 030 hand-keyed cells / cycle. The diagrams are how sponsors and SMEs validate that the modernization team understands the legacy reality before proposing the target architecture.

The pattern generalizes to **any business-process modernization** where you need to:
1. Document the as-is process across multiple actors / systems
2. Distinguish automated vs manual vs blocked vs out-of-scope steps visually
3. Maintain a sponsor-friendly summary AND an engineering-grade deep-dive **without drift between them**
4. Re-generate from a single source of truth as the analysis matures

## Install

```bash
pip install git+https://github.com/ievsantillan/process-swimlanes-drawio.git
```

Or, for local development:

```bash
git clone https://github.com/ievsantillan/process-swimlanes-drawio.git
cd process-swimlanes-drawio
pip install -e ".[dev]"
pytest
```

Requires Python ≥ 3.10. Zero runtime dependencies (stdlib only).

## 30-second quickstart

```python
from process_swimlanes import Lane, Step, Edge, emit_swimlane

lanes = [
    Lane(label="Engineering", y=30,  height=100),
    Lane(label="Operations",  y=130, height=100),
]
steps = [
    Step(id="s1", lane=0, x=10,  y=18, kind="macro",   label="Build artifact"),
    Step(id="s2", lane=0, x=240, y=18, kind="live",    label="Run tests"),
    Step(id="s3", lane=1, x=470, y=18, kind="handkey", label="Deploy manually", refs="C-12"),
]
edges = [Edge(source="s1", target="s2"), Edge(source="s2", target="s3")]

emit_swimlane(
    out_path="my_process.drawio",
    title="My Process — v1",
    lanes=lanes, steps=steps, edges=edges,
    pool_width=900,
)
```

Open `my_process.drawio` at <https://app.diagrams.net/> to view / edit.

## Default colour palette

| Kind        | Colour    | Meaning                                          |
| ----------- | --------- | ------------------------------------------------ |
| `macro`     | 🟦 blue   | Automated / VBA macro / solver step              |
| `live`      | 🟩 green  | Live workbook formula link                       |
| `received`  | 🟩 green  | Newly received external file (was blocked)       |
| `handkey`   | 🟧 orange | Analyst hand-keyed value                         |
| `missing`   | 🟥 red    | File not yet received / blocked                  |
| `stale`     | 🟨 yellow | Received but vintage-stale / suspect             |
| `dead`      | 🟪 purple | Dead code / abandoned path                       |
| `oos`       | ⬜ grey   | Out-of-scope / publication / external            |

The dynamic legend only shows kinds your steps actually use. Custom palettes are supported — see `examples/minimal.py` and `SKILL.md`.

## Examples

| File | What it shows |
|---|---|
| [`examples/minimal.py`](examples/minimal.py) | 3-step "Hello World" — smallest useful diagram |
| [`examples/ngsm_v1_sponsor.py`](examples/ngsm_v1_sponsor.py) | Full 24-step NGSM sponsor view from the AER PoC |
| [`examples/ngsm_v2_deep_dive.py`](examples/ngsm_v2_deep_dive.py) | 43-step deep-dive — macro internals, dead code, vintage-stale annotations |

Run any example:

```bash
python examples/minimal.py
# → wrote out/minimal.drawio
```

## Real-world use

A real-world consumer is the AER NGSM (Natural Gas Supply Model) modernization PoC, where the diagrams are committed alongside an `ASSUMPTIONS.md` registry (138 stable-ID rows) and per-workbook deep-dive analyses. Each step's `refs` field points back to one or more `ASSUMPTIONS.md` rows so the diagram is a navigation surface, not just art.

## For AI agents

If you're invoking this library from an AI coding agent (GitHub Copilot CLI, Claude, etc.), see [`SKILL.md`](SKILL.md) — it documents the input schema, common invocation patterns, success criteria, and gotchas.

## Design notes

- **Zero deps.** Pure stdlib XML emission + `xml.etree.ElementTree` validation pass.
- **Validation up front.** Bad lane indexes, unknown palette kinds, duplicate step IDs, and dangling edges raise `ValueError` before any XML is written.
- **HTML in labels.** Use `\n` for line breaks (converted to `<br/>`). Inline `<font>` styling works (escaped + un-escaped at render).
- **Hand-edit-friendly.** The emitted XML opens cleanly in draw.io for layout polish. Structural changes should go back into your Python source.

## Roadmap

- [ ] YAML/JSON config loader (no Python required for non-engineering authors)
- [ ] Auto-layout (currently x/y are manual — fine for ≤50 steps, painful beyond)
- [ ] Multiple-page / multi-pool documents
- [ ] Mermaid export

PRs welcome.

## License

MIT — see [LICENSE](LICENSE).
