from django.contrib import admin
from import_export.forms import ImportForm, ConfirmImportForm
from import_export.admin import ImportExportModelAdmin, ImportMixin
from django import forms
from .resources import *
from .models import *


# Register your models here.


@admin.register(ActivityType)
class ActivityTypeAdmin(ImportExportModelAdmin):
    resource_class = ActivityTypeResource
    fields = (
         'code',
         'desc_en',
         'desc_ar',
    )
    list_display = ('code', 'desc_en', 'desc_ar',)




@admin.register(CountryCode)
class CountryCodeAdmin(ImportExportModelAdmin):
    resource_class = CountryCodeResource
    fields = (
         'code',
         'desc_en',
         'desc_ar',
    )
    list_display = ('code', 'desc_en', 'desc_ar',)




@admin.register(UnitType)
class UnitTypeAdmin(ImportExportModelAdmin):
    resource_class = UnitTypeResource
    fields = (
         'code',
         'desc_en',
         'desc_ar',
    )
    list_display = ('code', 'desc_en', 'desc_ar',)




@admin.register(TaxTypes)
class TaxTypeAdmin(ImportExportModelAdmin):
    resource_class = TaxTypeResource
    fields = (
         'code',
         'Desc_en',
         'desc_ar',
    )
    list_display = ('code', 'desc_en', 'desc_ar',)




@admin.register(TaxSubtypes)
class TaxSubtypeAdmin(ImportExportModelAdmin):
    resource_class = TaxSubtypeResource
    fields = (
         'code',
         'Desc_en',
         'desc_ar',
         'taxtype_reference',
    )
    list_display = ('code', 'desc_en', 'desc_ar','taxtype_reference',)
