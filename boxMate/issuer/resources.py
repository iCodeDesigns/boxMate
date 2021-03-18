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
        model = Receiver
        exclude = ('last_updated_at', 'created_by', 'last_updated_by', 'created_at', 'id')

    name = fields.Field(
        column_name='Receiver Name',
        attribute='name',
    )

    type = fields.Field(
        column_name='Type',
        attribute='type',
    )

    issuer = fields.Field(
        column_name='Issuer',
        attribute='issuer',
    )

    reg_num = fields.Field(
        column_name='Registration Number',
        attribute='reg_num',
    )
