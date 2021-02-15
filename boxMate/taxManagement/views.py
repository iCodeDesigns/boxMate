import json

import requests
from django.shortcuts import render, redirect
from requests.auth import HTTPBasicAuth
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from demjson import decode
from taxManagement.resources import MainTableResource
from tablib import Dataset
from django.conf import settings
from taxManagement.tmp_storage import TempFolderStorage
from django.db.models import Count
from .models import MainTable, InvoiceHeader, InvoiceLine, TaxTypes, TaxLine, Signature, Submission
from issuer.models import Issuer, Receiver
from codes.models import ActivityType, TaxSubtypes, TaxTypes
from rest_framework.decorators import api_view
from issuer.models import *
from codes.models import *
from django.db.models import Q

from pprint import pprint
from decimal import Decimal
from django.http import HttpResponse, HttpResponseRedirect
from issuer import views as issuer_views
import time
from taxManagement.db_connection import get_data_from_db
TMP_STORAGE_CLASS = getattr(settings, 'IMPORT_EXPORT_TMP_STORAGE_CLASS',
                            TempFolderStorage)

auth_token = ""


def write_to_tmp_storage(import_file):
    tmp_storage = TMP_STORAGE_CLASS()
    data = bytes()
    for chunk in import_file.chunks():
        data += chunk

    tmp_storage.save(data, 'rb')
    return tmp_storage


# @api_view(['POST', ])
def import_data_to_invoice():
    headers = MainTable.objects.filter(~Q(internal_id=None)).values('document_type', 'document_type_version',
                                                                    'date_time_issued', 'taxpayer_activity_code',
                                                                    'internal_id',
                                                                    'purchase_order_reference',
                                                                    'purchase_order_description',
                                                                    'sales_order_reference',
                                                                    'sales_order_description',
                                                                    'proforma_invoice_number', 'total_sales_amount',
                                                                    'total_discount_amount', 'net_amount',
                                                                    'total_amount', 'total_items_discount_amount',
                                                                    'extra_discount_amount', 'issuer_registration_num',
                                                                    'receiver_registration_num',
                                                                    'signature_type', 'signature_value',
                                                                    'issuer_branch_id', 'receiver_building_num',
                                                                    'receiver_floor', 'receiver_room').annotate(
        Count('internal_id'))
    for header in headers:
        try:
            old_header = InvoiceHeader.objects.get(internal_id=header["internal_id"])
            old_header.delete()
        except InvoiceHeader.DoesNotExist:
            pass
        issuer = Issuer.objects.get(reg_num=header['issuer_registration_num'])
        issuer_address = Address.objects.get(branch_id=header['issuer_branch_id'])
        receiver = Receiver.objects.get(reg_num=header['receiver_registration_num'])
        receiver_address = Address.objects.get(receiver=receiver.id, buildingNumber=header['receiver_building_num'],
                                               floor=header['receiver_floor'], room=header['receiver_room'])
        taxpayer_activity_code = ActivityType.objects.get(code=header['taxpayer_activity_code'])
        header_obj = InvoiceHeader(
            issuer=issuer,
            issuer_address=issuer_address,
            receiver=receiver,
            receiver_address=receiver_address,
            document_type=header['document_type'],
            document_type_version=header['document_type_version'],
            date_time_issued=header['date_time_issued'],
            taxpayer_activity_code=taxpayer_activity_code,
            internal_id=header['internal_id'],
            purchase_order_reference=header['purchase_order_reference'],
            purchase_order_description=header['purchase_order_description'],
            sales_order_reference=header['sales_order_reference'],
            sales_order_description=header['sales_order_description'],
            proforma_invoice_number=header['proforma_invoice_number'],
            total_sales_amount=header['total_sales_amount'],
            total_discount_amount=header['total_discount_amount'],
            net_amount=header['net_amount'],
            extra_discount_amount=header['extra_discount_amount'],
            total_items_discount_amount=header['total_items_discount_amount'],
            total_amount=header['total_amount'],
        )
        header_obj.save()
        ####### create signature #######
        signature_obj = Signature(
            invoice_header=header_obj,
            signature_type=header['signature_type'],
            signature_value=header['signature_value']
        )
        signature_obj.save()
        ####### create lines per invoice header #######
        lines = MainTable.objects.filter(~Q(item_code=None)).values('description', 'item_code', 'item_type',
                                                                    'unit_type', 'quantity', 'sales_total',
                                                                    'currency_sold', 'amount_egp',
                                                                    'amount_sold', 'currency_exchange_rate', 'total',
                                                                    'value_difference',
                                                                    'total_taxable_fees', 'items_discount', 'net_total',
                                                                    'discount_rate',
                                                                    'discount_amount', 'internal_code').annotate(
            Count('item_code'))
        for line in lines:
            line_obj = InvoiceLine(
                invoice_header=header_obj,
                description=line['description'],
                itemType=line['item_type'],
                itemCode=line['item_code'],
                unitType=line['unit_type'],
                quantity=line['quantity'],
                currencySold=line['currency_sold'],
                amountEGP=line['amount_egp'],
                # amountSold=line['amount_sold'],
                # currencyExchangeRate=line['currency_exchange_rate'],
                salesTotal=line['sales_total'],
                total=line['total'],
                valueDifference=line['value_difference'],
                totalTaxableFees=line['total_taxable_fees'],
                itemsDiscount=line['items_discount'],
                netTotal=line['net_total'],
                rate=line['discount_rate'],
                amount=line['discount_amount'],
                internalCode=line['internal_code'],
            )
            line_obj.save()
            ##### create tax lines per invoice line #####
            tax_types = MainTable.objects.filter(~Q(item_code=None)).values('taxt_item_type', 'tax_item_amount',
                                                                            'tax_item_subtype',
                                                                            'tax_item_rate').annotate(
                Count('internal_id')).annotate(Count('item_code'))
            for tax_type in tax_types:
                tax_main_type = TaxTypes.objects.get(code=tax_type['taxt_item_type'])
                tax_subtype = TaxSubtypes.objects.get(code=tax_type['tax_item_subtype'])
                tax_type_obj = TaxLine(
                    invoice_line=line_obj,
                    taxType=tax_main_type,
                    subType=tax_subtype,
                    amount=tax_type['tax_item_amount'],
                    rate=tax_type['tax_item_rate']
                )
                tax_type_obj.save()
        header_obj.calculate_total_sales()
        header_obj.calculate_total_item_discount()
        header_obj.calculate_net_total()
        header_obj.save()


