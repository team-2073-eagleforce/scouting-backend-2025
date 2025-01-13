import json

import numpy as np
from django.http import JsonResponse
from django.shortcuts import render

from helpers import login_required
from teams.models import Teams, Team_Match_Data


# @login_required
def scanner(request):
    # Receive fetch from scanner.js
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data_from_post = json.load(request)

        Teams.objects.get_or_create(team_number=int(data_from_post["teamNumber"]), event=data_from_post["comp_code"])
        # Creates a new Team_Match_Data with given data if it doesn't exist
        Team_Match_Data.objects.get_or_create(team_number=int(data_from_post["teamNumber"]),
                                              name=data_from_post["name"],
                                              event=data_from_post["comp_code"],
                                              match_number=data_from_post["matchNumber"],
                                              quantifier=data_from_post["quantifier"],

                                              auto_leave=data_from_post["autoLeave"],
                                              auto_net=data_from_post["autoNet"],
                                              auto_processor=data_from_post["autoProcessor"],
                                              auto_removed=data_from_post["autoRemoved"],
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
                                              is_tipped=data_from_post["isTipped"],
                                              scout_name=data_from_post["name"])

        response = {"confirmation": "Successfully Sent"}
        return JsonResponse(response)

    return render(request, 'qr_scanner.html')
