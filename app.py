from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, dcc, html


PROJECT_DIR = Path(__file__).parent
PRIVATE_DATA_PATH = PROJECT_DIR / "cleaned_customer_sales_data.csv"
DEMO_DATA_PATH = PROJECT_DIR / "sample_sales_data.csv"
DATA_PATH = PRIVATE_DATA_PATH if PRIVATE_DATA_PATH.is_file() else DEMO_DATA_PATH
COLORS = {
    "background": "#f4f7fb",
    "surface": "#ffffff",
    "text": "#17243a",
    "muted": "#738098",
    "blue": "#4361ee",
    "teal": "#16a6a1",
    "purple": "#8b5cf6",
    "orange": "#f59e0b",
    "grid": "#e9edf4",
}


def load_sales_data() -> pd.DataFrame:
    if not DATA_PATH.is_file():
        raise FileNotFoundError(
            "Sales data not found. Add cleaned_customer_sales_data.csv or "
            f"restore the demo dataset at {DEMO_DATA_PATH}."
        )

    data = pd.read_csv(DATA_PATH)
    required_columns = {
        "Customer_ID",
        "Gender",
        "City",
        "Last_Purchase_Date",
        "Purchase_Amount",
        "Feedback_Score",
    }
    missing_columns = required_columns.difference(data.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Sales data is missing required columns: {missing}")

    data["City"] = data["City"].fillna("Unknown").astype(str).str.strip()
    data["Gender"] = data["Gender"].fillna("Unknown").astype(str).str.strip()
    data["Last_Purchase_Date"] = pd.to_datetime(
        data["Last_Purchase_Date"], errors="coerce"
    )
    data["Purchase_Amount"] = pd.to_numeric(data["Purchase_Amount"], errors="coerce")
    data["Feedback_Score"] = pd.to_numeric(data["Feedback_Score"], errors="coerce")
    return data


SALES = load_sales_data()
VALID_PURCHASE_DATES = SALES["Last_Purchase_Date"].dropna()
DATE_MIN = VALID_PURCHASE_DATES.min().date().isoformat()
DATE_MAX = VALID_PURCHASE_DATES.max().date().isoformat()


def format_inr(value: float) -> str:
    return f"₹{value:,.0f}"


def base_figure(fig: go.Figure, *, height: int = 330) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=12, r=18, t=18, b=12),
        paper_bgcolor=COLORS["surface"],
        plot_bgcolor=COLORS["surface"],
        font=dict(family="Inter, Segoe UI, sans-serif", color=COLORS["muted"]),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12),
        ),
        hoverlabel=dict(bgcolor="#17243a", font_color="#ffffff"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor=COLORS["grid"])
    fig.update_yaxes(showgrid=True, gridcolor=COLORS["grid"], zeroline=False)
    return fig


def empty_figure(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=14, color=COLORS["muted"]),
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return base_figure(fig)


def card(title: str, figure_id: str, class_name: str = "") -> html.Section:
    return html.Section(
        [
            html.Div(title, className="chart-title"),
            dcc.Graph(
                id=figure_id,
                config={"displayModeBar": False, "responsive": True},
                style={"height": "330px"},
            ),
        ],
        className=f"panel chart-panel {class_name}".strip(),
    )


