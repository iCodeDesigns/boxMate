from django import forms
from django.forms import inlineformset_factory

from .models import InvoiceHeader ,InvoiceLine , TaxLine
from issuer.models import Address

from codes.models import TaxSubtypes

class InvoiceHeaderForm(forms.ModelForm):
    class Meta:
        model = InvoiceHeader
        exclude = ('issuer' ,  'date_time_issued','invoice_status',)
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
            # Override the subtask queryset to not getting any objects by default until the user select a task then return the appropriate subtasks
            # self.fields['subType'].queryset = TaxSubtypes.objects.none()
            # if 'taxType' in self.data:
            #     try:
            #         taxType = int(self.data.get('taxType'))
            #         self.fields['subType'].queryset = TaxSubtypes.objects.filter(taxtype_reference=taxType)
            #     except (ValueError, TypeError):
            #         pass  # invalid input from the client; ignore and fallback to empty Subtask queryset

            for field in self.fields:
                self.fields[field].widget.attrs['class'] = 'form-control'

TaxLineInlineForm = inlineformset_factory(InvoiceLine,TaxLine ,form=TaxLineForm, extra=1)
