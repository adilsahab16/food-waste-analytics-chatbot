# World Food Waste Analytics Chatbot

A natural language analytics chatbot for exploring global food loss and GHG emissions data.
Ask questions in plain English — the app queries a structured SQLite database built from four
public datasets (FAO, World Bank, PIK, EDGAR) and returns clear, data-driven answers powered
by Claude via the Anthropic API.

**[Live Demo](https://adilsahab16-food-waste-analytics-chatbot.streamlit.app)** · Python · SQLite · Streamlit · Anthropic API

---

## Screenshots

> *Screenshots taken from the full dataset (local). The live demo runs on a curated regional sample.*

<!-- Add 2–3 screenshots here -->

---

## Project Background

The underlying data was cleaned and structured as part of original thesis research on global food
waste. Having spent considerable time on the data engineering side — modeling, transformations,
join logic across four heterogeneous sources — the natural next step was to make it queryable
in plain language.

The project has two parallel goals: build something analytically useful, and learn how Claude
and the Anthropic API work in practice — tool calling, the agentic loop, and MCP server
architecture.

---

## Development Approach

This was built with the same rigour I apply to data engineering projects — requirements before
code, decisions documented as they're made, and no phase started until the previous one is
committed and tested.

**The process:**
1. Wrote a full PRD covering analytical questions, data model, tool specifications, and success criteria
2. Converted the PRD into a living `CLAUDE_CONTEXT.md` — a session-by-session guide for Claude Code with explicit working rules (phase-gated, ask before assuming, never generate code without instruction)
3. Built in 6 discrete sessions: scaffold → data loading → tool functions → agentic loop → UI → sample data & deployment
4. Each session ended with a test, a commit, and a `/clear` — code lives in GitHub, not in the AI's memory

The result is a project where every architectural choice is traceable to a documented decision,
and where the AI tooling was directed rather than improvised.

---

## What It Can Answer

### Yearly Trends
- How has food loss changed over time in high vs low income regions?
- How have food system emissions trended across income groups?

### Food Loss Breakdown
- Which supply chain stage has the highest food loss by region?
- Food loss breakdown by commodity basket across regions

### Food System Emissions
- Emissions by supply chain stage or gas type, broken down by region
- How do crop emissions compare to livestock emissions across regions?

### Total GHG Emissions
- What share of total GHG emissions comes from the food system, by region?
- Total economy-wide GHG emissions by sector and region

---

## Architecture

```
User
  │
  ▼
Streamlit UI  (src/app.py)
  │
  ▼
Anthropic Python SDK  (src/agent.py — agentic loop)
Claude decides: call tool OR answer directly
  │
  ├──► query_food_loss(...)                  ──► SQLite (src/tools.py)
  ├──► query_food_system_emissions(...)       ──► SQLite
  ├──► query_population_gdp(...)             ──► SQLite
  ├──► query_total_emissions_by_sector(...)   ──► SQLite
  └──► query_total_ghg_with_food_share(...)   ──► SQLite
                                                    │
                                    data/raw/        (full data — local only)
                                    data/sample/     (demo data — committed to repo)
                                    controlled by DATA_MODE env variable
```

**How the agentic loop works:**
1. User sends a question
2. Claude receives it alongside all 5 tool definitions
3. Claude selects the right tool(s) and parameters based on the question
4. Tool executes parameterised SQL against SQLite, returns rows as JSON
5. Claude summarises results in plain language — raw rows never reach the user
6. Loop repeats if Claude needs more data; ends when Claude has a complete answer

---

## Key Design Decisions

**5 composable tools instead of 10 specialised ones** — each tool accepts a dynamic `group_by`
list and optional filters, so the same tool serves multiple analytical questions. Fewer tools
means less decision overhead for Claude and fewer tokens in every request.

**Named item presets (`supply_chain`, `crops_livestock`)** — filter logic lives in Python,
not in Claude's reasoning. Claude passes a preset name; the tool resolves it to the exact
FAO item values. Safer, cheaper, and easier to maintain.

**CTEs to avoid row fan-out** — PIK has ~20 rows per country/year (sector × gas combinations)
and EDGAR has ~9 (substance). A direct join inflates `SUM()` by a factor of 9. Tool 5 uses
CTEs to pre-aggregate each source by country/year before joining.

**Two join key paths** — FAO data uses UN M49 codes; WDI, PIK, and EDGAR use ISO3 country
codes. The star schema is built around both, with `dim_region` as the bridge table carrying
both keys. Every tool join is explicit about which path it uses.

**CO2eq IPCC AR5 as the standard unit** — consistent with thesis methodology and FAO
reporting. Applied as an `element_filter` default so Claude always works in comparable units
unless explicitly asked for gas-level breakdown.

---

## Data Engineering Notes

The database is a star schema with 4 fact tables and 4 dimension tables loaded from 4
heterogeneous public sources:

| Source | Fact / Dimension | Key Ingestion Work |
|---|---|---|
| FAO (food loss) | `fact_food_loss` | Already tall — add `source_name` only |
| FAO (emissions) | `fact_food_system_emissions` | Unpivot Y-prefixed wide format; filter to FAO TIER 1 and 3 gas types; strip Excel apostrophe prefix from M49 codes |
| PIK | `fact_total_emissions_pik` | Unpivot 170 year columns; trim to 1966+; exclude KYOTOGHG |
| EDGAR | `fact_food_emission_shares_edgar` | Unpivot; rename columns; shares averaged across substances at query time |
| FAO | `dim_region` | Join bridge — carries both M49 and ISO3 keys |
| FAO | `dim_commodity` | 3-level hierarchy: commodity → group → basket |
| World Bank (WDI) | `dim_population` | Unpivot wide format |
| World Bank (WDI) | `dim_gdp` | Unpivot wide format; drop 2023 (outside scope) |

`DATA_MODE` environment variable controls whether the app loads from `data/raw/` (full dataset,
local only) or `data/sample/` (curated regional subset, committed to repo for the live demo).

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.11+ |
| LLM | Anthropic API — Claude Sonnet |
| Database | SQLite |
| UI | Streamlit |
| Data processing | pandas |
| Dev environment | VS Code + Claude Code |

---

## Project Structure

```
food-waste-analytics-chatbot/
├── src/
│   ├── load_data.py        ← Reads source files, applies transformations, loads SQLite
│   ├── tools.py            ← 5 parameterised query functions (SQL)
│   ├── agent.py            ← Agentic loop: Claude + tool calling via Anthropic SDK
│   ├── app.py              ← Streamlit chat UI
│   └── create_sample.py    ← One-time script to generate data/sample/ from data/raw/
├── data/
│   └── sample/             ← Curated demo subset (committed — powers live demo)
├── db/                     ← SQLite database (gitignored — generated locally)
├── docs/
│   ├── decisions.md        ← Running log of design decisions
│   └── PRD_v0.5.pdf        ← Product Requirements Document (v0.5)
└── requirements.txt
```

---

## Local Setup

### Prerequisites
- Python 3.11+
- Anthropic API key — get one at [console.anthropic.com](https://console.anthropic.com)
- Full source files in `data/raw/` for full dataset (not included — see Data section)

### Steps

```bash
git clone https://github.com/adilsahab16/food-waste-analytics-chatbot.git
cd food-waste-analytics-chatbot

python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the repo root:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
DATA_MODE=full        # or 'sample' to run on the demo dataset
```

Load the database:
```bash
PYTHONPATH=. python src/load_data.py
```

Run the app:
```bash
PYTHONPATH=. streamlit run src/app.py
```

To run on sample data only (no raw files needed):
```bash
DATA_MODE=sample PYTHONPATH=. python src/load_data.py
DATA_MODE=sample PYTHONPATH=. streamlit run src/app.py
```

---

## Data

Source datasets are publicly available from FAO, World Bank, PIK, and EDGAR. The cleaning,
structuring, and join logic was carried out as part of original thesis research. Full cleaned
files are kept local and gitignored. A curated sample dataset (`data/sample/`) is committed
to power the live demo.

| Source | Dataset | Coverage |
|---|---|---|
| FAO | Food Loss and Waste Database | 1966–2022 |
| FAO | Agrifood System Emissions (FAOSTAT) | 1961–2022 |
| World Bank (WDI) | Population & GDP | 1960–2022 |
| PIK | Historical GHG Emissions by Sector | 1850–2021 |
| EDGAR | Food System Emission Shares | 1970–2018 |

---

## Current Development

**Phase 6 — MCP Server**

Implementing an MCP (Model Context Protocol) server that exposes the same 5 tools over the
MCP protocol. This allows any MCP-compatible client — including Claude Desktop and VS Code
extensions — to query the food waste database directly, without the Streamlit UI.

---

## Future Development

- **Predictive analytics** — apply machine learning to the historical dataset to enable
  forecasting of food loss trends and emission trajectories by region and income group
- **Extended data sources** — integrate additional FAO and IPCC datasets as they become available
- **Multi-region comparison UI** — side-by-side analytical views for selected regions