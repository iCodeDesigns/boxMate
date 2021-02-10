from django.db import IntegrityError
from issuer.models import *
from issuer.api.serializers import IssuerSerializer
from taxManagement.models import *
from django.db.models import Count
from django.utils import timezone
from django.shortcuts import render, redirect
from codes.models import CountryCode
from django.shortcuts import get_object_or_404
from django.db.models import Q



def get_issuer_data():
    issuer_data = MainTable.objects.filter(~Q(issuer_registration_num=None)).values(
        'issuer_type',
        'issuer_registration_num',
        'issuer_name',
        'issuer_building_num',
        'issuer_room',
        'issuer_floor',
        'issuer_street',
        'issuer_land_mark',
        'issuer_additional_information',
        'issuer_governate',
        'issuer_region_city',
        'issuer_postal_code',
        'issuer_country',
        'issuer_branch_id').annotate(Count('issuer_registration_num'))
    print(issuer_data)
    for data in issuer_data:
        issuer_code = data['issuer_registration_num']
        address = data['issuer_branch_id']
        try:
            issuer_id = Issuer.objects.get(reg_num=issuer_code)
            try:
                address_id = Address.objects.get(branch_id=address)
            except Address.DoesNotExist as e:
                country_code = data['issuer_country']
                code_obj = CountryCode.objects.get(pk=country_code)
                address_obj = Address(
                    issuer = issuer_id,
                    branch_id = data['issuer_branch_id'],
                    country = code_obj,
                    governate = data['issuer_governate'],
                    regionCity = data['issuer_region_city'],
                    street = data['issuer_street'],
                    buildingNumber = data['issuer_building_num'],
                    postalCode = data['issuer_postal_code'],
                    floor = data['issuer_floor'],
                    room = data['issuer_room'],
                    landmark = data['issuer_land_mark'],
                    additionalInformation = data['issuer_additional_information']
                )
                address_obj.save()
        except Issuer.DoesNotExist as e:
            issuer_obj = Issuer(
                type=data['issuer_type'],
                reg_num=data['issuer_registration_num'],
                name=data['issuer_name']
            )
            issuer_obj.save()
            issuer_id = issuer_obj
            country_code = data['issuer_country']
            code_obj = CountryCode.objects.get(pk=country_code)
            address = data['issuer_branch_id']
            address_obj = Address(
                issuer=issuer_id,
                branch_id=data['issuer_branch_id'],
                country=code_obj,
                governate=data['issuer_governate'],
                regionCity=data['issuer_region_city'],
                street=data['issuer_street'],
                buildingNumber=data['issuer_building_num'],
                postalCode=data['issuer_postal_code'],
                floor=data['issuer_floor'],
                room=data['issuer_room'],
                landmark=data['issuer_land_mark'],
                additionalInformation=data['issuer_additional_information']
            )
            address_obj.save()
        

def get_receiver_data():
    receiver_data = MainTable.objects.filter(~Q(receiver_registration_num=None)).values(
        'receiver_type',
        'receiver_registration_num',
        'receiver_name',
        'receiver_building_num',
        'receiver_room',
        'receiver_floor',
        'receiver_street',
        'receiver_land_mark',
        'receiver_additional_information',
        'receiver_governate',
        'receiver_region_city',
        'receiver_postal_code',
        'receiver_country').annotate(Count('receiver_registration_num'))
    for data in receiver_data:
        receiver_code = data['receiver_registration_num']
        building_num = data['receiver_building_num']
        floor = data['receiver_floor']
        room = data['receiver_room']
        try:
            receiver_id = Receiver.objects.get(reg_num=receiver_code)
            address = Address.objects.filter(buildingNumber=building_num, floor=floor, room=room)
            if len(address) == 0:
                country_code = data['receiver_country']
                code_obj = CountryCode.objects.get(pk=country_code)
                address_obj = Address(
                    receiver=receiver_id,
                    country=code_obj,
                    governate=data['receiver_governate'],
                    regionCity=data['receiver_region_city'],
                    street=data['receiver_street'],
                    buildingNumber=data['receiver_building_num'],
                    postalCode=data['receiver_postal_code'],
                    floor=data['receiver_floor'],
                    room=data['receiver_room'],
                    landmark=data['receiver_land_mark'],
                    additionalInformation=data['receiver_additional_information']
                )
                address_obj.save()
        except Receiver.DoesNotExist as e:
            receiver_obj = Receiver(
                type=data['receiver_type'],
                reg_num=data['receiver_registration_num'],
                name=data['receiver_name']
            )
            receiver_obj.save()
            receiver_id = receiver_obj
            country_code = data['receiver_country']
            code_obj = CountryCode.objects.get(pk=country_code)
            address_obj = Address(
                receiver=receiver_id,
                country=code_obj,
                governate=data['receiver_governate'],
                regionCity=data['receiver_region_city'],
                street=data['receiver_street'],
                buildingNumber=data['receiver_building_num'],
                postalCode=data['receiver_postal_code'],
                floor=data['receiver_floor'],
                room=data['receiver_room'],
                landmark=data['receiver_land_mark'],
                additionalInformation=data['receiver_additional_information']
            )
            address_obj.save()
    


def list_uploaded_invoice(request):
    return render(request, 'upload-invoice.html')