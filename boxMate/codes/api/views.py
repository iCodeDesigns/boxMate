
import json
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import api_view
from codes.api.serializers import ActivityTypeSerializer
from codes.models import ActivityType
import requests
from django.http import HttpResponse
from django.shortcuts import render, redirect
from codes.resources import (ActivityTypeResource, TaxTypeResource, 
                            TaxSubtypeResource, CountryCodeResource, UnitTypeResource)
from tablib import Dataset
from rest_framework.decorators import api_view
from django.conf import settings
from taxManagement.tmp_storage import TempFolderStorage
from codes.models import ActivityType , TaxTypes , TaxSubtypes , CountryCode , UnitType

TMP_STORAGE_CLASS = getattr(settings, 'IMPORT_EXPORT_TMP_STORAGE_CLASS',
                            TempFolderStorage)


def write_to_tmp_storage(import_file):
    tmp_storage = TMP_STORAGE_CLASS()
    data = bytes()
    for chunk in import_file.chunks():
        data += chunk

    tmp_storage.save(data, 'rb')
    return tmp_storage

@api_view(['POST', ])
def activity_type_upload(request):
    activity_type_resource = ActivityTypeResource()
    import_file = request.FILES['import_file']
    dataset = Dataset()

    imported_data = dataset.load(import_file.read(), format='json')
    
    result = activity_type_resource.import_data(
                imported_data, dry_run=False)  # Test the data import
    tmp_storage = write_to_tmp_storage(import_file)
    if not result.has_errors() and not result.has_validation_errors():
        tmp_storage = TMP_STORAGE_CLASS(name=tmp_storage.name)
        data = tmp_storage.read('rb')
        
        dataset = Dataset()
        # Enter format = 'csv' for csv file
        success = ActivityType.objects.all().delete()
        if not success:
            return HttpResponse(status = 500)
        imported_data = dataset.load(data, format='json')

        result = activity_type_resource.import_data(imported_data,
                                                 dry_run=False,
                                                 raise_errors=True,
                                                 file_name=tmp_storage.name, )
        tmp_storage.remove()

    else:
        data = {"success": False, "error": {
                "code": 400, "message": "Invalid Json Data"}}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    data = {"success": True}

    context = {
        'data': 'data'
    }
    return HttpResponse(status = 200)


@api_view(['POST', ])
def tax_type_upload(request):
    tax_type_resource =TaxTypeResource()
    import_file = request.FILES['import_file']
    dataset = Dataset()

    imported_data = dataset.load(import_file.read(), format='json')
    
    result = tax_type_resource.import_data(
                imported_data, dry_run=False)  # Test the data import
    tmp_storage = write_to_tmp_storage(import_file)
    if not result.has_errors() and not result.has_validation_errors():
        tmp_storage = TMP_STORAGE_CLASS(name=tmp_storage.name)
        data = tmp_storage.read('rb')
        
        dataset = Dataset()
        # Enter format = 'csv' for csv file
        success = TaxTypes.objects.all().delete()
        if not success:
            return HttpResponse(status = 500)
        imported_data = dataset.load(data, format='json')

        result = tax_type_resource.import_data(imported_data,
                                                 dry_run=False,
                                                 raise_errors=True,
                                                 file_name=tmp_storage.name, )
        tmp_storage.remove()

    else:
        data = {"success": False, "error": {
                "code": 400, "message": "Invalid Json Data"}}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    data = {"success": True}

    context = {
        'data': 'data'
    }
    return HttpResponse(status = 200)

