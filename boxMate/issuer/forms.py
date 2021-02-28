from django import forms
from issuer.models import Issuer ,IssuerTax, Address , IssuerOracleDB
from datetime import date
from django.forms import modelformset_factory

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

class IssuerOracleDBForm(forms.ModelForm):
    class Meta:
        model = IssuerOracleDB
        fields = '__all__'
        exclude = {'issuer',}
    def __init__(self ,is_update=False , *args , **kwargs):
        super(IssuerOracleDBForm , self).__init__(*args , **kwargs)
        if not is_update:
            self.fields['password'].widget.attrs['type'] = 'password'