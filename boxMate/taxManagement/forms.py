from django import forms
from django.forms import inlineformset_factory

from .models import InvoiceHeader ,InvoiceLine , TaxLine

class InvoiceHeaderForm(models.Model):
    class Meta:
        model = InvoiceHeader
        exclude = ('issuer' , 'issuer_address' , 'receiver_address' , 'date_time_issued')