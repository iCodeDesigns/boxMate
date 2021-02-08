from django.db import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import api_view

from issuer.models import *
from issuer.serializers import IssuerSerializer
from taxManagement.models import *
from django.db.models import Count
from django.utils import timezone
from django.shortcuts import render, redirect
from codes.models import CountryCode
from django.shortcuts import get_object_or_404



# Create your views here.
@api_view(['POST', ])
def add_issuer(request):
    issuer_serializer = IssuerSerializer(data=request.data)
    if issuer_serializer.is_valid():
        try:
            issuer_serializer.save()
        except Exception as e:
            print(e)
            data = {"success": False, "error": {"code": 400, "message": "Issuer not created"}}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        data = {"success": True, "data": issuer_serializer.data}
        return Response(data, status=status.HTTP_201_CREATED)
    else:
        data = {"success": False, "error": {"code": 400, "message": issuer_serializer.errors}}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)


class IssuerListView(ListAPIView):
    serializer_class = IssuerSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_fields = ('id', 'reg_num',)
    ordering_fields = ('id',)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return Issuer.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            data = {"success": True, "count": paginated_response.data["count"], "data": serializer.data, }
            return Response(data)

        serializer = self.get_serializer(queryset, many=True)
        data = {"success": True, "data": serializer.data}
        return Response(data)


def get_issuer_data():
    issuer_data = MainTable.objects.values(
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
    for x in issuer_data:
        issuer_code = x['issuer_registration_num']
        address = x['issuer_branch_id']
        try:
            issuer_id = Issuer.objects.get(reg_num=issuer_code)
            try:
                address_id = Address.objects.get(branch_id=address)
            except Address.DoesNotExist as e:    
                country_code = x['issuer_country']
                code_obj = CountryCode.objects.get(pk=country_code)
                address_obj = Address(
                    issuer = issuer_id,
                    branch_id = x['issuer_branch_id'],
                    country = code_obj,
                    governate = x['issuer_governate'],
                    regionCity = x['issuer_region_city'],
                    street = x['issuer_street'],
                    buildingNumber = x['issuer_building_num'],
                    postalCode = x['issuer_postal_code'],
                    floor = x['issuer_floor'],
                    room = x['issuer_room'],
                    landmark = x['issuer_land_mark'],
                    additionalInformation = x['issuer_additional_information']
                )
                address_obj.save()    
        except Issuer.DoesNotExist as e:
            issuer_obj = Issuer(
                type = x['issuer_type'],
                reg_num = x['issuer_registration_num'],
                name = x['issuer_name']
            )
            issuer_obj.save()
            issuer_id = issuer_obj
            country_code = x['issuer_country']
            code_obj = CountryCode.objects.get(pk=country_code)
            address = x['issuer_branch_id']
            address_obj = Address(
                issuer = issuer_id,
                branch_id = x['issuer_branch_id'],
                country = code_obj,
                governate = x['issuer_governate'],
                regionCity = x['issuer_region_city'],
                street = x['issuer_street'],
                buildingNumber = x['issuer_building_num'],
                postalCode = x['issuer_postal_code'],
                floor = x['issuer_floor'],
                room = x['issuer_room'],
                landmark = x['issuer_land_mark'],
                additionalInformation = x['issuer_additional_information']
                )
            address_obj.save()
        

def get_receiver_data():
    receiver_data = MainTable.objects.values(
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
    for x in receiver_data: 
        receiver_code = x['receiver_registration_num']
        building_num = x['receiver_building_num']
        floor = x['receiver_floor']
        room = x['receiver_room']
        try:
            receiver_id = Receiver.objects.get(reg_num=receiver_code)
            address = Address.objects.filter(buildingNumber=building_num, floor=floor, room=room)
            if len(address) == 0 :
                country_code = x['receiver_country']
                code_obj = CountryCode.objects.get(pk=country_code)      
                address_obj = Address(
                    receiver = receiver_id,
                    country = code_obj,
                    governate = x['receiver_governate'],
                    regionCity = x['receiver_region_city'],
                    street = x['receiver_street'],
                    buildingNumber = x['receiver_building_num'],
                    postalCode = x['receiver_postal_code'],
                    floor = x['receiver_floor'],
                    room = x['receiver_room'],
                    landmark = x['receiver_land_mark'],
                    additionalInformation = x['receiver_additional_information']
                )
                address_obj.save()
        except Receiver.DoesNotExist as e:
            receiver_obj = Receiver(
                type = x['receiver_type'],
                reg_num = x['receiver_registration_num'],
                name = x['receiver_name']
            )
            receiver_obj.save()
            receiver_id = receiver_obj
            country_code = x['receiver_country']
            code_obj = CountryCode.objects.get(pk=country_code)
            address_obj = Address(
                receiver = receiver_id,
                country = code_obj,
                governate = x['receiver_governate'],
                regionCity = x['receiver_region_city'],
                street = x['receiver_street'],
                buildingNumber = x['receiver_building_num'],
                postalCode = x['receiver_postal_code'],
                floor = x['receiver_floor'],
                room = x['receiver_room'],
                landmark = x['receiver_land_mark'],
                additionalInformation = x['receiver_additional_information']
                )
            address_obj.save()
        
    
        

