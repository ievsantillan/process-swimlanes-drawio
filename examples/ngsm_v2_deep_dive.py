"""NGSM Annual Cycle — Deep Dive (v2) — reference example.

The deep-dive companion to `ngsm_v1_sponsor.py`. Shares the same 8 lanes
but adds:
    * Macro internals (Mod19/20 paste-block targets, 5 driver sub-steps)
    * Dead-code branch (Mod21/22/23 stale 202309 paths)
    * Empty-Risk annotation (21/21 workbooks confirmed dormant as of 2026-06-02)
    * Canonical type-curve source (2002-20 NPVs.xlsm)
    * Conventional adjustment factor (2025Marketable Calculation.xlsx)
    * Royalty + CCA sub-engines

43 steps total. Same lanes / colors / refs convention as v1.

Run:

    python examples/ngsm_v2_deep_dive.py
"""
from __future__ import annotations

from pathlib import Path

from process_swimlanes import Edge, Lane, Step, emit_swimlane

# Same 8 lanes as v1 — kept in sync intentionally so the two diagrams overlay.
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
    Step("v2_01", 0, 220,  18, "handkey", "Sproule quarterly\nN24/O24 inflation",          "C-PROC-23 · E-SUSP-04"),
    Step("v2_02", 0, 410,  18, "handkey", "CanOils 32 type wells\n× 11 PSAC regions",      "B-COH-13"),
    # AER Data Services
    Step("v2_03", 1, 220,  18, "macro",   "Corporate_Query\nQryDBCorp\\Qry1",              "C-PROC-22"),
    Step("v2_04", 1, 410,  18, "macro",   "[DEVRDEDB].Forecasting\n.dbo.CBM_Well_List_YYYY","C-PROC-18"),
    # Tim Mack
    Step("v2_05", 2, 600,  18, "macro",   "Module1.Run dispatch\n(4 live targets)",         "C-PROC-14"),
    Step("v2_06", 2, 790,  18, "macro",   "8 staging xlsx outputs\n(GASProdHist, IP_GAS_Calcs, ...)"),
    Step("v2_07", 2, 980,  18, "dead",    "Mod21/22/23: stale\n202309 paths (dead)",        "E-SUSP-05 · C-PROC-17"),
    # Sanghmitra — top row
    Step("v2_08", 3, 1170, 18, "live",    "GASProdHist-TEMPLATE\ndata sheet (866k rows)",   "D-POC-02 · D-POC-03"),
    Step("v2_09", 3, 1360, 18, "handkey", "\"Change Data Source\"\non pivot (manual)",      "C-PROC-20 · E-SUSP-19"),
    Step("v2_10", 3, 1550, 18, "handkey", "Slicer toggles\n(~52 per cycle)",                "C-PROC-13 · B-COH-07"),
    Step("v2_11", 3, 1740, 18, "handkey", "Copy 225 cells\n→ NGSMTechDataFeed",             "C-PROC-08 · D-POC-07"),
    Step("v2_12", 3, 1930, 18, "live",    "NGSM_202501 PSAC tabs\n(13 sheets)",             "D-POC-02"),
    Step("v2_13", 3, 2120, 18, "macro",   "Mod19 ForecastNPVs:\nwrite 16 scalars + 30y",    "C-PROC-15"),
    Step("v2_14", 3, 2310, 18, "macro",   "Mod19 reads back\nEcon Ind's!E14 (NPV@8%)",      "A-DOM-07"),
    Step("v2_15", 3, 2500, 18, "macro",   "Mod20 CopyInitial\nWells2NGSM",                  "C-PROC-16"),
    # Sanghmitra — bottom row (Run_All_Macros 5-step paste loop)
    Step("v2_16", 3, 1170, 110, "macro",  "Run_All_Macros\nfor PSAC in 13:",                "C-PROC-12"),
    Step("v2_17", 3, 1360, 110, "macro",  "Paste D5:F14\n(prices) → Input!D5"),
    Step("v2_18", 3, 1550, 110, "macro",  "Paste D16:F22\n(capex) → Input!D16"),
    Step("v2_19", 3, 1740, 110, "macro",  "Paste D24:F28\n(opex×0.75) → Input!D24",         "A-DOM-33 · E-SUSP-09"),
    Step("v2_20", 3, 1930, 110, "macro",  "Paste K5:O33\n(prod) → Prod'n!C11"),
    Step("v2_21", 3, 2120, 110, "macro",  "Supply_Cost_Gas\nGoalSeek F42→D15",              "D-POC-10"),
    Step("v2_22", 3, 2310, 110, "macro",  "Supply_Cost_Sensitivities\n(Aug-25 patch)",      "E-SUSP-08"),
    Step("v2_23", 3, 2500, 110, "handkey","Selection.Copy →\n<PSAC>!B2 (C55)",              "E-SUSP-15"),
    # Glen Tsui — Carbon received 2026-06-02 (vintage-stale); Alberta Gas Demand received but OOS
    Step("v2_24", 4, 1740, 18, "stale",   "Carbon_pricing_cost\n.Aggregate_OptIn (27c)\n⚠️ 2023-vintage", "D-POC-27 · E-SUSP-10"),
    Step("v2_25", 4, 1930, 18, "oos",     "Alberta Gas Demand\n(received, OOS for\nNGSM PoC)", "D-POC-29"),
    # Analyst — top row (CAPEX + Sproule + assumption hand-keys)
    Step("v2_26", 5, 220,  18, "handkey", "CAPEX & OPEX-History\nrow 151 = E*1+F$150",      "C-PROC-11 · E-SUSP-01"),
    Step("v2_27", 5, 410,  18, "handkey", "Forward-roll\n\"New well2 2021\" block",         "C-PROC-11 · E-SUSP-07"),
    Step("v2_28", 5, 600,  18, "live",    "NewWell Input-Cost\nC8:G8 (live ref)",           "C-PROC-15"),
    Step("v2_29", 5, 790,  18, "handkey", "Sproule N24/O24\n(\"2024 9 mo Act\")",           "C-PROC-23 · E-SUSP-04"),
    Step("v2_30", 5, 980,  18, "handkey", "PSAC_Production_NGL\nfractions K39:M39",         "C-PROC-09 · B-COH-11"),
    Step("v2_31", 5, 1170, 18, "handkey", "Shrinkage row 39\n→ PSACAREA O39 × 13",          "C-PROC-10 · A-DOM-29 · E-SUSP-02 · E-SUSP-03"),
    Step("v2_32", 5, 1360, 18, "handkey", "D&I credits 4 cells\n+ TVD/TLL/TPP defaults",    "A-DOM-38"),
    # Analyst — bottom row (downstream)
    Step("v2_33", 5, 2120, 110, "handkey", "NG_Cashflow inputs\n(per-PSAC vintage matrix)", "D-POC-08 · A-DOM-20"),
    Step("v2_34", 5, 2310, 110, "live",    "Econ Ind's!E14\n(after-tax NPV @ 8%)",          "A-DOM-07 · D-POC-08"),
    Step("v2_35", 5, 2500, 110, "live",    "Royalty engine\n(NG/C5+/Propane/Butane)",       "A-DOM-16 · A-DOM-17 · A-DOM-18 · D-POC-13"),
    Step("v2_36", 5, 2690, 110, "live",    "CCA pools (0.3F+0.7G)\nClass 41-like",          "A-DOM-19 · E-SUSP-17"),
    Step("v2_37", 5, 2880, 110, "oos",     "Tableau ST98 2025\nNaturalGas_LINKED\n(Slice E target)", "C-PROC-29 · D-POC-28"),
    # Publication
    Step("v2_38", 6, 3070, 18, "oos",      "Mid-Oct 30-yr\nGoA publication",                "C-PROC-01"),
    Step("v2_39", 6, 3260, 18, "oos",      "Late-Jan AEO / ST98",                           "C-PROC-02"),
    # Sponsors
    Step("v2_40", 7, 3260,  8, "oos",      "Mo · Amanda · Brendan\n· Harvinder review",     "C-PROC-07"),
    # Annotation
    Step("v2_41", 2, 1170, 18, "oos",      "★ Empty-Risk pattern:\n21/21 wb dormant —\nSlice C DESCOPED", "A-DOM-41 · D-POC-23"),
    # Canonical Slice B source (resolves the long-running [6] mis-attribution)
    Step("v2_42", 3, 980,  18, "received", "2002-20 NPVs.xlsm\nVintaged IPs (6 825c)\n+ Shrinkage&NGLs", "A-DOM-42 · A-DOM-43 · D-POC-24 · D-POC-25 · E-SUSP-11"),
    # Conventional marketable adjustment factor for SUMMARY-FORST98(NEW) row 66
    Step("v2_43", 3, 2120, 18, "received", "2025Marketable Calc\n→ SUMMARY-FORST98\nrow 66 adj factor", "A-DOM-44 · D-POC-26"),
]

