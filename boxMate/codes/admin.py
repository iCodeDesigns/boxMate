from django.contrib import admin
from codes.models import (ActivityType, CountryCode, UnitType, TaxTypes, TaxSubtypes)




admin.site.register(ActivityType)
admin.site.register(CountryCode)
admin.site.register(UnitType)
admin.site.register(TaxTypes)
admin.site.register(TaxSubtypes)
