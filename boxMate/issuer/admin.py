from django.contrib import admin
from .models import Issuer, Address


# Register your models here.


class AddressInline(admin.TabularInline):
    model = Address


@admin.register(Issuer)
class IssuerAdmin(admin.ModelAdmin):
    inlines = [
        AddressInline,

    ]
