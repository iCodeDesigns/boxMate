from import_export.widgets import ForeignKeyWidget
from import_export import resources, fields
from .models import *


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
    """
    describes how columns of the model are displayed
    By: amira
    Date: 18-3-2021
    """

    class Meta:
        model = Address
        exclude = (
            'last_updated_at', 'created_by', 'last_updated_by', 'created_at', 'id', 'issuer', 'country', 'receiver')

    receiver__name = fields.Field(
        column_name='Receiver Name',
        attribute='name',
        widget=ForeignKeyWidget(Receiver, 'name')
    )
    receiver__type = fields.Field(
        column_name='Receiver Type',
        attribute='type',
        widget=ForeignKeyWidget(Receiver, 'Type')
    )
    receiver__reg_name = fields.Field(
        column_name='Registration Number',
        attribute='reg_num',
        widget=ForeignKeyWidget(Receiver, 'reg_num')
    )

    branch_id = fields.Field(
        column_name='Branch',
        attribute='branch_id'
    )
    governate = fields.Field(
        column_name='Governate',
        attribute='governate'
    )
    regionCity = fields.Field(
        column_name='Region City',
        attribute='regionCity'
    )
    street = fields.Field(
        column_name='Street',
        attribute='street'
    )
    buildingNumber = fields.Field(
        column_name='Building Number',
        attribute='buildingNumber'
    )
    postalCode = fields.Field(
        column_name='Postal Code',
        attribute='postalCode'
    )
    country = fields.Field(
        column_name='Country Code',
        attribute='country',
        widget=ForeignKeyWidget(CountryCode, 'code')
    )
    floor = fields.Field(
        column_name='Floor',
        attribute='floor'
    )
    room = fields.Field(
        column_name='Room',
        attribute='room'
    )
    landmark = fields.Field(
        column_name='landmark',
        attribute='Landmark'
    )
    additionalInformation = fields.Field(
        column_name='Additional Info',
        attribute='additionalInformation'
    )
