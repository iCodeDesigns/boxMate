from rest_framework import serializers
from taxManagement.models import InvoiceHeader , Signature

class SignatureSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(required=False)

    class Meta:
        model = Signature
        fields = (
             'signature_type' , 'signature_value'
        )

class InvoiceHeaderSerializer(serializers.ModelSerializer):
    signatures = SignatureSerializer(many=True)
    class Meta:
        model = InvoiceHeader
        fields = (
            'id','signatures','document_type' , 'document_type_version' , 'date_time_issued' ,
            'taxpayer_activity_code' , 'internal_id' , 'purchase_order_reference',
            'purchase_order_description' , 'sales_order_reference' , 'sales_order_description',
            'proforma_invoice_number' , 'total_sales_amount' , 'total_discount_amount' ,
            'net_amount' , 'extra_discount_amount' , 'total_items_discount_amount','total_amount'
        )
