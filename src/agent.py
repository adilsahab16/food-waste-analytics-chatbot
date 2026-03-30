import json
import os
import anthropic
from src.tools import (
    query_food_loss,
    query_food_system_emissions,
    query_population_gdp,
    query_total_emissions_by_sector,
    query_total_ghg_with_food_share,
)

MODEL = "claude-sonnet-4-20250514"

SYSTEM_PROMPT = """You are a food waste analytics assistant with access to 5 data tools.

Your tools query a SQLite database built from FAO, World Bank (WDI), PIK, and EDGAR datasets
covering food loss, food system emissions, total GHG emissions, population, and GDP.

When a user asks a question:
- Decide which tool(s) to call based on what the question is asking
- Call the tool with appropriate parameters
- Summarise the results in clear, plain language — never return raw data rows
- Briefly explain what the data shows and any notable patterns

Tool selection guide:
- Food loss/waste percentages → query_food_loss
- Food system emissions (FAO) → query_food_system_emissions
- Population or GDP context → query_population_gdp
- Total economy-wide emissions by sector → query_total_emissions_by_sector
- Total GHG + food system share together → query_total_ghg_with_food_share

Always answer in plain language. Mention the data source(s) used."""

# Tool definitions passed to the Anthropic API
TOOL_DEFINITIONS = [
    {
        "name": "query_food_loss",
        "description": (
            "Use this tool to query food loss and waste percentage data. "
            "Call this when the user asks about food loss or waste percentages across any "
            "combination of: time trends, regions, income groups, supply chain stages, "
            "commodity groups, or commodity baskets. "
            "This tool does NOT cover emissions — use the emissions tools for those questions."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "group_by": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Dimensions to group by. Any of: year, income, region, food_supply_stage, basket",
                },
                "filters": {
                    "type": "object",
                    "description": "Optional filters: region, income (High/Low), year_from, year_to, basket, food_supply_stage",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max rows to return. Default: 100",
                },
            },
            "required": ["group_by"],
        },
    },
    {
        "name": "query_food_system_emissions",
        "description": (
            "Use this tool to query food system emissions data from the FAO. "
            "Call this when the user asks about agrifood system emissions, emissions by supply "
            "chain stage, emissions by gas type, crop emissions, or livestock emissions. "
            "This tool covers food-system-specific emissions only — for total economy-wide "
            "emissions use the total emissions tool."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "group_by": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Dimensions to group by. Any of: year, income, region, item, element",
                },
                "item_filter": {
                    "type": "string",
                    "enum": ["supply_chain", "crops_livestock", "all"],
                    "description": "supply_chain = 8 supply chain stages, crops_livestock = crops vs livestock, all = no filter. Default: all",
                },
                "element_filter": {
                    "type": "string",
                    "enum": ["co2eq", "by_gas", "all"],
                    "description": "co2eq = AR5 CO2eq only, by_gas = CH4 + N2O + CO2eq, all = no filter. Default: co2eq",
                },
                "filters": {
                    "type": "object",
                    "description": "Optional filters: region, income, year_from, year_to",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max rows to return. Default: 100",
                },
            },
            "required": ["group_by"],
        },
    },
    {
        "name": "query_population_gdp",
        "description": (
            "Use this tool to retrieve population and GDP data as contextual support. "
            "Call this when the user asks about demographic or economic trends alongside "
            "food loss or emissions patterns, or when comparing income groups by population "
            "or economic output. Do not use this as a primary analytical tool — it provides "
            "supporting context for other insights."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "group_by": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Dimensions to group by. Any of: year, income, region",
                },
                "filters": {
                    "type": "object",
                    "description": "Optional filters: region, income, year_from, year_to",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max rows to return. Default: 100",
                },
            },
            "required": ["group_by"],
        },
    },
    {
        "name": "query_total_emissions_by_sector",
        "description": (
            "Use this tool to query total economy-wide GHG emissions broken down by sector, "
            "sourced from the PIK dataset. Call this when the user asks about total emissions "
            "by sector (Agriculture, Energy, Industry etc.) across regions. "
            "Excludes the KYOTOGHG aggregate — returns individual gas types only. "
            "For food system emission shares within total emissions, use "
            "query_total_ghg_with_food_share instead."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "group_by": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Dimensions to group by. Any of: year, income, region, sector, gas",
                },
                "filters": {
                    "type": "object",
                    "description": "Optional filters: region, income, sector, gas, year_from, year_to",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max rows to return. Default: 100",
                },
            },
            "required": ["group_by"],
        },
    },
    {
        "name": "query_total_ghg_with_food_share",
        "description": (
            "Use this tool when the user asks about total GHG emissions by region combined "
            "with the food system's share of those emissions. Joins PIK total emissions with "
            "EDGAR food emission shares and returns both values together per region. "
            "Use specifically for questions comparing overall emissions magnitude against "
            "food system contribution."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "group_by": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Dimensions to group by. Any of: region, income, year",
                },
                "filters": {
                    "type": "object",
                    "description": "Optional filters: region, income, year_from, year_to",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max rows to return. Default: 100",
                },
            },
            "required": ["group_by"],
        },
    },
]

# Map tool names to their Python functions
TOOL_FUNCTIONS = {
    "query_food_loss": query_food_loss,
    "query_food_system_emissions": query_food_system_emissions,
    "query_population_gdp": query_population_gdp,
    "query_total_emissions_by_sector": query_total_emissions_by_sector,
    "query_total_ghg_with_food_share": query_total_ghg_with_food_share,
}


def run_agent(user_message: str) -> tuple[str, list[dict]]:
    """
    Run the agentic loop for a single user message.

    Sends the message to Claude with all 5 tool definitions.
    Loops: if Claude returns tool_use blocks, executes each tool and feeds
    results back. Continues until Claude returns a final text response.

    Returns:
        (text, tool_calls) where tool_calls is a list of dicts:
        [{"tool_name": str, "inputs": dict, "result": list[dict]}, ...]
        Collected across all iterations — used by the UI to render charts.
    """
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    messages = [{"role": "user", "content": user_message}]
    tool_calls: list[dict] = []

    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        # Append Claude's response to the message history
        messages.append({"role": "assistant", "content": response.content})

        # If Claude is done (no tool calls), return text + collected tool data
        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text, tool_calls
            return "", tool_calls

        # If Claude wants to call tools, execute each one and collect results
        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    fn = TOOL_FUNCTIONS[block.name]
                    result_data = fn(**block.input)
                    tool_calls.append({
                        "tool_name": block.name,
                        "inputs": block.input,
                        "result": result_data,
                    })
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result_data),
                    })

            # Feed all tool results back to Claude in a single user turn
            messages.append({"role": "user", "content": tool_results})
            # Loop continues — Claude will now process the results and either
            # call more tools or produce the final answer

        else:
            # Unexpected stop reason — return whatever text is available
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text, tool_calls
            return f"Unexpected stop reason: {response.stop_reason}", tool_calls
