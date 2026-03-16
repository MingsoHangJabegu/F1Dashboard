import pandas as pd
import os
from functools import lru_cache

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
SESSION_DATASETS = {
    "Race": {
        "lap_folder": "laps",
        "lap_prefix": "laps",
        "results_folder": "race",
        "results_prefix": "race_results",
    },
    "Qualifying": {
        "lap_folder": "qualifying_laps",
        "lap_prefix": "qualifying_laps",
        "results_folder": "qualifying_results",
        "results_prefix": "qualifying_results",
    },
}


def load_csv(subfolder, filename):
    """
    Load a CSV file from the data directory.
    Args:
        subfolder (str): Subdirectory under 'data' (e.g. 'race', 'laps')
        filename (str): CSV file name (e.g. 'race_results_2024.csv')
    Returns:
        pd.DataFrame: Loaded DataFrame, or empty DataFrame if not found
    """
    path = os.path.join(DATA_DIR, subfolder, filename)
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        print(f"File not found: {path}")
        return pd.DataFrame()


def list_csv_files(subfolder):
    """
    List CSV files in a subfolder under 'data'.
    Args:
        subfolder (str): Subdirectory under 'data'
    Returns:
        list[str]: List of CSV file names
    """
    folder = os.path.join(DATA_DIR, subfolder)
    if not os.path.isdir(folder):
        return []
    return [f for f in os.listdir(folder) if f.endswith('.csv')]

@lru_cache(maxsize=1)
def get_all_seasons():
    """
    Get all available seasons from the supported session datasets.
    Returns:
        list[int]: Sorted list of seasons
    """
    seasons = set()
    for session_config in SESSION_DATASETS.values():
        for filename in list_csv_files(session_config["lap_folder"]):
            try:
                seasons.add(int(filename.split('_')[-1].replace('.csv', '')))
            except ValueError:
                continue
    return sorted(seasons, reverse=True)


def _load_session_lap_data(season, session_name):
    session_config = SESSION_DATASETS.get(session_name)
    if not session_config:
        return pd.DataFrame()
    return load_csv(
        session_config["lap_folder"],
        f"{session_config['lap_prefix']}_{season}.csv",
    )


def _load_session_results_data(season, session_name):
    session_config = SESSION_DATASETS.get(session_name)
    if not session_config:
        return pd.DataFrame()
    return load_csv(
        session_config["results_folder"],
        f"{session_config['results_prefix']}_{season}.csv",
    )


@lru_cache(maxsize=32)
def get_circuits_for_season(season):
    """
    Get all circuits (EventName) for a specific season.
    Args:
        season (int): Season year
    Returns:
        list[dict]: List of circuits with RoundNumber and EventName
    """
    filename = f'laps_{season}.csv'
    df = load_csv('laps', filename)
    
    if df.empty:
        return []
    
    # Get unique circuits with their round numbers
    circuits = df[['RoundNumber', 'EventName']].drop_duplicates()
    circuits = circuits.sort_values('RoundNumber')
    
    return circuits.to_dict('records')


@lru_cache(maxsize=32)
def get_available_sessions_for_season(season):
    """
    Get all sessions that have data files for a given season.
    Args:
        season (int): Season year
    Returns:
        list[str]: Session names with available data
    """
    available_sessions = []
    for session_name, session_config in SESSION_DATASETS.items():
        filename = f"{session_config['lap_prefix']}_{season}.csv"
        if filename in list_csv_files(session_config["lap_folder"]):
            available_sessions.append(session_name)
    return available_sessions


@lru_cache(maxsize=64)
def get_events_for_season_and_session(season, session_name):
    """
    Get all events that exist for the chosen season and session.
    Args:
        season (int): Season year
        session_name (str): Session label (e.g. 'Race', 'Qualifying')
    Returns:
        list[dict]: List of circuits with RoundNumber and EventName
    """
    df = _load_session_lap_data(season, session_name)
    if df.empty:
        return []

    circuits = df[['RoundNumber', 'EventName']].drop_duplicates()
    circuits = circuits.sort_values('RoundNumber')
    return circuits.to_dict('records')


