# World Food Waste Analytics Chatbot

A natural language analytics chatbot for exploring global food loss and GHG emissions data.
Ask questions in plain English — the app queries a structured database built from FAO, World Bank,
PIK, and EDGAR datasets and returns clear, data-driven answers powered by Claude (Anthropic API).

**[Live Demo](#)** · Python · SQLite · Streamlit · Anthropic API

---

## Screenshots

> *Screenshots taken from the full dataset (local). The live demo runs on a curated sample.*

<!-- Add screenshots here — chatbot answering a food loss question, and an emissions question -->

---

## What It Can Answer

### Food Loss & Waste
- How has food loss changed over time in high vs low income regions?
- Which supply chain stage has the highest food loss by region?
- Food loss breakdown by commodity basket across regions

### Food System Emissions
- Yearly trend in food system emissions — high income vs low income
- Emissions by supply chain stage or gas type, broken down by region
- How do crop emissions compare to livestock emissions across regions?

### Total GHG Emissions
- Total economy-wide GHG emissions by sector and region
- What share of total GHG emissions comes from the food system, by region?

### Economic & Demographic Context
- Population and GDP trends alongside food loss patterns by income group

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
2. Claude receives the question + 5 tool definitions
3. Claude decides which tool(s) to call and with what parameters
4. Tool executes SQL against SQLite, returns rows
5. Claude summarises the results in plain language
6. Loop repeats if Claude needs more data; ends when Claude has a complete answer

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.11+ |
| LLM | Anthropic API — Claude Sonnet |
| Database | SQLite |
| UI | Streamlit |
| Data processing | pandas |

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
│   └── decisions.md        ← Running log of design decisions
└── requirements.txt
```

---

## Local Setup

### Prerequisites
- Python 3.11+
- Anthropic API key — get one at [console.anthropic.com](https://console.anthropic.com)
- Full data files in `data/raw/` (not included — see Data section below)

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
DATA_MODE=full        # use 'sample' to run on the demo dataset without raw files
```

Load the database:
```bash
PYTHONPATH=. python src/load_data.py
```

Run the app:
```bash
PYTHONPATH=. streamlit run src/app.py
```

### Running on sample data (no raw files needed)

The repo includes a curated sample dataset in `data/sample/`. To use it:

```bash
DATA_MODE=sample PYTHONPATH=. python src/load_data.py
DATA_MODE=sample PYTHONPATH=. streamlit run src/app.py
```

---

## Deploying to Streamlit Community Cloud

1. Push the repo to GitHub (already done)
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo
3. Set the main file path to `src/app.py`
4. Under **Advanced settings → Secrets**, add:
   ```
   ANTHROPIC_API_KEY = "sk-ant-your-key-here"
   DATA_MODE = "sample"
   ```
5. Click **Deploy**

The app will run on `data/sample/` automatically. No raw data files are needed.

---

## Data

This project uses public datasets that were cleaned and processed as part of original thesis research.
Full cleaned files are kept local and gitignored. A curated sample dataset (`data/sample/`) is
committed to the repo to power the live Streamlit demo.

| Source | Dataset | Coverage |
|---|---|---|
| FAO | Food Loss and Waste Database | 1966–2022 |
| FAO | Agrifood System Emissions (FAOSTAT) | 1961–2022 |
| World Bank (WDI) | Population & GDP | 1960–2022 |
| PIK | Historical GHG Emissions by Sector | 1850–2021 |
| EDGAR | Food System Emission Shares | 1970–2018 |
