import json

import requests
from django.shortcuts import render
from requests.auth import HTTPBasicAuth
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from taxManagement.resources import MainTableResource
from tablib import Dataset
from django.conf import settings
from taxManagement.tmp_storage import TempFolderStorage
from django.db.models import Count
from taxManagement.models import MainTable, InvoiceHeader, InvoiceLine, TaxTypes, TaxLine, Signature , Submission
from issuer.models import Issuer, Receiver
from codes.models import ActivityType, TaxSubtypes, TaxTypes
from rest_framework.decorators import api_view
from issuer.models import *
from codes.models import *
from pprint import pprint
from decimal import Decimal
from .serializers import InvoiceHeaderSerializer , SubmissionSerializer


@api_view(['POST', ])
def upload_excel_sheet(request):
    main_table_resource = MainTableResource()
    import_file = request.FILES['import_file']
    dataset = Dataset()
    # # unhash the following line in case of csv file
    # # imported_data = dataset.load(import_file.read().decode(), format='csv')
    imported_data = dataset.load(import_file.read(), format='xlsx')  # this line in case of excel file
    #
    result = main_table_resource.import_data(imported_data, dry_run=False)  # Test the data import
    tmp_storage = write_to_tmp_storage(import_file)
    if not result.has_errors() and not result.has_validation_errors():
        tmp_storage = TMP_STORAGE_CLASS(name=tmp_storage.name)
        data = tmp_storage.read('rb')
        # Uncomment the following line in case of 'csv' file
        # data = force_str(data, "utf-8")
        dataset = Dataset()
        # Enter format = 'csv' for csv file
        imported_data = dataset.load(data, format='xlsx')

        result = main_table_resource.import_data(imported_data,
                                                 dry_run=False,
                                                 raise_errors=True,
                                                 file_name=tmp_storage.name, )
        tmp_storage.remove()

    else:
        print(result.base_errors)
        data = {"success": False, "error": {"code": 400, "message": "Invalid Excel sheet"}}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    data = {"success": True}
    return Response(data, status=status.HTTP_200_OK)



@api_view(['GET',])
def get_all_invoice_headers(request):
    invoice_headers = InvoiceHeader.objects.all()
    # headers = []
    # for invoice_header in invoice_headers:
    #     header = get_invoice_header(invoice_header.internal_id)
    #     headers.append(header)
    if request.method == 'GET':
        serializer =  InvoiceHeaderSerializer(invoice_headers , many=True)
        return Response(serializer.data , status=status.HTTP_200_OK)



@api_view(['GET', ])
def submission_list(request):
    submissions = Submission.objects.all()
    if request.method == 'GET':
        submissions_serializer = SubmissionSerializer(submissions, many=True)
        return Response(submissions_serializer.data)


