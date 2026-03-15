import dash_bootstrap_components as dbc
from dash import html

# ── Colour tokens ────────────────────────────────────────────────────
F1_RED = "#E10600"
NAV_BG = "#1A1A2E"

# ── Navigation bar ───────────────────────────────────────────────────
navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.Span(
                            "\U0001F3CE\uFE0F F1 Dashboard",
                            style={
                                "color": F1_RED,
                                "fontSize": "18px",
                                "fontWeight": "bold",
                                "marginRight": "40px",
                            },
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        dbc.Nav(
                            [
                                dbc.NavLink("Home", href="/", id="nav-home", active="exact"),
                                dbc.NavLink("Standings", href="/standings", id="nav-standings", active="exact"),
                                dbc.NavLink("Race Analysis", href="/race-analysis", id="nav-race", active="exact"),
                                dbc.NavLink("Compare", href="/compare", id="nav-compare", active="exact"),
                            ],
                            navbar=True,
                        ),
                    ),
                ],
                align="center",
                className="g-0 flex-nowrap",
            ),
        ],
        fluid=True,
    ),
    color=NAV_BG,
    dark=True,
    style={"borderBottom": f"2px solid {F1_RED}"},
)