# Create your views here.
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
        success = MainTable.objects.all().delete()
        if not success:
            return redirect('/tax/list/uploaded-invoices')
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
    issuer_views.get_issuer_data()
    issuer_views.get_receiver_data()
    import_data_to_invoice()
    context = {
        'data': 'data'
    }
    return redirect('/tax/list/uploaded-invoices')


def get_issuer_body(invoice_id):
    invoice = InvoiceHeader.objects.get(internal_id=invoice_id)
    issuer_id = invoice.issuer
    issuer = Issuer.objects.get(id=issuer_id.id)

    type = issuer.type
    reg_num = issuer.reg_num
    name = issuer.name

    address = get_issuer_address(invoice_id)

    return {
        "type": type,
        "id": '100324932',
        "name": name,
        "address": address,
    }


def get_receiver_body(invoice_id):
    invoice = InvoiceHeader.objects.get(internal_id=invoice_id)
    receiver_id = invoice.receiver
    receiver = Receiver.objects.get(id=receiver_id.id)

    type = receiver.type
    reg_num = receiver.reg_num
    name = receiver.name

    address = get_receiver_address(invoice_id)

    return {
        "type": type,
        "id": reg_num,
        "name": name,
        "address": address,
    }


def get_issuer_address(invoice_id):
    invoice = InvoiceHeader.objects.get(internal_id=invoice_id)
    address_id = invoice.issuer_address
    address = Address.objects.get(id=address_id.id)

    country_id = address.country
    country_code = CountryCode.objects.get(code=country_id.code)
    country = country_code.code
    branchID = address.branch_id
    governate = address.governate
    regionCity = address.regionCity
    street = address.street
    buildingNumber = address.buildingNumber
    postalCode = address.postalCode
    floor = address.floor
    room = address.room
    landmark = address.landmark
    additionalInformation = address.additionalInformation

    return {
        "branchID": branchID,
        "country": country,
        "governate": governate,
        "regionCity": regionCity,
        "street": street,
        "buildingNumber": buildingNumber,
        "postalCode": postalCode,
        "floor": floor,
        "room": room,
        "landmark": landmark,
        "additionalInformation": additionalInformation
    }


