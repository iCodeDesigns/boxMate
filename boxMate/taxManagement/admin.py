from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import InvoiceLine, InvoiceHeader, MainTable


# Register your models here.
class InvoiceInline(admin.TabularInline):
    model = InvoiceLine


@admin.register(InvoiceHeader)
class InvoiceHeaderAdmin(admin.ModelAdmin):
    inlines = [
        InvoiceInline,

    ]


admin.site.register(MainTable)
