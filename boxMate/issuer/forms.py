from django import forms
from issuer.models import Issuer ,IssuerTax, Address
from datetime import date


class IssuerForm(forms.ModelForm):
    class Meta:
        model = Issuer
        fields = '__all__'
        def __init__(self, *args, **kwargs):
            super(IssuerForm, self).__init__(*args, **kwargs)
            for field in self.fields:
                self.fields[field].widget.attrs['class'] = 'form-control'




class IssuerTaxForm(forms.ModelForm):
    class Meta:
        model = IssuerTax
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super(IssuerTaxForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'



class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = '__all__'
        def __init__(self, *args, **kwargs):
            super(AddressForm, self).__init__(*args, **kwargs)
            for field in self.fields:
                self.fields[field].widget.attrs['class'] = 'form-control'

