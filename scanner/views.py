import json

import numpy as np
from django.http import JsonResponse
from django.shortcuts import render

from helpers import login_required
from teams.models import Teams, Team_Match_Data


# @login_required
import json
from django.http import JsonResponse
from django.shortcuts import render
from teams.models import Teams, Team_Match_Data

def scanner(request):
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        try:
            # Safely parse JSON data
            data_from_post = json.loads(request.body.decode("utf-8"))

            # Ensure required keys exist
            required_keys = [
                "teamNumber", "comp_code", "name", "matchNumber", "startPos", "quantifier", "missed_auto","missed_teleop",
                "autoLeave", "autoNet", "autoProcessor", "autoRemoved", "autoPath", "autoL1", "autoL2",
                "autoL3", "autoL4", "telenet", "teleProcessor", "teleRemoved", "teleL1", "teleL2", "teleL3",
                "teleL4", "endClimb", "driverRanking", "defenseRanking", "comment", "isBroken", "isDisabled", "isTipped"
            ]

            # Check if any required key is missing
            missing_keys = [key for key in required_keys if key not in data_from_post]
            if missing_keys:
                return JsonResponse({"error": f"Missing keys: {', '.join(missing_keys)}"}, status=400)

            # Ensure team exists
            Teams.objects.get_or_create(team_number=int(data_from_post["teamNumber"]), event=data_from_post["comp_code"])

            # Create team match data entry
            Team_Match_Data.objects.get_or_create(
                team_number=int(data_from_post["teamNumber"]),
                scout_name=data_from_post["name"],
                event=data_from_post["comp_code"],
                match_number=data_from_post["matchNumber"],
                start_pos=data_from_post["startPos"],
                quantifier=data_from_post["quantifier"],
                missed_auto=data_from_post["missed_auto"],
                missed_teleop=data_from_post["missed_teleop"],
                auto_leave=data_from_post["autoLeave"],
                auto_net=data_from_post["autoNet"],
                auto_processor=data_from_post["autoProcessor"],
                auto_removed=data_from_post["autoRemoved"],
                auto_path=data_from_post["autoPath"],
                auto_L1=data_from_post["autoL1"],
                auto_L2=data_from_post["autoL2"],
                auto_L3=data_from_post["autoL3"],
                auto_L4=data_from_post["autoL4"], 
                telenet=data_from_post["telenet"],
                teleProcessor=data_from_post["teleProcessor"],
                teleRemoved=data_from_post["teleRemoved"],
                teleL1=data_from_post["teleL1"],
                teleL2=data_from_post["teleL2"],
                teleL3=data_from_post["teleL3"],
                teleL4=data_from_post["teleL4"],
                climb=data_from_post["endClimb"],
                driver_ranking=data_from_post["driverRanking"],
                defense_ranking=data_from_post["defenseRanking"],
                comment=data_from_post["comment"],
                is_broken=data_from_post["isBroken"],
                is_disabled=data_from_post["isDisabled"],
                is_tipped=data_from_post["isTipped"]
            )

            return JsonResponse({"confirmation": "Successfully Sent"}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    # If it's not an AJAX request, serve the HTML page
    return render(request, "qr_scanner.html")

