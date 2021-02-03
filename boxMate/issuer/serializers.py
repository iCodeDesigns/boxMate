from rest_framework import serializers
from issuer.models import Address, Issuer


class AddressSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Address
        #exclude = ('created_at', 'last_updated_at', 'created_by', 'last_updated_by',)
        fields = (
        'id', 'branch_id', 'country', 'governate', 'regionCity', 'street', 'buildingNumber', 'postalCode', 'floor',
        'room', 'landmark', 'additionalInformation')


class IssuerSerializer(serializers.ModelSerializer):
    issuer_addresses = AddressSerializer(many=True)

    class Meta:
        model = Issuer
        fields = ('id','issuer_addresses', 'type', 'reg_num', 'name', 'client_id', 'clientSecret1', 'clientSecret2')
        read_only_fields = ('id',)

    def create(self, validated_data):
        address_data = validated_data.pop('issuer_addresses')
        print("******", validated_data)
        issuer = Issuer.objects.create(**validated_data)
        for address in address_data:
            Address.objects.create(issuer=issuer, **address)
        return issuer
