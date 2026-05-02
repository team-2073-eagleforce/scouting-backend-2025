from django.db import models

class Teams(models.Model):
    # Anchor Fields
    team_number = models.IntegerField()
    event = models.CharField(max_length=10)
    robot_picture = models.URLField(max_length=200, null=True)
    # Optional team logo URL (uploadable via Pit Scouting)
    logo_url = models.URLField(max_length=512, null=True, blank=True)
    pit_scout_status = models.BooleanField(default=False)
    
    # Dynamic Data Bucket
    pit_data = models.JSONField(default=dict)

    class Meta:
        unique_together = ('team_number', 'event')

class Team_Match_Data(models.Model):
    # Anchor Fields (Never Change)
    team_number = models.IntegerField()
    event = models.CharField(max_length=16, default="testing")
    match_number = models.IntegerField()
    scout_name = models.CharField(max_length=32)
    quantifier = models.CharField(
        max_length=10,
        choices=[
            ('Quals', 'Qualifications'),
            ('Playoff', 'Play Off'),
            ('Prac', 'Practice')
        ],
        default='Quals'
    )
    start_pos = models.IntegerField(default=0)
    comment = models.CharField(max_length=256, default="")
    
    # Status Flags (Anchor)
    is_broken = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)
    is_tipped = models.BooleanField(default=False)
    is_excluded = models.BooleanField(default=False)
    
    # Subjective Ratings (Anchor)
    driverRanking = models.IntegerField(default=0)
    defenseRanking = models.IntegerField(default=0)
    autoLeave = models.IntegerField(default=0)
    
    # Dynamic Data Bucket
    data = models.JSONField(default=dict)

    class Meta:
        unique_together = ('team_number', 'event', 'match_number', 'scout_name')

class Human_Player_Match(models.Model):
    team_number = models.IntegerField()
    match_number = models.IntegerField(default=0)
    event = models.CharField(max_length=16, default="testing")
    human_player_comment = models.CharField(max_length=1000, default="None")
