from import_export.widgets import ForeignKeyWidget
from import_export import resources, fields
from .models import *
from taxManagement.models import MainTable


class IssuerResource(resources.ModelResource):
    # this class describes how the model will be imported
    class Meta:
        model = Issuer
        # defines which model fields will be imported
        exclude = ('last_updated_at', 'created_by', 'last_updated_by',)
        fields = ('type', 'name',)

    reg_num = fields.Field(
        column_name='id',  # this is the name of imported column
        attribute='reg_num', )  # this is the name of the model attribute it represents

    def after_import_instance(self, instance, new, **kwargs):
        user = User.objects.get(id=1)
        if new or not instance.created_by:
            instance.client_id = user
        instance.clientSecret1 = user
        instance.clientSecret2 = user
        instance.created_at = user
        instance.clientSecret1 = user


class ReceiverResource(resources.ModelResource):
    class Meta:
        model = MainTable
        fields = (
            'id',
            'receiver_type', 'receiver_registration_num', 'receiver_name',
            'receiver_building_num', 'receiver_room', 'receiver_floor',
            'receiver_street', 'receiver_land_mark', 'receiver_additional_information',
            'receiver_region_city', 'receiver_postal_code', 'receiver_country'

        )

    receiver_type = fields.Field(
        column_name='receiver_type',
        attribute='receiver_type', )

    receiver_registration_num = fields.Field(
        column_name='receiver_registration_num',
        attribute='receiver_registration_num', )

    receiver_name = fields.Field(
        column_name='receiver_name',
        attribute='receiver_name', )

    receiver_building_num = fields.Field(
        column_name='receiver_building_num',
        attribute='receiver_building_num', )

    receiver_room = fields.Field(
        column_name='receiver_room',
        attribute='receiver_room', )

    receiver_floor = fields.Field(
        column_name='receiver_floor',
        attribute='receiver_floor', )

    receiver_street = fields.Field(
        column_name='receiver_street',
        attribute='receiver_street', )

    receiver_land_mark = fields.Field(
        column_name='receiver_land_mark',
        attribute='receiver_land_mark', )

    receiver_additional_information = fields.Field(
        column_name='receiver_additional_information',
        attribute='receiver_additional_information', )

    receiver_governate = fields.Field(
        column_name='receiver_governate',
        attribute='receiver_governate', )

    receiver_region_city = fields.Field(
        column_name='receiver_region_city',
        attribute='receiver_region_city', )

    receiver_postal_code = fields.Field(
        column_name='receiver_postal_code',
        attribute='receiver_postal_code', )

    receiver_country = fields.Field(
        column_name='receiver_country',
        attribute='receiver_country', )

    def after_import_instance(self, instance, new, **kwargs):
        instance.user = kwargs['user']
