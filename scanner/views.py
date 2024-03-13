import json

import numpy as np
from django.http import JsonResponse
from django.shortcuts import render

from helpers import login_required
from teams.models import Teams, Team_Match_Data


@login_required
def scanner(request):
    # Receive fetch from scanner.js
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data_from_post = json.load(request)

        Teams.objects.get_or_create(team_number=int(data_from_post["teamNumber"]), event=data_from_post["comp_code"])
        # Creates a new Team_Match_Data with given data if it doesn't exist
        Team_Match_Data.objects.get_or_create(team_number=int(data_from_post["teamNumber"]),
                                              event=data_from_post["comp_code"],
                                              match_number=data_from_post["matchNumber"],
                                              quantifier="Quals",

                                              auto_leave=data_from_post["autoLeave"],
                                              auto_amp=data_from_post["autoAmp"],
                                              auto_speaker_make=data_from_post["autoSpeakerMake"],
                                              auto_speaker_miss=data_from_post["autoSpeakerMiss"],

                                              teleop_amp=data_from_post["teleopAmp"],
                                              teleop_speaker_make=data_from_post["teleopSpeakerMake"],
                                              teleop_speaker_miss=data_from_post["teleopSpeakerMiss"],

                                              trap=data_from_post["trapNumber"],
                                              climb=data_from_post["endClimb"],

                                              driver_ranking=data_from_post["driverRanking"],
                                              defense_ranking=data_from_post["defenseRanking"],
                                              comment=data_from_post["comment"],
                                              scout_name=data_from_post["name"])

        response = {"confirmation": "Successfully Sent"}
        return JsonResponse(response)

    return render(request, 'qr_scanner.html')
