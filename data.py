import fastf1
import pandas as pd
import os
import requests


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
        url = f"https://api.jolpi.ca/ergast/f1/{year}/driverStandings.json"
        response = requests.get(url, timeout=10)
        data = response.json()

        standings_list = data["MRData"]["StandingsTable"]["StandingsLists"]
        if not standings_list:
            return {"error": f"No standings data found for {year}"}

        standings_data = standings_list[0]["DriverStandings"][:5]

        standings = []
        for item in standings_data:
            standings.append({
                "position": int(item["position"]),
                "driver": f"{item['Driver']['givenName']} {item['Driver']['familyName']}",
                "team": item["Constructors"][0]["name"],
                "points": float(item["points"])
            })

        return {"year": year, "standings": standings}

    except Exception as e:
        print(f"Standings error: {e}")
        return {"error": str(e)}