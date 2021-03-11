from django.contrib.auth.models import User
from datetime import datetime, date
from django.utils import timezone
from django.db import models
from django.db import transaction
from codes.models import CountryCode, TaxTypes, ActivityType , TaxSubtypes
from django.conf import settings


# Create your models here.
class Issuer(models.Model):
    type = models.CharField(max_length=8,
                            choices=[('B', 'business'), ('P', 'natural person'), ('F', 'foreigner')], default='B')
    reg_num = models.CharField(max_length=20, verbose_name='reg_number', unique=True)
    name = models.CharField(max_length=50, verbose_name='issuer name', blank=True, null=True)
    client_id = models.CharField(max_length=50,blank=True, null=True )
    clientSecret1 = models.CharField(max_length=50,blank=True, null=True)
    clientSecret2 = models.CharField(max_length=50,blank=True, null=True)
    activity_code = models.ForeignKey(ActivityType, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True, null=True, blank=True)
    last_updated_at = models.DateField(null=True, auto_now=True, auto_now_add=False, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                                   related_name="Issuer_created_by")
    last_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="Issuer_last_updated_by")



class Receiver(models.Model):
    issuer = models.ForeignKey(Issuer , on_delete=models.CASCADE) #### by:Mamdouh
    type = models.CharField(max_length=8,
                            choices=[('B', 'business'), ('P', 'natural person'), ('F', 'foreigner')], default='B')
    reg_num = models.CharField(max_length=8, verbose_name='reg_number')
    name = models.CharField(max_length=50, verbose_name='reciever name', blank=True, null=True)
    created_at = models.DateField(auto_now_add=True, null=True, blank=True)
    last_updated_at = models.DateField(null=True, auto_now=True, auto_now_add=False, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                                   related_name="Receiver_created_by")
    last_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        return self.name

class Address(models.Model):
    branch_id = models.CharField(max_length=10)
    issuer = models.ForeignKey(Issuer, on_delete=models.CASCADE, null=True, blank=True, related_name='issuer_addresses')
    receiver = models.ForeignKey(Receiver, on_delete=models.CASCADE, null=True, blank=True,related_name='rec_addresses')
    country = models.ForeignKey(CountryCode, on_delete=models.CASCADE, blank=True, null=True)
    governate = models.CharField(max_length=50, blank=True, null=True)
    regionCity = models.CharField(max_length=50, blank=True, null=True)
    street = models.CharField(max_length=120, blank=True, null=True)
    buildingNumber = models.CharField(max_length=120, blank=True, null=True)
    postalCode = models.CharField(max_length=20, blank=True, null=True)
    floor = models.CharField(max_length=10, blank=True, null=True)
    room = models.CharField(max_length=10, blank=True, null=True)
    landmark = models.CharField(max_length=120, blank=True, null=True)
    additionalInformation = models.CharField(max_length=250, blank=True, null=True)
    created_at = models.DateField(auto_now_add=True, null=True, blank=True)
    last_updated_at = models.DateField(null=True, auto_now=True, auto_now_add=False, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                                   related_name="address_created_by")
    last_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)




class IssuerTax(models.Model):
    issuer = models.ForeignKey(Issuer, on_delete=models.CASCADE, null=True, blank=True, related_name='issuer_tax')
    issuer_sub_tax = models.ForeignKey(TaxSubtypes, on_delete=models.CASCADE, null=True, blank=True, related_name='issuer_sub_tax')
    start_date = models.DateField(default=timezone.now, null=True, blank=True)
    end_date = models.DateField(auto_now_add=True, null=True, blank=True)
    is_enabled = models.BooleanField()

    created_at = models.DateField(auto_now_add=True, null=True, blank=True)
    last_updated_at = models.DateField(null=True, auto_now=True, auto_now_add=False, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                                   related_name="issuer_tax_created_by")
    last_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="issuer_tax_last_update_by")

    def __str__(self):
        return self.issuer.name

class IssuerOracleDB(models.Model):
    issuer = models.ForeignKey(Issuer,on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=20)
    port_number = models.CharField(max_length=10)
    service_number = models.CharField(max_length=10)
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=100)
    database_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.is_active:
            return super(IssuerOracleDB, self).save(*args, **kwargs)
        with transaction.atomic():
            IssuerOracleDB.objects.filter(
                is_active=True , issuer=self.issuer).update(is_active=False)
            return super(IssuerOracleDB, self).save(*args, **kwargs)