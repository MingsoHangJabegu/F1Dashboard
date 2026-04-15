"""
Analysis Page 2 – Driver Performance Trend
===========================================
Answers : How has a driver's performance changed across seasons?
Purpose : Trend analysis
Charts  : Line chart (points per season) + Bar chart (wins per season)
Filters : Driver (multi-select), Season range (from / to)
"""

from dash import html, dcc, Input, Output
import pandas as pd
import plotly.graph_objects as go
import glob
import os

from app import app

# ── CONSTANTS 
F1_RED   = "#E10600"
CARD_BG  = "#1A1A2E"
BODY_BG  = "#111119"
BORDER   = "#2a2a40"
CHART_BG = "#15151E"

DD_STYLE = {
    "backgroundColor": "#1E1E2E",
    "color":           "#000",
    "border":          f"1px solid {BORDER}",
    "borderRadius":    "6px",
}

LABEL_STYLE = {
    "color":         "#888",
    "fontSize":      "11px",
    "textTransform": "uppercase",
    "letterSpacing": "1px",
    "marginBottom":  "6px",
    "display":       "block",
}

CARD_STYLE = {
    "background":   CARD_BG,
    "border":       f"1px solid {BORDER}",
    "borderRadius": "12px",
    "padding":      "20px",
    "marginBottom": "20px",
}

# ── DATA LOADING
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "race")


def _load_all_results():
    files = glob.glob(os.path.join(DATA_DIR, "race_results_*.csv"))
    if not files:
        return pd.DataFrame()
    dfs = []
    for f in files:
        try:
            dfs.append(pd.read_csv(f))
        except Exception:
            pass
    if not dfs:
        return pd.DataFrame()
    df = pd.concat(dfs, ignore_index=True)
    df["Points"]   = pd.to_numeric(df["Points"],   errors="coerce").fillna(0)
    df["Position"] = pd.to_numeric(df["Position"],  errors="coerce")
    df["Season"]   = pd.to_numeric(df["Season"],    errors="coerce")
    return df


_ALL_RESULTS = _load_all_results()


def _driver_options():
    """Return sorted list of drivers who raced in 2+ seasons."""
    if _ALL_RESULTS.empty:
        return []
    ds = _ALL_RESULTS.groupby("Abbreviation")["Season"].nunique()
    multi = ds[ds >= 2].index.tolist()
    name_map = (
        _ALL_RESULTS[_ALL_RESULTS["Abbreviation"].isin(multi)]
        .drop_duplicates("Abbreviation")[["Abbreviation", "FullName"]]
        .set_index("Abbreviation")["FullName"]
        .to_dict()
    )
    opts = sorted(
        [{"label": f"{name_map.get(a, a)} ({a})", "value": a} for a in multi],
        key=lambda x: x["label"],
    )
    return opts


def _season_options():
    if _ALL_RESULTS.empty:
        return []
    seasons = sorted(_ALL_RESULTS["Season"].dropna().unique().astype(int))
    return [{"label": str(s), "value": s} for s in seasons]


def _get_team_color(df, abbreviation):
    """Best-effort team colour for a driver (latest season)."""
    sub = df[df["Abbreviation"] == abbreviation].sort_values("Season", ascending=False)
    if sub.empty or "TeamColor" not in sub.columns:
        return "#888888"
    raw = str(sub.iloc[0]["TeamColor"]).strip()
    if not raw or raw.lower() in ("nan", "none", ""):
        return "#888888"
    return f"#{raw.lstrip('#')}"


# ── HELPERS – FIGURE BUILDERS

