# Food Waste Analytics Chatbot — Claude Code Context Document

> **How to use this file:** Attach this document at the start of every Claude Code session.
> It contains everything needed to understand the project: goals, architecture, data model, analytical questions, tool specifications, session plan, and working rules.
> It is a living document — update phase status and session progress as you go.

---

## 1. Project Summary

| Field | Detail |
|---|---|
| **Project Name** | World Food Waste Analytics Chatbot |
| **Type** | Learning & Portfolio Project |
| **Owner** | Data Engineer |
| **Purpose** | Learn Claude/Anthropic API, build a portfolio piece, gain MCP server experience |
| **Stack** | Python · SQLite · Streamlit · Anthropic Python SDK |
| **Dev Environment** | VS Code + Claude Code Extension |
| **Repo Name** | food-waste-analytics-chatbot |
| **Repo Visibility** | Private during development — made public only when complete |
| **Data** | Sourced from public datasets (FAO, WDI, PIK, EDGAR). Meticulously cleaned and processed as part of original thesis research. Full cleaned files are gitignored and never committed. A curated sample dataset in data/sample/ powers the live demo. |

---

## 2. Owner Background

- Data engineer — strong in SQL, data modeling, pipelines
- New to: chatbot development, Anthropic API, agentic systems, MCP servers
- First time using Claude Code (previously used GitHub Copilot + VS Code)

**Working style:** Phase-gated. Do not jump ahead. Do not generate code unless explicitly instructed. Ask questions rather than assume. When introducing agent/API concepts new to a data engineer, explain briefly before proceeding.

**Important:** At the start of each new task, re-read the relevant section of this file before writing any code. If any file already exists in the repo, read it before modifying it.

**Context file maintenance:** Whenever a decision changes, a new decision is made, or any meaningful change happens during a session — ask the user: "Can I go ahead and update CLAUDE_CONTEXT.md and commit it to Git?" Do not update the context file or commit without explicit approval.

---

## 3. Goals

1. Learn how Claude and the Anthropic API work — especially tool calling and the agentic loop
2. Build a working analytics chatbot answering natural language questions over structured food waste data
3. Produce a portfolio-ready project: clean architecture, documented decisions, clear README
4. Build and understand an MCP server (Phase 6)

---

## 4. Project Phases & Status

| Phase | Name | Status |
|---|---|---|
| 1 | Problem Definition & Use Case | ✅ Complete |
| 2 | Data & Schema Design | ✅ Complete |
| 3 | Question → SQL Mapping | ✅ Complete |
| 4 | Tool / Function Design | ✅ Complete |
| 5 | Agent Behavior & Streamlit UI | ✅ Complete |
| 6 | MCP Server | ⏳ Planned |

---

## 5. Phase 5 — Session Plan

Work through Phase 5 in the following sessions, in order. Complete, test, and commit each session before starting the next. Recommend user to `/clear` after committing for token efficiency.

### Session 1 — Repo Scaffold
**Goal:** Set up the project structure, dependencies, and Git connection.
**Prompt to use:**
> "Set up the project scaffold for food-waste-analytics-chatbot based on CLAUDE_CONTEXT.md. Create the full folder structure, requirements.txt, .gitignore (covering data/, db/, .env), and an empty README.md. Then initialise git, connect to my GitHub remote, and make the first commit. Do not create any Python files yet."

**What gets created:** folder structure, requirements.txt, .gitignore, README.md skeleton, initial commit
**Status:** ✅ Complete

---

### Session 2 — Data Loading
**Goal:** Build the script that reads source files, applies all ingestion transformations, and loads SQLite.
**Prompt to use:**
> "Build src/load_data.py based on the Data Model section of CLAUDE_CONTEXT.md. The full cleaned data files are in data/raw/ with the exact filenames listed in the data model. The sample data files are in data/sample/ with the same structure but fewer rows. The script should load whichever folder is specified by a config flag. Apply all ingestion transformations documented — unpivoting wide-format files, trimming PIK to 1966+, filtering FAO emissions elements and sources, renaming EDGAR columns, adding source_name columns, and dropping projection years. Create the SQLite database at db/food_waste.db."

**What gets created:** src/load_data.py, db/food_waste.db (local only, gitignored)
**Status:** ✅ Complete

---

