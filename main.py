from dash import html, dcc, Input, Output

from app import app
from components.navbar import navbar
from pages import home, standings, race_analysis, compare

# ── Colour tokens ────────────────────────────────────────────────────
BODY_BG = "#111119"

# ── App layout ───────────────────────────────────────────────────────
app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        navbar,
        html.Div(id="page-content", style={"padding": "28px 30px 60px"}),
    ],
    style={"backgroundColor": BODY_BG, "minHeight": "100vh"},
)


# ── URL routing ──────────────────────────────────────────────────────
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def display_page(pathname):
    if pathname == "/standings":
        return standings.layout
    if pathname == "/race-analysis":
        return race_analysis.layout
    if pathname == "/compare":
        return compare.layout
    return home.layout


# ── Run ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)

