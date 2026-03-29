# Design Decisions Log

Running log of design decisions made during development.
Full history is also captured in CLAUDE_CONTEXT.md Section 13.

| Decision | Rationale | Phase |
|---|---|---|
| SQLite over PostgreSQL | Local, zero-setup, sufficient for static dataset, portfolio-friendly | 1 |
| Streamlit for UI | Python-native, minimal frontend knowledge, fast to build | 1 |
| Commodity basket as primary aggregation | 6 baskets = clean top-level grouping; matches thesis methodology | 1 |
| loss_percentage not loss quantity | Research is fraction-based; consistent with thesis | 1 |
| Emissions in kilotons (kt) | Consistent unit across all emissions tables | 1 |
| CO2eq IPCC AR5 100-year GWP | Standard methodology; consistent with thesis and FAO reporting | 1 |
| Star schema for SQLite | Mirrors thesis data model; clean join structure | 1 |
| Full data gitignored, sample data committed | Full cleaned files kept local. Sample dataset in data/sample/ committed to power live demo | 1 |
| 4 fact tables not 3 | EDGAR (shares 0–1) and PIK (absolute kt) are different value types — must stay separate | 2 |
| dev_country column retained | Additional reporting attribute for future analysis | 2 |
| Year trim on PIK to 1966+ | Analysis scope starts 1966; pre-1966 adds size with no analytical value | 2 |
| source_name on all fact tables | Consistent provenance tracking across all tables | 2 |
| FAO TIER 1 only for food system emissions | UNFCCC rows are sparse with gaps; FAO TIER 1 is complete and consistent | 2 |
| Element filter: CH4, N2O, CO2eq AR5 only | Avoids double-counting from per-gas CO2eq conversions and direct/indirect splits | 2 |
| KYOTOGHG excluded from PIK | Aggregate metric — individual gases give more analytical value, avoid double-counting | 2 |
| GDP 2023 column dropped | Outside analysis scope; WDI data used to 2022 consistently | 2 |
| item_filter as named presets | Filter logic lives in Python not Claude's reasoning — safer, fewer tokens | 4 |
| group_by as dynamic list | Composable tools serve multiple questions; Claude selects from constrained valid set | 4 |
| limit parameter on all tools | Prevents unbounded result sets consuming context window tokens | 4 |
| Q4.1 as single combined tool | Simpler for Claude, cleaner answers — internal join more reliable than Claude combining two results | 4 |
| 5 tools not 10 | Composable parameterised design serves all 10 questions without redundancy | 4 |
| DATA_MODE env variable | Controls whether load_data.py uses full data (local dev) or sample data (demo/deployment) | 5 |
| Commit → clear → next session rhythm | Preserves continuity while managing token usage — code lives in GitHub, not in Claude's memory | 5 |
