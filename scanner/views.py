import json
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.html import escape

from helpers import login_required
from teams.models import Teams, Team_Match_Data


@csrf_exempt  # Only for API endpoint - consider implementing proper CSRF for production
@login_required
@require_http_methods(["GET", "POST"])
def scanner(request):
    if request.method == "POST":
        try:
            data_from_post = json.loads(request.body.decode("utf-8"))
            
            if not isinstance(data_from_post, list):
                return JsonResponse({"error": "Invalid data format. Expected a list of scans."}, status=400)

            with transaction.atomic():
                for scan_data in data_from_post:
                    # Use get_or_create for team to handle concurrency
                    Teams.objects.get_or_create(
                        team_number=int(scan_data["teamNumber"]),
                        event=scan_data["comp_code"]
                    )
                    
                    # Validate and sanitize input data
                    try:
                        team_number = int(scan_data["teamNumber"])
                        match_number = int(scan_data["matchNumber"])
                        scout_name = escape(str(scan_data["name"]))[:32]  # Sanitize and limit length
                        comment = escape(str(scan_data["comment"]))[:256]  # Sanitize and limit length
                    except (ValueError, KeyError) as e:
                        continue  # Skip invalid records
                    
                    # Use update_or_create for match data to handle duplicates
                    Team_Match_Data.objects.update_or_create(
                        team_number=team_number,
                        event=scan_data["comp_code"],
                        match_number=match_number,
                        defaults={
                            'scout_name': scout_name,
                            'start_pos': int(scan_data.get("startPos", 0)),
                            'quantifier': scan_data.get("quantifier", "Quals"),
                            'missed_auto': int(scan_data.get("missed_auto", 0)),
                            'auto_leave': int(scan_data.get("autoLeave", 0)),
                            'auto_net': int(scan_data.get("autoNet", 0)),
                            'auto_processor': int(scan_data.get("autoProcessor", 0)),
                            'auto_removed': int(scan_data.get("autoRemoved", 0)),
                            'auto_path': scan_data.get("autoPath", []),
                            'auto_L1': int(scan_data.get("autoL1", 0)),
                            'auto_L2': int(scan_data.get("autoL2", 0)),
                            'auto_L3': int(scan_data.get("autoL3", 0)),
                            'auto_L4': int(scan_data.get("autoL4", 0)),
                            'telenet': int(scan_data.get("telenet", 0)),
                            'teleProcessor': int(scan_data.get("teleProcessor", 0)),
                            'teleRemoved': int(scan_data.get("teleRemoved", 0)),
                            'teleL1': int(scan_data.get("teleL1", 0)),
                            'teleL2': int(scan_data.get("teleL2", 0)),
                            'teleL3': int(scan_data.get("teleL3", 0)),
                            'teleL4': int(scan_data.get("teleL4", 0)),
                            'climb': int(scan_data.get("endClimb", 0)),
                            'driver_ranking': int(scan_data.get("driverRanking", 0)),
                            'defense_ranking': int(scan_data.get("defenseRanking", 0)),
                            'comment': comment,
                            'is_broken': int(scan_data.get("isBroken", 0)),
                            'is_disabled': int(scan_data.get("isDisabled", 0)),
                            'is_tipped': int(scan_data.get("isTipped", 0))
                        }
                    )

            return JsonResponse({"confirmation": f"Successfully processed {len(data_from_post)} records."}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return render(request, "qr_scanner.html")