@lru_cache(maxsize=128)
def get_drivers_for_race(season, event_name):
    """
    Get all drivers who participated in a specific race.
    Args:
        season (int): Season year
        event_name (str): Event name (e.g., 'Bahrain Grand Prix')
    Returns:
        list[str]: Sorted list of driver abbreviations
    """
    filename = f'laps_{season}.csv'
    df = load_csv('laps', filename)
    
    if df.empty:
        return []
    
    race_df = df[df['EventName'] == event_name]
    drivers = sorted(race_df['Driver'].dropna().unique().tolist())
    
    return drivers


@lru_cache(maxsize=128)
def get_driver_options(season, event_name, session_name):
    """
    Get driver metadata for a selected season, event, and session.
    Args:
        season (int): Season year
        event_name (str): Event name
        session_name (str): Session label
    Returns:
        list[dict]: Driver metadata used by the global filter
    """
    laps_df = _load_session_lap_data(season, session_name)
    if laps_df.empty:
        return []

    race_df = laps_df[laps_df['EventName'] == event_name]
    if race_df.empty:
        return []

    results_df = _load_session_results_data(season, session_name)
    if not results_df.empty:
        results_df = results_df[results_df['EventName'] == event_name].copy()

    if not results_df.empty and 'Abbreviation' in results_df.columns:
        drivers = (
            results_df[
                ['Abbreviation', 'BroadcastName', 'TeamName', 'TeamColor', 'Position']
            ]
            .dropna(subset=['Abbreviation'])
            .drop_duplicates(subset=['Abbreviation'])
            .sort_values('Position', na_position='last')
        )
        return [
            {
                "value": row['Abbreviation'],
                "label": row['Abbreviation'],
                "full_name": row.get('BroadcastName', row['Abbreviation']),
                "team_name": row.get('TeamName', ''),
                "team_color": row.get('TeamColor', ''),
            }
            for _, row in drivers.iterrows()
        ]

    fallback = (
        race_df[['Driver', 'Team']]
        .dropna(subset=['Driver'])
        .drop_duplicates(subset=['Driver'])
        .sort_values('Driver')
    )
    return [
        {
            "value": row['Driver'],
            "label": row['Driver'],
            "full_name": row['Driver'],
            "team_name": row.get('Team', ''),
            "team_color": '',
        }
        for _, row in fallback.iterrows()
    ]


@lru_cache(maxsize=128)
def get_teams_for_race(season, event_name):
    """
    Get all teams who participated in a specific race.
    Args:
        season (int): Season year
        event_name (str): Event name
    Returns:
        list[str]: Sorted list of team names
    """
    filename = f'laps_{season}.csv'
    df = load_csv('laps', filename)
    
    if df.empty:
        return []
    
    race_df = df[df['EventName'] == event_name]
    teams = sorted(race_df['Team'].dropna().unique().tolist())
    
    return teams


def load_race_data(season, event_name, data_type='laps'):
    """
    Load race data for a specific season and event.
    Args:
        season (int): Season year
        event_name (str): Event name
        data_type (str): Type of data ('laps', 'race', 'qualifying_laps', 'qualifying_results')
    Returns:
        pd.DataFrame: Filtered DataFrame for the specific race
    """
    data_folder_map = {
        'laps': 'laps',
        'race': 'race',
        'qualifying_laps': 'qualifying_laps',
        'qualifying_results': 'qualifying_results',
    }
    filename_map = {
        'laps': f'laps_{season}.csv',
        'race': f'race_results_{season}.csv',
        'qualifying_laps': f'qualifying_laps_{season}.csv',
        'qualifying_results': f'qualifying_results_{season}.csv',
    }
    folder = data_folder_map.get(data_type)
    filename = filename_map.get(data_type)

    if not folder or not filename:
        return pd.DataFrame()

    df = load_csv(folder, filename)
    
    if df.empty:
        return pd.DataFrame()
    
    return df[df['EventName'] == event_name].copy()
