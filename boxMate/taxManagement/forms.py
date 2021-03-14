from django import forms
from django.forms import inlineformset_factory

from .models import InvoiceHeader ,InvoiceLine , TaxLine

class InvoiceHeaderForm(forms.ModelForm):
    class Meta:
        model = InvoiceHeader
        exclude = ('issuer' , 'issuer_address' , 'receiver_address' , 'date_time_issued',)
    def __init__(self, *args, **kwargs):
            super(InvoiceHeaderForm, self).__init__(*args, **kwargs)
            for field in self.fields:
                self.fields[field].widget.attrs['class'] = 'form-control'

class InvoiceLineForm(forms.ModelForm):
    class Meta:
        model = InvoiceLine
        exclude = ('invoice_header',)
    def __init__(self, *args, **kwargs):
            super(InvoiceLineForm, self).__init__(*args, **kwargs)
            for field in self.fields:
                self.fields[field].widget.attrs['class'] = 'form-control'

class TaxLineForm(forms.ModelForm):
    class Meta:
        model = TaxLine
        exclude = ('invoice_line',)
    def __init__(self, *args, **kwargs):
            super(TaxLineForm, self).__init__(*args, **kwargs)
            for field in self.fields:
                self.fields[field].widget.attrs['class'] = 'form-control'

TaxLineInlineForm = inlineformset_factory(InvoiceLine,TaxLine ,form=TaxLineForm, extra=1)