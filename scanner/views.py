import json

import numpy as np
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render

from helpers import login_required  # Make sure this import is here
from teams.models import Teams, Team_Match_Data


@login_required  # Corrected from @authorized_only and uncommented
def scanner(request):
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        try:
            # Safely parse JSON data, which should now be a list of scans
            data_from_post = json.loads(request.body.decode("utf-8"))

            # Ensure the incoming data is a list
            if not isinstance(data_from_post, list):
                return JsonResponse({"error": "Invalid data format. Expected a list of scans."}, status=400)

            teams_to_create = []
            team_match_data_to_create = []
            
            # Use a set to efficiently track teams we're about to create to avoid duplicates in this batch
            teams_in_batch = set()

            required_keys = [
                "teamNumber", "comp_code", "name", "matchNumber", "startPos", "quantifier", "missed_auto",
                "autoLeave", "autoNet", "autoProcessor", "autoRemoved", "autoPath", "autoL1", "autoL2",
                "autoL3", "autoL4", "telenet", "teleProcessor", "teleRemoved", "teleL1", "teleL2", "teleL3",
                "teleL4", "endClimb", "driverRanking", "defenseRanking", "comment", "isBroken", "isDisabled", "isTipped"
            ]
            
            # Use a single atomic transaction to ensure all data is saved or none at all
            with transaction.atomic():
                for scan_data in data_from_post:
                    # Check if any required key is missing in the current scan data
                    missing_keys = [key for key in required_keys if key not in scan_data]
                    if missing_keys:
                        # If keys are missing, we'll skip this record and could potentially log it
                        # For now, we'll continue, but you could add error logging here.
                        print(f"Skipping record due to missing keys: {', '.join(missing_keys)}")
                        continue

                    team_key = (int(scan_data["teamNumber"]), scan_data["comp_code"])
                    if team_key not in teams_in_batch:
                        teams_to_create.append(
                            Teams(team_number=int(scan_data["teamNumber"]), event=scan_data["comp_code"])
                        )
                        teams_in_batch.add(team_key)

                    # Append a new Team_Match_Data object to our list to be created later
                    team_match_data_to_create.append(
                        Team_Match_Data(
                            team_number=int(scan_data["teamNumber"]),
                            scout_name=scan_data["name"],
                            event=scan_data["comp_code"],
                            match_number=scan_data["matchNumber"],
                            start_pos=scan_data["startPos"],
                            quantifier=scan_data["quantifier"],
                            missed_auto=scan_data["missed_auto"],
                            auto_leave=scan_data["autoLeave"],
                            auto_net=scan_data["autoNet"],
                            auto_processor=scan_data["autoProcessor"],
                            auto_removed=scan_data["autoRemoved"],
                            auto_path=scan_data["autoPath"],
                            auto_L1=scan_data["autoL1"],
                            auto_L2=scan_data["autoL2"],
                            auto_L3=scan_data["autoL3"],
                            auto_L4=scan_data["autoL4"],
                            telenet=scan_data["telenet"],
                            teleProcessor=scan_data["teleProcessor"],
                            teleRemoved=scan_data["teleRemoved"],
                            teleL1=scan_data["teleL1"],
                            teleL2=scan_data["teleL2"],
                            teleL3=scan_data["teleL3"],
                            teleL4=scan_data["teleL4"],
                            climb=scan_data["endClimb"],
                            driver_ranking=scan_data["driverRanking"],
                            defense_ranking=scan_data["defenseRanking"],
                            comment=scan_data["comment"],
                            is_broken=scan_data["isBroken"],
                            is_disabled=scan_data["isDisabled"],
                            is_tipped=scan_data["isTipped"]
                        )
                    )
                
                # Use bulk_create to insert all teams and match data in two efficient queries
                # ignore_conflicts=True prevents errors if a team already exists in the database
                Teams.objects.bulk_create(teams_to_create, ignore_conflicts=True)
                Team_Match_Data.objects.bulk_create(team_match_data_to_create)

            return JsonResponse({"confirmation": f"Successfully Sent {len(team_match_data_to_create)} records."}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    # If it's not an AJAX POST request, serve the HTML page
    return render(request, "qr_scanner.html")
