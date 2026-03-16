from dash import ALL, Input, Output, State, callback_context, dcc, html

from app import app
from data_loader import (
    get_all_seasons,
    get_available_sessions_for_season,
    get_driver_options,
    get_events_for_season_and_session,
)

F1_RED = "#E10600"
CARD_BG = "#16161C"
SURFACE_BG = "#2A2A2D"
SURFACE_BORDER = "#54545A"
TEXT_PRIMARY = "#F4F4F5"
TEXT_MUTED = "#A1A1AA"
BUTTON_DISABLED = "#8B8B92"
DEFAULT_DRIVER_COLOR = "#4F8CFF"

FILTER_IDS = {
    "season": "global-season-dropdown",
    "circuit": "global-circuit-dropdown",
    "session": "global-session-dropdown",
    "drivers": "global-selected-drivers",
    "compare": "global-compare-button",
}


def _build_dropdown(dropdown_id, options, value, placeholder, compact=False):
    return dcc.Dropdown(
        id=dropdown_id,
        options=options,
        value=value,
        clearable=False,
        searchable=False,
        placeholder=placeholder,
        className="global-filter-dropdown",
        style={
            "backgroundColor": SURFACE_BG,
            "color": "#070707",
            "border": f"1px solid {SURFACE_BORDER}",
            "borderRadius": "14px" if compact else "16px",
        },
    )


def _build_driver_button(driver, selected_drivers, compact=False):
    driver_code = driver["value"]
    team_color = f"#{driver['team_color']}" if driver.get("team_color") else DEFAULT_DRIVER_COLOR
    is_selected = driver_code in selected_drivers

    return html.Button(
        driver["label"],
        id={"type": "global-driver-chip", "driver": driver_code},
        n_clicks=0,
        title=f"{driver.get('full_name', driver_code)} | {driver.get('team_name', 'Unknown team')}",
        style={
            "minWidth": "62px" if compact else "74px",
            "height": "46px" if compact else "54px",
            "padding": "0 14px" if compact else "0 18px",
            "borderRadius": "12px" if compact else "14px",
            "border": f"1.5px solid {team_color}",
            "background": f"rgba(255,255,255,0.08)" if is_selected else "transparent",
            "color": team_color,
            "fontSize": "16px" if compact else "18px",
            "letterSpacing": "0.5px",
            "cursor": "pointer",
            "transition": "all 0.2s ease",
        },
    )


def _default_filter_state():
    seasons = get_all_seasons()
    default_season = seasons[0] if seasons else None

    sessions = get_available_sessions_for_season(default_season) if default_season else []
    default_session = "Qualifying" if "Qualifying" in sessions else (sessions[0] if sessions else None)

    circuits = (
        get_events_for_season_and_session(default_season, default_session)
        if default_season and default_session
        else []
    )
    default_circuit = circuits[0]["EventName"] if circuits else None

    drivers = (
        get_driver_options(default_season, default_circuit, default_session)
        if default_season and default_circuit and default_session
        else []
    )
    default_drivers = [driver["value"] for driver in drivers[:2]]

    return {
        "seasons": seasons,
        "season": default_season,
        "sessions": sessions,
        "session": default_session,
        "circuits": circuits,
        "circuit": default_circuit,
        "drivers": drivers,
        "selected_drivers": default_drivers,
    }


def create_global_filter(compact=False):
    defaults = _default_filter_state()

    return html.Div(
        [
            dcc.Store(id=FILTER_IDS["drivers"], data=defaults["selected_drivers"]),
            html.Div(
                [
                    _build_dropdown(
                        FILTER_IDS["season"],
                        [{"label": str(season), "value": season} for season in defaults["seasons"]],
                        defaults["season"],
                        "Select season",
                        compact=compact,
                    ),
                    _build_dropdown(
                        FILTER_IDS["circuit"],
                        [
                            {"label": circuit["EventName"], "value": circuit["EventName"]}
                            for circuit in defaults["circuits"]
                        ],
                        defaults["circuit"],
                        "Select race",
                        compact=compact,
                    ),
                    _build_dropdown(
                        FILTER_IDS["session"],
                        [{"label": session, "value": session} for session in defaults["sessions"]],
                        defaults["session"],
                        "Select session",
                        compact=compact,
                    ),
                ],
                style={
                    "display": "grid",
                    "gap": "10px" if compact else "12px",
                    "marginBottom": "14px" if compact else "18px",
                },
            ),
            html.Div(
                id="global-driver-chip-grid",
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(4, minmax(0, 1fr))",
                    "gap": "8px" if compact else "10px",
                    "marginBottom": "14px" if compact else "18px",
                },
                children=[
                    _build_driver_button(driver, defaults["selected_drivers"], compact=compact)
                    for driver in defaults["drivers"]
                ],
            ),
            html.Button(
                "COMPARE FASTEST LAPS",
                id=FILTER_IDS["compare"],
                n_clicks=0,
                disabled=len(defaults["selected_drivers"]) < 2,
                style={
                    "width": "100%",
                    "height": "48px" if compact else "54px",
                    "border": "none",
                    "borderRadius": "12px" if compact else "14px",
                    "background": BUTTON_DISABLED if len(defaults["selected_drivers"]) < 2 else "#D0D0D4",
                    "color": "#23232B",
                    "fontSize": "14px" if compact else "16px",
                    "fontWeight": "700",
                    "fontColor": "#23232B",
                    "letterSpacing": "0.5px",
                    "cursor": "pointer",
                },
            ),
        ],
        style={
            "maxWidth": "300px" if compact else "420px",
            "margin": "0",
            "padding": "22px 20px 20px" if compact else "34px 36px 28px",
            "backgroundColor": CARD_BG,
            "borderRadius": "20px" if compact else "24px",
            "boxShadow": "0 22px 45px rgba(0, 0, 0, 0.28)",
            "border": "1px solid rgba(255, 255, 255, 0.06)",
        },
    )