def _empty_fig(message="No data available"):
    fig = go.Figure()
    fig.add_annotation(
        text=message, x=0.5, y=0.5,
        xref="paper", yref="paper",
        showarrow=False,
        font=dict(color="#888", size=14),
    )
    fig.update_layout(
        plot_bgcolor=CHART_BG,
        paper_bgcolor=CHART_BG,
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    return fig


def _build_points_line_chart(df, drivers, from_year, to_year):
    """Line chart: total points per season per driver."""
    if df.empty or not drivers:
        return _empty_fig("Select at least one driver to see the trend.")

    filtered = df[
        (df["Abbreviation"].isin(drivers)) &
        (df["Season"] >= from_year) &
        (df["Season"] <= to_year)
    ]
    if filtered.empty:
        return _empty_fig("No data for the selected filters.")

    season_pts = (
        filtered.groupby(["Abbreviation", "Season"])["Points"]
        .sum()
        .reset_index()
        .rename(columns={"Points": "TotalPoints"})
    )

    fig = go.Figure()
    for driver in drivers:
        d = season_pts[season_pts["Abbreviation"] == driver].sort_values("Season")
        if d.empty:
            continue
        color = _get_team_color(df, driver)
        full_name = (
            df[df["Abbreviation"] == driver]["FullName"]
            .dropna().iloc[0]
            if not df[df["Abbreviation"] == driver].empty else driver
        )
        fig.add_trace(go.Scatter(
            x=d["Season"],
            y=d["TotalPoints"],
            mode="lines+markers",
            name=full_name,
            line=dict(color=color, width=2.5),
            marker=dict(size=8, color=color, symbol="circle",
                        line=dict(color="#fff", width=1)),
            hovertemplate=(
                f"<b>{full_name}</b><br>"
                "Season: %{x}<br>"
                "Points: %{y}<extra></extra>"
            ),
        ))

    all_seasons = sorted(season_pts["Season"].unique().astype(int))
    fig.update_layout(
        title=dict(
            text="Championship Points per Season",
            font=dict(color="#ffffff", size=18,
                      family="'Titillium Web', Arial, sans-serif"),
            x=0.5,
        ),
        plot_bgcolor=CHART_BG,
        paper_bgcolor=CHART_BG,
        font=dict(color="#CCCCCC", family="'Titillium Web', Arial, sans-serif"),
        xaxis=dict(
            title="Season",
            tickvals=all_seasons,
            ticktext=[str(s) for s in all_seasons],
            gridcolor="#222230",
            gridwidth=1,
            griddash="dot",
            tickfont=dict(color="#888", size=11),
        ),
        yaxis=dict(
            title="Total Points",
            gridcolor="#222230",
            gridwidth=1,
            griddash="dot",
            tickfont=dict(color="#888", size=11),
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.18,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#fff", size=11),
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#1E1E2E",
            bordercolor="#444",
            font=dict(color="#fff", size=12),
        ),
        margin=dict(l=60, r=20, t=60, b=90),
        height=420,
    )
    return fig


def _build_wins_bar_chart(df, drivers, from_year, to_year):
    """Grouped bar chart: race wins per season per driver."""
    if df.empty or not drivers:
        return _empty_fig("Select at least one driver to see wins.")

    filtered = df[
        (df["Abbreviation"].isin(drivers)) &
        (df["Season"] >= from_year) &
        (df["Season"] <= to_year) &
        (df["Position"] == 1)
    ]

    all_seasons = sorted(
        df[
            (df["Abbreviation"].isin(drivers)) &
            (df["Season"] >= from_year) &
            (df["Season"] <= to_year)
        ]["Season"].dropna().unique().astype(int)
    )

    fig = go.Figure()

    for driver in drivers:
        d = (
            filtered[filtered["Abbreviation"] == driver]
            .groupby("Season")
            .size()
            .reindex(all_seasons, fill_value=0)
            .reset_index()
        )
        d.columns = ["Season", "Wins"]
        color = _get_team_color(df, driver)
        full_name = (
            df[df["Abbreviation"] == driver]["FullName"]
            .dropna().iloc[0]
            if not df[df["Abbreviation"] == driver].empty else driver
        )
        fig.add_trace(go.Bar(
            x=d["Season"],
            y=d["Wins"],
            name=full_name,
            marker=dict(
                color=color,
                line=dict(color="rgba(255,255,255,0.15)", width=1),
            ),
            hovertemplate=(
                f"<b>{full_name}</b><br>"
                "Season: %{x}<br>"
                "Wins: %{y}<extra></extra>"
            ),
        ))

    fig.update_layout(
        barmode="group",
        title=dict(
            text="Race Wins per Season",
            font=dict(color="#ffffff", size=18,
                      family="'Titillium Web', Arial, sans-serif"),
            x=0.5,
        ),
        plot_bgcolor=CHART_BG,
        paper_bgcolor=CHART_BG,
        font=dict(color="#CCCCCC", family="'Titillium Web', Arial, sans-serif"),
        xaxis=dict(
            title="Season",
            tickvals=all_seasons,
            ticktext=[str(s) for s in all_seasons],
            gridcolor="#222230",
            tickfont=dict(color="#888", size=11),
        ),
        yaxis=dict(
            title="Race Wins",
            dtick=1,
            gridcolor="#222230",
            gridwidth=1,
            griddash="dot",
            tickfont=dict(color="#888", size=11),
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.18,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#fff", size=11),
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#1E1E2E",
            bordercolor="#444",
            font=dict(color="#fff", size=12),
        ),
        margin=dict(l=60, r=20, t=60, b=90),
        height=420,
        bargap=0.15,
        bargroupgap=0.05,
    )
    return fig


def _build_summary_stats(df, drivers, from_year, to_year):
    """Build summary stat cards for the selected drivers."""
    if df.empty or not drivers:
        return html.Div()

    filtered = df[
        (df["Abbreviation"].isin(drivers)) &
        (df["Season"] >= from_year) &
        (df["Season"] <= to_year)
    ]
    if filtered.empty:
        return html.Div()

    cards = []
    for driver in drivers:
        d = filtered[filtered["Abbreviation"] == driver]
        if d.empty:
            continue
        total_pts  = int(d["Points"].sum())
        total_wins = int((d["Position"] == 1).sum())
        podiums    = int((d["Position"] <= 3).sum())
        best_season = (
            d.groupby("Season")["Points"].sum().idxmax()
            if not d.empty else "N/A"
        )
        color = _get_team_color(df, driver)
        full_name = d["FullName"].dropna().iloc[0] if not d.empty else driver

        cards.append(html.Div(
            style={
                "background":    "#15151E",
                "border":        f"1px solid {BORDER}",
                "borderLeft":    f"4px solid {color}",
                "borderRadius":  "10px",
                "padding":       "14px 18px",
                "minWidth":      "200px",
                "flex":          "1",
            },
            children=[
                html.Div(full_name, style={
                    "color": color, "fontWeight": "700",
                    "fontSize": "14px", "marginBottom": "10px",
                    "fontFamily": "'Titillium Web', Arial, sans-serif",
                }),
                html.Div([
                    html.Span("Points: ",    style={"color": "#888", "fontSize": "12px"}),
                    html.Span(str(total_pts), style={"color": "#fff", "fontWeight": "700"}),
                ], style={"marginBottom": "4px"}),
                html.Div([
                    html.Span("Wins: ",      style={"color": "#888", "fontSize": "12px"}),
                    html.Span(str(total_wins), style={"color": "#fff", "fontWeight": "700"}),
                ], style={"marginBottom": "4px"}),
                html.Div([
                    html.Span("Podiums: ",   style={"color": "#888", "fontSize": "12px"}),
                    html.Span(str(podiums),  style={"color": "#fff", "fontWeight": "700"}),
                ], style={"marginBottom": "4px"}),
                html.Div([
                    html.Span("Best Season: ", style={"color": "#888", "fontSize": "12px"}),
                    html.Span(str(best_season), style={"color": "#fff", "fontWeight": "700"}),
                ]),
            ]
        ))

    return html.Div(
        cards,
        style={"display": "flex", "flexWrap": "wrap", "gap": "12px"},
    )


# ── LAYOUT ─────────────────────────────────────────────────────────
_driver_opts = _driver_options()
_season_opts = _season_options()
_all_seasons = [o["value"] for o in _season_opts]
_min_season  = min(_all_seasons) if _all_seasons else 2018
_max_season  = max(_all_seasons) if _all_seasons else 2025

# Default: show Hamilton, Verstappen, Norris pre-selected
_default_drivers = [d["value"] for d in _driver_opts if d["value"] in ("HAM", "VER", "NOR")]

layout = html.Div(
    style={"maxWidth": "1200px", "margin": "0 auto"},
    children=[

        html.H1("Driver Performance Trend", style={"color": F1_RED, "fontSize": "22px"}),
        html.P(
            "How has a driver's performance changed across seasons? "
            "Explore points scored and race wins over time.",
            style={"color": "#555", "fontSize": "12px", "marginBottom": "28px"},
        ),

        # ── FILTERS
        html.Div(
            style={
                "display":     "flex",
                "gap":         "20px",
                "marginBottom":"24px",
                "flexWrap":    "wrap",
                "alignItems":  "flex-end",
            },
            children=[
                # Driver multi-select
                html.Div([
                    html.Label("Driver(s)", style=LABEL_STYLE),
                    dcc.Dropdown(
                        id="dpt-driver-dd",
                        options=_driver_opts,
                        value=_default_drivers,
                        multi=True,
                        placeholder="Select driver(s)…",
                        style={**DD_STYLE, "minWidth": "320px"},
                    ),
                ]),
                # From year
                html.Div([
                    html.Label("From Season", style=LABEL_STYLE),
                    dcc.Dropdown(
                        id="dpt-from-year-dd",
                        options=_season_opts,
                        value=_min_season,
                        clearable=False,
                        style={**DD_STYLE, "width": "110px"},
                    ),
                ]),
                # To year
                html.Div([
                    html.Label("To Season", style=LABEL_STYLE),
                    dcc.Dropdown(
                        id="dpt-to-year-dd",
                        options=_season_opts,
                        value=_max_season,
                        clearable=False,
                        style={**DD_STYLE, "width": "110px"},
                    ),
                ]),
            ],
        ),

        # ── SUMMARY STAT CARDS
        html.Div(
            style=CARD_STYLE,
            children=[
                html.H3("Summary", style={
                    "color": "#FFFFFF", "fontSize": "16px",
                    "marginBottom": "14px", "marginTop": "0",
                }),
                html.Div(id="dpt-summary-cards"),
            ],
        ),

        # ── POINTS LINE CHART
        html.Div(
            style=CARD_STYLE,
            children=[
                dcc.Graph(
                    id="dpt-points-line-chart",
                    config={"displayModeBar": False},
                ),
            ],
        ),

        # ── WINS BAR CHART
        html.Div(
            style=CARD_STYLE,
            children=[
                dcc.Graph(
                    id="dpt-wins-bar-chart",
                    config={"displayModeBar": False},
                ),
            ],
        ),

    ],
)


# ── CALLBACKS

@app.callback(
    Output("dpt-points-line-chart", "figure"),
    Output("dpt-wins-bar-chart",    "figure"),
    Output("dpt-summary-cards",     "children"),
    Input("dpt-driver-dd",    "value"),
    Input("dpt-from-year-dd", "value"),
    Input("dpt-to-year-dd",   "value"),
)
def update_charts(drivers, from_year, to_year):
    # Guard: ensure from <= to
    if not from_year or not to_year:
        empty = _empty_fig("Select a season range.")
        return empty, empty, html.Div()

    if from_year > to_year:
        from_year, to_year = to_year, from_year

    drivers = drivers or []

    line_fig   = _build_points_line_chart(_ALL_RESULTS, drivers, from_year, to_year)
    bar_fig    = _build_wins_bar_chart(_ALL_RESULTS,    drivers, from_year, to_year)
    stat_cards = _build_summary_stats(_ALL_RESULTS,     drivers, from_year, to_year)

    return line_fig, bar_fig, stat_cards
