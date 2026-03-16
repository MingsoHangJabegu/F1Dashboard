from dash import html
from dash.dependencies import Input, Output

from app import app
from components.global_filter import create_global_filter
from pages.standings import build_standings_sections

F1_RED = "#E10600"


layout = html.Div(
    [
        html.Div(
           
        ),
        html.Div(
            [
                html.Div(
                    create_global_filter(compact=True),
                    style={
                        "position": "sticky",
                        "top": "20px",
                        "height": "calc(100vh - 40px)",
                        "overflowY": "auto",
                        "overflowX": "hidden",
                        "display": "flex",
                        "alignItems": "flex-start",
                        "justifyContent": "center",
                        "paddingRight": "6px",
                    },
                    className="home-sidebar-scroll",
                ),
                html.Div(id="home-standings-content", style={"minWidth": 0}),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "300px minmax(0, 1fr)",
                "gap": "24px",
                "alignItems": "start",
            },
        ),
    ],
    style={"maxWidth": "1320px", "margin": "0 auto"},
)


@app.callback(
    Output("home-standings-content", "children"),
    Input("global-season-dropdown", "value"),
)
def update_home_content(season):
    return build_standings_sections(season, include_summary=True, include_progression=False)
