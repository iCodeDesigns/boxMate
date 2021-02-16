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
from .models import MainTable, InvoiceHeader, InvoiceLine, TaxTypes, TaxLine, Signature, Submission, HeaderTaxTotal
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
from taxManagement.db_connection import OracleConnection


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
            old_header = InvoiceHeader.objects.get(
                internal_id=header["internal_id"])
            old_header.delete()
        except InvoiceHeader.DoesNotExist:
            pass
        issuer = Issuer.objects.get(reg_num=header['issuer_registration_num'])
        issuer_address = Address.objects.get(
            branch_id=header['issuer_branch_id'],issuer_id=header['issuer_registration_num'])
        receiver = Receiver.objects.get(
            reg_num=header['receiver_registration_num'])
        receiver_address = Address.objects.get(receiver=receiver.id, buildingNumber=header['receiver_building_num'],
                                               floor=header['receiver_floor'], room=header['receiver_room'])
        taxpayer_activity_code = ActivityType.objects.get(
            code=header['taxpayer_activity_code'])
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
            tax_types = MainTable.objects.values('taxt_item_type', 'tax_item_amount',
                                                 'tax_item_subtype',
                                                 'tax_item_rate').annotate(
                Count('internal_id')).annotate(Count('item_code'))
            for tax_type in tax_types:
                tax_main_type = TaxTypes.objects.get(
                    code=tax_type['taxt_item_type'])
                tax_subtype = TaxSubtypes.objects.get(
                    code=tax_type['tax_item_subtype'])
                tax_type_obj = TaxLine(
                    invoice_line=line_obj,
                    taxType=tax_main_type,
                    subType=tax_subtype,
                    amount=tax_type['tax_item_amount'],
                    rate=tax_type['tax_item_rate']
                )
                tax_type_obj.save()
            print("***********")    
            line_taxes_totals(line_obj.id)
        # header_obj.calculate_total_sales()
        # header_obj.calculate_total_item_discount()
        # header_obj.calculate_net_total()
        header_obj.save()


# Create your views here.
def upload_excel_sheet(request):
    main_table_resource = MainTableResource()
    import_file = request.FILES['import_file']
    dataset = Dataset()
    # # unhash the following line in case of csv file
    # # imported_data = dataset.load(import_file.read().decode(), format='csv')
    # this line in case of excel file
    imported_data = dataset.load(import_file.read(), format='xlsx')
    #
    result = main_table_resource.import_data(
        imported_data, dry_run=False)  # Test the data import
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
        data = {"success": False, "error": {
            "code": 400, "message": "Invalid Excel sheet"}}
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
        "id": reg_num,
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
    taxtotals = HeaderTaxTotal.objects.filter(header=invoice_header)
    tax_total_list = []
    for total in taxtotals:
        tax_total_object = {
            "taxType": total.tax.code,
            "amount": total.total.__float__()
        }
        tax_total_list.append(tax_total_object)
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
        "dateTimeIssued": "2021-02-15T15:37:51Z",
        # "dateTimeIssued": datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + "Z",
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
        "taxTotals": tax_total_list,
        "totalAmount": invoice_header.total_amount.__float__(),
        "extraDiscountAmount": invoice_header.extra_discount_amount.__float__(),
        "totalItemsDiscountAmount": invoice_header.total_items_discount_amount.__float__(),
        "signatures": signature_list
    }
    return data