@api_view(['POST', ])
def tax_subtype_upload(request):
    tax_subtype_resource =TaxSubtypeResource()
    import_file = request.FILES['import_file']
    dataset = Dataset()

    imported_data = dataset.load(import_file.read(), format='json')
    
    result = tax_subtype_resource.import_data(
                imported_data, dry_run=False)  # Test the data import
    tmp_storage = write_to_tmp_storage(import_file)
    if not result.has_errors() and not result.has_validation_errors():
        tmp_storage = TMP_STORAGE_CLASS(name=tmp_storage.name)
        data = tmp_storage.read('rb')
        
        dataset = Dataset()
        # Enter format = 'csv' for csv file
        success = TaxSubtypes.objects.all().delete()
        if not success:
            return HttpResponse(status = 500)
        imported_data = dataset.load(data, format='json')

        result = tax_subtype_resource.import_data(imported_data,
                                                 dry_run=False,
                                                 raise_errors=True,
                                                 file_name=tmp_storage.name, )
        tmp_storage.remove()

    else:
        data = {"success": False, "error": {
                "code": 400, "message": "Invalid Json Data"}}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    data = {"success": True}

    context = {
        'data': 'data'
    }
    return HttpResponse(status = 200)

@api_view(['POST', ])
def unit_type_upload(request):
    unit_type_resource =UnitTypeResource()
    import_file = request.FILES['import_file']
    dataset = Dataset()

    imported_data = dataset.load(import_file.read(), format='json')
    
    result = unit_type_resource.import_data(
                imported_data, dry_run=False)  # Test the data import
    tmp_storage = write_to_tmp_storage(import_file)
    if not result.has_errors() and not result.has_validation_errors():
        tmp_storage = TMP_STORAGE_CLASS(name=tmp_storage.name)
        data = tmp_storage.read('rb')
        
        dataset = Dataset()
        # Enter format = 'csv' for csv file
        success = UnitType.objects.all().delete()
        if not success:
            return HttpResponse(status = 500)
        imported_data = dataset.load(data, format='json')

        result = unit_type_resource.import_data(imported_data,
                                                 dry_run=False,
                                                 raise_errors=True,
                                                 file_name=tmp_storage.name, )
        tmp_storage.remove()

    else:
        data = {"success": False, "error": {
                "code": 400, "message": "Invalid Json Data"}}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    data = {"success": True}

    context = {
        'data': 'data'
    }
    return HttpResponse(status = 200)


@api_view(['POST', ])
def country_code_upload(request):
    country_code_resource =CountryCodeResource()
    import_file = request.FILES['import_file']
    dataset = Dataset()

    imported_data = dataset.load(import_file.read(), format='json')
    
    result = country_code_resource.import_data(
                imported_data, dry_run=False)  # Test the data import
    tmp_storage = write_to_tmp_storage(import_file)
    if not result.has_errors() and not result.has_validation_errors():
        tmp_storage = TMP_STORAGE_CLASS(name=tmp_storage.name)
        data = tmp_storage.read('rb')
        
        dataset = Dataset()
        # Enter format = 'csv' for csv file
        success = CountryCode.objects.all().delete()
        if not success:
            return HttpResponse(status = 500)
        imported_data = dataset.load(data, format='json')

        result = country_code_resource.import_data(imported_data,
                                                 dry_run=False,
                                                 raise_errors=True,
                                                 file_name=tmp_storage.name, )
        tmp_storage.remove()

    else:
        data = {"success": False, "error": {
                "code": 400, "message": "Invalid Json Data"}}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    data = {"success": True}

    context = {
        'data': 'data'
    }
    return HttpResponse(status = 200)


@api_view(['POST', ])
def add_activity_code(request):
    activity_code_serializer = ActivityTypeSerializer(data=request.data)
    if activity_code_serializer.is_valid():
        try:
            activity_code_serializer.save()
        except Exception as e:
            print(e)
            data = {"success": False, "error": {"code": 400, "message": "ِActivity type not created"}}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        data = {"success": True, "data": activity_code_serializer.data}
        return Response(data, status=status.HTTP_201_CREATED)
    else:
        data = {"success": False, "error": {"code": 400, "message": activity_code_serializer.errors}}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

class ActivityListView(ListAPIView):
    serializer_class = ActivityTypeSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_fields = ('code',)
    ordering_fields = ('code',)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return ActivityType.objects.all()

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

