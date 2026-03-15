from dash import html

F1_RED = "#E10600"
CARD_BG = "#1A1A2E"

layout = html.Div(
    [
        html.H1("Race Analysis", style={"color": F1_RED, "fontSize": "22px"}),
        html.P(
            "Lap times, positions, tyres, and pit stops — all in one place",
            style={"color": "#555", "fontSize": "12px", "marginBottom": "28px"},
        ),
        html.Div(
            "Lap times chart will go here",
            style={
                "background": CARD_BG,
                "border": "1px dashed #2a2a40",
                "borderRadius": "12px",
                "padding": "40px",
                "color": "#444",
                "textAlign": "center",
                "marginBottom": "16px",
            },
        ),
        html.Div(
            "Position changes chart will go here",
            style={
                "background": CARD_BG,
                "border": "1px dashed #2a2a40",
                "borderRadius": "12px",
                "padding": "40px",
                "color": "#444",
                "textAlign": "center",
                "marginBottom": "16px",
            },
        ),
        html.Div(
            style={"display": "flex", "gap": "16px"},
            children=[
                html.Div(
                    "Tyre strategy chart will go here",
                    style={
                        "flex": "1",
                        "background": CARD_BG,
                        "border": "1px dashed #2a2a40",
                        "borderRadius": "12px",
                        "padding": "40px",
                        "color": "#444",
                        "textAlign": "center",
                    },
                ),
                html.Div(
                    "Pit stops chart will go here",
                    style={
                        "flex": "1",
                        "background": CARD_BG,
                        "border": "1px dashed #2a2a40",
                        "borderRadius": "12px",
                        "padding": "40px",
                        "color": "#444",
                        "textAlign": "center",
                    },
                ),
            ],
        ),
    ],
    style={"maxWidth": "1200px", "margin": "0 auto"},
)