def get_invoice_lines(invoice_id):
    invoice_lines = InvoiceLine.objects.filter(
        invoice_header__internal_id=invoice_id)
    invoice_lines_list = []
    for line in invoice_lines:
        invoice_line = {
            "description": line.description,
            "itemType": line.itemType,
            "itemCode": line.itemCode,
            "unitType": line.unitType,
            "quantity": line.quantity.__float__(),
            "internalCode": line.internalCode,
            "salesTotal": line.salesTotal.__float__(),
            "total": line.total.__float__(),
            "valueDifference": line.valueDifference.__float__(),
            "totalTaxableFees": line.totalTaxableFees.__float__(),
            "netTotal": line.netTotal.__float__(),
            "itemsDiscount": line.itemsDiscount.__float__(),
            "unitValue": {
                "amountEGP": line.amountEGP.__float__(),
                # "amountSold": line.amountSold.__float__(),
                # "currencyExchangeRate": line.currencyExchangeRate.__float__(),
                "currencySold": line.currencySold},
            "discount": {"rate": line.rate.__float__(),
                         "amount": line.amount.__float__()}
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
    url = 'https://api.preprod.invoicing.eta.gov.eg/api/v1.0/documentSubmissions/' + \
        submission_id + '?PageSize=1'
    response = requests.get(url, verify=False,
                            headers={'Authorization': 'Bearer ' + auth_token, }
                            )
    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        get_token()
        response = requests.get(url, verify=False,
                                headers={
                                    'Authorization': 'Bearer ' + auth_token, }
                                )

    if (response.status_code != status.HTTP_200_OK):
        time.sleep(10)
        response = requests.get(url, verify=False,
                                headers={
                                    'Authorization': 'Bearer ' + auth_token, }
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
    json_data = json.dumps({"documents": [invoice]})
    data = decode(json_data)
    print(data)
    url = 'https://api.preprod.invoicing.eta.gov.eg/api/v1/documentsubmissions'
    response = requests.post(url, verify=False,
                             headers={'Content-Type': 'application/json',
                                      'Authorization': 'Bearer ' + auth_token},
                             json=data)
    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        get_token()
        response = requests.post(url, verify=False,
                                 headers={'Content-Type': 'application/json',
                                          'Authorization': 'Bearer ' + auth_token},
                                 json=data)

    response_code = response
    response_json = response_code.json()
    submissionId = response_json['submissionId']
    print("**************")

    acceptedDocuments = response_json['acceptedDocuments']
    uuid = acceptedDocuments[0]['uuid']

    internalId = acceptedDocuments[0]['internalId']
    save_submition_response(internalId, submissionId)
    print(response.json())
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
                                headers={
                                    'Authorization': 'Bearer ' + auth_token, }
                                )

    validation_steps = response.json()['validationResults']['validationSteps']
    header_errors = []
    lines_errors = []
    for validation_step in validation_steps:
        if validation_step['status'] == 'Invalid':
            inner_errors = validation_step['error']['innerError']
            for inner_error in inner_errors:
                if inner_error['propertyPath'].startswith('invoiceLine'):
                    lines_errors.append(inner_error['error'])
                elif inner_error['propertyPath'].startswith('document'):
                    header_errors.append(inner_error['error'])

    get_doc_context = {
        "response_json": response.json(),
        'header_errors': header_errors,
        'lines_errors': lines_errors,
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

    data = {"grant_type": "client_credentials", "client_id": client_id,
            "client_secret": client_secret, "scope": scope}
    response = requests.post(url, verify=False,
                             data=data)
    global auth_token
    auth_token = response.json()["access_token"]


def resubmit(request, sub_id):
    submission = Submission.objects.get(subm_id=sub_id)
    header_id = submission.invoice.internal_id
    submit_invoice(request, header_id)
    return redirect("taxManagement:list-eta-invoice")


# for TaxLine totals
def get_amount_egp(id):
    line = InvoiceLine.objects.get(id=id)
    if line.currencySold is not None:
        if line.currencySold != 'EGP':
            amount_egp = line.amountSold * line.currencyExchangeRate
            line.amountEGP = amount_egp
        else:
            amount_egp = line.amountEGP
    line.save()
    return amount_egp


def calculate_sales_total(id):
    amount_egp = get_amount_egp(id)
    line = InvoiceLine.objects.get(id=id)
    line.salesTotal = line.quantity * amount_egp
    line.save()
    return line.salesTotal


def calculate_discount_amount(id):
    line = InvoiceLine.objects.get(id=id)
    if line.rate is not None:
        line.amount = (line.rate/ 100) * line.salesTotal
        line.save()
    return line.amount


def calculate_net_total(id):
    salesTotal = calculate_sales_total(id)
    amount = calculate_discount_amount(id)
    line = InvoiceLine.objects.get(id=id)
    if line.amount is not None:
        line.netTotal = salesTotal - amount
        line.save()
    else:
        line.netTotal = salesTotal
        line.save()
    return line.netTotal


# for taxable items from T5 to T12
def calculate_taxable_item_amount_t5(invoice_line):
    sum = 0
    net_total = calculate_net_total(invoice_line)
    taxline = TaxLine.objects.filter(invoice_line=invoice_line, taxType='T5')
    for line in taxline:
        line.amount = (line.rate/100) * net_total
        line.save()
        sum += line.amount
    return sum


def calculate_taxable_item_amount_t6(invoice_line):
    sum = 0
    net_total = calculate_net_total(invoice_line)
    taxline = TaxLine.objects.filter(invoice_line=invoice_line, taxType='T6')
    for line in taxline:
        line.amount = line.rate * net_total
        line.save()
        sum += line.amount
    return sum


def calculate_taxable_item_amount_t7(invoice_line):
    sum = 0
    net_total = calculate_net_total(invoice_line)
    taxline = TaxLine.objects.filter(invoice_line=invoice_line, taxType='T7')
    for line in taxline:
        line.amount = (line.rate/100) * net_total
        line.save()
        sum += line.amount
    return sum


def calculate_taxable_item_amount_t8(invoice_line):
    sum = 0
    net_total = calculate_net_total(invoice_line)
    taxline = TaxLine.objects.filter(invoice_line=invoice_line, taxType='T8')
    for line in taxline:
        line.amount = (line.rate/100) * net_total
        line.save()
        sum += line.amount
    return sum


def calculate_taxable_item_amount_t9(invoice_line):
    sum = 0
    net_total = calculate_net_total(invoice_line)
    taxline = TaxLine.objects.filter(invoice_line=invoice_line, taxType='T9')
    for line in taxline:
        line.amount = line.rate * net_total
        line.save()
        sum += line.amount
    return sum


def calculate_taxable_item_amount_t10(invoice_line):
    sum = 0
    net_total = calculate_net_total(invoice_line)
    taxline = TaxLine.objects.filter(invoice_line=invoice_line, taxType='T10')
    for line in taxline:
        line.amount = (line.rate/100) * net_total
        line.save()
        sum += line.amount
    return sum


def calculate_taxable_item_amount_t11(invoice_line):
    sum = 0
    net_total = calculate_net_total(invoice_line)
    taxline = TaxLine.objects.filter(invoice_line=invoice_line, taxType='T11')
    for line in taxline:
        line.amount = (line.rate/100) * net_total
        line.save()
        sum += line.amount
    return sum


def calculate_taxable_item_amount_t12(invoice_line):
    sum = 0
    net_total = calculate_net_total(invoice_line)
    taxline = TaxLine.objects.filter(invoice_line=invoice_line, taxType='T12')
    for line in taxline:
        line.amount = (line.rate/100) * net_total
        line.save()
        sum += line.amount
    return sum


def total_taxable_fees(invoice_line):
    five = calculate_taxable_item_amount_t5(invoice_line)
    six = calculate_taxable_item_amount_t6(invoice_line)
    seven = calculate_taxable_item_amount_t7(invoice_line)
    eight = calculate_taxable_item_amount_t8(invoice_line)
    nine = calculate_taxable_item_amount_t9(invoice_line)
    ten = calculate_taxable_item_amount_t10(invoice_line)
    eleven = calculate_taxable_item_amount_t11(invoice_line)
    twelve = calculate_taxable_item_amount_t12(invoice_line)
    totalTaxableFees = five + six + seven + eight + nine + ten + eleven + twelve
    return totalTaxableFees

# for taxable items from T13 to T20


def calculate_non_taxable_item_amount_t13(invoice_line):
    sum = 0
    net_total = calculate_net_total(invoice_line)
    taxline = TaxLine.objects.filter(invoice_line=invoice_line, taxType='T13')
    for line in taxline:
        line.amount = (line.rate/100) * net_total
        line.save()
        sum += line.amount
    return sum


def calculate_non_taxable_item_amount_t14(invoice_line):
    sum = 0
    net_total = calculate_net_total(invoice_line)
    net_total = calculate_net_total(invoice_line)
    taxline = TaxLine.objects.filter(invoice_line=invoice_line, taxType='T14')
    for line in taxline:
        line.amount = (line.rate/100) * net_total
        line.save()
        sum += line.amount
    return sum


def calculate_non_taxable_item_amount_t15(invoice_line):
    sum = 0
    net_total = calculate_net_total(invoice_line)
    net_total = calculate_net_total(invoice_line)
    taxline = TaxLine.objects.filter(invoice_line=invoice_line, taxType='T15')
    for line in taxline:
        line.amount = (line.rate/100) * net_total
        line.save()
        sum += line.amount
    return sum


def calculate_non_taxable_item_amount_t16(invoice_line):
    sum = 0
    net_total = calculate_net_total(invoice_line)
    net_total = calculate_net_total(invoice_line)
    taxline = TaxLine.objects.filter(invoice_line=invoice_line, taxType='T16')
    for line in taxline:
        line.amount = (line.rate/100) * net_total
        line.save()
        sum += line.amount
    return sum


def calculate_non_taxable_item_amount_t17(invoice_line):
    sum = 0
    net_total = calculate_net_total(invoice_line)
    net_total = calculate_net_total(invoice_line)
    taxline = TaxLine.objects.filter(invoice_line=invoice_line, taxType='T17')
    for line in taxline:
        line.amount = (line.rate/100) * net_total
        line.save()
        sum += line.amount
    return sum


def calculate_non_taxable_item_amount_t18(invoice_line):
    sum = 0
    net_total = calculate_net_total(invoice_line)
    net_total = calculate_net_total(invoice_line)
    taxline = TaxLine.objects.filter(invoice_line=invoice_line, taxType='T18')
    for line in taxline:
        line.amount = (line.rate/100) * net_total
        line.save()
        sum += line.amount
    return sum


def calculate_non_taxable_item_amount_t19(invoice_line):
    sum = 0
    net_total = calculate_net_total(invoice_line)
    net_total = calculate_net_total(invoice_line)
    taxline = TaxLine.objects.filter(invoice_line=invoice_line, taxType='T19')
    for line in taxline:
        line.amount = (line.rate/100) * net_total
        line.save()
        sum += line.amount
    return sum


def calculate_non_taxable_item_amount_t20(invoice_line):
    sum = 0
    net_total = calculate_net_total(invoice_line)
    net_total = calculate_net_total(invoice_line)
    taxline = TaxLine.objects.filter(invoice_line=invoice_line, taxType='T12')
    for line in taxline:
        line.amount = (line.rate/100) * net_total
        line.save()
        sum += line.amount
    return sum


def non_total_taxable_fees(invoice_line):
    thirteen = calculate_non_taxable_item_amount_t13(invoice_line)
    fourteen = calculate_non_taxable_item_amount_t14(invoice_line)
    fifteen = calculate_non_taxable_item_amount_t15(invoice_line)
    sixteen = calculate_non_taxable_item_amount_t16(invoice_line)
    seventeen = calculate_non_taxable_item_amount_t17(invoice_line)
    eighteen = calculate_non_taxable_item_amount_t18(invoice_line)
    nineteen = calculate_non_taxable_item_amount_t19(invoice_line)
    twenty = calculate_non_taxable_item_amount_t20(invoice_line)
    nonTotalTaxableFees = thirteen + fourteen + fifteen + \
        sixteen + seventeen + eighteen + nineteen + twenty
    return nonTotalTaxableFees


# for taxable items T2
def calculate_taxable_item_amount_t2(invoice_line):
    sum = 0
    net_total = calculate_net_total(invoice_line)
    totalTaxableFees = total_taxable_fees(invoice_line)
    amount_t3 = calculate_t3_amount_per_line(invoice_line)
    line = InvoiceLine.objects.get(id=invoice_line)
    valueDifference = line.valueDifference
    taxline = TaxLine.objects.filter(invoice_line=invoice_line, taxType='T2')
    for line in taxline:
        rate = (line.rate/100)
        line.amount = (net_total + totalTaxableFees +
                       valueDifference + amount_t3) * rate
        line.save()
        sum += line.amount
    return sum


def calculate_t3_amount_per_line(invoice_line_id):
    try:
        taxline = TaxLine.objects.filter(
            invoice_line=invoice_line_id, taxType='T3')
        t3_amount = taxline.amount
    except:
        t3_amount = 0
    return t3_amount


def calculate_t1_amount_per_line(invoice_line_id):
    invoice_line = InvoiceLine.objects.get(id=invoice_line_id)
    t2_amount = calculate_taxable_item_amount_t2(invoice_line_id)
    t3_amount = calculate_t3_amount_per_line(invoice_line_id)
    taxlines = TaxLine.objects.filter(
        invoice_line=invoice_line_id, taxType="T1")
    t1_amounts = 0
    for taxline in taxlines:
        t1_amount = (invoice_line.totalTaxableFees + invoice_line.valueDifference + invoice_line.netTotal +
                     t2_amount + t3_amount) *( taxline.rate/100)
        t1_amounts += t1_amount
        taxline.amount = t1_amount
        taxline.save()

    return t1_amounts


def calculate_t4_subtypes_amounts_per_line(invoice_line_id):
    invoice_line = InvoiceLine.objects.get(id=invoice_line_id)
    subtypes = ['W001', 'W002', 'W003', 'W004', 'W005', 'W006', 'W007', 'W008']
    t4_amounts = 0
    for subtype in subtypes:
        try:
            taxline = TaxLine.objects.get(
                invoice_line=invoice_line_id, subType=subtype)
            subtype_amount = (taxline.rate/100) * \
                (invoice_line.netTotal - invoice_line.itemsDiscount)
            taxline.amount = subtype_amount
            taxline.save()
        except:
            subtype_amount = 0
        t4_amounts += subtype_amount
    return t4_amounts


def calculate_line_total(invoice_line_id):
    invoice_line = InvoiceLine.objects.get(id=invoice_line_id)
    t3_amount = calculate_t3_amount_per_line(invoice_line_id)
    t4_amounts = calculate_t4_subtypes_amounts_per_line(invoice_line_id)
    t1_amount = calculate_t1_amount_per_line(invoice_line_id)
    t2_amount = calculate_taxable_item_amount_t2(invoice_line_id)
    total_non_taxable_fees = non_total_taxable_fees(invoice_line_id)
    line_total = 0
    line_total = invoice_line.netTotal + invoice_line.totalTaxableFees + total_non_taxable_fees + \
        t1_amount + t2_amount + t3_amount - t4_amounts - invoice_line.itemsDiscount
    invoice_line.total = line_total
    invoice_line.save()
    return line_total


def line_taxes_totals(id):
    invoice_line = InvoiceLine.objects.get(id=id)
    sales_total = calculate_sales_total(id)
    discount_amount = calculate_discount_amount(id)
    net_total = calculate_net_total(id)
    five = calculate_taxable_item_amount_t5(id)
    six = calculate_taxable_item_amount_t6(id)
    seven = calculate_taxable_item_amount_t7(id)
    eight = calculate_taxable_item_amount_t8(id)
    nine = calculate_taxable_item_amount_t9(id)
    ten = calculate_taxable_item_amount_t10(id)
    eleven = calculate_taxable_item_amount_t11(id)
    twelve = calculate_taxable_item_amount_t12(id)
    totaltaxable_fees = total_taxable_fees(id)
    thirteen = calculate_non_taxable_item_amount_t13(id)
    fourteen = calculate_non_taxable_item_amount_t14(id)
    fifteen = calculate_non_taxable_item_amount_t15(id)
    sixteen = calculate_non_taxable_item_amount_t16(id)
    seventeen = calculate_non_taxable_item_amount_t17(id)
    eighteen = calculate_non_taxable_item_amount_t18(id)
    nineteen = calculate_non_taxable_item_amount_t19(id)
    twenty = calculate_non_taxable_item_amount_t20(id)
    nontotal_taxable_fees = non_total_taxable_fees(id)
    t3_amount = calculate_t3_amount_per_line(id)
    t2_amount = calculate_taxable_item_amount_t2(id)
    t1_amount = calculate_t1_amount_per_line(id)
    t4_amount = calculate_t4_subtypes_amounts_per_line(id)
    calculate_line_totals = calculate_line_total(id)

def import_data_from_db(request):
    address = '156.4.58.40'
    port = '1521'
    service_nm = 'prod'
    username = 'apps'
    password = 'applmgr_42'
    connection_class = OracleConnection(
        address, port, service_nm, username, password)
    data = connection_class.get_data_from_db()
    # print(data)
    for invoice in data:
        try:
            old_header = InvoiceHeader.objects.get(
                internal_id=invoice["INTERNAL_ID"])
            old_header.delete()
        except InvoiceHeader.DoesNotExist:
            pass
        # Make sure an issuer already exists before import
        issuer = Issuer.objects.all()[0]
        print(issuer.activity_code)
        issuer_address = Address.objects.filter(issuer=issuer)[
            0]  # Make sure issuer address already exists already exists before import
        try:
            # Make sure receiver address exist
            receiver = Receiver.objects.get(
                reg_num=invoice["REGISTERATION_NUMBER"])
        except Receiver.DoesNotExist:
            receiver = Receiver(
                reg_num=invoice["REGISTERATION_NUMBER"],
                name="New Receiver",
                type="B"
            )
            receiver.save()
        receiver_add = Address.objects.all()[0]  # get any address
        taxpayer_activity_code = issuer.activity_code
        header_obj = InvoiceHeader(
            issuer=issuer,
            issuer_address=issuer_address,
            receiver=receiver,
            receiver_address=receiver_add,
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
            signature_type="I",
            signature_value="MIAGCSqGSIb3DQEHAqCAMIACAQMxDzANBglghkgBZQMEAgEFADCABgkqhkiG9w0BBwUAAKCAMIIFoDCCA4igAwIBAgICUPYwDQYJKoZIhvcNAQELBQAwXTELMAkGA1UEBhMCRUcxOjA4BgNVBAoTMU1pc3IgZm9yIGNlbnRyYWwgY2xlYXJpbmcsZGVwb3NpdG9yeSBhbmQgcmVnaXN0cnkxEjAQBgNVBAMTCU1DRFIgMjAxOTAeFw0yMTAxMjcxMjAzMTRaFw0yNDAxMjcxMjAzMTRaMF8xGDAWBgNVBGEMD1ZBVEVHLTEwMDMyNDkzMjELMAkGA1UEBhMCRUcxGjAYBgNVBAoMEdi02LHZg9mHINiv2LHZitmFMRowGAYDVQQDDBHYtNix2YPZhyDYr9ix2YrZhTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALwr+fR4tZi8Nad/xHDuxiEjqnUk4NzBbjzBGHUV2yAaNX79RYeOG8qE2343EUr+CxSb+oHp0I/nHl2NMstDOnBQekKrscNiyxBEyYoQuU4zWbApTkt0hY4ecq1h30HlwLM9zSw9SBn8OBa2eicOvv/3UpH1tfZ3dvRX7DzEo+UbSGS2rbF4CAyzZhtPHlOBsdEmwlfIzcwr6wksfVxW25voVDXIU12P0HTlofz7WbGKm63oJNopqOoXRg1fZRxlcffasNvNoXiMr9OZVNPTFXnpEeLcCKxrCv2vqx0FCGHhQ+3jtkeaBAE2++dUujcstOBY675AUhCEp88/iUuAQ1kCAwEAAaOCAWYwggFiMBEGA1UdDgQKBAhNgm/TAGE1+jBvBgNVHSAEaDBmMGQGCSsGAQUFBw0BAjBXMCsGCCsGAQUFBwIBFh9odHRwOi8vd3d3Lm1jZHItY2EuY29tL0NTUC5odG1sMCgGCCsGAQUFBwICMBwaGk1DRFIgUXVhbGlmaWVkIENlcnRpZmljYXRlMB8GA1UdIwQYMBaAFA+LIBjn/DC9qbtU2OwnoyDmyoUPMA4GA1UdDwEB/wQEAwIGwDCBqgYDVR0fBIGiMIGfMDGgL6AthitodHRwOi8vd3d3Lm1jZHItY2EuY29tL2NybHMvbWNkcmNybDIwMTkuY3JsMGqgaKBmhmRsZGFwOi8vd3d3Lm1jZHItY2EuY29tL0NOPW1jZHJjcmwyMDE5LENOPUNSTCxEQz1tY2RyLWNhLERDPWNvbT9DZXJ0aWZpY2F0ZVJldm9jYXRpb25MaXN0O2JpbmFyeT9iYXNlMA0GCSqGSIb3DQEBCwUAA4ICAQCbtubOJ0SEa2BKOkGd4YzBkJYA89FvSJ6emTV+T9tEuNqOKjkby/qIOovD31FOvJdpOQn3ZKXnlVVtfQV35RIW61rEnU1mwz3g0ZXA+ck0uZDeSHXBbHl/5P48GqvnVFKK1KG4C4r8Hem1OrlRkVmz93TJNV0pPE5qfjwTpkfe7yBhJv0sdk5woJuOVsyJ0BogoqxQTwd0zz4PAGxoM0m7nueGoRYaNhJHn/3uUhgo0mYUMyqkMtCw8Mi3jCLN/L2L6ATB4TAJ1QVr2N9oGmIj2hDEK0va6xyVNK37xwdkC1t8hdyZLGNZvHuojjQqi5/gVeo/3mgforCkzEZ3AOsnVAIaxfDCmLXyNtMbrJ3pwMj2uMOcHsqqiuSrWGS43DQejMluvfpNF5ORYqJjJCSbArywDMgRZtbFnO/ARtDkPBUEjt9xbxhPZ2oyZ7gB9GxoPjoUJCH9Y7XDt6NoYuiUGtaSSRfEWUHV9WL2x/+2PGvzuBiTZ+YDt+nA16hPWSRG3XC2XGfcdj9EfkuJvm0WtQxmwWwA1a/DEoBytoLI2zg+H+X6vW7WcedQNiA0G5GBYHOXDyYJT+M4u3+FhwiPxGwKagOsX4ahDXT0WculkB//Ri24xFI4Y9016AaJ7oaWRiAm5Sv7E8QyGLXKzXQowDM7je4hlYrIpkKiOZenAwAAMYIolDCCKJACAQEwYzBdMQswCQYDVQQGEwJFRzE6MDgGA1UEChMxTWlzciBmb3IgY2VudHJhbCBjbGVhcmluZyxkZXBvc2l0b3J5IGFuZCByZWdpc3RyeTESMBAGA1UEAxMJTUNEUiAyMDE5AgJQ9jANBglghkgBZQMEAgEFAKCCJwIwGAYJKoZIhvcNAQkDMQsGCSqGSIb3DQEHBTAcBgkqhkiG9w0BCQUxDxcNMjEwMjE0MTQ0NzI5WjAvBgkqhkiG9w0BCQQxIgQgYrsSAA0bsO1hV2sCnODcPzqMuRG561ad54Qclp9W0Z8wNwYLKoZIhvcNAQkQAi8xKDAmMCQwIgQgYTC/d3h3IIYFxyhASOoqVcYecN00SX3zYRo5W+K5StswgiZcBgkqhkiG9w0BBwUxgiZNBIImSSJJU1NVRVIiIkFERFJFU1MiIkJSQU5DSElEIiIwIiJDT1VOVFJZIiJFRyIiR09WRVJOQVRFIiJDYWlybyIiUkVHSU9OQ0lUWSIiTmFzciBDaXR5IiJTVFJFRVQiIjU4MCBDbGVtZW50aW5hIEtleSIiQlVJTERJTkdOVU1CRVIiIkJsZGcuIDAiIlBPU1RBTENPREUiIjY4MDMwIiJGTE9PUiIiMSIiUk9PTSIiMTIzIiJMQU5ETUFSSyIiNzY2MCBNZWxvZHkgVHJhaWwiIkFERElUSU9OQUxJTkZPUk1BVElPTiIiYmVzaWRlIFRvd25oYWxsIiJUWVBFIiJCIiJJRCIiMTAwMzI0OTMyIiJOQU1FIiJEcmVlbSIiUkVDRUlWRVIiIkFERFJFU1MiIkNPVU5UUlkiIkVHIiJHT1ZFUk5BVEUiIkVneXB0IiJSRUdJT05DSVRZIiJNdWZhemF0IGFsIElzbWx5YWgiIlNUUkVFVCIiNTgwIENsZW1lbnRpbmEgS2V5IiJCVUlMRElOR05VTUJFUiIiQmxkZy4gMCIiUE9TVEFMQ09ERSIiNjgwMzAiIkZMT09SIiIxIiJST09NIiIxMjMiIkxBTkRNQVJLIiI3NjYwIE1lbG9keSBUcmFpbCIiQURESVRJT05BTElORk9STUFUSU9OIiJiZXNpZGUgVG93bmhhbGwiIlRZUEUiIkIiIklEIiIzMTM3MTc5MTkiIk5BTUUiIlJlY2VpdmVyIiJET0NVTUVOVFRZUEUiIkkiIkRPQ1VNRU5UVFlQRVZFUlNJT04iIjEuMCIiREFURVRJTUVJU1NVRUQiIjIwMjEtMDItMTRUMDI6MDQ6NDVaIiJUQVhQQVlFUkFDVElWSVRZQ09ERSIiMTA3OSIiSU5URVJOQUxJRCIiQVItMDAwMjIiIlBVUkNIQVNFT1JERVJSRUZFUkVOQ0UiIlAtMjMzLUE2Mzc1IiJQVVJDSEFTRU9SREVSREVTQ1JJUFRJT04iInB1cmNoYXNlIE9yZGVyIGRlc2NyaXB0aW9uIiJTQUxFU09SREVSUkVGRVJFTkNFIiIxMjMxIiJTQUxFU09SREVSREVTQ1JJUFRJT04iIlNhbGVzIE9yZGVyIGRlc2NyaXB0aW9uIiJQUk9GT1JNQUlOVk9JQ0VOVU1CRVIiIlNvbWVWYWx1ZSIiUEFZTUVOVCIiQkFOS05BTUUiIlNvbWVWYWx1ZSIiQkFOS0FERFJFU1MiIlNvbWVWYWx1ZSIiQkFOS0FDQ09VTlROTyIiU29tZVZhbHVlIiJCQU5LQUNDT1VOVElCQU4iIiIiU1dJRlRDT0RFIiIiIlRFUk1TIiJTb21lVmFsdWUiIklOVk9JQ0VMSU5FUyIiSU5WT0lDRUxJTkVTIiJERVNDUklQVElPTiIiRnJ1aXR5IE1hY2hpbmUiIklURU1UWVBFIiJFR1MiIklURU1DT0RFIiJFRy0xMDAzMjQ5MzItMTExMTEiIlVOSVRUWVBFIiJFQSIiUVVBTlRJVFkiIjcuMDAwMDAiIklOVEVSTkFMQ09ERSIiRlNQTTAwMSIiU0FMRVNUT1RBTCIiNjYyLjkwMDAwIiJUT1RBTCIiMjIyMC4wODkxNCIiVkFMVUVESUZGRVJFTkNFIiI3LjAwMDAwIiJUT1RBTFRBWEFCTEVGRUVTIiI2MTguNjkyMTIiIk5FVFRPVEFMIiI2NDkuNjQyMDAiIklURU1TRElTQ09VTlQiIjUuMDAwMDAiIlVOSVRWQUxVRSIiQ1VSUkVOQ1lTT0xEIiJVU0QiIkFNT1VOVEVHUCIiOTQuNzAwMDAiIkFNT1VOVFNPTEQiIjQuNzM1MDAiIkNVUlJFTkNZRVhDSEFOR0VSQVRFIiIyMC4wMDAwMCIiRElTQ09VTlQiIlJBVEUiIjIiIkFNT1VOVCIiMTMuMjU4MDAiIlRBWEFCTEVJVEVNUyIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMSIiQU1PVU5UIiIyMDQuNjc2MzkiIlNVQlRZUEUiIlYwMDEiIlJBVEUiIjE0LjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQyIiJBTU9VTlQiIjE1Ni42NDAwOSIiU1VCVFlQRSIiVGJsMDEiIlJBVEUiIjEyIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQzIiJBTU9VTlQiIjMwLjAwMDAwIiJTVUJUWVBFIiJUYmwwMiIiUkFURSIiMC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUNCIiQU1PVU5UIiIzMi4yMzIxMCIiU1VCVFlQRSIiVzAwMSIiUkFURSIiNS4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUNSIiQU1PVU5UIiI5MC45NDk4OCIiU1VCVFlQRSIiU1QwMSIiUkFURSIiMTQuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDYiIkFNT1VOVCIiNjAuMDAwMDAiIlNVQlRZUEUiIlNUMDIiIlJBVEUiIjAuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDciIkFNT1VOVCIiNjQuOTY0MjAiIlNVQlRZUEUiIkVudDAxIiJSQVRFIiIxMC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUOCIiQU1PVU5UIiI5MC45NDk4OCIiU1VCVFlQRSIiUkQwMSIiUkFURSIiMTQuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDkiIkFNT1VOVCIiNzcuOTU3MDQiIlNVQlRZUEUiIlNDMDEiIlJBVEUiIjEyLjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQxMCIiQU1PVU5UIiI2NC45NjQyMCIiU1VCVFlQRSIiTW4wMSIiUkFURSIiMTAuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDExIiJBTU9VTlQiIjkwLjk0OTg4IiJTVUJUWVBFIiJNSTAxIiJSQVRFIiIxNC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTIiIkFNT1VOVCIiNzcuOTU3MDQiIlNVQlRZUEUiIk9GMDEiIlJBVEUiIjEyLjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQxMyIiQU1PVU5UIiI2NC45NjQyMCIiU1VCVFlQRSIiU1QwMyIiUkFURSIiMTAuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDE0IiJBTU9VTlQiIjkwLjk0OTg4IiJTVUJUWVBFIiJTVDA0IiJSQVRFIiIxNC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTUiIkFNT1VOVCIiNzcuOTU3MDQiIlNVQlRZUEUiIkVudDAzIiJSQVRFIiIxMi4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTYiIkFNT1VOVCIiNjQuOTY0MjAiIlNVQlRZUEUiIlJEMDMiIlJBVEUiIjEwLjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQxNyIiQU1PVU5UIiI2NC45NjQyMCIiU1VCVFlQRSIiU0MwMyIiUkFURSIiMTAuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDE4IiJBTU9VTlQiIjkwLjk0OTg4IiJTVUJUWVBFIiJNbjAzIiJSQVRFIiIxNC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTkiIkFNT1VOVCIiNzcuOTU3MDQiIlNVQlRZUEUiIk1JMDMiIlJBVEUiIjEyLjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQyMCIiQU1PVU5UIiI2NC45NjQyMCIiU1VCVFlQRSIiT0YwMyIiUkFURSIiMTAuMDAiIklOVk9JQ0VMSU5FUyIiREVTQ1JJUFRJT04iIkVHLTEwMDMyNDkzMi0wMDIiIklURU1UWVBFIiJFR1MiIklURU1DT0RFIiJFRy0xMDAzMjQ5MzItMDAyIiJVTklUVFlQRSIiRUEiIlFVQU5USVRZIiI1LjAwMDAwIiJJTlRFUk5BTENPREUiIkZTUE0wMDIiIlNBTEVTVE9UQUwiIjk0Ny4wMDAwMCIiVE9UQUwiIjMxMjMuNTEzMjMiIlZBTFVFRElGRkVSRU5DRSIiNy4wMDAwMCIiVE9UQUxUQVhBQkxFRkVFUyIiODU4LjEzMTYwIiJORVRUT1RBTCIiOTI4LjA2MDAwIiJJVEVNU0RJU0NPVU5UIiI1LjAwMDAwIiJVTklUVkFMVUUiIkNVUlJFTkNZU09MRCIiRVVSIiJBTU9VTlRFR1AiIjE4OS40MDAwMCIiQU1PVU5UU09MRCIiMTAuMDAwMDAiIkNVUlJFTkNZRVhDSEFOR0VSQVRFIiIxOC45NDAwMCIiRElTQ09VTlQiIlJBVEUiIjIiIkFNT1VOVCIiMTguOTQwMDAiIlRBWEFCTEVJVEVNUyIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMSIiQU1PVU5UIiIyODUuODc2NDQiIlNVQlRZUEUiIlYwMDEiIlJBVEUiIjE0LjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQyIiJBTU9VTlQiIjIxOC43ODI5OSIiU1VCVFlQRSIiVGJsMDEiIlJBVEUiIjEyIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQzIiJBTU9VTlQiIjMwLjAwMDAwIiJTVUJUWVBFIiJUYmwwMiIiUkFURSIiMC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUNCIiQU1PVU5UIiI0Ni4xNTMwMCIiU1VCVFlQRSIiVzAwMSIiUkFURSIiNS4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUNSIiQU1PVU5UIiIxMjkuOTI4NDAiIlNVQlRZUEUiIlNUMDEiIlJBVEUiIjE0LjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQ2IiJBTU9VTlQiIjYwLjAwMDAwIiJTVUJUWVBFIiJTVDAyIiJSQVRFIiIwLjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQ3IiJBTU9VTlQiIjkyLjgwNjAwIiJTVUJUWVBFIiJFbnQwMSIiUkFURSIiMTAuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDgiIkFNT1VOVCIiMTI5LjkyODQwIiJTVUJUWVBFIiJSRDAxIiJSQVRFIiIxNC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUOSIiQU1PVU5UIiIxMTEuMzY3MjAiIlNVQlRZUEUiIlNDMDEiIlJBVEUiIjEyLjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQxMCIiQU1PVU5UIiI5Mi44MDYwMCIiU1VCVFlQRSIiTW4wMSIiUkFURSIiMTAuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDExIiJBTU9VTlQiIjEyOS45Mjg0MCIiU1VCVFlQRSIiTUkwMSIiUkFURSIiMTQuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDEyIiJBTU9VTlQiIjExMS4zNjcyMCIiU1VCVFlQRSIiT0YwMSIiUkFURSIiMTIuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDEzIiJBTU9VTlQiIjkyLjgwNjAwIiJTVUJUWVBFIiJTVDAzIiJSQVRFIiIxMC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTQiIkFNT1VOVCIiMTI5LjkyODQwIiJTVUJUWVBFIiJTVDA0IiJSQVRFIiIxNC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTUiIkFNT1VOVCIiMTExLjM2NzIwIiJTVUJUWVBFIiJFbnQwMyIiUkFURSIiMTIuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDE2IiJBTU9VTlQiIjkyLjgwNjAwIiJTVUJUWVBFIiJSRDAzIiJSQVRFIiIxMC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTciIkFNT1VOVCIiOTIuODA2MDAiIlNVQlRZUEUiIlNDMDMiIlJBVEUiIjEwLjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQxOCIiQU1PVU5UIiIxMjkuOTI4NDAiIlNVQlRZUEUiIk1uMDMiIlJBVEUiIjE0LjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQxOSIiQU1PVU5UIiIxMTEuMzY3MjAiIlNVQlRZUEUiIk1JMDQiIlJBVEUiIjEyLjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQyMCIiQU1PVU5UIiI5Mi44MDYwMCIiU1VCVFlQRSIiT0YwMyIiUkFURSIiMTAuMDAiIklOVk9JQ0VMSU5FUyIiREVTQ1JJUFRJT04iIkVHLTEwMDMyNDkzMi0wMDMiIklURU1UWVBFIiJFR1MiIklURU1DT0RFIiJFRy0xMDAzMjQ5MzItMDAzIiJVTklUVFlQRSIiRUEiIlFVQU5USVRZIiI2LjU3MjY1IiJJTlRFUk5BTENPREUiIkZTUE0wMDMiIlNBTEVTVE9UQUwiIjE0NDUuOTgzMDAiIlRPVEFMIiI0NTIyLjQxNzcwIiJWQUxVRURJRkZFUkVOQ0UiIjMuMDAwMDAiIlRPVEFMVEFYQUJMRUZFRVMiIjEyMjguOTMyNjQiIk5FVFRPVEFMIiIxMzU5LjIyNDAyIiJJVEVNU0RJU0NPVU5UIiI0LjAwMDAwIiJVTklUVkFMVUUiIkNVUlJFTkNZU09MRCIiVVNEIiJBTU9VTlRFR1AiIjIyMC4wMDAwMCIiQU1PVU5UU09MRCIiMTEuMDAwMDAiIkNVUlJFTkNZRVhDSEFOR0VSQVRFIiIyMC4wMDAwMCIiRElTQ09VTlQiIlJBVEUiIjYiIkFNT1VOVCIiODYuNzU4OTgiIlRBWEFCTEVJVEVNUyIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMSIiQU1PVU5UIiI0MTAuOTk3MzYiIlNVQlRZUEUiIlYwMDEiIlJBVEUiIjE0LjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQyIiJBTU9VTlQiIjMxNC41Mzg4MCIiU1VCVFlQRSIiVGJsMDEiIlJBVEUiIjEyIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQzIiJBTU9VTlQiIjMwLjAwMDAwIiJTVUJUWVBFIiJUYmwwMiIiUkFURSIiMC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUNCIiQU1PVU5UIiI2Ny43NjEyMCIiU1VCVFlQRSIiVzAwMSIiUkFURSIiNS4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUNSIiQU1PVU5UIiIxOTAuMjkxMzYiIlNVQlRZUEUiIlNUMDEiIlJBVEUiIjE0LjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQ2IiJBTU9VTlQiIjYwLjAwMDAwIiJTVUJUWVBFIiJTVDAyIiJSQVRFIiIwLjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQ3IiJBTU9VTlQiIjEzNS45MjI0MCIiU1VCVFlQRSIiRW50MDEiIlJBVEUiIjEwLjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQ4IiJBTU9VTlQiIjE5MC4yOTEzNiIiU1VCVFlQRSIiUkQwMSIiUkFURSIiMTQuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDkiIkFNT1VOVCIiMTYzLjEwNjg4IiJTVUJUWVBFIiJTQzAxIiJSQVRFIiIxMi4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTAiIkFNT1VOVCIiMTM1LjkyMjQwIiJTVUJUWVBFIiJNbjAxIiJSQVRFIiIxMC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTEiIkFNT1VOVCIiMTkwLjI5MTM2IiJTVUJUWVBFIiJNSTAxIiJSQVRFIiIxNC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTIiIkFNT1VOVCIiMTYzLjEwNjg4IiJTVUJUWVBFIiJPRjAxIiJSQVRFIiIxMi4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTMiIkFNT1VOVCIiMTM1LjkyMjQwIiJTVUJUWVBFIiJTVDAzIiJSQVRFIiIxMC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTQiIkFNT1VOVCIiMTkwLjI5MTM2IiJTVUJUWVBFIiJTVDA0IiJSQVRFIiIxNC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTUiIkFNT1VOVCIiMTYzLjEwNjg4IiJTVUJUWVBFIiJFbnQwMyIiUkFURSIiMTIuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDE2IiJBTU9VTlQiIjEzNS45MjI0MCIiU1VCVFlQRSIiUkQwMyIiUkFURSIiMTAuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDE3IiJBTU9VTlQiIjEzNS45MjI0MCIiU1VCVFlQRSIiU0MwMyIiUkFURSIiMTAuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDE4IiJBTU9VTlQiIjE5MC4yOTEzNiIiU1VCVFlQRSIiTW4wMyIiUkFURSIiMTQuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDE5IiJBTU9VTlQiIjE2My4xMDY4OCIiU1VCVFlQRSIiTUkwNCIiUkFURSIiMTIuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDIwIiJBTU9VTlQiIjEzNS45MjI0MCIiU1VCVFlQRSIiT0YwMyIiUkFURSIiMTAuMDAiIklOVk9JQ0VMSU5FUyIiREVTQ1JJUFRJT04iIkVHLTEwMDMyNDkzMi0wMDQiIklURU1UWVBFIiJFR1MiIklURU1DT0RFIiJFRy0xMDAzMjQ5MzItMDA0IiJVTklUVFlQRSIiRUEiIlFVQU5USVRZIiI5LjAwMDAwIiJJTlRFUk5BTENPREUiIkZTUE0wMDQiIlNBTEVTVE9UQUwiIjEzNjMuNjgwMDAiIlRPVEFMIiI0MjIxLjg2NTM1IiJWQUxVRURJRkZFUkVOQ0UiIjguMDAwMDAiIlRPVEFMVEFYQUJMRUZFRVMiIjExNTAuNjcxMjgiIk5FVFRPVEFMIiIxMjY4LjIyMjQwIiJJVEVNU0RJU0NPVU5UIiIxMS4wMDAwMCIiVU5JVFZBTFVFIiJDVVJSRU5DWVNPTEQiIkVVUiIiQU1PVU5URUdQIiIxNTEuNTIwMDAiIkFNT1VOVFNPTEQiIjguMDAwMDAiIkNVUlJFTkNZRVhDSEFOR0VSQVRFIiIxOC45NDAwMCIiRElTQ09VTlQiIlJBVEUiIjciIkFNT1VOVCIiOTUuNDU3NjAiIlRBWEFCTEVJVEVNUyIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMSIiQU1PVU5UIiIzODUuMjQwOTMiIlNVQlRZUEUiIlYwMDEiIlJBVEUiIjE0LjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQyIiJBTU9VTlQiIjI5NC44MjcyNCIiU1VCVFlQRSIiVGJsMDEiIlJBVEUiIjEyIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQzIiJBTU9VTlQiIjMwLjAwMDAwIiJTVUJUWVBFIiJUYmwwMiIiUkFURSIiMC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUNCIiQU1PVU5UIiI2Mi44NjExMiIiU1VCVFlQRSIiVzAwMSIiUkFURSIiNS4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUNSIiQU1PVU5UIiIxNzcuNTUxMTQiIlNVQlRZUEUiIlNUMDEiIlJBVEUiIjE0LjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQ2IiJBTU9VTlQiIjYwLjAwMDAwIiJTVUJUWVBFIiJTVDAyIiJSQVRFIiIwLjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQ3IiJBTU9VTlQiIjEyNi44MjIyNCIiU1VCVFlQRSIiRW50MDEiIlJBVEUiIjEwLjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQ4IiJBTU9VTlQiIjE3Ny41NTExNCIiU1VCVFlQRSIiUkQwMSIiUkFURSIiMTQuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDkiIkFNT1VOVCIiMTUyLjE4NjY5IiJTVUJUWVBFIiJTQzAxIiJSQVRFIiIxMi4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTAiIkFNT1VOVCIiMTI2LjgyMjI0IiJTVUJUWVBFIiJNbjAxIiJSQVRFIiIxMC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTEiIkFNT1VOVCIiMTc3LjU1MTE0IiJTVUJUWVBFIiJNSTAxIiJSQVRFIiIxNC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTIiIkFNT1VOVCIiMTUyLjE4NjY5IiJTVUJUWVBFIiJPRjAxIiJSQVRFIiIxMi4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTMiIkFNT1VOVCIiMTI2LjgyMjI0IiJTVUJUWVBFIiJTVDAzIiJSQVRFIiIxMC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTQiIkFNT1VOVCIiMTc3LjU1MTE0IiJTVUJUWVBFIiJTVDA0IiJSQVRFIiIxNC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTUiIkFNT1VOVCIiMTUyLjE4NjY5IiJTVUJUWVBFIiJFbnQwMyIiUkFURSIiMTIuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDE2IiJBTU9VTlQiIjEyNi44MjIyNCIiU1VCVFlQRSIiUkQwMyIiUkFURSIiMTAuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDE3IiJBTU9VTlQiIjEyNi44MjIyNCIiU1VCVFlQRSIiU0MwMyIiUkFURSIiMTAuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDE4IiJBTU9VTlQiIjE3Ny41NTExNCIiU1VCVFlQRSIiTW4wMyIiUkFURSIiMTQuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDE5IiJBTU9VTlQiIjE1Mi4xODY2OSIiU1VCVFlQRSIiTUkwNCIiUkFURSIiMTIuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDIwIiJBTU9VTlQiIjEyNi44MjIyNCIiU1VCVFlQRSIiT0YwMyIiUkFURSIiMTAuMDAiIlRPVEFMRElTQ09VTlRBTU9VTlQiIjIxNC40MTQ1OCIiVE9UQUxTQUxFU0FNT1VOVCIiNDQxOS41NjMwMCIiTkVUQU1PVU5UIiI0MjA1LjE0ODQyIiJUQVhUT1RBTFMiIlRBWFRPVEFMUyIiVEFYVFlQRSIiVDEiIkFNT1VOVCIiMTI4Ni43OTExMiIiVEFYVE9UQUxTIiJUQVhUWVBFIiJUMiIiQU1PVU5UIiI5ODQuNzg5MTIiIlRBWFRPVEFMUyIiVEFYVFlQRSIiVDMiIkFNT1VOVCIiMTIwLjAwMDAwIiJUQVhUT1RBTFMiIlRBWFRZUEUiIlQ0IiJBTU9VTlQiIjIwOS4wMDc0MiIiVEFYVE9UQUxTIiJUQVhUWVBFIiJUNSIiQU1PVU5UIiI1ODguNzIwNzgiIlRBWFRPVEFMUyIiVEFYVFlQRSIiVDYiIkFNT1VOVCIiMjQwLjAwMDAwIiJUQVhUT1RBTFMiIlRBWFRZUEUiIlQ3IiJBTU9VTlQiIjQyMC41MTQ4NCIiVEFYVE9UQUxTIiJUQVhUWVBFIiJUOCIiQU1PVU5UIiI1ODguNzIwNzgiIlRBWFRPVEFMUyIiVEFYVFlQRSIiVDkiIkFNT1VOVCIiNTA0LjYxNzgxIiJUQVhUT1RBTFMiIlRBWFRZUEUiIlQxMCIiQU1PVU5UIiI0MjAuNTE0ODQiIlRBWFRPVEFMUyIiVEFYVFlQRSIiVDExIiJBTU9VTlQiIjU4OC43MjA3OCIiVEFYVE9UQUxTIiJUQVhUWVBFIiJUMTIiIkFNT1VOVCIiNTA0LjYxNzgxIiJUQVhUT1RBTFMiIlRBWFRZUEUiIlQxMyIiQU1PVU5UIiI0MjAuNTE0ODQiIlRBWFRPVEFMUyIiVEFYVFlQRSIiVDE0IiJBTU9VTlQiIjU4OC43MjA3OCIiVEFYVE9UQUxTIiJUQVhUWVBFIiJUMTUiIkFNT1VOVCIiNTA0LjYxNzgxIiJUQVhUT1RBTFMiIlRBWFRZUEUiIlQxNiIiQU1PVU5UIiI0MjAuNTE0ODQiIlRBWFRPVEFMUyIiVEFYVFlQRSIiVDE3IiJBTU9VTlQiIjQyMC41MTQ4NCIiVEFYVE9UQUxTIiJUQVhUWVBFIiJUMTgiIkFNT1VOVCIiNTg4LjcyMDc4IiJUQVhUT1RBTFMiIlRBWFRZUEUiIlQxOSIiQU1PVU5UIiI1MDQuNjE3ODEiIlRBWFRPVEFMUyIiVEFYVFlQRSIiVDIwIiJBTU9VTlQiIjQyMC41MTQ4NCIiVE9UQUxBTU9VTlQiIjE0MDgyLjg4NTQyIiJFWFRSQURJU0NPVU5UQU1PVU5UIiI1LjAwMDAwIiJUT1RBTElURU1TRElTQ09VTlRBTU9VTlQiIjI1LjAwMDAwIjANBgkqhkiG9w0BAQEFAASCAQB4RS/P5UYIOouJq2sGLss0U1P+Z9oza9z0bbbhobIaY01tSdqKH07fqfDqLNlnvNIykaPrdgCiGaqMg8cTwAzgNrt/TDKW8p4eSJs5D6NnKuoWZEmVGGeOyoqBcdvyqNLTXPQQz9T0k8pj/DQBM8gLVcdAqIW1VWzFp3/bwGjFpTLmQ9W5AJ+/tdiz5vcBlDxPy66OI3hLjD3UU+KWRsLH6fEsc6VO0bKbFIV7b1xxWrh+RK9t6kAe4DBkBDRKfwVnbKTS24Rc+jkjDWWfYk6tTGLqt38APbxPzBPjXHRPI9j9xQmeT57Dr8uMVFxpCXAaRML1ngqNAMTiP1v07oXoAAAAAAAA"
        )
        signature_obj.save()
        line_obj = InvoiceLine(
            invoice_header=header_obj,
            description=invoice['DESCRIPTION'],
            itemType="EGS",
            itemCode=invoice['GS1_CODE'],
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
        line_taxes_totals(line_obj.id)
        header_totals(header_obj.id)
        header_tax_total = HeaderTaxTotal(
            header=header_obj, tax=tax_main_type, total=invoice['TAX_AMOUNT'])
        header_tax_total.save()

        # header_tax_totals[tax_type['taxt_itaxt_item_typetem_type']] = header_tax_totals[tax_type['taxt_item_type']] + \
        #                                                 tax_type['tax_item_amount']

        # header_obj.calculate_total_sales()
        # header_obj.calculate_total_item_discount()
        # header_obj.calculate_net_total()
        # header_obj.save()
    return redirect('taxManagement:get-all-invoice-headers')



def header_sales_total(header_id):
    invoice_header = InvoiceHeader.objects.get(id = header_id)
    invoice_lines = InvoiceLine.objects.filter(invoice_header=invoice_header)
    total_sales_amount = 0
    for line in invoice_lines:
        total_sales_amount += line.salesTotal

    invoice_header.total_sales_amount = total_sales_amount
    invoice_header.save()

    return total_sales_amount

def header_sales_amount(header_id):
    invoice_header = InvoiceHeader.objects.get(id = header_id)
    invoice_lines = InvoiceLine.objects.filter(invoice_header=invoice_header)
    total_item_discount = 0
    for line in invoice_lines:
        total_item_discount += line.itemsDiscount

    invoice_header.total_discount_amount = total_item_discount
    invoice_header.save()    
    return total_item_discount

def header_net_amount(header_id):
    invoice_header = InvoiceHeader.objects.get(id = header_id)
    invoice_lines = InvoiceLine.objects.filter(invoice_header=invoice_header)
    total_net_amount = 0
    for line in invoice_lines:
        total_net_amount += line.netTotal

    invoice_header.net_amount = total_net_amount
    invoice_header.save()    
    return total_net_amount

def header_total_item_discounts_amount(header_id):
    invoice_header = InvoiceHeader.objects.get(id = header_id)
    invoice_lines = InvoiceLine.objects.filter(invoice_header=invoice_header)
    header_total_item_discounts_amount = 0
    for line in invoice_lines:
        header_total_item_discounts_amount += line.itemsDiscount

    invoice_header.total_items_discount_amount = header_total_item_discounts_amount
    invoice_header.save()
    return header_total_item_discounts_amount


def header_total_amount(header_id):
    invoice_header = InvoiceHeader.objects.get(id = header_id)
    invoice_lines = InvoiceLine.objects.filter(invoice_header=invoice_header)
    invoiceline_total = 0
    extra_discount_amount = invoice_header.extra_discount_amount
    for line in invoice_lines:
        invoiceline_total += line.total 

    header_total_amount = invoiceline_total - extra_discount_amount
    invoice_header.total_amount = header_total_amount
    invoice_header.save()
    return header_total_amount

def extra_discount_amount(header_id):
    invoice_header = InvoiceHeader.objects.get(id = header_id)
    extra_discount_amount = 0
    extra_discount_amount= invoice_header.extra_discount_amount
    invoice_header.extra_discount_amount = extra_discount_amount
    invoice_header.save()
    return extra_discount_amount

def tax_totals_t1(header_id):
    invoice_header = InvoiceHeader.objects.get(id = header_id)
    invoice_lines = InvoiceLine.objects.filter(invoice_header=invoice_header)
    tax_totals_t1 = 0
    for line in invoice_lines:
        tax_line_t1=calculate_t1_amount_per_line(line.id)
        tax_totals_t1 += tax_line_t1

    tax_type_obj = TaxTypes.objects.get(code="T1")
    if tax_totals_t1 !=0:
        header_tax_t1 = HeaderTaxTotal(
            header=invoice_header,
            tax= tax_type_obj,
            total=tax_totals_t1,
        )
        header_tax_t1.save()

    return tax_totals_t1


#Non Taxable fees total (T13-->T20) Tax Totals = sum of all NonTaxableItems
def tax_totals_t13(header_id):
    invoice_header = InvoiceHeader.objects.get(id = header_id)
    invoice_lines = InvoiceLine.objects.filter(invoice_header=invoice_header)
    Tax_type = TaxTypes.objects.get(code= "T13")
    tax_totals_t13 = 0
    for line in invoice_lines:
        tax_line_t13=calculate_non_taxable_item_amount_t13(line.id)
        tax_totals_t13 += tax_line_t13

    if tax_totals_t13 != 0 :
        tax_total_obj = HeaderTaxTotal(
            header = invoice_header,
            tax = Tax_type,
            total = tax_totals_t13
        )
        tax_total_obj.save()
    return tax_totals_t13

def tax_totals_t14(header_id):
    invoice_header = InvoiceHeader.objects.get(id = header_id)
    invoice_lines = InvoiceLine.objects.filter(invoice_header=invoice_header)
    Tax_type = TaxTypes.objects.get(code= "T14")
    tax_totals_t14 = 0
    for line in invoice_lines:
        tax_line_t14=calculate_non_taxable_item_amount_t14(line.id)
        tax_totals_t14 += tax_line_t14

    if tax_totals_t14 != 0 :
        tax_total_obj = HeaderTaxTotal(
            header = invoice_header,
            tax = Tax_type,
            total = tax_totals_t14
        )
        tax_total_obj.save()
    return tax_totals_t14

def tax_totals_t15(header_id):
    invoice_header = InvoiceHeader.objects.get(id = header_id)
    invoice_lines = InvoiceLine.objects.filter(invoice_header=invoice_header)
    Tax_type = TaxTypes.objects.get(code= "T15")
    tax_totals_t15 = 0
    for line in invoice_lines:
        tax_line_t15=calculate_non_taxable_item_amount_t15(line.id)
        tax_totals_t15 += tax_line_t15

    if tax_totals_t15 !=0 :
        tax_total_obj = HeaderTaxTotal(
            header = invoice_header,
            tax = Tax_type,
            total = tax_totals_t15
        )
        tax_total_obj.save()
    return tax_totals_t15


def tax_totals_t16(header_id):
    invoice_header = InvoiceHeader.objects.get(id = header_id)
    invoice_lines = InvoiceLine.objects.filter(invoice_header=invoice_header)
    Tax_type = TaxTypes.objects.get(code= "T16")
    tax_totals_t16 = 0
    for line in invoice_lines:
        tax_line_t16=calculate_non_taxable_item_amount_t16(line.id)
        tax_totals_t16 += tax_line_t16

    if tax_totals_t16 != 0 :
        tax_total_obj = HeaderTaxTotal(
            header = invoice_header,
            tax = Tax_type,
            total = tax_totals_t16
        )
        tax_total_obj.save()
    return tax_totals_t16


def tax_totals_t17(header_id):
    invoice_header = InvoiceHeader.objects.get(id = header_id)
    invoice_lines = InvoiceLine.objects.filter(invoice_header=invoice_header)
    Tax_type = TaxTypes.objects.get(code= "T17")
    tax_totals_t17 = 0
    for line in invoice_lines:
        tax_line_t17=calculate_non_taxable_item_amount_t17(line.id)
        tax_totals_t17 += tax_line_t17

    if tax_totals_t17 != 0 :
        tax_total_obj = HeaderTaxTotal(
            header = invoice_header,
            tax = Tax_type,
            total = tax_totals_t17
        )
        tax_total_obj.save()
    return tax_totals_t17


def tax_totals_t18(header_id):
    invoice_header = InvoiceHeader.objects.get(id = header_id)
    invoice_lines = InvoiceLine.objects.filter(invoice_header=invoice_header)
    Tax_type = TaxTypes.objects.get(code= "T18")

    tax_totals_t18 = 0
    for line in invoice_lines:
        tax_line_t18=calculate_non_taxable_item_amount_t18(line.id)
        tax_totals_t18 += tax_line_t18

    if tax_totals_t18 != 0 :
        tax_total_obj = HeaderTaxTotal(
            header = invoice_header,
            tax = Tax_type,
            total = tax_totals_t18
        )
        tax_total_obj.save()
    return tax_totals_t18


def tax_totals_t19(header_id):
    invoice_header = InvoiceHeader.objects.get(id = header_id)
    invoice_lines = InvoiceLine.objects.filter(invoice_header=invoice_header)
    Tax_type = TaxTypes.objects.get(code= "T19")

    tax_totals_t19 = 0
    for line in invoice_lines:
        tax_line_t19=calculate_non_taxable_item_amount_t19(line.id)
        tax_totals_t19 += tax_line_t19

    if tax_totals_t19 != 0:
        tax_total_obj = HeaderTaxTotal(
            header = invoice_header,
            tax = Tax_type,
            total = tax_totals_t19
        )
        tax_total_obj.save()
    return tax_totals_t19                       

def tax_totals_t20(header_id):
    invoice_header = InvoiceHeader.objects.get(id = header_id)
    invoice_lines = InvoiceLine.objects.filter(invoice_header=invoice_header)
    Tax_type = TaxTypes.objects.get(code= "T20")

    tax_totals_t20 = 0
    for line in invoice_lines:
        tax_line_t20=calculate_non_taxable_item_amount_t20(line.id)
        tax_totals_t20 += tax_line_t20

    if tax_totals_t20 != 0 :
        tax_total_obj = HeaderTaxTotal(
            header = invoice_header,
            tax = Tax_type,
            total = tax_totals_t20
        )
        tax_total_obj.save()
    return tax_totals_t20 


#def header_taxes_totals(id):
   
def tax_totals_t2(header_id):
    invoice_header = InvoiceHeader.objects.get(id = header_id)
    invoice_lines = InvoiceLine.objects.filter(invoice_header=invoice_header)
    tax_totals_t2 = 0
    for line in invoice_lines:
        tax_line_t2=calculate_taxable_item_amount_t2(line.id)
        tax_totals_t2 += tax_line_t2
    
    tax_type_obj = TaxTypes.objects.get(code="T2")
    if tax_totals_t2 !=0:
        header_tax_t2 = HeaderTaxTotal(
            header=invoice_header,
            tax= tax_type_obj,
            total=tax_totals_t2,
        )
        header_tax_t2.save()

    return tax_totals_t2

def tax_totals_t3(header_id):
    invoice_header = InvoiceHeader.objects.get(id = header_id)
    invoice_lines = InvoiceLine.objects.filter(invoice_header=invoice_header)
    tax_totals_t3 = 0
    for line in invoice_lines:
        tax_line_t3=calculate_t3_amount_per_line(line.id)
        tax_totals_t3 += tax_line_t3

    tax_type_obj = TaxTypes.objects.get(code="T3")
    if tax_totals_t3 !=0:
        header_tax_t3 = HeaderTaxTotal(
            header=invoice_header,
            tax= tax_type_obj,
            total=tax_totals_t3,
        )
        header_tax_t3.save()

    return tax_totals_t3

def tax_totals_t4(header_id):
    invoice_header = InvoiceHeader.objects.get(id = header_id)
    invoice_lines = InvoiceLine.objects.filter(invoice_header=invoice_header)
    tax_totals_t4 = 0
    for line in invoice_lines:
        tax_line_t4=calculate_t4_subtypes_amounts_per_line(line.id)
        tax_totals_t4 += tax_line_t4

    tax_type_obj = TaxTypes.objects.get(code="T4")
    if tax_totals_t4 !=0:
        header_tax_t4 = HeaderTaxTotal(
            header=invoice_header,
            tax= tax_type_obj,
            total=tax_totals_t4,
        )
        header_tax_t4.save()

    return tax_totals_t4


def tax_totals_t5(header_id):
    invoice_header = InvoiceHeader.objects.get(id = header_id)
    invoice_lines = InvoiceLine.objects.filter(invoice_header=invoice_header)
    tax_totals_t5 = 0
    for line in invoice_lines:
        tax_line_t5=calculate_taxable_item_amount_t5(line.id)
        tax_totals_t5 += tax_line_t5

    tax_type_obj = TaxTypes.objects.get(code="T5")
    if tax_totals_t5 !=0:
        header_tax_t5 = HeaderTaxTotal(
            header=invoice_header,
            tax= tax_type_obj,
            total=tax_totals_t5,
        )
        header_tax_t5.save()

    return tax_totals_t5


def tax_totals_t6(header_id):
    invoice_header = InvoiceHeader.objects.get(id = header_id)
    invoice_lines = InvoiceLine.objects.filter(invoice_header=invoice_header)
    tax_totals_t6 = 0
    for line in invoice_lines:
        tax_line_t6=calculate_taxable_item_amount_t6(line.id)
        tax_totals_t6 += tax_line_t6

    tax_type_obj = TaxTypes.objects.get(code="T6")
    if tax_totals_t6 !=0:
        header_tax_t6 = HeaderTaxTotal(
            header=invoice_header,
            tax= tax_type_obj,
            total=tax_totals_t6,
        )
        header_tax_t6.save()

    return tax_totals_t6


def tax_totals_t7(header_id):
    invoice_header = InvoiceHeader.objects.get(id = header_id)
    invoice_lines = InvoiceLine.objects.filter(invoice_header=invoice_header)
    tax_totals_t7 = 0
    for line in invoice_lines:
        tax_line_t7=calculate_taxable_item_amount_t7(line.id)
        tax_totals_t7 += tax_line_t7

    tax_type_obj = TaxTypes.objects.get(code="T7")
    if tax_totals_t7 !=0:
        header_tax_t7 = HeaderTaxTotal(
            header=invoice_header,
            tax= tax_type_obj,
            total=tax_totals_t7,
        )
        header_tax_t7.save()

    return tax_totals_t7


def tax_totals_t8(header_id):
    invoice_header = InvoiceHeader.objects.get(id = header_id)
    invoice_lines = InvoiceLine.objects.filter(invoice_header=invoice_header)
    tax_totals_t8 = 0
    for line in invoice_lines:
        tax_line_t8=calculate_taxable_item_amount_t8(line.id)
        tax_totals_t8 += tax_line_t8

    tax_type_obj = TaxTypes.objects.get(code="T8")
    if tax_totals_t8 !=0:
        header_tax_t8 = HeaderTaxTotal(
            header=invoice_header,
            tax= tax_type_obj,
            total=tax_totals_t8,
        )
        header_tax_t8.save()

    return tax_totals_t8


def tax_totals_t9(header_id):
    invoice_header = InvoiceHeader.objects.get(id = header_id)
    invoice_lines = InvoiceLine.objects.filter(invoice_header=invoice_header)
    tax_totals_t9 = 0
    for line in invoice_lines:
        tax_line_t9=calculate_taxable_item_amount_t9(line.id)
        tax_totals_t9 += tax_line_t9

    tax_type_obj = TaxTypes.objects.get(code="T9")
    if tax_totals_t9 !=0:
        header_tax_t9 = HeaderTaxTotal(
            header=invoice_header,
            tax= tax_type_obj,
            total=tax_totals_t9,
        )
        header_tax_t9.save()

    return tax_totals_t9


def tax_totals_t10(header_id):
    invoice_header = InvoiceHeader.objects.get(id = header_id)
    invoice_lines = InvoiceLine.objects.filter(invoice_header=invoice_header)
    tax_totals_t10 = 0
    for line in invoice_lines:
        tax_line_t10=calculate_taxable_item_amount_t10(line.id)
        tax_totals_t10 += tax_line_t10

    tax_type_obj = TaxTypes.objects.get(code="T10")
    if tax_totals_t10 !=0:
        header_tax_t10 = HeaderTaxTotal(
            header=invoice_header,
            tax= tax_type_obj,
            total=tax_totals_t10,
        )
        header_tax_t10.save()

    return tax_totals_t10


def tax_totals_t11(header_id):
    invoice_header = InvoiceHeader.objects.get(id = header_id)
    invoice_lines = InvoiceLine.objects.filter(invoice_header=invoice_header)
    tax_totals_t11 = 0
    for line in invoice_lines:
        tax_line_t11=calculate_taxable_item_amount_t11(line.id)
        tax_totals_t11 += tax_line_t11

    tax_type_obj = TaxTypes.objects.get(code="T11")
    if tax_totals_t11 !=0:
        header_tax_t11 = HeaderTaxTotal(
            header=invoice_header,
            tax= tax_type_obj,
            total=tax_totals_t11,
        )
        header_tax_t11.save()

    return tax_totals_t11


def tax_totals_t12(header_id):
    invoice_header = InvoiceHeader.objects.get(id = header_id)
    invoice_lines = InvoiceLine.objects.filter(invoice_header=invoice_header)
    tax_totals_t12 = 0
    for line in invoice_lines:
        tax_line_t12=calculate_taxable_item_amount_t12(line.id)
        tax_totals_t12 += tax_line_t12

    tax_type_obj = TaxTypes.objects.get(code="T12")
    if tax_totals_t12 !=0:
        header_tax_t12 = HeaderTaxTotal(
            header=invoice_header,
            tax= tax_type_obj,
            total=tax_totals_t12,
        )
        header_tax_t12.save()

    return tax_totals_t12


def header_totals(id):
    header_sales_total(id)
    header_sales_amount(id)
    header_net_amount(id)
    header_total_item_discounts_amount(id)
    header_total_amount(id)
    extra_discount_amount(id)
    tax_totals_t1(id)
    tax_totals_t2(id)
    tax_totals_t3(id)
    tax_totals_t4(id)
    tax_totals_t5(id)
    tax_totals_t6(id)
    tax_totals_t7(id)
    tax_totals_t8(id)
    tax_totals_t9(id)
    tax_totals_t10(id)
    tax_totals_t11(id)
    tax_totals_t12(id)
    tax_totals_t13(id)
    tax_totals_t14(id)
    tax_totals_t15(id)
    tax_totals_t16(id)
    tax_totals_t17(id)
    tax_totals_t18(id)
    tax_totals_t19(id)
    tax_totals_t20(id)