EDGES = [
    Edge("v2_01", "v2_26"),
    Edge("v2_02", "v2_26"),
    Edge("v2_03", "v2_05"),
    Edge("v2_04", "v2_05"),
    Edge("v2_05", "v2_06"),
    Edge("v2_06", "v2_08"),
    Edge("v2_08", "v2_09"),
    Edge("v2_09", "v2_10"),
    Edge("v2_10", "v2_11"),
    Edge("v2_11", "v2_12"),
    Edge("v2_26", "v2_27"),
    Edge("v2_27", "v2_28"),
    Edge("v2_28", "v2_13"),
    Edge("v2_29", "v2_26"),
    Edge("v2_30", "v2_12"),
    Edge("v2_31", "v2_12"),
    Edge("v2_32", "v2_33"),
    Edge("v2_12", "v2_13"),
    Edge("v2_13", "v2_14"),
    Edge("v2_14", "v2_15"),
    Edge("v2_15", "v2_16"),
    Edge("v2_16", "v2_17"),
    Edge("v2_17", "v2_18"),
    Edge("v2_18", "v2_19"),
    Edge("v2_19", "v2_20"),
    Edge("v2_20", "v2_21"),
    Edge("v2_21", "v2_22"),
    Edge("v2_22", "v2_23"),
    Edge("v2_24", "v2_33"),
    Edge("v2_25", "v2_33", label="demand", style_extra="dashed=1;"),
    Edge("v2_23", "v2_33"),
    Edge("v2_33", "v2_34"),
    Edge("v2_34", "v2_35"),
    Edge("v2_34", "v2_36"),
    Edge("v2_34", "v2_37"),
    Edge("v2_37", "v2_38"),
    Edge("v2_38", "v2_39"),
    Edge("v2_39", "v2_40"),
    Edge("v2_42", "v2_12", label="type curves", style_extra="dashed=1;"),
    Edge("v2_43", "v2_34", label="conv adj", style_extra="dashed=1;"),
]


def main() -> None:
    out = Path(__file__).parent.parent / "out" / "ngsm_v2_deep_dive.drawio"
    emit_swimlane(
        out_path=str(out),
        title="NGSM Annual Cycle — Deep Dive (v2)",
        lanes=LANES,
        steps=STEPS,
        edges=EDGES,
        # v2 width: max step x = 3260 + 170 = 3430 → + lane title (200) + pad = 3650
        pool_width=3650,
    )
    print(f"Wrote {out} — {len(STEPS)} steps, {len(EDGES)} edges, {len(LANES)} lanes")


if __name__ == "__main__":
    main()
