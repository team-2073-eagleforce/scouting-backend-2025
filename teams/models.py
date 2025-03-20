from django.db import models
from django.db.models import Model

class Teams(models.Model):
    team_number = models.IntegerField()
    event = models.CharField(max_length=10)
    drivetrain = models.CharField(max_length=50)
    weight = models.IntegerField(null=True)
    length = models.IntegerField(null=True)
    width = models.IntegerField(null=True)
    intake_design = models.CharField(max_length=50)
    intake_locations = models.CharField(max_length=100)
    scoring_locations = models.CharField(max_length=100)
    cage_positions = models.CharField(max_length=100)
    under_shallow = models.CharField(max_length=10)
    algae_picker = models.CharField(max_length=10)
    auto_positions = models.CharField(max_length=100)
    auto_leave = models.CharField(max_length=10)
    auto_algae_max = models.IntegerField(null=True)
    auto_coral_max = models.IntegerField(null=True)
    robot_picture = models.URLField(max_length=200, null=True)
    additional_info = models.TextField(null=True)
    pit_scout_status = models.BooleanField(default=False)

    class Meta:
        unique_together = ('team_number', 'event')

class Team_Match_Data(models.Model):
    # Meta Information
    team_number = models.IntegerField()
    event = models.CharField(max_length=16, default="testing")
    match_number = models.IntegerField()
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
    missed_auto = models.IntegerField(default=0)

    # Auto Period
    auto_leave = models.IntegerField()
    auto_L1 = models.IntegerField()
    auto_L2 = models.IntegerField()
    auto_L3 = models.IntegerField()
    auto_L4 = models.IntegerField()
    auto_net = models.IntegerField()
    auto_processor = models.IntegerField()
    auto_removed = models.IntegerField()

    # Teleop Period
    teleL1 = models.IntegerField()
    teleL2 = models.IntegerField()
    teleL3 = models.IntegerField()
    teleL4 = models.IntegerField()
    telenet = models.IntegerField()
    teleProcessor = models.IntegerField()
    teleRemoved = models.IntegerField()

    # End Game
    climb = models.IntegerField()

    # Rankings and Comments
    driver_ranking = models.IntegerField()
    defense_ranking = models.IntegerField()
    comment = models.CharField(max_length=256)
    
    # Status Flags
    is_broken = models.IntegerField(default=0)
    is_disabled = models.IntegerField(default=0)
    is_tipped = models.IntegerField(default=0)
    
    auto_path = models.JSONField(default=list) 
    
    # Scout Information
    scout_name = models.CharField(max_length=32)

class Human_Player_Match(models.Model):
    team_number = models.IntegerField()
    match_number = models.IntegerField(default=0)
    event = models.CharField(max_length=16, default="testing")
    human_player_comment = models.CharField(max_length=1000, default="None")