def get_receiver_address(invoice_id):
    invoice = InvoiceHeader.objects.get(internal_id=invoice_id)
    address_id = invoice.receiver_address
    address = Address.objects.filter(id=address_id.id)[0]
    #
    country_id = address.country
    country_code = CountryCode.objects.get(code=country_id.code)
    country = country_code.code
    #
    governate = address.governate
    regionCity = address.regionCity
    street = address.street
    buildingNumber = address.buildingNumber
    postalCode = address.postalCode
    floor = address.floor
    room = address.room
    landmark = address.landmark
    additionalInformation = address.additionalInformation
    return {

            "country": country,
            "governate": governate,
            "regionCity": regionCity,
            "street": street,
            "buildingNumber": buildingNumber,
            "postalCode": postalCode,
            "floor": floor,
            "room": room,
            "landmark": landmark,
            "additionalInformation": additionalInformation

    }


def get_invoice_header(invoice_id):
    invoice_header = InvoiceHeader.objects.get(internal_id=invoice_id)
    signatures = Signature.objects.filter(invoice_header=invoice_header)
    signature_list = []
    for signature in signatures:
        signature_obj = {
            "signatureType": signature.signature_type,
            "value": signature.signature_value
        }
        signature_list.append(signature_obj)

    data = {
        "documentType": invoice_header.document_type,
        "documentTypeVersion": invoice_header.document_type_version,
        "dateTimeIssued": datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + "Z",
        "taxpayerActivityCode": invoice_header.taxpayer_activity_code.code,
        "internalID": invoice_header.internal_id,
        "purchaseOrderReference": invoice_header.purchase_order_reference,
        "purchaseOrderDescription": invoice_header.purchase_order_description,
        "salesOrderReference": invoice_header.sales_order_description,
        "salesOrderDescription": invoice_header.sales_order_description,
        "proformaInvoiceNumber": invoice_header.proforma_invoice_number,
        # "payment": {
        #     "bankName": "SomeValue",
        #     "bankAddress": "SomeValue",
        #     "bankAccountNo": "SomeValue",
        #     "bankAccountIBAN": "",
        #     "swiftCode": "",
        #     "terms": "SomeValue"
        # },
        # "delivery": {
        #     "approach": "SomeValue",
        #     "packaging": "SomeValue",
        #     "dateValidity": "2020-09-28T09:30:10Z",
        #     "exportPort": "SomeValue",
        #     "countryOfOrigin": "LS",
        #     "grossWeight": 10.59100,
        #     "netWeight": 20.58700,
        #     "terms": "SomeValue"
        # },
        "totalDiscountAmount": invoice_header.total_discount_amount.__float__(),
        "totalSalesAmount": invoice_header.total_sales_amount.__float__(),
        "netAmount": invoice_header.net_amount.__float__(),
        "taxTotals": [
            #     {
            #         "taxType": "T1",
            #         "amount": 1286.79112
            #     },
            #     {
            #         "taxType": "T2",
            #         "amount": 984.78912
            #     }
        ],
        "totalAmount": invoice_header.total_amount.__float__(),
        "extraDiscountAmount": invoice_header.extra_discount_amount.__float__(),
        "totalItemsDiscountAmount": invoice_header.total_items_discount_amount.__float__(),
        "signatures": signature_list
    }
    return data


def get_invoice_lines(invoice_id):
    invoice_lines = InvoiceLine.objects.filter(invoice_header__internal_id=invoice_id)
    invoice_lines_list = []
    for line in invoice_lines:
        invoice_line = {
            "description": line.description, "itemType": line.itemType,
            "itemCode": line.itemCode, "unitType": line.unitType, "quantity": line.quantity.__float__(),
            "internalCode": line.internalCode, "salesTotal": line.salesTotal.__float__(),
            "total": line.total.__float__(),
            "valueDifference": line.valueDifference.__float__(), "totalTaxableFees": line.totalTaxableFees.__float__(),
            "netTotal": line.netTotal.__float__(), "itemsDiscount": line.itemsDiscount.__float__(),
            "unitValue": {},
            "discount": {"rate": line.rate.__float__(), "amount": line.amount.__float__()}
        }

        taxable_lines = get_taxable_lines(line.id)
        invoice_line.update({"taxableItems": taxable_lines})
        invoice_lines_list.append(invoice_line)
    return invoice_lines_list


def get_taxable_lines(invoice_line_id):
    tax_lines = TaxLine.objects.filter(invoice_line__id=invoice_line_id)
    tax_lines_list = []
    for line in tax_lines:
        tax_line = {"taxType": line.taxType.code, "amount": line.amount.__float__(),
                    "subType": line.subType.code, "rate": line.rate.__float__()}
        tax_lines_list.append(tax_line)
    return tax_lines_list


