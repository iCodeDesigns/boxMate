from django import forms
from issuer.models import Issuer ,IssuerTax, Address , IssuerOracleDB , Receiver
from datetime import date
from django.forms import modelformset_factory , formset_factory


def clean_unique(form, field, exclude_initial=True, 
                 format="The %(field)s %(value)s has already been taken."):
    value = form.cleaned_data.get(field)
    if value:
        qs = form._meta.model._default_manager.filter(**{field:value})
        if exclude_initial and form.initial:
            initial_value = form.initial.get(field)
            qs = qs.exclude(**{field:initial_value})
        if qs.count() > 0:
            raise forms.ValidationError(format % {'field':field, 'value':value})
    return value

class IssuerForm(forms.ModelForm):
    class Meta:
        model = Issuer
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        update = kwargs.pop('update')
        super(IssuerForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        if update:
            self.fields['reg_num'].widget.attrs['readonly'] = True
            self.fields['client_id'].widget.attrs['readonly'] = True
            self.fields['activity_code'].widget.attrs['readonly'] = True
            self.fields['type'].widget.attrs['readonly'] = True







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
        self.fields['country'].widget.attrs.update(width=200)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'



class IssuerOracleDBForm(forms.ModelForm):
    class Meta:
        model = IssuerOracleDB
        fields = '__all__'
        exclude = {'issuer',}
    def __init__(self , *args , **kwargs):
        super(IssuerOracleDBForm , self).__init__(*args , **kwargs)


class ReceiverForm(forms.ModelForm):
    class Meta:
        model = Receiver
        fields = '__all__'
        exclude = ('issuer',)
    def __init__(self, *args, **kwargs):
        super(ReceiverForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

AddressInlineForm = formset_factory(form=AddressForm, extra=1)