### Session 3 — Tool Functions
**Goal:** Implement all 5 tool functions that execute SQL against SQLite.
**Prompt to use:**
> "Build src/tools.py based on the Tool Specifications section of CLAUDE_CONTEXT.md. Implement all 5 tool functions exactly as specified: query_food_loss, query_food_system_emissions, query_population_gdp, query_total_emissions_by_sector, and query_total_ghg_with_food_share. Each function should accept the parameters defined in the spec, build the appropriate SQL query dynamically, execute it against db/food_waste.db, and return results as a list of dicts. Include the limit parameter in all queries. Use the SQL mappings in section 7 of CLAUDE_CONTEXT.md as the basis for each query."

**What gets created:** src/tools.py
**Status:** ✅ Complete

---

### Session 4 — Agentic Loop
**Goal:** Build the agent that connects Claude to the tools.
**Prompt to use:**
> "Build src/agent.py based on CLAUDE_CONTEXT.md. Implement the agentic loop using the Anthropic Python SDK. The agent should: accept a user message, send it to Claude with all 5 tool definitions from src/tools.py, handle tool call responses by executing the relevant tool function, return the tool result to Claude, and loop until Claude returns a final text response. Use claude-sonnet-4-20250514 as the model. Claude should summarise tool results in plain language before returning to the user — never return raw rows. Include a system prompt that tells Claude it is a food waste analytics assistant with access to 5 tools, and that it should call tools when needed to answer questions and explain its reasoning briefly."

**What gets created:** src/agent.py
**Status:** ✅ Complete

---

### Session 5 — Streamlit UI
**Goal:** Build the chat interface wired to the agent loop.
**Prompt to use:**
> "Build src/app.py as a Streamlit chat interface wired to src/agent.py. The UI should show a chat window with message history, accept user input, pass the user message to the agent, and display Claude's response. Keep the UI clean and minimal — this is an analytics tool not a consumer app. Add a sidebar that shows which data mode is active (full data or sample data) and the data sources (FAO, WDI, PIK, EDGAR) with brief descriptions, and a short About blurb for portfolio visitors. When the chat is empty, show 4 conversation starter cards in a 2×2 grid — one per analytical group (trends, loss breakdown, emissions share, emissions breakdown). Cards disappear once the conversation starts. Render Claude's responses as markdown. Show a spinner while the agent is running. Pass only the user's question to the agent — no UI state. Test that the app runs with streamlit run src/app.py."

**What gets created:** src/app.py
**Status:** ✅ Complete

---

### Session 6 — Sample Dataset & Deployment Prep
**Goal:** Create the sample dataset for the live demo and prepare for Streamlit Community Cloud deployment.
**Prompt to use:**
> "Create a curated sample dataset in data/sample/ that mirrors the structure of data/raw/ but contains a representative subset — approximately 3–5 regions, 10–15 years, all 4 fact tables and all 4 dimension tables. The sample data should be enough for the chatbot to answer at least one question from each of the 4 analytical groups defined in CLAUDE_CONTEXT.md. Commit the sample data to the repo. Then update src/load_data.py so that a DATA_MODE environment variable controls whether it loads from data/raw/ (full) or data/sample/ (demo). Update the README with setup instructions, data source credits, and architecture overview."

**What gets created:** data/sample/ files, updated load_data.py, updated README.md
**Status:** ✅ Complete

---

### Session 7 — Plotly Charts
**Goal:** Render an interactive chart after every agent response that called a tool.
**What was built:**
- `src/charts.py` — chart rendering module. `render_charts(tool_calls)` loops over collected tool call results. Chart type is determined by `group_by`: line chart when `year` is a dimension, grouped bar chart otherwise. One chart per metric column (tools with multiple metrics produce multiple charts). Single-row results are skipped.
- `src/agent.py` — `run_agent()` signature changed from `-> str` to `-> tuple[str, list[dict]]`. Tool results are now collected into a `tool_calls` list during the loop and returned alongside the text response.
- `src/app.py` — unpacks the tuple from `run_agent`, calls `render_charts` immediately after the text response. `chart_data` is stored on each assistant message in session state so charts re-render correctly when scrolling through history. Charts render on every response that called a tool.
- `requirements.txt` — added `plotly`

**Status:** ✅ Complete

---

## 6. Phase 6 — MCP Server Session Plan

Expose the same 5 tools over the MCP (Model Context Protocol) so any MCP-compatible client — including Claude Desktop and VS Code extensions — can query the food waste database without the Streamlit UI.

