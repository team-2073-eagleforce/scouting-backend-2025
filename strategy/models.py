from django.db import models

# Create your models here.

class PickList_Data(models.Model):
    event = models.CharField(max_length=16, default="testing")
    no_pick = models.JSONField(default=list)
    first_pick = models.JSONField(default=list)
    second_pick = models.JSONField(default=list)
    third_pick = models.JSONField(default=list)
    dn_pick = models.JSONField(default=list)