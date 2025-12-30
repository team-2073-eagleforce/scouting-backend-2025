import json
from django.http import JsonResponse
from django.shortcuts import render
from teams.models import Teams, Team_Match_Data
from utils import config_loader
from helpers import login_required

@login_required
def scanner(request):
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        try:
            data_from_post = json.loads(request.body.decode("utf-8"))
            config = config_loader.get_config()

            # Extract anchor fields
            try:
                team_num = int(data_from_post["teamNumber"])
                event_code = data_from_post["comp_code"]
                match_num = int(data_from_post["matchNumber"])
                scout_name = data_from_post.get("name", "")
            except (KeyError, ValueError, TypeError) as e:
                return JsonResponse({"error": f"Missing or invalid key identifier: {e}"}, status=400)

            # Ensure team exists
            Teams.objects.get_or_create(team_number=team_num, event=event_code)

            # Helper to safely get values
            def get_value(key, default=None):
                val = data_from_post.get(key)
                return val if val not in [None, ""] else default

            # Build anchor fields
            quantifier_val = data_from_post.get("quantifier")
            if quantifier_val not in ['Quals', 'Playoff', 'Prac']:
                quantifier_val = 'Quals'

            match_data_defaults = {
                'scout_name': scout_name,
                'quantifier': quantifier_val,
                'start_pos': int(get_value("startPos", 0)),
                'comment': get_value("comment", ""),
                'is_broken': bool(int(get_value("isBroken", 0))),
                'is_disabled': bool(int(get_value("isDisabled", 0))),
                'is_tipped': bool(int(get_value("isTipped", 0))),
            }

            # Dynamic data bucket - loop through config metrics
            data_bucket = {}
            validation_errors = []
            
            for metric in config['metrics']:
                key = metric['key']
                value = get_value(key)
                
                if value is not None:
                    # Validate
                    is_valid, error_msg = config_loader.validate_data({key: value}, key)
                    if not is_valid:
                        validation_errors.append(error_msg)
                        continue
                    
                    # Type conversion
                    if metric['type'] == 'number':
                        try:
                            data_bucket[key] = float(value)
                        except (ValueError, TypeError):
                            data_bucket[key] = 0
                    elif metric['type'] == 'boolean':
                        data_bucket[key] = bool(int(value)) if isinstance(value, (int, str)) else bool(value)
                    else:
                        data_bucket[key] = value

            if validation_errors:
                return JsonResponse({"error": "; ".join(validation_errors)}, status=400)

            match_data_defaults['data'] = data_bucket

            # Save to database
            obj, created = Team_Match_Data.objects.update_or_create(
                team_number=team_num,
                event=event_code,
                match_number=match_num,
                scout_name=scout_name,
                defaults=match_data_defaults
            )

            confirmation_msg = "Successfully Updated" if not created else "Successfully Sent (New)"
            return JsonResponse({"confirmation": confirmation_msg, "id": obj.id}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            print(f"Error in scanner view: {e}")
            return JsonResponse({"error": f"An unexpected error occurred: {e}"}, status=500)

    return render(request, "qr_scanner.html")