Work through Phase 6 in the following sessions, in order. Complete, test, and commit each session before starting the next. Recommend user to `/clear` after committing for token efficiency.

### Session 1 — MCP Server Scaffold
**Goal:** Build the MCP server that exposes all 5 tools over the MCP protocol.
**Prompt to use:**
> "Build mcp/server.py based on CLAUDE_CONTEXT.md. Implement an MCP server using FastMCP that exposes all 5 tools from src/tools.py over the MCP protocol. The server should register each tool with the same name, description, and parameter schema as defined in the Tool Specifications section. Each tool should call the matching Python function from src/tools.py and return the result. Do not change src/tools.py."

**What gets created:** `mcp/server.py`
**Status:** ⏳ Planned

---

### Session 2 — MCP Client Test
**Goal:** Verify all 5 tools are callable end-to-end from an MCP-compatible client.
**Prompt to use:**
> "Help me test mcp/server.py end-to-end. Run the MCP server locally and verify that each of the 5 tools can be called and returns results. Confirm the server works with Claude Desktop or VS Code MCP client configuration."

**What gets created:** test confirmation, MCP client config (if needed)
**Status:** ⏳ Planned

---

### Session 3 — README Update & Final Commit
**Goal:** Document the MCP server setup and make the final project commit.
**Prompt to use:**
> "Update README.md with MCP server setup instructions — how to run mcp/server.py locally and how to connect it to a compatible MCP client. Add a project structure entry for mcp/server.py. Make a final commit marking the project complete."

**What gets created:** Updated README.md, final commit
**Status:** ⏳ Planned

---

## 7. Analytical Questions (Phase 1 Output)

### Group 1 — Yearly Trends: High Income vs Low Income Regions
- **Q1.1** Yearly trend in food loss/waste percentage — high income vs low income regions
- **Q1.2** Yearly trend in food system emissions — high income vs low income regions
- **Q1.3** Population & GDP trends by income group — contextual enrichment alongside Q1.1/Q1.2, not standalone

### Group 2 — Food Loss Breakdown
- **Q2.1** Food loss by food supply chain stage — broken down by region
- **Q2.2** Food loss of each region, broken down by commodity basket

### Group 3 — Food System Emissions Breakdown
- **Q3.1** Food system emissions by supply chain stage — broken down by region
- **Q3.2** Food system emissions of each region, broken down by gas type
- **Q3.3** Food system emissions — Crops vs Livestock comparison by region

### Group 4 — Total GHG Emissions
- **Q4.1** Total GHG emissions by region with food system emission share (PIK + EDGAR combined)
- **Q4.2** Total GHG emissions of each region, broken down by sector (PIK only)

---

## 8. Data Model (Phase 2 Output)

### Overview

Star-schema pattern. Two join key paths:
- `m49_code` — links `fact_food_loss` and `fact_food_system_emissions` to `dim_region`
- `country_code` — links `fact_total_emissions_pik`, `fact_food_emission_shares_edgar`, `dim_population`, `dim_gdp` to `dim_region`

### Source File Mapping
| Source File | Produces |
|---|---|
| `World_Food Loss and Waste Database_FAO_1966-2022` | `fact_food_loss` |
| `Emissions_Totals_E_All_Data_NOFLAG` | `fact_food_system_emissions` |
| `CW_HistoricalEmissions_PIK` + `EDGAR-FOOD_EMISSIONS_SHARES` | `fact_total_emissions_pik` + `fact_food_emission_shares_edgar` |

---

### Dimension Tables

#### dim_region
**Source file:** `country_income_region_mapping`

| Column | Type | Notes |
|---|---|---|
| region | string | NAOCE, NAWACA, SSEA, SSA + others |
| country | string | Country name |
| country_code | string | e.g. AFG, AUS — join key for WDI, PIK, EDGAR data |
| m49_code | integer | UN M49 code — join key for FAO data |
| dev_country | string | D = Developing, I = Industrialised — retained as reporting attribute |
| income | string | High or Low |

#### dim_commodity
**Source file:** `commodity tagging`

| Column | Type | Notes |
|---|---|---|
| cpc_code | integer | CPC code — join key to fact_food_loss |
| commodity | string | Individual commodity |
| commodity_group | string | Intermediate grouping |
| basket | string | Top-level grouping — 6 baskets. Primary aggregation level |

