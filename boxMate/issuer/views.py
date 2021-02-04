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
from django.shortcuts import render,redirect
from codes.models import CountryCode


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



def get_issuer_data(request):
    issuer = MainTable.objects.values('issuer_registration_num').annotate(Count('issuer_registration_num'))
    issuer_code = issuer[0]['issuer_registration_num']
    try:
        issuer_id = Issuer.objects.get(reg_num=issuer_code)
    except Issuer.DoesNotExist as e:
        issuer_data = MainTable.objects.values(
        'issuer_type',
        'issuer_registration_num',
        'issuer_name').annotate(Count('issuer_registration_num'))
        for x in issuer_data:
            issuer_obj = Issuer(
                type = x['issuer_type'],
                reg_num = x['issuer_registration_num'],
                name = x['issuer_name']
            )
            issuer_obj.save()
            issuer_addresses = MainTable.objects.values(
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
            'issuer_branch_id').annotate(Count('issuer_building_num'))
            issuer_id = issuer_obj
            country = MainTable.objects.values('issuer_country').first()
            country_code = country.get("issuer_country")
            code_obj = CountryCode.objects.get(pk=country_code)
            for x in issuer_addresses:
                address_obj = Address(
                    issuer = issuer_id,
                    branch_id = x['issuer_branch_id'],
                    country = code_obj,
                    governate = x['issuer_governate'],
                    regionCity = x['issuer_governate'],
                    street = x['issuer_street'],
                    buildingNumber = x['issuer_building_num'],
                    postalCode = x['issuer_postal_code'],
                    floor = x['issuer_floor'],
                    room = x['issuer_room'],
                    landmark = x['issuer_land_mark'],
                    additionalInformation = x['issuer_additional_information']
                )
                address_obj.save()
        