app = Dash(__name__, title="Sales Analytics")
app.layout = html.Main(
    [
        html.Header(
            [
                html.Div(
                    [
                        html.Div("SALES INTELLIGENCE", className="eyebrow"),
                        html.H1("Sales analytics"),
                        html.P(
                            "A clear view of purchase activity, customer mix, and "
                            "feedback across India."
                        ),
                    ],
                    className="hero-copy",
                ),
                html.Div(
                    [
                        html.Span(className="status-dot"),
                        html.Span("DATASET LOADED"),
                    ],
                    className="status-pill",
                ),
            ],
            className="hero",
        ),
        html.Section(
            [
                html.Div(
                    [
                        html.Label("Purchase date", htmlFor="date-range"),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=DATE_MIN,
                            max_date_allowed=DATE_MAX,
                            start_date=None,
                            end_date=None,
                            display_format="DD MMM YYYY",
                            minimum_nights=0,
                            clearable=True,
                            className="date-picker",
                        ),
                    ],
                    className="filter-field date-field",
                ),
                html.Div(
                    [
                        html.Label("City", htmlFor="city-filter"),
                        dcc.Dropdown(
                            id="city-filter",
                            options=[
                                {"label": city, "value": city}
                                for city in sorted(SALES["City"].unique())
                            ],
                            value=[],
                            multi=True,
                            placeholder="All cities",
                            className="filter-dropdown",
                        ),
                    ],
                    className="filter-field",
                ),
                html.Div(
                    [
                        html.Label("Gender", htmlFor="gender-filter"),
                        dcc.Dropdown(
                            id="gender-filter",
                            options=[
                                {"label": gender, "value": gender}
                                for gender in sorted(SALES["Gender"].unique())
                            ],
                            value=None,
                            clearable=True,
                            placeholder="All genders",
                            className="filter-dropdown",
                        ),
                    ],
                    className="filter-field gender-field",
                ),
                html.Button(
                    "Reset filters",
                    id="reset-filters",
                    n_clicks=0,
                    className="reset-button",
                ),
            ],
            className="panel filter-bar",
        ),
        html.Section(
            [
                html.Div(
                    [
                        html.Div("TOTAL PURCHASE VALUE", className="metric-label"),
                        html.Div(id="total-revenue", className="metric-value"),
                        html.Div("Sum of purchase amounts", className="metric-note"),
                    ],
                    className="panel metric-card metric-blue",
                ),
                html.Div(
                    [
                        html.Div("SALES RECORDS", className="metric-label"),
                        html.Div(id="record-count", className="metric-value"),
                        html.Div("Rows in the selected view", className="metric-note"),
                    ],
                    className="panel metric-card metric-teal",
                ),
                html.Div(
                    [
                        html.Div("AVERAGE PURCHASE", className="metric-label"),
                        html.Div(id="avg-purchase", className="metric-value"),
                        html.Div("Average amount per record", className="metric-note"),
                    ],
                    className="panel metric-card metric-purple",
                ),
                html.Div(
                    [
                        html.Div("AVERAGE FEEDBACK", className="metric-label"),
                        html.Div(id="avg-feedback", className="metric-value"),
                        html.Div("Out of 10", className="metric-note"),
                    ],
                    className="panel metric-card metric-orange",
                ),
            ],
            className="metrics-grid",
        ),
        html.Section(
            [
                card("Purchase value over time", "revenue-trend"),
                card("Purchase value by city", "city-chart"),
            ],
            className="charts-grid charts-primary",
        ),
        html.Section(
            [
                card("Sales records by gender", "gender-chart"),
                card("Feedback score distribution", "feedback-chart"),
            ],
            className="charts-grid",
        ),
        html.Footer(
            [
                html.Span(
                    "All values are shown as supplied in the source dataset. "
                    "Records without a purchase date remain included until a date "
                    "range is selected."
                ),
                html.Span("Currency: INR  ·  Source: customer sales dataset"),
            ],
            className="dashboard-footer",
        ),
    ],
    className="dashboard",
)


@app.callback(
    Output("city-filter", "value"),
    Output("gender-filter", "value"),
    Output("date-range", "start_date"),
    Output("date-range", "end_date"),
    Input("reset-filters", "n_clicks"),
    prevent_initial_call=True,
)
def reset_filters(_clicks: int) -> tuple[list[str], None, None, None]:
    return [], None, None, None


