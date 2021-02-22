from django.contrib import admin
from django.contrib.admin import site

from .models import Issuer, Address, Receiver, IssuerTax


# Register your models here.


class AddressInline(admin.TabularInline):
    model = Address


@admin.register(Issuer)
class IssuerAdmin(admin.ModelAdmin):
    inlines = [
        AddressInline,

    ]


site.register(Receiver)
site.register(IssuerTax)
