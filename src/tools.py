import sqlite3
from pathlib import Path

DB_PATH = Path('db/food_waste.db')

# Named item presets for query_food_system_emissions — filter logic lives here, not in Claude
SUPPLY_CHAIN_ITEMS = [
    'Food Household Consumption',
    'Waste',
    'Pre- and Post- Production',
    'Food Packaging',
    'Agrifood Systems Waste Disposal',
    'Food Retail',
    'Food Transport',
    'Food Processing',
]

CROPS_LIVESTOCK_ITEMS = [
    'Emissions from crops',
    'Emissions from livestock',
]


def _execute(sql: str, params: list) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def query_food_loss(
    group_by: list,
    filters: dict = None,
    limit: int = 100,
) -> list:
    """
    Query food loss/waste percentage data.
    group_by: any of [year, income, region, food_supply_stage, basket]
    filters: optional {region, income, year_from, year_to, basket, food_supply_stage}
    Returns: [{group_by cols..., avg_loss_percentage}]
    Serves: Q1.1, Q2.1, Q2.2
    """
    filters = filters or {}
    needs_commodity = 'basket' in group_by or 'basket' in filters

    col_map = {
        'year':              'f.year',
        'income':            'r.income',
        'region':            'r.region',
        'food_supply_stage': 'f.food_supply_stage',
        'basket':            'c.basket',
    }

    select_cols = [col_map[g] for g in group_by]
    select_clause = ', '.join(select_cols + ['AVG(f.loss_percentage) AS avg_loss_percentage'])

    sql = f"""
        SELECT {select_clause}
        FROM fact_food_loss f
        JOIN dim_region r ON f.m49_code = r.m49_code
    """
    if needs_commodity:
        sql += ' JOIN dim_commodity c ON f.cpc_code = c.cpc_code'

    where, params = [], []

    if 'region' in filters:
        where.append('r.region = ?')
        params.append(filters['region'])
    if 'income' in filters:
        where.append('r.income = ?')
        params.append(filters['income'])
    if 'year_from' in filters:
        where.append('f.year >= ?')
        params.append(filters['year_from'])
    if 'year_to' in filters:
        where.append('f.year <= ?')
        params.append(filters['year_to'])
    if 'basket' in filters:
        where.append('c.basket = ?')
        params.append(filters['basket'])
    if 'food_supply_stage' in filters:
        where.append('f.food_supply_stage = ?')
        params.append(filters['food_supply_stage'])

    if where:
        sql += ' WHERE ' + ' AND '.join(where)
    if select_cols:
        sql += ' GROUP BY ' + ', '.join(select_cols)

    sql += f' LIMIT {int(limit)}'
    return _execute(sql, params)


def query_food_system_emissions(
    group_by: list,
    item_filter: str = 'all',
    element_filter: str = 'co2eq',
    filters: dict = None,
    limit: int = 100,
) -> list:
    """
    Query food system emissions from FAO.
    group_by: any of [year, income, region, item, element]
    item_filter: 'supply_chain' | 'crops_livestock' | 'all'
    element_filter: 'co2eq' (AR5 only) | 'by_gas' (CH4, N2O, CO2eq) | 'all'
    filters: optional {region, income, year_from, year_to}
    Returns: [{group_by cols..., total_emissions_kt}]
    Serves: Q1.2, Q3.1, Q3.2, Q3.3
    """
    filters = filters or {}

    col_map = {
        'year':    'f.year',
        'income':  'r.income',
        'region':  'r.region',
        'item':    'f.item',
        'element': 'f.element',
    }

    select_cols = [col_map[g] for g in group_by]
    select_clause = ', '.join(select_cols + ['SUM(f.emissions) AS total_emissions_kt'])

    sql = f"""
        SELECT {select_clause}
        FROM fact_food_system_emissions f
        JOIN dim_region r ON f.m49_code = r.m49_code
    """

    where, params = [], []

    # item preset — filter logic lives in Python, not Claude's reasoning
    if item_filter == 'supply_chain':
        where.append(f'f.item IN ({",".join("?" * len(SUPPLY_CHAIN_ITEMS))})')
        params.extend(SUPPLY_CHAIN_ITEMS)
    elif item_filter == 'crops_livestock':
        where.append(f'f.item IN ({",".join("?" * len(CROPS_LIVESTOCK_ITEMS))})')
        params.extend(CROPS_LIVESTOCK_ITEMS)

    # element preset
    if element_filter == 'co2eq':
        where.append('f.element = ?')
        params.append('Emissions (CO2eq) (AR5)')
    elif element_filter == 'by_gas':
        where.append('f.element IN (?, ?, ?)')
        params.extend(['Emissions (CH4)', 'Emissions (N2O)', 'Emissions (CO2eq) (AR5)'])

    if 'region' in filters:
        where.append('r.region = ?')
        params.append(filters['region'])
    if 'income' in filters:
        where.append('r.income = ?')
        params.append(filters['income'])
    if 'year_from' in filters:
        where.append('f.year >= ?')
        params.append(filters['year_from'])
    if 'year_to' in filters:
        where.append('f.year <= ?')
        params.append(filters['year_to'])

    if where:
        sql += ' WHERE ' + ' AND '.join(where)
    if select_cols:
        sql += ' GROUP BY ' + ', '.join(select_cols)

    sql += f' LIMIT {int(limit)}'
    return _execute(sql, params)


