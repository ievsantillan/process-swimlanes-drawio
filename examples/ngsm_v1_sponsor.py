"""NGSM Annual Cycle — Sponsor View (v1) — reference example.

Faithful port of the v1 swimlane currently maintained for the AER NGSM
(Natural Gas Supply Model) modernization PoC at
https://github.com/ievsantillan/aer_economic-forecast-modelling.

24 steps across 8 lanes:
    External Vendors → AER Data Services → Tim Mack (Test Judy macros)
    → Sanghmitra Banerjee (NGSM workbook chain) → Glen Tsui (Carbon/Demand/DB)
    → Analyst (SME TBC) → Publication (owner TBC) → Sponsors

Each step's `refs` field cross-references the project's ASSUMPTIONS.md
registry IDs (A-DOM-*, C-PROC-*, E-SUSP-*) so a reader can drill from the
diagram to the underlying assumption.

Run:

    python examples/ngsm_v1_sponsor.py
"""
from __future__ import annotations

from pathlib import Path

from process_swimlanes import Edge, Lane, Step, emit_swimlane

# 8 lanes shared with v2 deep-dive — keep these in sync if both examples evolve.
LANES = [
    Lane("External Vendors",                            30,  100),
    Lane("AER Data Services",                          130,  100),
    Lane("Tim Mack — Test Judy macros",                230,  100),
    Lane("Sanghmitra Banerjee — NGSM workbook chain",  330,  220),
    Lane("Glen Tsui — Carbon / Demand / DB gatekeeper",550,  100),
    Lane("Analyst — SME TBC",                          650,  220),
    Lane("Publication — Owner TBC",                    870,  100),
    Lane("Sponsors — ME&E Leadership",                 970,   80),
]

STEPS = [
    # External Vendors
    Step("v1_01", 0, 220,  18, "handkey", "Sproule quarterly\nprice deck",                  "A-DOM-13 · C-PROC-03"),
    Step("v1_02", 0, 410,  18, "handkey", "CanOils annual\ntype-well cost CSV",             "B-COH-13 · D-POC-17"),
    # AER Data Services
    Step("v1_03", 1, 220,  18, "macro",   "Corporate_Query\nSQL Server pull",               "C-PROC-22"),
    # Tim Mack
    Step("v1_04", 2, 410,  18, "macro",   "Run GAS_Forecasting_Macro\n(\"Test Judy\")",     "C-PROC-14 · C-PROC-18"),
    Step("v1_05", 2, 600,  18, "macro",   "8 staging xlsx →\n@Forecasting_Downloads"),
    # Sanghmitra — top row
    Step("v1_06", 3, 790,  18, "live",    "Refresh GASProdHist\n-TEMPLATE pivot",           "C-PROC-20"),
    Step("v1_07", 3, 980,  18, "handkey", "Toggle slicers per\nPSAC × drilltype × fluid",   "C-PROC-13 · B-COH-07"),
    Step("v1_08", 3, 1170, 18, "handkey", "Copy ANALYSIS 22-29\n→ NGSMTechDataFeed",        "C-PROC-08 · D-POC-02"),
    Step("v1_09", 3, 1360, 18, "handkey", "Update NGSM_202501\nPSAC tab inputs",            "C-PROC-08"),
    Step("v1_10", 3, 1670, 18, "macro",   "NG_NewWell Mod19\nForecastNPVs",                 "C-PROC-15"),
    Step("v1_11", 3, 1860, 18, "macro",   "NG_NewWell Mod20\nCopyInitialWells2NGSM",        "C-PROC-16"),
    # Sanghmitra — bottom row
    Step("v1_12", 3, 2050, 110, "macro",  "Run_All_Macros in\nAssumptions wb (~3 min)",     "C-PROC-12 · A-DOM-09"),
    Step("v1_13", 3, 2240, 110, "macro",  "NG Supply Cost Model\nGoalSeek × 13 PSAC",       "A-DOM-12 · D-POC-10"),
    Step("v1_14", 3, 2430, 110, "handkey","Update NG_Cashflow\ninputs (per cohort)",        "D-POC-08"),
    # Glen Tsui — Carbon received 2026-06-02 (vintage-stale); Alberta Gas Demand out-of-scope
    Step("v1_15", 4, 1360, 18, "stale",   "Carbon_pricing_cost\n.xlsx (received,\n2023-vintage)", "D-POC-27 · E-SUSP-10"),
    Step("v1_16", 4, 1550, 18, "oos",     "Alberta Gas Demand\n(received, out of\nNGSM scope)",   "D-POC-29"),
    # Analyst — top row
    Step("v1_17", 5, 410,  18, "handkey", "Update CAPEX & OPEX\n-History (from Sproule)",   "C-PROC-11 · E-SUSP-01"),
    Step("v1_18", 5, 600,  18, "handkey", "Hand-key cost feeds\n→ NewWell Input-Cost",      "C-PROC-11"),
    Step("v1_19", 5, 980,  18, "handkey", "NGL fractions K39:M39\n→ PSACAREA × 13",         "C-PROC-09 · B-COH-11"),
    Step("v1_20", 5, 1170, 18, "handkey", "Shrinkage O39\n→ PSACAREA × 13",                 "C-PROC-10 · A-DOM-29 · E-SUSP-03"),
    # Analyst — bottom row (Tableau received 2026-06-02; Slice E target)
    Step("v1_21", 5, 2620, 110, "oos",    "Tableau ST98 2025\nNaturalGas_LINKED\n(received, Slice E)", "C-PROC-29 · D-POC-28"),
    # Publication
    Step("v1_22", 6, 2810, 18, "oos",     "Mid-Oct: 30-yr\nGoA publication",                "C-PROC-01"),
    Step("v1_23", 6, 3000, 18, "oos",     "Late-Jan: AEO / ST98\npublication",              "C-PROC-02"),
    # Sponsors
    Step("v1_24", 7, 3000,  8, "oos",     "Sponsor review:\nMo · Amanda · Brendan · Harvinder", "C-PROC-07"),
]

