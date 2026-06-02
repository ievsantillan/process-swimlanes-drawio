# SKILL.md — `process-swimlanes-drawio`

> **For AI coding agents (GitHub Copilot CLI, Claude, Cursor, etc.).** This file documents how to invoke `process-swimlanes-drawio` from a code-generation context: when it applies, what inputs to gather from the user, what the success criteria are, and what gotchas to avoid.

## When this skill applies

Use this library when the user asks for any of:

- "Generate a swimlane / process flow / BPMN-style diagram"
- "Diagram the as-is workflow for [X]"
- "Show me a process map of how [team / system] handles [Y]"
- "Make a sponsor-friendly view + an engineering deep-dive of the same process"
- "Re-generate the swimlane diagrams from the updated source"

Especially relevant for:

- **Legacy-system modernization** — current-state documentation
- **Cross-team handoff mapping** — where multiple actors touch one process
- **Audit trail diagrams** — when each step needs a stable ID linking to an external registry
- **Risk-shaded process maps** — when steps need colour-coding by risk class (manual / automated / blocked / stale / dead)

**Not** the right tool for:

- Flowcharts without lanes / actors (use Mermaid `flowchart` instead)
- Class diagrams, sequence diagrams, ER diagrams (use Mermaid / PlantUML)
- Architecture diagrams with non-process semantics (consider `diagrams.mingrammer.com`)

## Inputs to gather from the user

Before generating, get these from the user (or infer + confirm):

1. **Title** of the process (one short string)
2. **Lanes** — list of actors / roles / systems, top-to-bottom. Each lane is a horizontal band.
3. **Steps** — for each step:
   - Short label (use `\n` for line breaks)
   - Which lane it belongs to
   - What `kind` it is (drives the colour — see palette below)
   - Optional: `refs` footnote (e.g. assumption-registry IDs)
4. **Edges** — directed connections between steps (source → target). Optional label, dashed style.
5. **Output format**: usually `v1` sponsor (high-level, ≤30 steps) and/or `v2` deep-dive (50+ steps, macro internals). The library supports both as separate emit calls sharing lanes.

If the user only provides a process description in prose, **propose a draft lane list and step list back to them for confirmation before generating**. Don't burn tokens on a 40-step diagram only to find out you misunderstood the lanes.

## Default palette (8 kinds)

| Kind        | Meaning                                          | When to use                                          |
| ----------- | ------------------------------------------------ | ---------------------------------------------------- |
| `macro`     | Automated / macro / solver step (blue)           | VBA macros, scheduled jobs, CI tasks, scripts        |
| `live`      | Live formula / data link (green)                 | Real-time references, API pulls, live dashboards     |
| `received`  | Recently received external file (green = live)   | When tracking unblocking events over time            |
| `handkey`   | Analyst hand-keyed value (orange)                | Manual copy/paste, type-in-by-hand                   |
| `missing`   | File not yet received / blocked (red)            | Outstanding dependencies, gating items               |
| `stale`     | Received but vintage-stale / suspect (yellow)    | Files received but ⚠️ from older cycle, suspect data |
| `dead`      | Dead code / abandoned path (purple)              | Documented-as-dead branches preserved for audit      |
| `oos`       | Out-of-scope / publication / external (grey)     | Sponsor review, publication artefacts, demand-side   |

Always justify your kind choice in a comment near the step. If a user's process needs kinds outside this palette, define a custom `Palette` (see Custom Palette section below).

## Canonical invocation pattern

```python
from pathlib import Path
from process_swimlanes import Lane, Step, Edge, emit_swimlane

# 1. Define lanes once — reused by v1 and v2.
LANES = [
    Lane(label="External Vendors", y=30,  height=100),
    Lane(label="Engineering",      y=130, height=100),
    Lane(label="Sponsors",         y=230, height=80),
]

# 2. v1 sponsor view (high-level)
V1_STEPS = [
    Step("v1_01", 0, 10,  18, "handkey", "Quarterly cost report",    "A-01"),
    Step("v1_02", 1, 240, 18, "macro",   "CI build + deploy",        "C-03"),
    Step("v1_03", 2, 470, 18, "oos",     "Q3 board review",          "C-07"),
]
V1_EDGES = [
    Edge("v1_01", "v1_02"),
    Edge("v1_02", "v1_03"),
]

# 3. v2 deep-dive (same lanes, more steps)
V2_STEPS = [
    # ... 30-50 steps including macro internals, dead branches, annotations ...
]

# 4. Emit both
out = Path("out")
emit_swimlane(out / "process_v1_sponsor.drawio",
              "My Process — Sponsor View",
              LANES, V1_STEPS, V1_EDGES, pool_width=900)
emit_swimlane(out / "process_v2_deep_dive.drawio",
              "My Process — Deep Dive",
              LANES, V2_STEPS, V2_EDGES, pool_width=2400)
```

