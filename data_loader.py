import pandas as pd
import os
import fastf1
import fastf1.plotting

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

# ── FILE HELPERS ──────────────────────────────────────────────────
def load_csv(subfolder, filename):
    path = os.path.join(DATA_DIR, subfolder, filename)
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        print(f"File not found: {path}")
        return pd.DataFrame()

def list_csv_files(subfolder):
    folder = os.path.join(DATA_DIR, subfolder)
    if not os.path.isdir(folder):
        print(f"Folder not found: {folder}")
        return []
    return [f for f in os.listdir(folder) if f.endswith('.csv')]

def _load_all(subfolder):
    files = list_csv_files(subfolder)
    dfs = [load_csv(subfolder, f) for f in files]
    dfs = [df for df in dfs if not df.empty]
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

# ── LOAD ALL DATA ONCE ────────────────────────────────────────────
race_df    = _load_all("laps")
quali_laps_df   = _load_all("qualifying_laps")
quali_df   = _load_all("qualifying_results")
results_df = _load_all("race")

# ── SEASONS ───────────────────────────────────────────────────────
seasons = (
    sorted(race_df["Season"].dropna().unique().astype(int), reverse=True)
    if "Season" in race_df.columns and not race_df.empty
    else []
)

# ── FILTER HELPERS ────────────────────────────────────────────────
def filter_laps(season, race, session):
    if not season or not race: return pd.DataFrame()
    df = race_df if session == "Race" else quali_df
    if df.empty: return pd.DataFrame()
    required = {"Season", "EventName", "LapTime", "LapNumber"}
    if not required.issubset(df.columns): return pd.DataFrame()
    return df[
        (df["Season"] == season) &
        (df["EventName"] == race)
    ].copy()

def filter_results(season, race):
    if not season or not race: return pd.DataFrame()
    if results_df.empty: return pd.DataFrame()
    return results_df[
        (results_df["Season"] == season) &
        (results_df["EventName"] == race)
    ].copy()

def get_races(season, session):
    df = race_df if session == "Race" else quali_df
    if df.empty or "Season" not in df.columns: return []
    return (
        df[df["Season"] == season]
        .sort_values("RoundNumber")["EventName"]
        .dropna().unique().tolist()
    )

def get_color_map(season, race, session_type):
    try:
        session_code = "R" if session_type == "Race" else "Q"
        session = fastf1.get_session(season, race, session_code)
        session.load(laps=False, telemetry=False, weather=False, messages=False)

        color_map = {}
        for driver_num in session.drivers:
            try:
                # ── Get abbreviation from driver number ───────────
                abbr = session.get_driver(driver_num)["Abbreviation"]
                color_map[abbr] = fastf1.plotting.get_driver_color(abbr, session=session)
            except Exception as e:
                print(f"  Could not get color for driver {driver_num}: {e}")
                if abbr:
                    color_map[abbr] = "#888888"
        return color_map

    except Exception as e:
        print(f"Could not load driver colors: {e}")
        return {}