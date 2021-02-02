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
class TaxTypes(models.Model):
    code = models.CharField(max_length=4 , unique=True)
    desc_en = models.CharField(max_length=50)
    desc_ar = models.CharField(max_length=50)
    is_taxable = models.BooleanField()

class TaxSubtypes(models.Model):
    code = models.CharField(max_length=4 , unique=True)
    desc_en = models.CharField(max_length=50)
    desc_ar = models.CharField(max_length=50)
    taxtype_reference = models.ForeignKey(TaxTypes , on_delete=models.CASCADE)