#### dim_population
**Source file:** `world_bank_population_data`

| Column | Type | Notes |
|---|---|---|
| country | string | Country name |
| country_code | string | Join key to dim_region |
| year | integer | Unpivoted from wide format. Range: 1960–2022 |
| population | integer | Annual headcount |

#### dim_gdp
**Source file:** `world_bank_gdp_data`

| Column | Type | Notes |
|---|---|---|
| country | string | Country name |
| country_code | string | Join key to dim_region |
| year | integer | Unpivoted from wide format. Range: 1960–2022. 2023 column dropped at ingestion |
| gdp | integer | Total GDP in current USD (sourced from WDI — confirmed to be total GDP, not per capita) |

---

### Fact Tables

#### fact_food_loss
**Source file:** `World_Food Loss and Waste Database_FAO_1966-2022`

| Column | Type | Notes |
|---|---|---|
| m49_code | integer | Join key → dim_region |
| country | string | Country name |
| year | integer | From 1966 |
| loss_percentage | float | % food wasted vs production. Fractions not quantities |
| food_supply_stage | string | e.g. Storage, Harvest, Farm, Processing, Transport, Households |
| cpc_code | integer | Join key → dim_commodity |
| commodity | string | Commodity name |
| source_name | string | Fixed value: 'FAO' — added at ingestion |

**Transformations:** Already tall format. Add source_name column only.

---

#### fact_food_system_emissions
**Source file:** `Emissions_Totals_E_All_Data_NOFLAG`

| Column | Type | Notes |
|---|---|---|
| m49_code | integer | Join key → dim_region |
| area | string | Country name |
| year | integer | Y-prefix stripped. Y2030 and Y2050 dropped |
| emissions | float | Emissions in kilotons (kt) |
| item | string | Emission category — supply chain stages or crops/livestock |
| element | string | Gas type — see filter below |
| source_name | string | Fixed value: 'FAO' — added at ingestion |

**Transformations at ingestion:**
- Unpivot Y-prefixed year columns to tall format. Strip 'Y' prefix from year values
- Keep only `Source = 'FAO TIER 1'` — drop all UNFCCC rows
- Keep only `element IN ('Emissions (CH4)', 'Emissions (N2O)', 'Emissions (CO2eq) (AR5)')` — drop all others
- Drop columns: `Area_Code`, `Item_Code`, `Element_Code`, `Source_Code`, `Source`, `Unit`
- Drop rows where year IN (2030, 2050)
- Add source_name = 'FAO'

**Item values by query:**
- Q3.1 supply chain: `'Food Household Consumption'`, `'Waste'`, `'Pre- and Post- Production'`, `'Food Packaging'`, `'Agrifood Systems Waste Disposal'`, `'Food Retail'`, `'Food Transport'`, `'Food Processing'`
- Q3.3 crops/livestock: `'Emissions from crops'`, `'Emissions from livestock'`

---

#### fact_total_emissions_pik
**Source file:** `CW_HistoricalEmissions_PIK`

| Column | Type | Notes |
|---|---|---|
| country_code | string | Join key → dim_region via country_code |
| year | integer | Trimmed to 1966+ at ingestion |
| sector | string | e.g. Agriculture, Energy, Industrial Processes and Product Use |
| gas | string | e.g. CH4, N2O, CO2. KYOTOGHG excluded at ingestion |
| emissions | float | Emissions in kt |
| source_name | string | Fixed value: 'PIK' — added at ingestion |

**Transformations at ingestion:**
- Unpivot year columns (1850–2021) to tall format
- Filter to year >= 1966
- Exclude rows where `gas = 'KYOTOGHG'`
- Drop original `Source` column — replaced by source_name = 'PIK'

---

#### fact_food_emission_shares_edgar
**Source file:** `EDGAR-FOOD_EMISSIONS_SHARES`

| Column | Type | Notes |
|---|---|---|
| country_code | string | Renamed from `Country_code_A3`. Join key → dim_region |
| country | string | Renamed from `Name` |
| year | integer | Unpivoted from wide format. Range: 1970–2018 |
| substance | string | Renamed from `Substance`. Averaged across at query time |
| share | float | Food system emission share as fraction (0–1) |
| source_name | string | Fixed value: 'EDGAR' — added at ingestion |