@app.callback(
    Output("total-revenue", "children"),
    Output("record-count", "children"),
    Output("avg-purchase", "children"),
    Output("avg-feedback", "children"),
    Output("revenue-trend", "figure"),
    Output("city-chart", "figure"),
    Output("gender-chart", "figure"),
    Output("feedback-chart", "figure"),
    Input("city-filter", "value"),
    Input("gender-filter", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
)
def update_dashboard(
    selected_cities: list[str] | None,
    selected_gender: str | None,
    start_date: str | None,
    end_date: str | None,
) -> tuple[str, str, str, str, go.Figure, go.Figure, go.Figure, go.Figure]:
    filtered = SALES
    if selected_cities:
        filtered = filtered[filtered["City"].isin(selected_cities)]
    if selected_gender:
        filtered = filtered[filtered["Gender"] == selected_gender]
    if start_date:
        filtered = filtered[
            filtered["Last_Purchase_Date"] >= pd.to_datetime(start_date)
        ]
    if end_date:
        inclusive_end = pd.to_datetime(end_date) + pd.Timedelta(days=1)
        filtered = filtered[filtered["Last_Purchase_Date"] < inclusive_end]

    amounts = filtered["Purchase_Amount"].dropna()
    feedback = filtered["Feedback_Score"].dropna()
    revenue = amounts.sum()
    count = len(filtered)
    average_purchase = amounts.mean()
    average_feedback = feedback.mean()

    if filtered.empty:
        no_data = empty_figure("No records match these filters.")
        return (
            format_inr(revenue),
            f"{count:,}",
            format_inr(average_purchase) if pd.notna(average_purchase) else "—",
            f"{average_feedback:.1f} / 10"
            if pd.notna(average_feedback)
            else "—",
            no_data,
            no_data,
            no_data,
            no_data,
        )

    dated_sales = filtered.dropna(subset=["Last_Purchase_Date"])
    if dated_sales.empty:
        trend = empty_figure("No dated purchases in this selection.")
    else:
        monthly = (
            dated_sales.assign(
                Month=dated_sales["Last_Purchase_Date"].dt.to_period("M").dt.to_timestamp()
            )
            .groupby("Month", as_index=False)["Purchase_Amount"]
            .sum()
        )
        trend = px.area(
            monthly,
            x="Month",
            y="Purchase_Amount",
            markers=True,
            color_discrete_sequence=[COLORS["blue"]],
            labels={"Month": "", "Purchase_Amount": "Purchase value (INR)"},
        )
        trend.update_traces(
            line=dict(width=3),
            fillcolor="rgba(67, 97, 238, 0.12)",
            hovertemplate="%{x|%b %Y}<br>₹%{y:,.0f}<extra></extra>",
        )
        trend.update_yaxes(tickprefix="₹", tickformat=",.0f")
        base_figure(trend)

    city_sales = (
        filtered.groupby("City", as_index=False)["Purchase_Amount"]
        .sum()
        .sort_values("Purchase_Amount", ascending=True)
    )
    city_fig = px.bar(
        city_sales,
        x="Purchase_Amount",
        y="City",
        orientation="h",
        color_discrete_sequence=[COLORS["blue"]],
        labels={"City": "", "Purchase_Amount": "Purchase value (INR)"},
    )
    city_fig.update_traces(
        hovertemplate="%{y}<br>₹%{x:,.0f}<extra></extra>",
        marker_line_width=0,
    )
    city_fig.update_xaxes(tickprefix="₹", tickformat=",.0f")
    base_figure(city_fig)

    gender_counts = filtered["Gender"].value_counts().rename_axis("Gender").reset_index(
        name="Records"
    )
    gender_fig = px.pie(
        gender_counts,
        names="Gender",
        values="Records",
        hole=0.68,
        color="Gender",
        color_discrete_sequence=[COLORS["blue"], COLORS["teal"], COLORS["purple"]],
    )
    gender_fig.update_traces(
        textposition="inside",
        textinfo="percent",
        hovertemplate="%{label}<br>%{value:,} records (%{percent})<extra></extra>",
        marker=dict(line=dict(color="#ffffff", width=3)),
    )
    base_figure(gender_fig)

    feedback_counts = (
        feedback.round()
        .astype(int)
        .value_counts()
        .reindex(range(1, 11), fill_value=0)
        .rename_axis("Score")
        .reset_index(name="Records")
    )
    feedback_fig = px.bar(
        feedback_counts,
        x="Score",
        y="Records",
        color_discrete_sequence=[COLORS["teal"]],
        labels={"Score": "Feedback score (out of 10)", "Records": "Sales records"},
    )
    feedback_fig.update_traces(
        hovertemplate="Score %{x}/10<br>%{y:,} records<extra></extra>",
        marker_line_width=0,
    )
    feedback_fig.update_xaxes(dtick=1)
    base_figure(feedback_fig)

    return (
        format_inr(revenue),
        f"{count:,}",
        format_inr(average_purchase) if pd.notna(average_purchase) else "—",
        f"{average_feedback:.1f} / 10" if pd.notna(average_feedback) else "—",
        trend,
        city_fig,
        gender_fig,
        feedback_fig,
    )


if __name__ == "__main__":
    app.run(debug=False)
