import json
from django.http import JsonResponse
from django.shortcuts import render
from teams.models import Teams, Team_Match_Data

# We don't need numpy or login_required for this view
# @login_required 

def scanner(request):
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        try:
            # Safely parse JSON data
            data_from_post = json.loads(request.body.decode("utf-8"))

            # --- Robust Data Handling and Validation ---

            # 1. Get the key identifying fields. We must fail if these are invalid.
            try:
                team_num = int(data_from_post["teamNumber"])
                event_code = data_from_post["comp_code"]
                match_num = int(data_from_post["matchNumber"])
            except (KeyError, ValueError, TypeError) as e:
                return JsonResponse({"error": f"Missing or invalid key identifier: {e}"}, status=400)

            # 2. Ensure team exists
            Teams.objects.get_or_create(team_number=team_num, event=event_code)

            # 3. Helper function to get an integer from the data or return a default
            def get_int_default(key, default_val=0):
                """Safely gets an integer from the POST data, or returns a default."""
                try:
                    # Check for None or empty string before int conversion
                    val = data_from_post.get(key)
                    if val is None or val == "":
                        return default_val
                    return int(val)
                except (ValueError, TypeError):
                    return default_val

            # 4. Get quantifier, falling back to the model's default
            quantifier_val = data_from_post.get("quantifier")
            if not quantifier_val in ['Quals', 'Playoff', 'Prac']:
                quantifier_val = 'Quals' # Default from model

            # 5. Build the 'defaults' dictionary for all other data fields
            #    This is everything we want to update if the match is found.
            match_data_defaults = {
                'scout_name': data_from_post.get("name", ""),
                'quantifier': quantifier_val,
                'start_pos': get_int_default("startPos", 0),
                'missed_auto': get_int_default("missed_auto", 0),
                
                'auto_leave': get_int_default("autoLeave"),
                'auto_L1': get_int_default("autoL1"),
                'auto_L2': get_int_default("autoL2"),
                'auto_L3': get_int_default("autoL3"),
                'auto_L4': get_int_default("autoL4"),
                'auto_net': get_int_default("autoNet"),
                'auto_processor': get_int_default("autoProcessor"),
                'auto_removed': get_int_default("autoRemoved"),
                
                'auto_path': data_from_post.get("autoPath", list), # Uses model default
                
                'teleL1': get_int_default("teleL1"),
                'teleL2': get_int_default("teleL2"),
                'teleL3': get_int_default("teleL3"),
                'teleL4': get_int_default("teleL4"),
                'telenet': get_int_default("telenet"),
                'teleProcessor': get_int_default("teleProcessor"),
                'teleRemoved': get_int_default("teleRemoved"),
                
                'climb': get_int_default("endClimb"),
                'driver_ranking': get_int_default("driverRanking"),
                'defense_ranking': get_int_default("defenseRanking"),
                
                'comment': data_from_post.get("comment", ""),
                
                'is_broken': get_int_default("isBroken", 0),
                'is_disabled': get_int_default("isDisabled", 0),
                'is_tipped': get_int_default("isTipped", 0),
            }

            # 6. Use update_or_create
            #    This finds a match based on the key fields (team, event, match).
            #    If found, it UPDATES it with the 'defaults' dict.
            #    If not found, it CREATES a new entry.
            obj, created = Team_Match_Data.objects.update_or_create(
                team_number=team_num,
                event=event_code,
                match_number=match_num,
                defaults=match_data_defaults
            )

            confirmation_msg = "Successfully Updated"
            if created:
                confirmation_msg = "Successfully Sent (New)"

            # Return the ID of the object that was created or updated
            return JsonResponse({"confirmation": confirmation_msg, "id": obj.id}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            # Log the error for easier debugging
            print(f"Error in scanner view: {e}")
            print(f"Failing data: {request.body.decode('utf-8', 'ignore')}")
            return JsonResponse({"error": f"An unexpected error occurred: {e}"}, status=500)

    # If it's not an AJAX request, serve the HTML page
    return render(request, "qr_scanner.html")