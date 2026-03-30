import pandas as pd
import plotly.express as px
import streamlit as st

# Metric columns and display labels for each tool.
# Each entry is (column_name, y-axis label).
# For tools with multiple metrics, each is rendered as a separate chart.
TOOL_METRIC_SPECS: dict[str, list[tuple[str, str]]] = {
    "query_food_loss": [
        ("avg_loss_percentage", "Avg Food Loss (%)"),
    ],
    "query_food_system_emissions": [
        ("total_emissions_kt", "Total Emissions (kt CO₂eq)"),
    ],
    "query_population_gdp": [
        ("total_population", "Total Population"),
        ("avg_gdp_per_capita", "Avg GDP per Capita (USD)"),
    ],
    "query_total_emissions_by_sector": [
        ("total_emissions_kt", "Total Emissions (kt CO₂eq)"),
    ],
    "query_total_ghg_with_food_share": [
        ("total_emissions_kt", "Total GHG Emissions (kt CO₂eq)"),
        ("avg_food_share_pct", "Food System Share of GHG (%)"),
    ],
}


def render_charts(tool_calls: list[dict], key_prefix: str = "") -> None:
    """Render a chart for each tool call that returned more than one row.

    key_prefix must be unique per render_charts call on the page to avoid
    Streamlit duplicate element ID errors when the same chart data appears
    in multiple messages in the conversation history.
    """
    for i, call in enumerate(tool_calls):
        _render_one(call, key=f"{key_prefix}_{i}")


def _render_one(call: dict, key: str = "") -> None:
    tool_name = call["tool_name"]
    inputs = call["inputs"]
    result = call["result"]

    if not result or len(result) <= 1:
        return

    df = pd.DataFrame(result)
    group_by: list[str] = inputs.get("group_by", [])

    if not group_by:
        return

    metric_specs = TOOL_METRIC_SPECS.get(tool_name, [])
    if not metric_specs:
        return

    # Chart type: line when year is a dimension, bar otherwise
    use_line = "year" in group_by
    x_col = "year" if use_line else group_by[0]
    # Color dimension: first group_by dim that is not the x-axis
    color_col = next((d for d in group_by if d != x_col), None)

    for metric_col, y_label in metric_specs:
        if metric_col not in df.columns:
            continue

        label_map = {
            x_col: x_col.replace("_", " ").title(),
            metric_col: y_label,
        }
        if color_col:
            label_map[color_col] = color_col.replace("_", " ").title()

        if use_line:
            fig = px.line(
                df,
                x=x_col,
                y=metric_col,
                color=color_col,
                labels=label_map,
                title=y_label,
            )
        else:
            fig = px.bar(
                df,
                x=x_col,
                y=metric_col,
                color=color_col,
                barmode="group",
                labels=label_map,
                title=y_label,
            )

        fig.update_layout(legend_title_text="")
        st.plotly_chart(fig, use_container_width=True, key=f"chart_{key}_{metric_col}")
