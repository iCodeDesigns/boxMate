from import_export.widgets import ForeignKeyWidget
from import_export import resources, fields
from .models import *


class ActivityTypeResource(resources.ModelResource):
    # this class describes how the model will be imported
    class Meta:
        model = ActivityType
        # id is required here to save attendance object
        import_id_fields = ('code',)# which fields are used as the id when importing
        # defines which model fields will be imported
        fields = ('code', 'desc_en', 'desc_ar')

    desc_en = fields.Field(
        column_name='Desc_en',  # this is the name of imported column
        attribute='desc_en',)  # this is the name of the model attribute it represents

    desc_ar = fields.Field(
        column_name='Desc_ar',  # this is the name of imported column
        attribute='desc_ar',)  # this is the name of the model attribute it represents



class CountryCodeResource(resources.ModelResource):
    class Meta:
        model = CountryCode
        import_id_fields = ('code',)
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
        import_id_fields = ('code',)
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
        import_id_fields = ('code',)
        fields = ('code', 'desc_en', 'desc_ar', 'is_taxable')



    code = fields.Field(
        column_name='Code',
        attribute='code',)

    desc_en = fields.Field(
        column_name='Desc_en',
        attribute='desc_en',)

    desc_ar = fields.Field(
        column_name='Desc_ar',
        attribute='desc_ar',)



class TaxSubtypeResource(resources.ModelResource):
    class Meta:
        model = TaxSubtypes
        import_id_fields = ('code',)
        fields = ('code', 'desc_en', 'desc_ar', 'taxtype_reference')
        
    code = fields.Field(
        column_name='Code',
        attribute='code',)

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
