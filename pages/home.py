from dash import html

F1_RED = "#E10600"
CARD_BG = "#1A1A2E"


def _nav_card(title, href, description):
    return html.A(
        html.Div(
            [
                html.H3(title, style={"color": F1_RED, "fontSize": "18px", "marginBottom": "8px"}),
                html.P(description, style={"color": "#888", "fontSize": "12px", "margin": 0}),
            ],
            style={
                "background": CARD_BG,
                "border": "1px solid #2a2a40",
                "borderRadius": "12px",
                "padding": "28px",
                "flex": "1",
                "minWidth": "250px",
            },
        ),
        href=href,
        style={"textDecoration": "none", "flex": "1", "minWidth": "250px"},
    )


layout = html.Div(
    [
        html.H1(
            "\U0001F3CE\uFE0F Welcome to the F1 Dashboard",
            style={"color": F1_RED, "fontSize": "28px", "marginBottom": "8px"},
        ),
        html.P(
            "Interactive Formula 1 data analysis — explore standings, race performance, and head-to-head comparisons.",
            style={"color": "#888", "fontSize": "14px", "marginBottom": "36px"},
        ),
        html.Div(
            style={"display": "flex", "gap": "16px", "flexWrap": "wrap"},
            children=[
                _nav_card("Standings", "/standings", "View driver & constructor championship tables and points progression."),
                _nav_card("Race Analysis", "/race-analysis", "Dive into lap times, position changes, tyre strategies and pit stops."),
                _nav_card("Compare", "/compare", "Head-to-head driver comparison with lap-time overlays and deltas."),
            ],
        ),
    ],
    style={"maxWidth": "1200px", "margin": "0 auto"},
)
