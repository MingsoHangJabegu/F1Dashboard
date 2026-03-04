import fastf1
import pandas as pd

# get data from 2018 to 2026 (might have to do in batches as number of requests exceeds
# what is allowed by fastf1)
for year in range(2018, 2026):

    schedule = fastf1.get_event_schedule(year, include_testing=False)

    all_laps = []
    all_results = []
    all_qualifying = []

    for _, event in schedule.iterrows():
        gp_name = event["EventName"]
        gp_round = event["RoundNumber"]

        print(f"\n  [{year}] {gp_name}...")

        # for laps data
        try:
            race = fastf1.get_session(year, gp_round, "R")
            race.load(laps=True, telemetry=False, weather=False, messages=False)

            laps = race.laps.copy()
            laps["RoundNumber"] = gp_round
            laps["EventName"] = gp_name
            laps["Season"] = year
            all_laps.append(laps)
        except Exception as e:
            print(f"Race laps: {e}")

        # for race results
        try:
            results = race.results.copy()
            results["RoundNumber"] = gp_round
            results["EventName"] = gp_name
            results["Season"] = year
            all_results.append(results)
        except Exception as e:
            print(f"Race results: {e}")

        # for qualifying data
        try:
            quali = fastf1.get_session(year, gp_round, "Q")
            quali.load(laps=True, telemetry=False, weather=False, messages=False)

            quali_results = quali.results.copy()
            quali_results["RoundNumber"] = gp_round
            quali_results["EventName"] = gp_name
            quali_results["Season"] = year
            all_qualifying.append(quali_results)
            print("Qualifying")
        except Exception as e:
            print(f"Qualifying: {e}")

    # saving to csv

    if all_laps:
        laps_df = pd.concat(all_laps, ignore_index=True)
        laps_df.to_csv(f"data/laps/laps_{year}.csv", index=False)

    if all_results:
        results_df = pd.concat(all_results, ignore_index=True)
        # results_cols = [
        #     "Season", "RoundNumber", "EventName",
        #     "Position", "GridPosition",
        #     "FullName", "Abbreviation", "DriverNumber",
        #     "TeamName", "TeamColor",
        #     "Time", "Status", "Points",
        #     "Q1", "Q2", "Q3"
        # ]
        # results_cols = [c for c in results_cols if c in results_df.columns]
        # results_df = results_df[results_cols]
        results_df.to_csv(f"data/race/race_results_{year}.csv", index=False)

    if all_qualifying:
        quali_df = pd.concat(all_qualifying, ignore_index=True)
        # quali_cols = [
        #     "Season", "RoundNumber", "EventName",
        #     "Position",
        #     "FullName", "Abbreviation", "DriverNumber",
        #     "TeamName", "TeamColor",
        #     "Q1", "Q2", "Q3"
        # ]
        # quali_cols = [c for c in quali_cols if c in quali_df.columns]
        # quali_df = quali_df[quali_cols]
        quali_df.to_csv(f"data/qualifying/qualifying_results_{year}.csv", index=False)