import pandas as pd
import plotly.graph_objects as go


def plot_position_changes(
    df,
    color_map=None,
    selected_drivers=None,
    show_group="top10",
):
    color_map = color_map or {}

    if df is None or df.empty:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_dark",
            title="No position data available",
            paper_bgcolor="#12121c",
            plot_bgcolor="#12121c",
        )
        return fig

    data = df.copy()

    required_cols = {"Driver", "LapNumber", "Position"}
    missing = required_cols - set(data.columns)
    if missing:
        fig = go.Figure()
        fig.update_layout(
            template="plotly_dark",
            title=f"Missing columns: {', '.join(missing)}",
            paper_bgcolor="#12121c",
            plot_bgcolor="#12121c",
        )
        return fig

    data = data.dropna(subset=["Driver", "LapNumber", "Position"])
    data["LapNumber"] = pd.to_numeric(data["LapNumber"], errors="coerce")
    data["Position"] = pd.to_numeric(data["Position"], errors="coerce")
    data = data.dropna(subset=["LapNumber", "Position"])

    final_pos = (
        data.sort_values("LapNumber")
        .groupby("Driver")["Position"]
        .last()
        .sort_values()
    )

    if selected_drivers:
        drivers = selected_drivers
        title_suffix = "Highlighted Drivers"
    else:
        if show_group == "bottom10":
            drivers = final_pos.tail(10).index.tolist()
            title_suffix = "Bottom 10"
        else:
            drivers = final_pos.head(10).index.tolist()
            title_suffix = "Top 10"

    plot_df = data[data["Driver"].isin(drivers)].copy()

    fig = go.Figure()

    for driver in drivers:
        driver_df = plot_df[plot_df["Driver"] == driver].sort_values("LapNumber")

        if driver_df.empty:
            continue

        color = color_map.get(driver, None)

        fig.add_trace(
            go.Scatter(
                x=driver_df["LapNumber"],
                y=driver_df["Position"],
                mode="lines",
                name=driver,
                line=dict(width=3, color=color, shape="spline"),
                hovertemplate=(
                    f"<b>{driver}</b><br>"
                    "Lap: %{x}<br>"
                    "Position: P%{y}<extra></extra>"
                ),
            )
        )

        if "PitInTime" in driver_df.columns:
            pit_df = driver_df[driver_df["PitInTime"].notna()]
        elif "pit_event" in driver_df.columns:
            pit_df = driver_df[driver_df["pit_event"] == True]
        else:
            pit_df = pd.DataFrame()

        if not pit_df.empty:
            fig.add_trace(
                go.Scatter(
                    x=pit_df["LapNumber"],
                    y=pit_df["Position"],
                    mode="markers",
                    name=f"{driver} pit",
                    showlegend=False,
                    marker=dict(
                        size=10,
                        color=color,
                        line=dict(width=2, color="#00ff99"),
                    ),
                    hovertemplate=(
                        f"<b>{driver} Pit Stop</b><br>"
                        "Lap: %{x}<br>"
                        "Position: P%{y}<extra></extra>"
                    ),
                )
            )

    fig.update_yaxes(
        autorange="reversed",
        title="Position",
        tickprefix="P",
        gridcolor="rgba(255,255,255,0.08)",
    )

    fig.update_xaxes(
        title="Lap Number",
        gridcolor="rgba(255,255,255,0.08)",
    )

    fig.update_layout(
        title=f"Race Position Changes — {title_suffix}",
        template="plotly_dark",
        height=620,
        paper_bgcolor="#12121c",
        plot_bgcolor="#12121c",
        font=dict(color="#FFFFFF"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
        ),
        margin=dict(l=60, r=30, t=80, b=120),
    )

    return fig