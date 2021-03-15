from django.db import models
from django.conf import settings
from django.utils.translation import get_language


# Create your models here.

class ActivityType(models.Model):
    code = models.CharField(max_length=6, primary_key=True)
    desc_en = models.TextField(null=True, blank=True)
    desc_ar = models.TextField(null=True, blank=True)

    def __str__(self):
        if get_language() == 'en-us':  # BY: amira/ to return language according to current language
            return self.desc_en
        return self.desc_ar


class CountryCode(models.Model):
    code = models.CharField(max_length=4, primary_key=True)
    desc_en = models.TextField(null=True, blank=True)
    desc_ar = models.TextField(null=True, blank=True)

    def __str__(self):
        if get_language() == 'en-us':  # By: amira/ to return language according to current language
            return self.desc_en
        return self.desc_ar


class UnitType(models.Model):
    code = models.CharField(max_length=5, primary_key=True)
    desc_en = models.TextField(null=True, blank=True)
    desc_ar = models.TextField(null=True, blank=True)

    def __str__(self):
        if get_language() == 'en-us':  # By: amira/ to return language according to current language
            return self.desc_en
        return self.desc_ar


class TaxTypes(models.Model):
    code = models.CharField(max_length=4, primary_key=True)
    desc_en = models.CharField(max_length=50)
    desc_ar = models.CharField(max_length=50)
    is_taxable = models.BooleanField(null=True, blank=True)

    def __str__(self):
        if get_language() == 'en-us':  # By: amira/ to return language according to current language
            return self.desc_en
        return self.desc_ar


class TaxSubtypes(models.Model):
    code = models.CharField(max_length=10, primary_key=True)
    desc_en = models.CharField(max_length=50)
    desc_ar = models.CharField(max_length=50)
    taxtype_reference = models.ForeignKey(TaxTypes, on_delete=models.CASCADE, )

    def __str__(self):
        return self.code