def query_population_gdp(
    group_by: list,
    filters: dict = None,
    limit: int = 100,
) -> list:
    """
    Query population and GDP per capita as contextual support.
    group_by: any of [year, income, region]
    filters: optional {region, income, year_from, year_to}
    Returns: [{group_by cols..., total_population, avg_total_gdp_usd, avg_gdp_per_capita}]
    Serves: Q1.3 (contextual enrichment)
    """
    filters = filters or {}

    col_map = {
        'year':   'p.year',
        'income': 'r.income',
        'region': 'r.region',
    }

    select_cols = [col_map[g] for g in group_by]
    select_clause = ', '.join(select_cols + [
        'SUM(p.population) AS total_population',
        'AVG(g.gdp) AS avg_total_gdp_usd',
        'SUM(g.gdp) / NULLIF(SUM(p.population), 0) AS avg_gdp_per_capita',
    ])

    sql = f"""
        SELECT {select_clause}
        FROM dim_population p
        JOIN dim_region r ON p.country_code = r.country_code
        JOIN dim_gdp g ON p.country_code = g.country_code AND p.year = g.year
    """

    where, params = [], []

    if 'region' in filters:
        where.append('r.region = ?')
        params.append(filters['region'])
    if 'income' in filters:
        where.append('r.income = ?')
        params.append(filters['income'])
    if 'year_from' in filters:
        where.append('p.year >= ?')
        params.append(filters['year_from'])
    if 'year_to' in filters:
        where.append('p.year <= ?')
        params.append(filters['year_to'])

    if where:
        sql += ' WHERE ' + ' AND '.join(where)
    if select_cols:
        sql += ' GROUP BY ' + ', '.join(select_cols)

    sql += f' LIMIT {int(limit)}'
    return _execute(sql, params)


def query_total_emissions_by_sector(
    group_by: list,
    filters: dict = None,
    limit: int = 100,
) -> list:
    """
    Query total economy-wide GHG emissions by sector from PIK.
    group_by: any of [year, income, region, sector, gas]
    filters: optional {region, income, sector, gas, year_from, year_to}
    Returns: [{group_by cols..., total_emissions_kt}]
    Serves: Q4.2
    """
    filters = filters or {}

    col_map = {
        'year':   'p.year',
        'income': 'r.income',
        'region': 'r.region',
        'sector': 'p.sector',
        'gas':    'p.gas',
    }

    select_cols = [col_map[g] for g in group_by]
    select_clause = ', '.join(select_cols + ['SUM(p.emissions) AS total_emissions_kt'])

    sql = f"""
        SELECT {select_clause}
        FROM fact_total_emissions_pik p
        JOIN dim_region r ON p.country_code = r.country_code
    """

    where, params = [], []

    if 'region' in filters:
        where.append('r.region = ?')
        params.append(filters['region'])
    if 'income' in filters:
        where.append('r.income = ?')
        params.append(filters['income'])
    if 'sector' in filters:
        where.append('p.sector = ?')
        params.append(filters['sector'])
    if 'gas' in filters:
        where.append('p.gas = ?')
        params.append(filters['gas'])
    if 'year_from' in filters:
        where.append('p.year >= ?')
        params.append(filters['year_from'])
    if 'year_to' in filters:
        where.append('p.year <= ?')
        params.append(filters['year_to'])

    if where:
        sql += ' WHERE ' + ' AND '.join(where)
    if select_cols:
        sql += ' GROUP BY ' + ', '.join(select_cols)

    sql += f' LIMIT {int(limit)}'
    return _execute(sql, params)


def query_total_ghg_with_food_share(
    group_by: list,
    filters: dict = None,
    limit: int = 100,
) -> list:
    """
    Query total GHG emissions combined with food system emission share.
    Uses CTEs to pre-aggregate PIK and EDGAR separately before joining,
    avoiding fan-out inflation (PIK has 20 rows/country/year, EDGAR has 9).
    group_by: any of [region, income, year]
    filters: optional {region, income, year_from, year_to}
    Returns: [{group_by cols..., total_emissions_kt, avg_food_share_pct}]
    Serves: Q4.1
    """
    filters = filters or {}

    col_map = {
        'region': 'r.region',
        'income': 'r.income',
        'year':   'pik.year',
    }

    select_cols = [col_map[g] for g in group_by]
    select_clause = ', '.join(select_cols + [
        'SUM(pik.total_emissions_kt) AS total_emissions_kt',
        'AVG(edgar.avg_share) * 100 AS avg_food_share_pct',
    ])

    # Pre-aggregate each source by country+year before joining to avoid row fan-out
    sql = f"""
        WITH pik AS (
            SELECT country_code, year, SUM(emissions) AS total_emissions_kt
            FROM fact_total_emissions_pik
            GROUP BY country_code, year
        ),
        edgar AS (
            SELECT country_code, year, AVG(share) AS avg_share
            FROM fact_food_emission_shares_edgar
            GROUP BY country_code, year
        )
        SELECT {select_clause}
        FROM pik
        JOIN dim_region r ON pik.country_code = r.country_code
        JOIN edgar ON pik.country_code = edgar.country_code AND pik.year = edgar.year
    """

    where, params = [], []

    if 'region' in filters:
        where.append('r.region = ?')
        params.append(filters['region'])
    if 'income' in filters:
        where.append('r.income = ?')
        params.append(filters['income'])
    if 'year_from' in filters:
        where.append('pik.year >= ?')
        params.append(filters['year_from'])
    if 'year_to' in filters:
        where.append('pik.year <= ?')
        params.append(filters['year_to'])

    if where:
        sql += ' WHERE ' + ' AND '.join(where)
    if select_cols:
        sql += ' GROUP BY ' + ', '.join(select_cols)

    sql += f' LIMIT {int(limit)}'
    return _execute(sql, params)
