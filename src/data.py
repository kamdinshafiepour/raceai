import fastf1
import pandas as pd
import os

cache_dir = "cache"
os.makedirs(cache_dir, exist_ok=True)
fastf1.Cache.enable_cache(cache_dir)

def get_fastest_laps(race: str, year: int) -> dict:
    try:
        session = fastf1.get_session(year, race, "R")
        session.load(telemetry=False, weather=False, messages=False)

        laps = session.laps
        drivers = session.drivers

        results = []
        for pos, driver in enumerate(drivers[:5], start=1):
            driver_laps = laps.pick_drivers(driver)
            if driver_laps.empty:
                continue
            fastest = driver_laps.pick_fastest()
            lap_time = str(fastest["LapTime"]).split("0 days 00:")[-1][:9]
            results.append({
                "position": pos,
                "driver": session.get_driver(driver)["Abbreviation"],
                "team": session.get_driver(driver)["TeamName"],
                "time": lap_time,
                "lap": int(fastest["LapNumber"])
            })

        return {"race": race, "year": year, "fastest_laps": results}

    except Exception as e:
        return {"error": str(e)}


def get_driver_standings(year: int) -> dict:
    try:
        schedule = fastf1.get_event_schedule(year)
        last_round = schedule[schedule["EventFormat"] != "testing"]["RoundNumber"].max()

        session = fastf1.get_session(year, int(last_round), "R")
        session.load(telemetry=False, weather=False, messages=False)

        results = session.results[["Abbreviation", "TeamName", "Points"]].copy()
        results = results.sort_values("Points", ascending=False).head(5)

        standings = []
        for pos, (_, row) in enumerate(results.iterrows(), start=1):
            standings.append({
                "position": pos,
                "driver": row["Abbreviation"],
                "team": row["TeamName"],
                "points": int(row["Points"])
            })

        return {"year": year, "standings": standings}

    except Exception as e:
        return {"error": str(e)}