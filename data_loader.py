import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')


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
