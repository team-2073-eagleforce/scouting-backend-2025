from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.

class PickList_Data(models.Model):
    event = models.CharField(max_length=16, default="testing")
    no_pick = ArrayField(models.IntegerField(), default=list)
    first_pick = ArrayField(models.IntegerField(), default=list)
    second_pick = ArrayField(models.IntegerField(), default=list)
    third_pick = ArrayField(models.IntegerField(), default=list)
    dn_pick = ArrayField(models.IntegerField(), default=list)