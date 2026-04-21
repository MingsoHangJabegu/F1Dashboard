"""
Position Changes – Upgraded Bump Chart
=======================================
Features:
  - Top 10 / Bottom 10 toggle
  - Driver name labels at lap 1 and final lap
  - Highlighted lines for selected drivers, others dimmed
  - Pit stop markers shown as dots on the line
  - Smooth curved lines using spline interpolation
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import make_interp_spline

# ── CONSTANTS ──────────────────────────────────────────────────────
CHART_BG = "#15151E"
CARD_BG  = "#1A1A2E"

# Tyre compound colours (official F1 colours)
TYRE_COLORS = {
    "SOFT":        "#E8002D",
    "MEDIUM":      "#FFF200",
    "HARD":        "#FFFFFF",
    "INTERMEDIATE":"#39B54A",
    "WET":         "#0067FF",
    "UNKNOWN":     "#888888",
}

DASH_STYLES = ["solid", "dot", "dash", "longdash"]


# ── HELPERS ────────────────────────────────────────────────────────

def _empty_fig(message="No data available"):
    fig = go.Figure()
    fig.add_annotation(
        text=message, x=0.5, y=0.5,
        xref="paper", yref="paper",
        showarrow=False,
        font=dict(color="#888", size=14),
    )
    fig.update_layout(
        plot_bgcolor=CHART_BG, paper_bgcolor=CHART_BG,
        height=520, margin=dict(l=20, r=20, t=40, b=20),
    )
    return fig


def _smooth(x, y, points=300):
    """
    Return smoothed (x_new, y_new) using cubic spline interpolation.
    Falls back to original data if not enough points.
    """
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    if len(x) < 4:
        return x, y
    try:
        x_new  = np.linspace(x.min(), x.max(), points)
        spline = make_interp_spline(x, y, k=3)
        y_new  = spline(x_new)
        # Clip to valid position range
        y_new  = np.clip(y_new, 1, 20)
        return x_new, y_new
    except Exception:
        return x, y


def _get_color(color_map, driver):
    color = color_map.get(driver, "#888888")
    if not color or str(color).lower() in ("nan", "none", ""):
        return "#888888"
    c = str(color).strip()
    return c if c.startswith("#") else f"#{c}"


def _get_pit_stops(df, driver):
    """Return list of (lap_number, tyre_compound) for each pit stop."""
    d = df[df["Driver"] == driver].copy()
    pits = d[d["PitInTime"].notna()][["LapNumber", "Compound"]].dropna()
    return list(zip(pits["LapNumber"].astype(int), pits["Compound"].fillna("UNKNOWN")))


# ── MAIN CHART FUNCTION ────────────────────────────────────────────

def plot_position_changes(
    df,
    color_map=None,
    selected_drivers=None,
    show_group="top10",       # "top10" or "bottom10"
):
    """
    Bump chart showing race position changes lap by lap.

    Parameters
    ----------
    df               : laps dataframe filtered by season + race (Race session)
    color_map        : dict driver abbreviation -> hex colour
    selected_drivers : list of drivers to highlight (None = all highlighted)
    show_group       : 'top10' or 'bottom10'
    """
    color_map = color_map or {}

    if df is None or df.empty:
        return _empty_fig("No data available")

    df = df.copy()
    df["Position"]  = pd.to_numeric(df["Position"],  errors="coerce")
    df["LapNumber"] = pd.to_numeric(df["LapNumber"], errors="coerce")
    df = df[df["Position"].notna() & df["LapNumber"].notna()]

    if df.empty:
        return _empty_fig("No position data found for this race")

    # ── Get finishing order ────────────────────────────────────────
    final_lap = df["LapNumber"].max()
    finishing = (
        df[df["LapNumber"] == final_lap]
        .sort_values("Position")
        .drop_duplicates("Driver")[["Driver", "Position"]]
    )

    top10_drivers    = finishing.head(10)["Driver"].tolist()
    bottom10_drivers = finishing.tail(10)["Driver"].tolist()

    display_drivers = top10_drivers if show_group == "top10" else bottom10_drivers

    # Track used colours to detect teammates
    seen_colors = {}
    fig = go.Figure()

    for driver in display_drivers:
        d = df[df["Driver"] == driver].sort_values("LapNumber")
        if d.empty:
            continue

        color      = _get_color(color_map, driver)
        is_selected = (selected_drivers is None) or (driver in selected_drivers)
        opacity    = 1.0 if is_selected else 0.18
        line_width = 3.0 if is_selected else 1.5

        # Teammate dash fix
        dash = DASH_STYLES[seen_colors.get(color, 0) % len(DASH_STYLES)]
        seen_colors[color] = seen_colors.get(color, 0) + 1

        x_raw = d["LapNumber"].values
        y_raw = d["Position"].values

        # ── Smooth curved line ─────────────────────────────────────
        x_smooth, y_smooth = _smooth(x_raw, y_raw)

        # Main smooth line
        fig.add_trace(go.Scatter(
            x=x_smooth,
            y=y_smooth,
            mode="lines",
            name=driver,
            line=dict(color=color, width=line_width,
                      dash=dash, shape="spline"),
            opacity=opacity,
            showlegend=True,
            hoverinfo="skip",
        ))

        # Invisible hover trace on actual data points
        finishing_pos = int(d[d["LapNumber"] == final_lap]["Position"].values[0]) \
            if not d[d["LapNumber"] == final_lap].empty else "?"
        start_pos = int(d[d["LapNumber"] == d["LapNumber"].min()]["Position"].values[0])

        fig.add_trace(go.Scatter(
            x=x_raw,
            y=y_raw,
            mode="markers",
            name=driver,
            marker=dict(size=6, color=color, opacity=0),
            opacity=opacity,
            showlegend=False,
            hovertemplate=(
                f"<b>{driver}</b><br>"
                "Lap: %{x}<br>"
                "Position: P%{y}<br>"
                f"Started: P{start_pos} → Finished: P{finishing_pos}"
                "<extra></extra>"
            ),
        ))

        # ── Driver name labels at start and finish ─────────────────
        if is_selected or selected_drivers is None:
            start_pos_val = float(d[d["LapNumber"] == d["LapNumber"].min()]["Position"].values[0])
            end_pos_val   = float(d[d["LapNumber"] == final_lap]["Position"].values[0]) \
                if not d[d["LapNumber"] == final_lap].empty else float(y_raw[-1])

            # Label at lap 1
            fig.add_annotation(
                x=float(d["LapNumber"].min()) - 0.3,
                y=start_pos_val,
                text=f"<b>{driver}</b>",
                showarrow=False,
                font=dict(color=color, size=10,
                          family="'Titillium Web', Arial, sans-serif"),
                xanchor="right",
                opacity=opacity,
            )

            # Label at final lap
            fig.add_annotation(
                x=float(final_lap) + 0.3,
                y=end_pos_val,
                text=f"<b>{driver}</b>",
                showarrow=False,
                font=dict(color=color, size=10,
                          family="'Titillium Web', Arial, sans-serif"),
                xanchor="left",
                opacity=opacity,
            )

        # ── Pit stop markers ───────────────────────────────────────
        pit_stops = _get_pit_stops(df, driver)
        for pit_lap, compound in pit_stops:
            pit_row = d[d["LapNumber"] == pit_lap]
            if pit_row.empty:
                continue
            pit_pos = float(pit_row["Position"].values[0])
            tyre_color = TYRE_COLORS.get(compound.upper(), "#888888")

            fig.add_trace(go.Scatter(
                x=[pit_lap],
                y=[pit_pos],
                mode="markers",
                name=f"{driver} pit ({compound})",
                marker=dict(
                    size=10,
                    color=tyre_color,
                    symbol="circle",
                    line=dict(color=color, width=2),
                ),
                opacity=opacity,
                showlegend=False,
                hovertemplate=(
                    f"<b>{driver} — Pit Stop</b><br>"
                    f"Lap: {pit_lap}<br>"
                    f"New Tyre: {compound}<br>"
                    f"Position: P{int(pit_pos)}"
                    "<extra></extra>"
                ),
            ))

    # ── Tyre legend annotations ────────────────────────────────────
    tyre_x   = float(final_lap) + 1
    tyre_y   = 18
    fig.add_annotation(
        x=tyre_x, y=tyre_y - 0.3,
        text="⬤ Pit Stop Tyres:",
        showarrow=False,
        font=dict(color="#666", size=9),
        xanchor="left",
    )
    for j, (compound, tcol) in enumerate(
        [("SOFT","#E8002D"), ("MEDIUM","#FFF200"),
         ("HARD","#FFFFFF"), ("INTER","#39B54A")]
    ):
        fig.add_annotation(
            x=tyre_x, y=tyre_y + 1.2 + j * 1.1,
            text=f"⬤ {compound}",
            showarrow=False,
            font=dict(color=tcol, size=9),
            xanchor="left",
        )

    max_lap   = int(final_lap)
    group_lbl = "Top 10" if show_group == "top10" else "Bottom 10"

    fig.update_layout(
        title=dict(
            text=f"Race Position Changes — {group_lbl}  "
                 f"<i style='font-size:12px;color:#666'>"
                 f"(coloured dots = pit stops)</i>",
            font=dict(color="#ffffff", size=17,
                      family="'Titillium Web', Arial, sans-serif"),
            x=0.5,
            pad=dict(t=10),
        ),
        plot_bgcolor=CHART_BG,
        paper_bgcolor=CHART_BG,
        font=dict(color="#CCCCCC",
                  family="'Titillium Web', Arial, sans-serif"),
        xaxis=dict(
            title="Lap Number",
            range=[-1, max_lap + 5],
            gridcolor="#222230",
            gridwidth=1,
            griddash="dot",
            tickfont=dict(color="#888", size=11),
            dtick=5,
            zeroline=False,
        ),
        yaxis=dict(
            title="Position",
            autorange="reversed",
            tickvals=list(range(1, 21)),
            ticktext=[f"P{i}" for i in range(1, 21)],
            gridcolor="#222230",
            gridwidth=1,
            griddash="dot",
            tickfont=dict(color="#888", size=11),
            zeroline=False,
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#fff", size=11),
            itemclick="toggleothers",
        ),
        hovermode="closest",
        hoverlabel=dict(
            bgcolor="#1E1E2E",
            bordercolor="#444",
            font=dict(color="#fff", size=12),
        ),
        margin=dict(l=70, r=80, t=70, b=100),
        height=560,
    )

    return fig