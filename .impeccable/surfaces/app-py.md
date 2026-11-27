---
version: 1
slug: "app-py"
primary_target: "app.py"
related_targets: ["ui.py"]
---

Scope: DIVMA Streamlit app, all seven pages (app.py shell via ui.py + .streamlit/config.toml). Mode: Operate.
Audience/job: professor and graders verify baseline results against the prospectus and try assumption changes. Constraints: no change to any number, calculation, or on-page wording; must deploy on Streamlit Community Cloud. Visual changes live in ui.py, config.toml, assets.

## Direction contract

THESIS: The backtest read like a money app account: calm soft-grey ground, white rounded tiles, one violet ink for the strategy. Refuses the navy institutional research-portal shell with bordered boxes and uppercase labels.

OWN-WORLD: Ground #F4F4F6, tiles #FFFFFF radius 20 with soft offset shadow and no borders, ink #0B0B0F, muted #6E6E7A, violet #5B4BFF strategy and selection, benchmark #A9A9B8, assets SPY sky, IEF violet, GLD amber, SHY lilac. Manrope throughout, sentence-case labels, pill chips, pill nav, pill buttons, tabular figures.

STORY: Grader lands on Overview, sees baseline status pill and period chips, edits assumptions in one tile, reads five KPI tiles, compares strategy vs 60/40 in two chart tiles, checks the measures table, then moves through the pill sidebar.

FIRST VIEWPORT: White sidebar with DIVMA mark and pill-highlighted page list; main: title left with green status pill right, lede, a row of rounded period chips; assumptions tile; KPI row of five white tiles where the last, Growth of $1, is the black account card (signature move).

FORM: Neobank app, my ranked candidate 1 (pick card). seed:1cb23b2aa442ad95

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