**Transformations at ingestion:**
- Unpivot year columns to tall format
- Rename `Country_code_A3` → `country_code`, `Name` → `country`, `Substance` → `substance`
- Add source_name = 'EDGAR'

---

## 9. Question → SQL Mapping (Phase 3 Output)

| ID | Tables | Join Key | Group By | Measure | Key Filters |
|---|---|---|---|---|---|
| Q1.1 | fact_food_loss, dim_region | m49_code | year, income | AVG(loss_percentage) | None |
| Q1.2 | fact_food_system_emissions, dim_region | m49_code | year, income | SUM(emissions) | element = 'Emissions (CO2eq) (AR5)' |
| Q1.3 | dim_population, dim_gdp, dim_region | country_code | year, income | SUM(population), AVG(gdp) | Two sub-queries combined |
| Q2.1 | fact_food_loss, dim_region | m49_code | region, food_supply_stage | AVG(loss_percentage) | None |
| Q2.2 | fact_food_loss, dim_region, dim_commodity | m49_code + cpc_code | region, basket | AVG(loss_percentage) | None |
| Q3.1 | fact_food_system_emissions, dim_region | m49_code | region, item | SUM(emissions) | CO2eq AR5 + 8 supply chain items |
| Q3.2 | fact_food_system_emissions, dim_region | m49_code | region, element | SUM(emissions) | CH4, N2O, CO2eq AR5 |
| Q3.3 | fact_food_system_emissions, dim_region | m49_code | region, item | SUM(emissions) | CO2eq AR5 + crops/livestock items |
| Q4.1 | fact_total_emissions_pik, fact_food_emission_shares_edgar, dim_region | country_code | region | SUM(kt) + AVG(share) | Excl. KYOTOGHG. AVG EDGAR across substances |
| Q4.2 | fact_total_emissions_pik, dim_region | country_code | region, sector | SUM(emissions) | Excl. KYOTOGHG |

---

## 10. Tool Specifications (Phase 4 Output)

5 tools total. All tools include `limit` (default: 100). `group_by` is a dynamic list — Claude selects dimensions from the constrained valid set based on the user's question.

---

### Tool 1: `query_food_loss`
**Description:** "Use this tool to query food loss and waste percentage data. Call this when the user asks about food loss or waste percentages across any combination of: time trends, regions, income groups, supply chain stages, commodity groups, or commodity baskets. This tool does NOT cover emissions — use the emissions tools for those questions."

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `group_by` | list[string] | Yes | Any of: `year`, `income`, `region`, `food_supply_stage`, `basket` |
| `filters` | object | No | Optional: `region`, `income` (High/Low), `year_from`, `year_to`, `basket`, `food_supply_stage` |
| `limit` | int | No | Default: 100 |

**Returns:** `{group_by columns..., avg_loss_percentage}` | **Serves:** Q1.1, Q2.1, Q2.2

---

### Tool 2: `query_food_system_emissions`
**Description:** "Use this tool to query food system emissions data from the FAO. Call this when the user asks about agrifood system emissions, emissions by supply chain stage, emissions by gas type, crop emissions, or livestock emissions. This tool covers food-system-specific emissions only — for total economy-wide emissions use the total emissions tool."

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `group_by` | list[string] | Yes | Any of: `year`, `income`, `region`, `item`, `element` |
| `item_filter` | string | No | `'supply_chain'` (8 stages), `'crops_livestock'`, `'all'`. Default: `'all'` |
| `element_filter` | string | No | `'co2eq'` (AR5 only), `'by_gas'` (CH4, N2O, CO2eq), `'all'`. Default: `'co2eq'` |
| `filters` | object | No | Optional: `region`, `income`, `year_from`, `year_to` |
| `limit` | int | No | Default: 100 |

**Returns:** `{group_by columns..., total_emissions_kt}` | **Serves:** Q1.2, Q3.1, Q3.2, Q3.3

---

### Tool 3: `query_population_gdp`
**Description:** "Use this tool to retrieve population and GDP per capita data as contextual support. Call this when the user asks about demographic or economic trends alongside food loss or emissions patterns, or when comparing income groups by population or economic output. Do not use this as a primary analytical tool — it provides supporting context for other insights."

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `group_by` | list[string] | Yes | Any of: `year`, `income`, `region` |
| `filters` | object | No | Optional: `region`, `income`, `year_from`, `year_to` |
| `limit` | int | No | Default: 100 |