EDGES = [
    Edge("v1_01", "v1_17"),
    Edge("v1_02", "v1_17"),
    Edge("v1_03", "v1_04"),
    Edge("v1_04", "v1_05"),
    Edge("v1_05", "v1_06"),
    Edge("v1_06", "v1_07"),
    Edge("v1_07", "v1_08"),
    Edge("v1_08", "v1_09"),
    Edge("v1_17", "v1_18"),
    Edge("v1_18", "v1_10"),
    Edge("v1_19", "v1_09"),
    Edge("v1_20", "v1_09"),
    Edge("v1_09", "v1_10"),
    Edge("v1_10", "v1_11"),
    Edge("v1_11", "v1_12"),
    Edge("v1_12", "v1_13"),
    Edge("v1_15", "v1_14"),
    Edge("v1_13", "v1_14"),
    Edge("v1_13", "v1_21"),
    Edge("v1_14", "v1_21"),
    Edge("v1_21", "v1_22"),
    Edge("v1_22", "v1_23"),
    Edge("v1_23", "v1_24"),
    Edge("v1_16", "v1_14", label="demand", style_extra="dashed=1;"),
]


def main() -> None:
    out = Path(__file__).parent.parent / "out" / "ngsm_v1_sponsor.drawio"
    emit_swimlane(
        out_path=str(out),
        title="NGSM Annual Cycle — Sponsor View (v1)",
        lanes=LANES,
        steps=STEPS,
        edges=EDGES,
        # v1 width: max step x = 3000 + 170 = 3170 → + lane title (200) + pad = 3390
        pool_width=3390,
    )
    print(f"Wrote {out} — {len(STEPS)} steps, {len(EDGES)} edges, {len(LANES)} lanes")


if __name__ == "__main__":
    main()
