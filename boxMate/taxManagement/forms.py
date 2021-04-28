from django import forms
from django.forms import inlineformset_factory

from .models import InvoiceHeader ,InvoiceLine , TaxLine
from issuer.models import Address

class InvoiceHeaderForm(forms.ModelForm):
    class Meta:
        model = InvoiceHeader
        exclude = ('date_time_issued','invoice_status',)
    def __init__(self, issuer,*args, **kwargs):
            super(InvoiceHeaderForm, self).__init__(*args, **kwargs)
            for field in self.fields:
                self.fields[field].widget.attrs['class'] = 'form-control'
            print(issuer)
            self.fields['issuer_address'].queryset = Address.objects.filter(issuer=issuer)
            self.fields['receiver_address'].queryset = Address.objects.none()
            if 'receiver' in self.data:
                try:
                    receiver_id = int(self.data.get('receiver'))
                    self.fields['receiver_address'].queryset = Address.objects.filter(receiver=receiver_id)
                except (ValueError, TypeError):
                    pass

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