**Returns:** `{group_by columns..., total_population, avg_total_gdp_usd, avg_gdp_per_capita}` | **Serves:** Q1.3 (contextual enrichment)
Note: `avg_total_gdp_usd` = AVG(total GDP per country as stored in WDI). `avg_gdp_per_capita` = SUM(gdp) / SUM(population), derived at query time.

---

### Tool 4: `query_total_emissions_by_sector`
**Description:** "Use this tool to query total economy-wide GHG emissions broken down by sector, sourced from the PIK dataset. Call this when the user asks about total emissions by sector (Agriculture, Energy, Industry etc.) across regions. Excludes the KYOTOGHG aggregate — returns individual gas types only. For food system emission shares within total emissions, use query_total_ghg_with_food_share instead."

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `group_by` | list[string] | Yes | Any of: `year`, `income`, `region`, `sector`, `gas` |
| `filters` | object | No | Optional: `region`, `income`, `sector`, `gas`, `year_from`, `year_to` |
| `limit` | int | No | Default: 100 |

**Returns:** `{group_by columns..., total_emissions_kt}` | **Serves:** Q4.2

---

### Tool 5: `query_total_ghg_with_food_share`
**Description:** "Use this tool when the user asks about total GHG emissions by region combined with the food system's share of those emissions. Joins PIK total emissions with EDGAR food emission shares and returns both values together per region. Use specifically for questions comparing overall emissions magnitude against food system contribution."

| Parameter | Type | Required | Notes |
|---|---|---|---|
| `group_by` | list[string] | Yes | Any of: `region`, `income`, `year` |
| `filters` | object | No | Optional: `region`, `income`, `year_from`, `year_to` |
| `limit` | int | No | Default: 100 |

**Returns:** `{group_by columns..., total_emissions_kt, avg_food_share_pct}` | **Serves:** Q4.1

---

## 11. Token Efficiency & Session Management

**The recommended development rhythm:**
1. Attach CLAUDE_CONTEXT.md at the start of the session
2. Tell Claude Code which session you are on and what files already exist
3. Complete the task
4. Test it works
5. Commit to GitHub
6. Run `/clear`
7. Start next session fresh with CLAUDE_CONTEXT.md attached again

**Why this works:** The code lives in GitHub, not in Claude Code's memory. After a `/clear`, Claude Code re-reads the actual files from the repo rather than relying on memory — so nothing is lost.

**When to run /clear:**
- After completing and committing any session from the Phase 5 session plan
- If a session has been running for more than 30–40 minutes without a commit
- If Claude Code starts giving inconsistent answers or seems confused about what files exist
- Never run /clear mid-task — always complete and commit first

**Claude Code will remind you** to run /clear at the end of each committed task. If a session runs long without a commit, flag it.

**Other token efficiency rules:**
- Tool descriptions are precise and non-overlapping — Claude won't redundantly call multiple tools
- Named item presets (`supply_chain`, `crops_livestock`) keep filter logic in Python, not Claude's reasoning
- Streamlit UI passes only the user's question to Claude — no UI state
- Claude summarises tool results in plain language before presenting to user — never dumps raw rows

---

## 12. Architecture

### Post Phase 5 (Pre-MCP)
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
  ├──► query_food_loss(...)                 ──► SQLite (src/tools.py)
  ├──► query_food_system_emissions(...)      ──► SQLite
  ├──► query_population_gdp(...)            ──► SQLite
  ├──► query_total_emissions_by_sector(...)  ──► SQLite
  └──► query_total_ghg_with_food_share(...)  ──► SQLite
                                                    │
                                    data/raw/       (full data — local only)
                                    data/sample/    (demo data — committed to repo)
                                    controlled by DATA_MODE env variable
