from dash import html

F1_RED = "#E10600"
CARD_BG = "#1A1A2E"

layout = html.Div(
    [
        html.H1("Compare", style={"color": F1_RED, "fontSize": "22px"}),
        html.P(
            "Head-to-head driver comparison — lap times, deltas, and filtered analysis",
            style={"color": "#555", "fontSize": "12px", "marginBottom": "28px"},
        ),
        html.Div(
            "Lap time overlay chart will go here",
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
            "Time delta chart will go here",
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
            "Filtered lap times chart will go here",
            style={
                "background": CARD_BG,
                "border": "1px dashed #2a2a40",
                "borderRadius": "12px",
                "padding": "40px",
                "color": "#444",
                "textAlign": "center",
            },
        ),
    ],
    style={"maxWidth": "1200px", "margin": "0 auto"},
)
