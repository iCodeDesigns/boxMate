from import_export.widgets import ForeignKeyWidget
from import_export import resources, fields
from .models import *


class ActivityTypeResource(resources.ModelResource):
    # this class describes how the model will be imported
    class Meta:
        model = ActivityType
        fields = ('code', 'desc_en', 'desc_ar')
        exclude = ('id',)
          # defines which model fields will be imported
        # id is required here to save attendance object

    desc_en = fields.Field(
        column_name='Desc_en',  # this is the name of imported column
        attribute='desc_en',)  # this is the name of the model attribute it represents

    desc_ar = fields.Field(
        column_name='Desc_ar',  # this is the name of imported column
        attribute='desc_ar',)  # this is the name of the model attribute it represents



class CountryCodeResource(resources.ModelResource):
    class Meta:
        model = CountryCode
        fields = ('code', 'desc_en', 'desc_ar') 

    desc_en = fields.Field(
        column_name='Desc_en',  
        attribute='desc_en',)
    
    desc_ar = fields.Field(
        column_name='Desc_ar',  
        attribute='desc_ar',)    



class UnitTypeResource(resources.ModelResource):
    class Meta:
        model = UnitType
        fields = ('code', 'desc_en', 'desc_ar') 

    desc_en = fields.Field(
        column_name='desc_en', 
        attribute='desc_en',)
    
    desc_ar = fields.Field(
        column_name='desc_ar',  
        attribute='desc_ar',)    



class TaxTypeResource(resources.ModelResource):
    class Meta:
        model = TaxTypes
        fields = ('code', 'desc_en', 'desc_ar')  

    desc_en = fields.Field(
        column_name='Desc_en',  
        attribute='desc_en',)
    
    desc_ar = fields.Field(
        column_name='Desc_ar', 
        attribute='desc_ar',)

            

class TaxSubtypeResource(resources.ModelResource):
    class Meta:
        model = TaxSubtypes
        fields = ('code', 'desc_en', 'desc_ar', 'taxtype_reference')  

    desc_en = fields.Field(
        column_name='Desc_en',  
        attribute='desc_en',)
    
    desc_ar = fields.Field(
        column_name='Desc_ar',  
        attribute='desc_ar',)        


    taxtype_reference = fields.Field(
        column_name='TaxtypeReference',  
        attribute='taxtype_reference',  
        widget=ForeignKeyWidget(TaxTypes, 'pk')) 