```

### Post Phase 6 (With MCP)
```
Claude ──► MCP Server (mcp/server.py) ──► same 5 tools over MCP protocol
```

---

## 13. Repository Structure

```
food-waste-analytics-chatbot/
├── CLAUDE_CONTEXT.md          ← Attach to every Claude Code session
├── README.md                  ← Portfolio-facing: architecture, setup, data sources
├── .gitignore                 ← Covers data/raw/, db/, .env
├── requirements.txt
├── data/
│   ├── raw/                  ← Full cleaned files (gitignored — never committed)
│   └── sample/               ← Curated demo subset (committed — powers live demo)
├── db/
│   └── food_waste.db         ← SQLite database (gitignored)
├── src/
│   ├── load_data.py          ← Reads files, applies transformations, loads SQLite
│   │                            DATA_MODE env var controls raw vs sample
│   ├── tools.py              ← 5 tool function definitions
│   ├── agent.py              ← Agentic loop: Claude + tool calling. Returns (text, tool_calls)
│   ├── app.py                ← Streamlit chat UI
│   ├── charts.py             ← Plotly chart rendering from tool call results
│   └── create_sample.py      ← One-time script: slices data/raw/ → data/sample/
├── mcp/
│   └── server.py             ← MCP server (Phase 6)
└── docs/
    ├── decisions.md          ← Running log of design decisions
    └── PRD_v0.5.pdf          ← Product Requirements Document (v0.5)
