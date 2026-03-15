from dash import html, dcc, Input, Output, ALL, MATCH

from app import app
from data_loader import (
    seasons,
    filter_laps, filter_results, get_races, get_color_map
)
from visualisation.lap_times import plot_lap_times, lap_times_layout, _empty_fig

# ── STYLES ────────────────────────────────────────────────────────
F1_RED  = "#E10600"
CARD_BG = "#1A1A2E"
BORDER  = "#2a2a40"

DD_STYLE = {
    "backgroundColor": "#1E1E2E",
    "color":           "#000",
    "border":          f"1px solid {BORDER}",
    "borderRadius":    "6px"
}

LABEL_STYLE = {
    "color":         "#888",
    "fontSize":      "11px",
    "textTransform": "uppercase",
    "letterSpacing": "1px",
    "marginBottom":  "6px",
    "display":       "block"
}

CARD_STYLE = {
    "background":   CARD_BG,
    "border":       f"1px solid {BORDER}",
    "borderRadius": "12px",
    "padding":      "16px",
    "marginBottom": "16px",
}

# ── LAYOUT ────────────────────────────────────────────────────────
layout = html.Div(
    style={"maxWidth": "1200px", "margin": "0 auto"},
    children=[

        html.H1("Race Analysis", style={"color": F1_RED, "fontSize": "22px"}),
        html.P(
            "Lap times, positions, tyres, and pit stops — all in one place",
            style={"color": "#555", "fontSize": "12px", "marginBottom": "28px"},
        ),

        # ── GLOBAL FILTERS ────────────────────────────────────────
        html.Div(
            style={"display": "flex", "gap": "20px", "marginBottom": "24px",
                   "flexWrap": "wrap", "alignItems": "flex-end"},
            children=[
                html.Div([
                    html.Label("Season", style=LABEL_STYLE),
                    dcc.Dropdown(
                        id="ra-season-dd",
                        options=[{"label": str(s), "value": s} for s in seasons],
                        value=seasons[0] if seasons else None,
                        clearable=False,
                        style={**DD_STYLE, "width": "110px"}
                    )
                ]),
                html.Div([
                    html.Label("Session", style=LABEL_STYLE),
                    dcc.Dropdown(
                        id="ra-session-dd",
                        options=[
                            {"label": "Race",       "value": "Race"},
                            {"label": "Qualifying", "value": "Qualifying"}
                        ],
                        value="Race",
                        clearable=False,
                        style={**DD_STYLE, "width": "140px"}
                    )
                ]),
                html.Div([
                    html.Label("Grand Prix", style=LABEL_STYLE),
                    dcc.Dropdown(
                        id="ra-gp-dd",
                        clearable=False,
                        style={**DD_STYLE, "width": "260px"}
                    )
                ]),
            ]
        ),

        dcc.Store(id="ra-color-map-store"),

        # ── LAP TIMES CHART ───────────────────────────────────────
        html.Div(style=CARD_STYLE, children=[
            html.Div(id="lap-times-container")
        ]),

        # ── PLACEHOLDER CHARTS ────────────────────────────────────
        html.Div(
            "Position changes chart will go here",
            style={**CARD_STYLE, "color": "#444", "textAlign": "center",
                   "padding": "40px"},
        ),
        html.Div(
            style={"display": "flex", "gap": "16px"},
            children=[
                html.Div(
                    "Tyre strategy chart will go here",
                    style={**CARD_STYLE, "flex": "1", "color": "#444",
                           "textAlign": "center", "padding": "40px",
                           "marginBottom": "0"},
                ),
                html.Div(
                    "Pit stops chart will go here",
                    style={**CARD_STYLE, "flex": "1", "color": "#444",
                           "textAlign": "center", "padding": "40px",
                           "marginBottom": "0"},
                ),
            ],
        ),
    ]
)

# ── CALLBACKS ─────────────────────────────────────────────────────

@app.callback(
    Output("ra-gp-dd", "options"),
    Output("ra-gp-dd", "value"),
    Input("ra-season-dd", "value"),
    Input("ra-session-dd", "value")
)
def update_gp(season, session):
    races   = get_races(season, session)
    options = [{"label": r, "value": r} for r in races]
    return options, races[0] if races else None


@app.callback(
    Output("ra-color-map-store", "data"),
    Input("ra-season-dd", "value"),
    Input("ra-gp-dd", "value"),
    Input("ra-session-dd", "value")
)
def update_color_map(season, gp, session):
    if not gp: return {}
    return get_color_map(season, gp, session)


@app.callback(
    Output("lap-times-container", "children"),
    Input("ra-season-dd", "value"),
    Input("ra-gp-dd", "value"),
    Input("ra-session-dd", "value"),
    Input("ra-color-map-store", "data")
)
def render_lap_times(season, gp, session, color_map):
    if not gp:
        return html.Div("Select a Grand Prix",
                        style={"color": "#666", "padding": "40px",
                               "textAlign": "center"})
    laps_df = filter_laps(season, gp, session)
    res_df  = filter_results(season, gp)
    return lap_times_layout(laps_df, res_df, session, color_map or {})


@app.callback(
    Output("lap-chart", "figure"),
    Input("ra-season-dd", "value"),
    Input("ra-gp-dd", "value"),
    Input("ra-session-dd", "value"),
    Input({"type": "driver-btn", "index": ALL}, "n_clicks"),
    Input({"type": "driver-btn", "index": ALL}, "id"),
    Input("ra-color-map-store", "data")
)
def update_chart(season, gp, session, n_clicks_list, ids, color_map):
    if not gp:
        return _empty_fig("Select a Grand Prix")
    selected = [
        btn["index"]
        for btn, n in zip(ids, n_clicks_list)
        if n and n % 2 == 1
    ]
    laps_df = filter_laps(season, gp, session)
    return plot_lap_times(
        df=laps_df,
        session_type=session,
        selected_drivers=selected or None,
        color_map=color_map or {}
    )


@app.callback(
    Output({"type": "driver-btn", "index": MATCH}, "style"),
    Input({"type": "driver-btn", "index": MATCH}, "n_clicks"),
)
def toggle_button_style(n_clicks):
    active = n_clicks and n_clicks % 2 == 1
    return {
        "backgroundColor": "#1E1E2E"        if active else "rgba(0,0,0,0)",
        "color":           "#FFFFFF"         if active else "#666",
        "border":          "1px solid #555" if active else "1px solid #333",
        "borderRadius":    "20px",
        "padding":         "5px 14px",
        "fontSize":        "12px",
        "fontFamily":      "'Titillium Web', Arial, sans-serif",
        "fontWeight":      "700",
        "cursor":          "pointer",
        "letterSpacing":   "1px",
    }