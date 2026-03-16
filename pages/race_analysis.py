from dash import html, dcc
from dash.dependencies import Input, Output
from app import app
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data_loader import load_race_data

F1_RED = "#E10600"
CARD_BG = "#1A1A2E"


layout = html.Div(
    [
        html.H1("Race Analysis", style={"color": F1_RED, "fontSize": "22px"}),
        html.P(
            "Lap times, positions, tyres, and pit stops — all in one place",
            style={"color": "#555", "fontSize": "12px", "marginBottom": "28px"},
        ),
        html.Div(id="race-analysis-content"),
    ],
    style={"maxWidth": "1200px", "margin": "0 auto"},
)

# Callback to update content based on global filters
@app.callback(
    Output("race-analysis-content", "children"),
    [Input("global-season-dropdown", "value"),
     Input("global-circuit-dropdown", "value")]
)
def update_race_analysis_content(season, circuit):
    """
    Update race analysis content based on selected season and circuit.
    """
    if not season or not circuit:
        return html.Div(
            "Please select a season and circuit from the filters above.",
            style={"color": "#888", "textAlign": "center", "padding": "40px"}
        )
    
    # Load data for the selected race
    laps_df = load_race_data(season, circuit, 'laps')
    
    if laps_df.empty:
        return html.Div(
            f"No data available for {circuit} {season}",
            style={"color": "#888", "textAlign": "center", "padding": "40px"}
        )
    
    # Get race statistics
    total_laps = laps_df['LapNumber'].max()
    total_drivers = laps_df['Driver'].nunique()
    
    return html.Div([
        # Race Info Card
        html.Div(
            [
                html.H3(f"{circuit} {season}", style={"color": F1_RED, "marginBottom": "12px"}),
                html.Div([
                    html.Span(f"Total Laps: {total_laps}", style={"marginRight": "20px"}),
                    html.Span(f"Drivers: {total_drivers}"),
                ], style={"color": "#CCCCCC", "fontSize": "14px"}),
            ],
            style={
                "background": CARD_BG,
                "borderRadius": "12px",
                "padding": "20px",
                "marginBottom": "16px",
            },
        ),
        
        # Lap Times Chart Placeholder
        html.Div(
            [
                html.H4("Lap Times", style={"color": "#FFFFFF", "marginBottom": "16px"}),
                html.Div(
                    f"Interactive lap times chart will be displayed here",
                    style={"color": "#666", "textAlign": "center", "padding": "60px"}
                ),
            ],
            style={
                "background": CARD_BG,
                "border": "1px dashed #2a2a40",
                "borderRadius": "12px",
                "padding": "20px",
                "marginBottom": "16px",
            },
        ),
        
        # Position Changes Chart Placeholder
        html.Div(
            [
                html.H4("Position Changes", style={"color": "#FFFFFF", "marginBottom": "16px"}),
                html.Div(
                    f"Position changes throughout the race will be shown here",
                    style={"color": "#666", "textAlign": "center", "padding": "60px"}
                ),
            ],
            style={
                "background": CARD_BG,
                "border": "1px dashed #2a2a40",
                "borderRadius": "12px",
                "padding": "20px",
                "marginBottom": "16px",
            },
        ),
        
        # Tyre Strategy and Pit Stops Row
        html.Div(
            style={"display": "flex", "gap": "16px"},
            children=[
                # Tyre Strategy
                html.Div(
                    [
                        html.H4("Tyre Strategy", style={"color": "#FFFFFF", "marginBottom": "16px"}),
                        html.Div(
                            f"Tyre compound usage visualization",
                            style={"color": "#666", "textAlign": "center", "padding": "40px"}
                        ),
                    ],
                    style={
                        "flex": "1",
                        "background": CARD_BG,
                        "border": "1px dashed #2a2a40",
                        "borderRadius": "12px",
                        "padding": "20px",
                    },
                ),
                # Pit Stops
                html.Div(
                    [
                        html.H4("Pit Stops", style={"color": "#FFFFFF", "marginBottom": "16px"}),
                        html.Div(
                            f"Pit stop timing and duration",
                            style={"color": "#666", "textAlign": "center", "padding": "40px"}
                        ),
                    ],
                    style={
                        "flex": "1",
                        "background": CARD_BG,
                        "border": "1px dashed #2a2a40",
                        "borderRadius": "12px",
                        "padding": "20px",
                    },
                ),
            ],
        ),
    ])