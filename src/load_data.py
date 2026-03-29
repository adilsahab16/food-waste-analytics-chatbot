import os
import sqlite3
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DATA_MODE = os.getenv('DATA_MODE', 'full')
DATA_DIR = Path('data/raw') if DATA_MODE == 'full' else Path('data/sample')
DB_PATH = Path('db/food_waste.db')


def load_dim_region(data_dir):
    df = pd.read_excel(data_dir / 'country_income_region_mapping.xlsx')
    df = df.rename(columns={
        'Country': 'country',
        'Country_code': 'country_code',
        'Income': 'income',
        'Region': 'region',
    })
    return df[['region', 'country', 'country_code', 'm49_code', 'dev_country', 'income']]


def load_dim_commodity(data_dir):
    df = pd.read_excel(data_dir / 'commodity tagging.xlsx')
    df = df.rename(columns={
        'Commodity': 'commodity',
        'Commodity_Group': 'commodity_group',
        'Basket': 'basket',
    })
    return df[['cpc_code', 'commodity', 'commodity_group', 'basket']]


def load_dim_population(data_dir):
    df = pd.read_csv(data_dir / 'world_bank_population_data.csv')
    df = df.rename(columns={'Country_code': 'country_code'})
    year_cols = [c for c in df.columns if str(c).isdigit()]
    df = df.melt(
        id_vars=['country', 'country_code'],
        value_vars=year_cols,
        var_name='year',
        value_name='population',
    )
    df['year'] = df['year'].astype(int)
    df['population'] = pd.to_numeric(df['population'], errors='coerce')
    df = df.dropna(subset=['population'])
    df['population'] = df['population'].astype(int)
    return df[['country', 'country_code', 'year', 'population']]


def load_dim_gdp(data_dir):
    df = pd.read_csv(data_dir / 'world_bank_gdp_data.csv')
    df = df.rename(columns={'Country_code': 'country_code'})
    if '2023' in df.columns:
        df = df.drop(columns=['2023'])
    year_cols = [c for c in df.columns if str(c).isdigit()]
    df = df.melt(
        id_vars=['country', 'country_code'],
        value_vars=year_cols,
        var_name='year',
        value_name='gdp',
    )
    df['year'] = df['year'].astype(int)
    df['gdp'] = pd.to_numeric(df['gdp'], errors='coerce')
    df = df.dropna(subset=['gdp'])
    df['gdp'] = df['gdp'].astype(int)
    return df[['country', 'country_code', 'year', 'gdp']]


def load_fact_food_loss(data_dir):
    df = pd.read_excel(data_dir / 'World_Food Loss and Waste Database_FAO_1966-2022.xlsx')
    df['source_name'] = 'FAO'
    return df[['m49_code', 'country', 'year', 'loss_percentage', 'food_supply_stage', 'cpc_code', 'commodity', 'source_name']]


def load_fact_food_system_emissions(data_dir):
    df = pd.read_excel(data_dir / 'Emissions_Totals_E_All_Data_NOFLAG.xlsx')
    # Filter to FAO TIER 1 source and required gas types only
    df = df[df['Source'] == 'FAO TIER 1']
    df = df[df['Element'].isin([
        'Emissions (CH4)',
        'Emissions (N2O)',
        'Emissions (CO2eq) (AR5)',
    ])]
    # Unpivot Y-prefixed year columns to tall format
    year_cols = [c for c in df.columns if str(c).startswith('Y') and str(c)[1:].isdigit()]
    df = df.melt(
        id_vars=['m49_code', 'Area', 'Item', 'Element'],
        value_vars=year_cols,
        var_name='year',
        value_name='emissions',
    )
    # Strip Y prefix
    df['year'] = df['year'].str.lstrip('Y').astype(int)
    # Drop projection years
    df = df[~df['year'].isin([2030, 2050])]
    # Strip leading apostrophe added by Excel text-prefix formatting (e.g. '004 → 4)
    df['m49_code'] = df['m49_code'].astype(str).str.lstrip("'").astype(int)
    df = df.rename(columns={'Area': 'area', 'Item': 'item', 'Element': 'element'})
    df['emissions'] = pd.to_numeric(df['emissions'], errors='coerce')
    df['source_name'] = 'FAO'
    return df[['m49_code', 'area', 'year', 'emissions', 'item', 'element', 'source_name']]


def load_fact_total_emissions_pik(data_dir):
    df = pd.read_csv(data_dir / 'CW_HistoricalEmissions_PIK.csv')
    # 'country' column contains ISO3 country codes — rename to country_code
    df = df.rename(columns={'country': 'country_code'})
    # Exclude KYOTOGHG aggregate — individual gases give more analytical value
    df = df[df['gas'] != 'KYOTOGHG']
    df = df.drop(columns=['Source'])
    # Unpivot year columns to tall format
    year_cols = [c for c in df.columns if str(c).isdigit()]
    df = df.melt(
        id_vars=['country_code', 'sector', 'gas'],
        value_vars=year_cols,
        var_name='year',
        value_name='emissions',
    )
    df['year'] = df['year'].astype(int)
    # Trim to 1966+ — pre-1966 outside analysis scope
    df = df[df['year'] >= 1966]
    df['emissions'] = pd.to_numeric(df['emissions'], errors='coerce')
    df['source_name'] = 'PIK'
    return df[['country_code', 'year', 'sector', 'gas', 'emissions', 'source_name']]


def load_fact_food_emission_shares_edgar(data_dir):
    df = pd.read_csv(data_dir / 'EDGAR-FOOD_EMISSIONS_SHARES.csv')
    df = df.rename(columns={
        'Country_code_A3': 'country_code',
        'Name': 'country',
        'Substance': 'substance',
    })
    year_cols = [c for c in df.columns if str(c).isdigit()]
    df = df.melt(
        id_vars=['country_code', 'country', 'substance'],
        value_vars=year_cols,
        var_name='year',
        value_name='share',
    )
    df['year'] = df['year'].astype(int)
    df['share'] = pd.to_numeric(df['share'], errors='coerce')
    df['source_name'] = 'EDGAR'
    return df[['country_code', 'country', 'year', 'substance', 'share', 'source_name']]


def main():
    print(f'DATA_MODE : {DATA_MODE}')
    print(f'Source dir: {DATA_DIR}')
    print(f'Database  : {DB_PATH}')
    print()

    DB_PATH.parent.mkdir(exist_ok=True)

    # Start fresh each run
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)

    loaders = [
        ('dim_region',                    load_dim_region),
        ('dim_commodity',                 load_dim_commodity),
        ('dim_population',                load_dim_population),
        ('dim_gdp',                       load_dim_gdp),
        ('fact_food_loss',                load_fact_food_loss),
        ('fact_food_system_emissions',    load_fact_food_system_emissions),
        ('fact_total_emissions_pik',      load_fact_total_emissions_pik),
        ('fact_food_emission_shares_edgar', load_fact_food_emission_shares_edgar),
    ]

    for table_name, loader in loaders:
        print(f'  Loading {table_name}...', end=' ', flush=True)
        df = loader(DATA_DIR)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f'{len(df):,} rows')

    conn.close()
    print(f'\nDone. Database written to {DB_PATH}')


if __name__ == '__main__':
    main()
