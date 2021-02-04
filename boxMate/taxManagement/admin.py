from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import *
from import_export.forms import ImportForm, ConfirmImportForm
from import_export.admin import ImportExportModelAdmin, ImportMixin
from django import forms
from .resources import *


# Register your models here.


class InvoiceInline(admin.TabularInline):
    model = InvoiceLine 


@admin.register(InvoiceHeader)
class InvoiceHeaderAdmin(admin.ModelAdmin):
    inlines = [
        InvoiceInline,

    ]



@admin.register(MainTable)
class MainTableAdmin(ImportExportModelAdmin):
    resource_class = MainTableResource

