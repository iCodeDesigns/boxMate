from django.db import models

# Create your models here.

class ActivityType(models.Model):
    code = models.CharField(max_length=6,primary_key=True)
    desc_en = models.TextField(null=True, blank=True) 
    desc_ar = models.TextField(null=True, blank=True) 


class CountryCode(models.Model):
    code = models.CharField(max_length=4,primary_key=True)
    desc_en = models.TextField(null=True, blank=True) 
    desc_ar = models.TextField(null=True, blank=True) 



class UnitType(models.Model):
    code = models.CharField(max_length=5,primary_key=True)
    desc_en = models.TextField(null=True, blank=True) 
    desc_ar = models.TextField(null=True, blank=True)         