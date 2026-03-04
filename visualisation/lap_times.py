import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import fastf1
from fastf1 import plotting

fastf1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme='fastf1')


def plot_lap_times(year, grand_prix, session_type):
    """
    Plots lap times for all drivers in a given session from CSV data.

    Parameters
    ----------
    year         : int  e.g. 2025
    grand_prix   : str  e.g. "Australian Grand Prix"
    session_type : str  "Race" or "Qualifying"
    """

    # Load data
    if session_type == "Race":
        path = f"data/laps/laps_{year}.csv"
    else:
        path = f"data/qualifying_laps/qualifying_laps_{year}.csv"

    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        print(f"File not found: {path}")
        return

    df = df[df["EventName"] == grand_prix].copy()

    if df.empty:
        print(f"No data found for {grand_prix} {year} {session_type}")
        return

    # Parsing to seconds for plotting
    def parse_to_seconds(val):
        try:
            if pd.isna(val): return None
            val = str(val)
            if "days" in val:
                val = val.split("days")[-1].strip()
            parts = val.split(":")
            if len(parts) == 3:
                h, m, s = parts
                return int(h) * 3600 + int(m) * 60 + float(s)
            elif len(parts) == 2:
                m, s = parts
                return int(m) * 60 + float(s)
        except:
            return None

    df["LapTimeSec"] = df["LapTime"].apply(parse_to_seconds)
    df = df[df["LapTimeSec"].notna()]
    df = df[df["LapTimeSec"].between(60, 300)]

    # Exclude pit laps for race
    if session_type == "Race":
        df = df[df["PitInTime"].isna() & df["PitOutTime"].isna()]

    # Getting driver colors for plotting
    session_code = "R" if session_type == "Race" else "Q"
    session = fastf1.get_session(year, grand_prix, session_code)
    session.load(laps=False, telemetry=False, weather=False, messages=False)

    # Plotting
    fig, ax = plt.subplots(figsize=(14, 6))

    for driver in sorted(df["Driver"].dropna().unique()):
        laps = df[df["Driver"] == driver].sort_values("LapNumber")

        try:
            style = plotting.get_driver_style(
                identifier=driver,
                style=["color", "linestyle"],
                session=session
            )
        except Exception:
            style = {"color": "#ffffff", "linestyle": "-"}

        ax.plot(laps["LapNumber"], laps["LapTimeSec"],
                **style, label=driver, linewidth=1.2)

    # Y axis formatting, tick every 5 seconds
    def fmt_laptime(sec, _):
        sec = int(sec)
        return f"{sec // 60}:{sec % 60:02d}"

    ax.yaxis.set_major_locator(ticker.MultipleLocator(5))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(fmt_laptime))
    ax.set_xlabel("Lap Number")
    ax.set_ylabel("Lap Time")
    ax.set_title(f"{grand_prix} {year} — {session_type}")
    ax.legend(loc="upper right", fontsize=8, ncol=2)

    plt.tight_layout()
    plt.savefig(f"lap_times_{year}_{session_type}.png", dpi=150, bbox_inches="tight")
    plt.show()

    return fig


# calling the function for demo
if __name__ == "__main__":
    plot_lap_times(2023, "Azerbaijan Grand Prix", "Qualifying")


# TODO: Make chart interactive (possibly use plotly, not matplotlib)