from dash import html

F1_RED = "#E10600"
CARD_BG = "#1A1A2E"

layout = html.Div(
    [
        html.H1("Standings", style={"color": F1_RED, "fontSize": "22px"}),
        html.P(
            "Season standings & driver performance overview",
            style={"color": "#555", "fontSize": "12px", "marginBottom": "28px"},
        ),
        # Placeholder — will be replaced with real charts
        html.Div(
            "Championship points bar chart will go here",
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
            "Standings table will go here",
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
            "Points progression line chart will go here",
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