def get_one_invoice(invoice_id):
    issuer_body = get_issuer_body(invoice_id)
    receiver_body = get_receiver_body(invoice_id)
    invoice_header = get_invoice_header(invoice_id)
    invoice_lines = get_invoice_lines(invoice_id)
    invoice = {
        "issuer": issuer_body,
        "receiver": receiver_body,

    }
    invoice.update(invoice_header)
    invoice.update({"invoiceLines": invoice_lines})

    return invoice


def get_submition_response(submission_id):
    url = 'https://api.preprod.invoicing.eta.gov.eg/api/v1.0/documentSubmissions/' + submission_id + '?PageSize=1'
    response = requests.get(url, verify=False,
                            headers={'Authorization': 'Bearer ' + auth_token, }
                            )
    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        get_token()
        response = requests.get(url, verify=False,
                                headers={'Authorization': 'Bearer ' + auth_token, }
                                )

    if (response.status_code != status.HTTP_200_OK):
        time.sleep(10)
        response = requests.get(url, verify=False,
                                headers={'Authorization': 'Bearer ' + auth_token, }
                                )
    response_code = response
    response_json = response_code.json()
    documentCount = response_json['documentCount']
    dateTimeReceived = response_json['dateTimeReceived']
    overallStatus = response_json['overallStatus']

    documentSummary = response_json['documentSummary']
    uuid = documentSummary[0]['uuid']
    submission = Submission.objects.get(subm_id=submission_id)
    submission.subm_uuid = uuid
    submission.document_count = documentCount
    submission.date_time_received = dateTimeReceived
    submission.over_all_status = overallStatus
    submission.save()

    return response


def save_submition_response(invoice_id, submission_id):
    invoice = InvoiceHeader.objects.get(internal_id=invoice_id)
    try:
        old_sub = Submission.objects.get(invoice__internal_id=invoice_id)
        old_sub.subm_id = submission_id
        old_sub.save()
    except Submission.DoesNotExist:
        submission_obj = Submission(
            invoice=invoice,
            subm_id=submission_id,
        )
        submission_obj.save()
    get_submition_response(submission_id)


def submit_invoice(request, invoice_id):
    invoice = get_one_invoice(invoice_id)
    json_data = json.dumps({'documents': [invoice]})
    data = decode(json_data)
    print(json_data)
    url = 'https://api.preprod.invoicing.eta.gov.eg/api/v1/documentsubmissions'
    response = requests.post(url, verify=False,
                             headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + auth_token},
                             json=data)
    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        get_token()
        response = requests.post(url, verify=False,
                                 headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + auth_token},
                                 json=data)

    response_code = response
    response_json = response_code.json()
    submissionId = response_json['submissionId']

    acceptedDocuments = response_json['acceptedDocuments']
    uuid = acceptedDocuments[0]['uuid']

    internalId = acceptedDocuments[0]['internalId']
    save_submition_response(internalId, submissionId)
    return redirect('taxManagement:get-all-invoice-headers')
    # return response


def submission_list(request):
    submissions = Submission.objects.all()
    context = {
        'submissions': 'submissions'
    }
    return render(request, 'list-submissions.html', context=context)


##### get all invoices ######

def get_all_invoice_headers(request):
    invoice_headers = InvoiceHeader.objects.all()
    count = 0
    for invoice_header in invoice_headers:
        submissions = Submission.objects.filter(invoice=invoice_header).last()
        invoice_headers[count].submissions = submissions
        count += 1
    context = {
        "invoice_headers": invoice_headers
    }
    return render(request, 'upload-invoice.html', context)
    # headers = []
    # for invoice_header in invoice_headers:
    #     header = get_invoice_header(invoice_header.internal_id)
    #     headers.append(header)
    # if request.method == 'GET':
    #     serializer =  InvoiceHeaderSerializer(invoice_headers , many=True)
    #     return Response(serializer.data , status=status.HTTP_200_OK)