## Success criteria

A successful invocation produces:

- ✅ A `.drawio` file that opens cleanly in <https://app.diagrams.net/> without errors
- ✅ Lanes appear in the order specified, with correct heights (no overlap)
- ✅ Step colours match the user's intent (manual vs automated vs blocked)
- ✅ Legend at the right side shows only the kinds actually used
- ✅ Edges connect to the correct steps (visible arrows L→R)
- ✅ `xml.etree.ElementTree.parse(output_path)` succeeds (the library validates this automatically)

If any of the above fails, the library raises `ValueError` before write — surface that to the user with the specific failing constraint.

## Common gotchas

| Gotcha | Mitigation |
|---|---|
| Steps overlapping inside a lane | Use distinct `y` offsets within the lane (e.g. y=18 top row, y=110 bottom row) |
| Step horizontal positions colliding | Use `x` increments of `~190` for default 170-px-wide steps |
| Pool too narrow → steps clipped | Set `pool_width` ≥ `lane_title_width (200) + max(step.x + step.w) + 20` |
| Lane heights too small for two rows of steps | Lane needs `height ≥ 220` for two 64-px rows + padding |
| HTML in labels not rendering | Use `\n` for line breaks (not `<br/>`); the library handles the conversion |
| Edge labels not appearing | Pass via `Edge(label="...")`, not embedded in step labels |
| Duplicate step IDs | Each step needs a unique `id`. Convention: `<diagram>_<NN>` (e.g. `v1_03`) |
| Want a dashed/colored edge | Pass `style_extra="dashed=1;strokeColor=#999;"` (raw draw.io style fragment) |

## Custom palette

If the default palette doesn't fit, define your own:

```python
from process_swimlanes import Palette, emit_swimlane

palette = Palette(
    colors={
        "good":    ("#d5e8d4", "#82b366"),
        "warn":    ("#fff2cc", "#d6b656"),
        "blocked": ("#f8cecc", "#b85450"),
    },
    legend_labels={
        "good":    "Approved & on track",
        "warn":    "Needs attention",
        "blocked": "Blocked on dependency",
    },
)

emit_swimlane(
    "out.drawio", "My Process",
    lanes, steps, edges,
    pool_width=900, palette=palette,
)
```

Only kinds used by your steps appear in the legend. The library validates that each step's `kind` exists in the palette and raises `ValueError` otherwise.

## Layout overrides

If you need bigger labels, wider steps, or smaller margins, override `EmitConfig`:

```python
from process_swimlanes import EmitConfig

cfg = EmitConfig(
    lane_title_width=300,    # wider left bar for long lane names
    step_default_w=200,      # wider steps
    legend_box_width=400,    # roomier legend
)

emit_swimlane("out.drawio", "Custom Layout",
              lanes, steps, edges, pool_width=2000, config=cfg)
```

## Maintenance pattern

The recommended workflow for an ongoing modernization project:

1. **One Python source file per diagram pair** (`gen_<project>_swimlanes.py`)
2. Commit the script to the project repo's `scripts/` folder
3. Re-run on every material finding update (file arrival, SME closure, scope change)
4. Hand-edits inside draw.io are tolerated for layout polish only — structural changes go back into the script
5. Cross-reference steps to a stable-ID registry (e.g. `ASSUMPTIONS.md`) so the diagram becomes a navigation surface

For projects with multiple swimlane diagrams (e.g. multi-team modernization), consider promoting the per-project generator script into a thin wrapper around shared LANE definitions.

## Validation checklist before delivering

Run through this before presenting a generated diagram:

- [ ] Lane labels readable, no truncation
- [ ] Step labels readable at default font sizes
- [ ] No overlapping steps within a lane
- [ ] Every step's kind is justified by the user's described risk class
- [ ] Edge directions match the actual data/control flow
- [ ] `refs` footnotes (if used) point to real assumption-registry IDs, not made up
- [ ] File opens in <https://app.diagrams.net/> without "broken file" warning
- [ ] If the user has a related v1/v2 pair, lanes are identical between them

## Reference implementations

- [`examples/minimal.py`](examples/minimal.py) — smallest possible diagram (3 steps)
- [`examples/ngsm_v1_sponsor.py`](examples/ngsm_v1_sponsor.py) — full sponsor view, 24 steps
- [`examples/ngsm_v2_deep_dive.py`](examples/ngsm_v2_deep_dive.py) — full deep-dive, 43 steps
- Live consumer: <https://github.com/ievsantillan/aer_economic-forecast-modelling> (NGSM modernization PoC)