global_filter = create_global_filter()


@app.callback(
    [
        Output(FILTER_IDS["session"], "options"),
        Output(FILTER_IDS["session"], "value"),
        Output(FILTER_IDS["circuit"], "options"),
        Output(FILTER_IDS["circuit"], "value"),
    ],
    Input(FILTER_IDS["season"], "value"),
    [
        State(FILTER_IDS["session"], "value"),
        State(FILTER_IDS["circuit"], "value"),
    ],
)
def update_filter_dropdowns(selected_season, current_session, current_circuit):
    if not selected_season:
        return [], None, [], None

    sessions = get_available_sessions_for_season(selected_season)
    next_session = current_session if current_session in sessions else None
    if not next_session and sessions:
        next_session = "Qualifying" if "Qualifying" in sessions else sessions[0]

    circuits = get_events_for_season_and_session(selected_season, next_session) if next_session else []
    circuit_options = [
        {"label": circuit["EventName"], "value": circuit["EventName"]}
        for circuit in circuits
    ]
    next_circuit = current_circuit if any(c["EventName"] == current_circuit for c in circuits) else None
    if not next_circuit and circuits:
        next_circuit = circuits[0]["EventName"]

    return (
        [{"label": session, "value": session} for session in sessions],
        next_session,
        circuit_options,
        next_circuit,
    )


@app.callback(
    [
        Output("global-driver-chip-grid", "children"),
        Output(FILTER_IDS["drivers"], "data"),
    ],
    [
        Input(FILTER_IDS["season"], "value"),
        Input(FILTER_IDS["circuit"], "value"),
        Input(FILTER_IDS["session"], "value"),
        Input({"type": "global-driver-chip", "driver": ALL}, "n_clicks"),
    ],
    [State(FILTER_IDS["drivers"], "data"), State("url", "pathname")],
)
def update_driver_selection(
    selected_season,
    selected_circuit,
    selected_session,
    _clicks,
    selected_drivers,
    pathname,
):
    selected_drivers = selected_drivers or []
    compact = pathname == "/"

    if not selected_season or not selected_circuit or not selected_session:
        return [], []

    drivers = get_driver_options(selected_season, selected_circuit, selected_session)
    valid_driver_codes = [driver["value"] for driver in drivers]

    triggered = callback_context.triggered[0]["prop_id"] if callback_context.triggered else ""
    if '"type":"global-driver-chip"' in triggered:
        triggered_driver = triggered.split('"driver":"', 1)[1].split('"', 1)[0]
        if triggered_driver in selected_drivers:
            selected_drivers = [driver for driver in selected_drivers if driver != triggered_driver]
        elif triggered_driver in valid_driver_codes:
            selected_drivers = [*selected_drivers[:1], triggered_driver]
    else:
        selected_drivers = [driver for driver in selected_drivers if driver in valid_driver_codes]
        if len(selected_drivers) < 2:
            for driver_code in valid_driver_codes:
                if driver_code not in selected_drivers:
                    selected_drivers.append(driver_code)
                if len(selected_drivers) == 2:
                    break

    chip_buttons = [
        _build_driver_button(driver, selected_drivers, compact=compact) for driver in drivers
    ]
    return chip_buttons, selected_drivers[:2]


@app.callback(
    [
        Output(FILTER_IDS["compare"], "disabled"),
        Output(FILTER_IDS["compare"], "style"),
    ],
    Input(FILTER_IDS["drivers"], "data"),
)
def update_compare_button(selected_drivers):
    selected_drivers = selected_drivers or []
    is_disabled = len(selected_drivers) < 2
    button_style = {
        "width": "100%",
        "height": "54px",
        "border": "none",
        "borderRadius": "14px",
        "background": BUTTON_DISABLED if is_disabled else "#D0D0D4",
        "color": "#23232B",
        "fontSize": "16px",
        "fontWeight": "700",
        "letterSpacing": "0.5px",
        "cursor": "not-allowed" if is_disabled else "pointer",
        "opacity": 0.7 if is_disabled else 1,
    }
    return is_disabled, button_style


@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    Input(FILTER_IDS["compare"], "n_clicks"),
    State(FILTER_IDS["drivers"], "data"),
    prevent_initial_call=True,
)
def open_compare_page(n_clicks, selected_drivers):
    if not n_clicks or len(selected_drivers or []) < 2:
        return "/"
    return "/compare"
