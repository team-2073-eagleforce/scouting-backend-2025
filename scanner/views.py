import json
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.html import escape

from helpers import login_required
from teams.models import Teams, Team_Match_Data
from .validation import validate_scan_data, sanitize_scan_data

@csrf_exempt
@login_required
@require_http_methods(["GET", "POST"])
def scanner(request):
    if request.method == "POST":
        try:
            data_from_post = json.loads(request.body.decode("utf-8"))
            
            # Handle single scan or batch
            if isinstance(data_from_post, dict):
                data_from_post = [data_from_post]
            elif not isinstance(data_from_post, list):
                return JsonResponse({"error": "Invalid data format"}, status=400)
            
            validation_errors = []
            valid_scans = []
            
            # Validate all scans first
            for i, scan_data in enumerate(data_from_post):
                is_valid, errors = validate_scan_data(scan_data)
                if not is_valid:
                    validation_errors.append({"scan": i + 1, "errors": errors})
                else:
                    valid_scans.append(sanitize_scan_data(scan_data))
            
            # If any validation errors, return them
            if validation_errors:
                return JsonResponse({
                    "error": "Validation failed",
                    "validation_errors": validation_errors,
                    "valid_count": len(valid_scans),
                    "total_count": len(data_from_post)
                }, status=400)
            
            # Process valid scans
            with transaction.atomic():
                for scan_data in valid_scans:
                    team_number = int(scan_data["teamNumber"])
                    match_number = int(scan_data["matchNumber"])
                    scout_name = escape(str(scan_data["name"]).strip())[:32]
                    comment = escape(str(scan_data.get("comment", "")).strip())[:256]
                    comp_code = str(scan_data["comp_code"]).strip()
                    
                    Teams.objects.get_or_create(
                        team_number=team_number,
                        event=comp_code
                    )
                    
                    Team_Match_Data.objects.update_or_create(
                        team_number=team_number,
                        event=comp_code,
                        match_number=match_number,
                        defaults={
                            'scout_name': scout_name,
                            'start_pos': max(0, min(4, int(scan_data.get("startPos", 0)))),
                            'quantifier': scan_data.get("quantifier", "Quals"),
                            'missed_auto': max(0, int(scan_data.get("missed_auto", 0))),
                            'auto_leave': max(0, int(scan_data.get("autoLeave", 0))),
                            'auto_net': max(0, int(scan_data.get("autoNet", 0))),
                            'auto_processor': max(0, int(scan_data.get("autoProcessor", 0))),
                            'auto_removed': max(0, int(scan_data.get("autoRemoved", 0))),
                            'auto_path': scan_data.get("autoPath", []),
                            'auto_L1': max(0, int(scan_data.get("autoL1", 0))),
                            'auto_L2': max(0, int(scan_data.get("autoL2", 0))),
                            'auto_L3': max(0, int(scan_data.get("autoL3", 0))),
                            'auto_L4': max(0, int(scan_data.get("autoL4", 0))),
                            'telenet': max(0, int(scan_data.get("telenet", 0))),
                            'teleProcessor': max(0, int(scan_data.get("teleProcessor", 0))),
                            'teleRemoved': max(0, int(scan_data.get("teleRemoved", 0))),
                            'teleL1': max(0, int(scan_data.get("teleL1", 0))),
                            'teleL2': max(0, int(scan_data.get("teleL2", 0))),
                            'teleL3': max(0, int(scan_data.get("teleL3", 0))),
                            'teleL4': max(0, int(scan_data.get("teleL4", 0))),
                            'climb': max(0, min(4, int(scan_data.get("endClimb", 0)))),
                            'driver_ranking': max(1, min(5, int(scan_data.get("driverRanking", 3)))),
                            'defense_ranking': max(1, min(5, int(scan_data.get("defenseRanking", 3)))),
                            'comment': comment,
                            'is_broken': max(0, min(1, int(scan_data.get("isBroken", 0)))),
                            'is_disabled': max(0, min(1, int(scan_data.get("isDisabled", 0)))),
                            'is_tipped': max(0, min(1, int(scan_data.get("isTipped", 0))))
                        }
                    )
            
            return JsonResponse({"success": True, "processed": len(valid_scans)}, status=200)
        
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)
    
    return render(request, "scanner/qr_scanner.html")
