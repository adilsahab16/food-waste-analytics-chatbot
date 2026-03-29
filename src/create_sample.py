"""
Creates data/sample/ from data/raw/ for Streamlit Community Cloud deployment.

Selects 4 regions (Europe, SSA, S&SE Asia, LA) covering high/low income spread.
Trims to 2005 onwards for wide-format time-series files.
Output files mirror the exact structure of data/raw/ so load_data.py works unchanged.

Run once locally from the repo root:
    PYTHONPATH=. python src/create_sample.py
Then commit data/sample/ to the repo.
"""

import pandas as pd
from pathlib import Path

RAW_DIR = Path('data/raw')
SAMPLE_DIR = Path('data/sample')

SAMPLE_REGIONS = ['Europe', 'SSA', 'S&SE Asia', 'LA']
YEAR_FROM = 2005


def main():
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Regions selected : {SAMPLE_REGIONS}")
    print(f"Year cutoff      : {YEAR_FROM}+")
    print()

    # ── dim_region ────────────────────────────────────────────────────────────
    dim_region = pd.read_excel(RAW_DIR / 'country_income_region_mapping.xlsx')
    dim_region_sample = dim_region[dim_region['Region'].isin(SAMPLE_REGIONS)].copy()

    sample_country_codes = set(dim_region_sample['Country_code'])
    sample_m49_codes = set(dim_region_sample['m49_code'])

    dim_region_sample.to_excel(SAMPLE_DIR / 'country_income_region_mapping.xlsx', index=False)
    print(f"  dim_region                  : {len(dim_region_sample)} countries")

    # ── dim_commodity ─────────────────────────────────────────────────────────
    # Small reference table — keep in full, no filtering needed
    dim_commodity = pd.read_excel(RAW_DIR / 'commodity tagging.xlsx')
    dim_commodity.to_excel(SAMPLE_DIR / 'commodity tagging.xlsx', index=False)
    print(f"  dim_commodity               : {len(dim_commodity)} rows (full — no filter)")

    # ── dim_population ────────────────────────────────────────────────────────
    pop = pd.read_csv(RAW_DIR / 'world_bank_population_data.csv')
    pop_sample = pop[pop['Country_code'].isin(sample_country_codes)].copy()
    year_cols = [c for c in pop_sample.columns if str(c).isdigit() and int(c) >= YEAR_FROM]
    id_cols = [c for c in pop_sample.columns if not str(c).isdigit()]
    pop_sample = pop_sample[id_cols + year_cols]
    pop_sample.to_csv(SAMPLE_DIR / 'world_bank_population_data.csv', index=False)
    print(f"  dim_population              : {len(pop_sample)} countries × {len(year_cols)} years")

    # ── dim_gdp ───────────────────────────────────────────────────────────────
    gdp = pd.read_csv(RAW_DIR / 'world_bank_gdp_data.csv')
    gdp_sample = gdp[gdp['Country_code'].isin(sample_country_codes)].copy()
    year_cols_gdp = [
        c for c in gdp_sample.columns
        if str(c).isdigit() and int(c) >= YEAR_FROM and c != '2023'
    ]
    id_cols_gdp = [c for c in gdp_sample.columns if not str(c).isdigit()]
    gdp_sample = gdp_sample[id_cols_gdp + year_cols_gdp]
    gdp_sample.to_csv(SAMPLE_DIR / 'world_bank_gdp_data.csv', index=False)
    print(f"  dim_gdp                     : {len(gdp_sample)} countries × {len(year_cols_gdp)} years")

    # ── fact_food_loss ────────────────────────────────────────────────────────
    food_loss = pd.read_excel(RAW_DIR / 'World_Food Loss and Waste Database_FAO_1966-2022.xlsx')
    food_loss_sample = food_loss[
        food_loss['m49_code'].isin(sample_m49_codes) &
        (food_loss['year'] >= YEAR_FROM)
    ].copy()
    food_loss_sample.to_excel(
        SAMPLE_DIR / 'World_Food Loss and Waste Database_FAO_1966-2022.xlsx', index=False
    )
    print(f"  fact_food_loss              : {len(food_loss_sample):,} rows")

    # ── fact_food_system_emissions ────────────────────────────────────────────
    emissions = pd.read_excel(RAW_DIR / 'Emissions_Totals_E_All_Data_NOFLAG.xlsx')
    # Strip Excel apostrophe prefix before filtering (e.g. '004 → 4)
    emissions['m49_code'] = emissions['m49_code'].astype(str).str.lstrip("'")
    emissions['m49_code_int'] = pd.to_numeric(emissions['m49_code'], errors='coerce')
    emissions_sample = emissions[emissions['m49_code_int'].isin(sample_m49_codes)].copy()
    emissions_sample = emissions_sample.drop(columns=['m49_code_int'])
    # Keep only year columns >= YEAR_FROM
    y_year_cols = [
        c for c in emissions_sample.columns
        if str(c).startswith('Y') and str(c)[1:].isdigit() and int(str(c)[1:]) >= YEAR_FROM
    ]
    non_year_cols = [
        c for c in emissions_sample.columns
        if not (str(c).startswith('Y') and str(c)[1:].isdigit())
    ]
    emissions_sample = emissions_sample[non_year_cols + y_year_cols]
    emissions_sample.to_excel(SAMPLE_DIR / 'Emissions_Totals_E_All_Data_NOFLAG.xlsx', index=False)
    print(f"  fact_food_system_emissions  : {len(emissions_sample):,} rows × {len(y_year_cols)} years")

    # ── fact_total_emissions_pik ──────────────────────────────────────────────
    # Raw file uses 'country' column for ISO3 codes (renamed to country_code in load_data.py)
    pik = pd.read_csv(RAW_DIR / 'CW_HistoricalEmissions_PIK.csv')
    pik_sample = pik[pik['country'].isin(sample_country_codes)].copy()
    year_cols_pik = [c for c in pik_sample.columns if str(c).isdigit() and int(c) >= YEAR_FROM]
    id_cols_pik = [c for c in pik_sample.columns if not str(c).isdigit()]
    pik_sample = pik_sample[id_cols_pik + year_cols_pik]
    pik_sample.to_csv(SAMPLE_DIR / 'CW_HistoricalEmissions_PIK.csv', index=False)
    print(f"  fact_total_emissions_pik    : {len(pik_sample):,} rows × {len(year_cols_pik)} years")

    # ── fact_food_emission_shares_edgar ───────────────────────────────────────
    edgar = pd.read_csv(RAW_DIR / 'EDGAR-FOOD_EMISSIONS_SHARES.csv')
    edgar_sample = edgar[edgar['Country_code_A3'].isin(sample_country_codes)].copy()
    year_cols_edgar = [c for c in edgar_sample.columns if str(c).isdigit() and int(c) >= YEAR_FROM]
    id_cols_edgar = [c for c in edgar_sample.columns if not str(c).isdigit()]
    edgar_sample = edgar_sample[id_cols_edgar + year_cols_edgar]
    edgar_sample.to_csv(SAMPLE_DIR / 'EDGAR-FOOD_EMISSIONS_SHARES.csv', index=False)
    print(f"  fact_food_emission_shares_edgar: {len(edgar_sample):,} rows × {len(year_cols_edgar)} years")

    print(f"\nSample data written to {SAMPLE_DIR}/")
    print("Next steps:")
    print("  1. DATA_MODE=sample PYTHONPATH=. python src/load_data.py  ← verify DB loads cleanly")
    print("  2. DATA_MODE=sample PYTHONPATH=. streamlit run src/app.py  ← verify app works on sample")
    print("  3. git add data/sample/ && commit")


if __name__ == '__main__':
    main()