def get_decument_detail_after_submit(request, doc_uuid):
    url = 'https://api.preprod.invoicing.eta.gov.eg/api/v1/documents/' + doc_uuid + '/details'
    response = requests.get(url, verify=False,
                            headers={'Authorization': 'Bearer ' + auth_token, }
                            )
    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        get_token()
        response = requests.get(url, verify=False,
                                headers={'Authorization': 'Bearer ' + auth_token, }
                                )

    validation_steps = response.json()['validationResults']['validationSteps']
    header_errors=[]
    lines_errors=[]
    for validation_step in validation_steps:
        if validation_step['status'] == 'Invalid':
            inner_errors = validation_step['error']['innerError']
            for inner_error in inner_errors:
                if inner_error['propertyPath'].startswith('invoiceLine') :
                    lines_errors.append(inner_error['error'])
                elif inner_error['propertyPath'].startswith('document'):
                    header_errors.append(inner_error['error'])


    get_doc_context = {
        "response_json": response.json(),
        'header_errors':header_errors,
        'lines_errors':lines_errors,
    }
    return render(request, 'doc-detail.html', get_doc_context)


def list_eta_invoice(request):
    eta_invoice_list = Submission.objects.filter()
    eta_context = {
        "eta_invoice_list": eta_invoice_list,
    }
    return render(request, 'eta-invoice.html', eta_context)


def get_token():
    url = "https://id.preprod.eta.gov.eg/connect/token"
    client_id = "547413a4-79ee-4715-8530-a7ddbe392848"
    client_secret = "913e5e19-6119-45a1-910f-f060f15e666c"
    scope = "InvoicingAPI"

    data = {"grant_type": "client_credentials", "client_id": client_id, "client_secret": client_secret, "scope": scope}
    response = requests.post(url, verify=False,
                             data=data)
    global auth_token
    auth_token = response.json()["access_token"]


def resubmit(request, sub_id):
    submission = Submission.objects.get(subm_id=sub_id)
    header_id = submission.invoice.internal_id
    submit_invoice(request, header_id)
    return redirect("taxManagement:list-eta-invoice")


def import_data_from_db():
    data = get_data_from_db()
    for invoice in data:
        try:
            old_header = InvoiceHeader.objects.get(internal_id=invoice["INTERNAL_ID"])
            old_header.delete()
        except InvoiceHeader.DoesNotExist:
            pass
        issuer = Issuer.objects.all()[0]
        issuer_address = Address.objects.filter(issuer=issuer)[0]
        try:
            receiver = Receiver.objects.get(reg_num=invoice["CUSTOMER_TRX_ID"])
        except Receiver.DoesNotExist:
            receiver = Receiver(
                reg_num=invoice["CUSTOMER_TRX_ID"],
            )
            receiver.save()
        receiver_add=Address.objects.all()[0]
        taxpayer_activity_code = issuer.activity_code
        header_obj = InvoiceHeader(
            issuer=issuer,
            issuer_address=issuer_address,
            receiver=receiver,
            receiver_address=receiver_add ,
            document_type=invoice['INVOICE_TYPE'],
            document_type_version="0.9",
            taxpayer_activity_code=taxpayer_activity_code,
            internal_id=invoice["INTERNAL_ID"],
            purchase_order_reference=invoice['PURCHASE_ORDER'],
            sales_order_reference=invoice['SALES_ORDER'],
            sales_order_description=invoice['SALES_ORDER_DESCRIPTION'],
        )
        header_obj.save()
        ####### create signature #######
        signature_obj = Signature(
            invoice_header=header_obj,
        )
        signature_obj.save()
        line_obj = InvoiceLine(
            invoice_header=header_obj,
            description=invoice['DESCRIPTION'],
            itemType="GPC",
            itemCode=invoice['INTERNAL_ITEM_CODE'],
            unitType="EA",
            quantity=invoice['QUANTITY_INVOICED'],
            currencySold=invoice['INVOICE_CURRENCY_CODE'],
            amountEGP=invoice['AMOUNTEGP'],
            amountSold=invoice['AMOUNTSOLD'],
            currencyExchangeRate=invoice['CURRENT_EXCHANGE_RATE'],
            internalCode=invoice['INTERNAL_ITEM_CODE'],
        )
        line_obj.save()
        tax_main_type = TaxTypes.objects.get(code=invoice['TAX_TYPE'])
        tax_subtype = TaxSubtypes.objects.get(code=invoice['TAX_SUB_TYPE'])
        tax_type_obj = TaxLine(
            invoice_line=line_obj,
            taxType=tax_main_type,
            subType=tax_subtype,
            amount=invoice['TAX_AMOUNT'],
            rate=invoice['TAX_RATE']
        )
        tax_type_obj.save()
        header_obj.calculate_total_sales()
        header_obj.calculate_total_item_discount()
        header_obj.calculate_net_total()
        header_obj.save()