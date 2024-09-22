import os

import requests

import constants

TEAM_KEY = "frc2073"
YEAR = str(constants.CONST_YEAR)
X_TBA_Auth_Key = os.environ.get("X_TBA_AUTH_KEY")


def get_team_events():
    team_events = requests.get(f"https://www.thebluealliance.com/api/v3/team/{TEAM_KEY}/events/{YEAR}",
                               headers={"X-TBA-Auth-Key": X_TBA_Auth_Key})
    events = {}
    for event in team_events.json():
        events[event["key"]] = event["name"]
    events["testing"] = "Training"

    return events


def get_match_schedule(event_key):
    matches_at_event = requests.get(f"https://www.thebluealliance.com/api/v3/event/{event_key}/matches/simple",
                                    headers={"X-TBA-Auth-Key": X_TBA_Auth_Key}).json()
    return matches_at_event


def get_teams_list(event_key):
    teams_at_event = requests.get(f"https://www.thebluealliance.com/api/v3/event/{event_key}/teams/simple",
                                  headers={"X-TBA-Auth-Key": X_TBA_Auth_Key}).json()
    return teams_at_event


def get_single_match(event_key, match_id):
    match_key = event_key + "_" + match_id
    raw_match = requests.get(f"https://www.thebluealliance.com/api/v3/match/{match_key}/simple",
                             headers={"X-TBA-Auth-Key": X_TBA_Auth_Key}).json()
    
    match = {"red": [], "blue": []}
    for red_team in raw_match["alliances"]["red"]["team_keys"]:
        match["red"].append(red_team.split("frc")[1])
    for blue_team in raw_match["alliances"]["blue"]["team_keys"]:
        match["blue"].append(blue_team.split("frc")[1])

    return match