```

---

## 14. Design Decisions Log

| Decision | Rationale | Phase |
|---|---|---|
| SQLite over PostgreSQL | Local, zero-setup, sufficient for static dataset, portfolio-friendly | 1 |
| Streamlit for UI | Python-native, minimal frontend knowledge, fast to build | 1 |
| Commodity basket as primary aggregation | 6 baskets = clean top-level grouping; matches thesis methodology | 1 |
| loss_percentage not loss quantity | Research is fraction-based; consistent with thesis | 1 |
| Emissions in kilotons (kt) | Consistent unit across all emissions tables | 1 |
| CO2eq IPCC AR5 100-year GWP | Standard methodology; consistent with thesis and FAO reporting | 1 |
| Star schema for SQLite | Mirrors thesis data model; clean join structure | 1 |
| Full data gitignored, sample data committed | Data sourced from public datasets (FAO, WDI, PIK, EDGAR), meticulously cleaned as part of original thesis research. Full cleaned files kept local and gitignored. A curated sample dataset in data/sample/ is committed to the repo to power the live Streamlit demo. Repo kept private during development — made public only when complete | 1 |
| Repo name: food-waste-analytics-chatbot | Clean, descriptive, portfolio-friendly. Lowercase with hyphens is standard GitHub convention | 1 |
| 4 fact tables not 3 | EDGAR (shares 0–1) and PIK (absolute kt) are different value types — must stay separate | 2 |
| dev_country column retained | Additional reporting attribute for future analysis | 2 |
| Year trim on PIK to 1966+ | Analysis scope starts 1966; pre-1966 adds size with no analytical value | 2 |
| source_name on all fact tables | Consistent provenance tracking across all tables | 2 |
| FAO TIER 1 only for food system emissions | UNFCCC rows are sparse with gaps; FAO TIER 1 is complete and consistent | 2 |
| Element filter: CH4, N2O, CO2eq AR5 only | Avoids double-counting from per-gas CO2eq conversions and direct/indirect splits | 2 |
| KYOTOGHG excluded from PIK | Aggregate metric — individual gases give more analytical value, avoid double-counting | 2 |
| GDP 2023 column dropped | Outside analysis scope; WDI data used to 2022 consistently | 2 |
| Q1.3 reframed as contextual enrichment | Population/GDP alone don't tell a food waste story — value is as supporting context | 3 |
| Q2.1 broken down by region | Regional breakdown reveals where supply chain losses are most severe | 3 |
| Q3.3 added: Crops vs Livestock | Livestock emissions are generally high — important analytical dimension missed in initial scope | 3 |
| item_filter as named presets | Filter logic lives in Python not Claude's reasoning — safer, fewer tokens | 4 |
| group_by as dynamic list | Composable tools serve multiple questions; Claude selects from constrained valid set | 4 |
| limit parameter on all tools | Prevents unbounded result sets consuming context window tokens | 4 |
| Q4.1 as single combined tool | Simpler for Claude, cleaner answers — internal join more reliable than Claude combining two results | 4 |
| 5 tools not 10 | Composable parameterised design serves all 10 questions without redundancy | 4 |
| DATA_MODE env variable | Controls whether load_data.py uses full data (local dev) or sample data (demo/deployment) without code changes | 5 |
| Commit → clear → next session rhythm | Preserves development continuity while managing token usage — code lives in GitHub, not in Claude's memory | 5 |
| FAO emissions m49_code has Excel apostrophe prefix | Source file stores m49_code as text with leading apostrophe (e.g. '004). Stripped and cast to int in load_data.py to match dim_region join key | 5 |
| WDI GDP data is total GDP not per capita | world_bank_gdp_data.csv contains total GDP in current USD, not per capita. query_population_gdp returns both avg_total_gdp_usd (as stored) and avg_gdp_per_capita (derived: SUM(gdp)/SUM(population)) | 5 |
| query_total_ghg_with_food_share uses CTEs | PIK has 20 rows/country/year, EDGAR has 9. Direct join inflates SUM by 9×. CTEs pre-aggregate each source before joining | 5 |
| Streamlit chat UI with conversation starters | 4 clickable question cards in a 2×2 grid shown when chat is empty (one per analytical group). Cards disappear once conversation starts. Clean entry point for portfolio visitors | 5 |
| Sidebar shows data mode + sources + About | Data mode indicator, FAO/WDI/PIK/EDGAR descriptions, and a short About blurb. Useful for portfolio visitors and demo context | 5 |
| Claude responses rendered as markdown | Claude returns structured markdown (bold, bullets). Rendering it improves readability with no extra effort | 5 |
| Spinner shown while agent runs | Agentic loop can take a few seconds. Spinner provides feedback so user knows the app is working | 5 |
| Sample data: 4 regions, 2005–2022 | Europe, SSA, S&SE Asia, LA — covers high/low income spread and all 4 analytical groups. 2005+ keeps files small while preserving trend depth | 6 |
| create_sample.py reads raw, writes same format | Output files mirror data/raw/ structure exactly so load_data.py works unchanged in both modes | 6 |
| Full data never committed; screenshots show full results | Thesis data kept local. README screenshots taken from full-data local run to demonstrate analytical depth for portfolio/recruiters | 6 |
| Deployment: DATA_MODE=sample set as Streamlit secret | Streamlit Community Cloud has no access to raw files. DATA_MODE=sample in secrets ensures app loads from committed data/sample/ | 6 |
| Plotly charts rendered when called in response | Adds analytical value without requiring Claude to reason about visualisation. Chart type (line vs bar) is derived from group_by: year → line, otherwise → bar. Single-row results skipped. | 5 |
| Charts stored in session state on assistant messages | chart_data saved alongside content in session state so charts replay correctly when scrolling through conversation history | 5 |
| run_agent() returns (text, tool_calls) tuple | UI needs raw tool results to render charts. Returning both from agent keeps concerns separated — agent handles Claude loop, charts module handles rendering | 5 |
| query_population_gdp renders two charts (population + GDP per capita) | Two distinct measures on different scales — combining on one axis would be misleading | 5 |
| query_total_ghg_with_food_share renders two charts (total emissions + food share %) | Same reason — kt and percentage are incompatible axes | 5 |

---

## 15. Glossary

| Term | Definition |
|---|---|
| GHG | Greenhouse gases — CO2, CH4, N2O, F-gases |
| CO2eq | CO2 equivalent — common GWP metric. 100-year IPCC AR5 values used |
| IPCC | Intergovernmental Panel on Climate Change |
| FAO | Food and Agriculture Organization |
| WDI | World Development Indicators (World Bank) |
| PIK | Potsdam Institute for Climate Impact Research — source of total economy-wide emissions |
| EDGAR | Emissions Database for Global Atmospheric Research — source of food emission shares |
| LULUCF | Land use, land-use change, and forestry |
| CPC | Central Product Classification — UN product coding system |
| M49 code | UN standard country/area code |
| Agrifood systems | All activities for primary production of food and non-food agricultural products |
| Agentic loop | Cycle where Claude reads a message, decides whether to call a tool or answer directly, executes if needed, returns response |
| Tool calling | Anthropic API feature — Claude invokes developer-defined functions to fetch data or perform actions |
| MCP | Model Context Protocol — standard for exposing tools to Claude. Used in Claude Code and workplace integrations |
| DATA_MODE | Environment variable controlling data source: 'full' loads data/raw/, 'sample' loads data/sample/ |
| NAOCE | North America & Oceania |
| NAWACA | North Africa, Western & Central Asia |
| SSEA | South & Southeast Asia |
| SSA | Sub-Saharan Africa |

---

*Last updated: Phase 5 complete including Session 7 (Plotly charts). Phase 6 (MCP Server) session plan added — ready to start.*
