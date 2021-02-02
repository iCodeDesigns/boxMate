from django.db import models

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