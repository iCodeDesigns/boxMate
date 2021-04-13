import json
import simplejson
import requests
import time
from demjson import decode
from django.conf import settings
from django.db.models import Q, Count
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from requests.auth import HTTPBasicAuth
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import api_view
from tablib import Dataset
from pprint import pprint
from decimal import Decimal
from django.http import HttpResponse, HttpResponseRedirect
from taxManagement.resources import MainTableResource
from taxManagement.models import MainTable, InvoiceHeader, InvoiceLine, TaxTypes, TaxLine, Signature, Submission, \
    HeaderTaxTotal
from taxManagement.tmp_storage import TempFolderStorage
from taxManagement.db_connection import OracleConnection
from taxManagement.tax_calculator import InoviceTaxLineCalculator
from taxManagement.java import call_java
from issuer.models import Issuer, Receiver, Address, IssuerOracleDB
from issuer import views as issuer_views
from codes.models import ActivityType, TaxSubtypes, TaxTypes
from ast import literal_eval
from taxManagement.invoice_generation import Invoicegeneration
from .forms import *
from issuer.decorators import is_issuer
from currencies.models import Currency
import zipfile
from django.utils.translation import ugettext_lazy as _
from .portal_api import *

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
def import_data_to_invoice(user):
    headers = MainTable.objects.filter(~Q(internal_id=None) & Q(user=user)).values('document_type',
                                                                                   'document_type_version',
                                                                                   'date_time_issued',
                                                                                   'taxpayer_activity_code',
                                                                                   'internal_id',
                                                                                   'purchase_order_reference',
                                                                                   'purchase_order_description',
                                                                                   'sales_order_reference',
                                                                                   'sales_order_description',
                                                                                   'proforma_invoice_number',
                                                                                   'total_sales_amount',
                                                                                   'total_discount_amount',
                                                                                   'net_amount',
                                                                                   'total_amount',
                                                                                   'total_items_discount_amount',
                                                                                   'extra_discount_amount',
                                                                                   'issuer_registration_num',
                                                                                   'receiver_registration_num',
                                                                                   'signature_type', 'signature_value',
                                                                                   'issuer_branch_id',
                                                                                   'receiver_building_num',
                                                                                   'receiver_floor',
                                                                                   'receiver_room').annotate(
        Count('internal_id'))
    for header in headers:
        try:
            old_header = InvoiceHeader.objects.filter(
                issuer=user.issuer).get(internal_id=header['internal_id'])
            old_header.delete()
        except InvoiceHeader.DoesNotExist:
            pass
        issuer = user.issuer
        issuer_address = Address.objects.get(issuer=issuer)
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
        lines = MainTable.objects.filter(~Q(item_code=None) & Q(user=user)).values('description', 'item_code',
                                                                                   'item_type',
                                                                                   'unit_type', 'quantity',
                                                                                   'sales_total',
                                                                                   'currency_sold', 'amount_egp',
                                                                                   'amount_sold',
                                                                                   'currency_exchange_rate', 'total',
                                                                                   'value_difference',
                                                                                   'total_taxable_fees',
                                                                                   'items_discount', 'net_total',
                                                                                   'discount_rate',
                                                                                   'discount_amount',
                                                                                   'internal_code').annotate(
            Count('item_code'))
        print(lines)
        for line in lines:
            currency_sold = Currency.objects.get(code=line['currency_sold'])
            line_obj = InvoiceLine(
                invoice_header=header_obj,
                description=line['description'],
                itemType=line['item_type'],
                itemCode=line['item_code'],
                unitType=line['unit_type'],
                quantity=line['quantity'],
                currencySold=currency_sold,
                amountEGP=line['amount_egp'],
                amountSold=line['amount_sold'],
                currencyExchangeRate=line['currency_exchange_rate'],
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
            tax_types = MainTable.objects.values('taxt_item_type', 'tax_item_amount', 'tax_item_subtype',
                                                 'tax_item_rate').all()
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

        header_obj.save()
        calculate_all_invoice_lines(header_obj)
        header_totals(header_obj)


@login_required(login_url='home:user-login')
def upload_excel_sheet(request):
    # try to handle uploading our template with no data
    try:
        main_table_resource = MainTableResource()
        import_file = request.FILES['import_file']
        print('import file: ', import_file)
        dataset = Dataset()
        # # unhash the following line in case of csv file
        # # imported_data = dataset.uplload(import_file.read().decode(), format='csv')
        # this line in case of excel file
        imported_data = dataset.load(import_file.read(), format='xlsx')
        #
        # handle case uploading empty excel sheet
        # check file is empty
        if issuer_views.is_empty(import_file, request):
            messages.error(request, _('Please, make sure file is filled with data'))
            return redirect('/tax/list/uploaded-invoices')

        result = main_table_resource.import_data(imported_data, dry_run=True, user=request.user)  # Test the data import
        print('result: ', result)
        tmp_storage = write_to_tmp_storage(import_file)
        if not result.has_errors() and not result.has_validation_errors():
            tmp_storage = TMP_STORAGE_CLASS(name=tmp_storage.name)
            data = tmp_storage.read('rb')
            # Uncomment the following line in case of 'csv' file
            # data = force_str(data, "utf-8")
            dataset = Dataset()
            # Enter format = 'csv' for csv file
            # TODO delete only the data of the issuer
            success = MainTable.objects.filter(user=request.user).delete()
            if not success:
                messages.error(request, 'Failed to import Excel sheet')
                return redirect('/tax/list/uploaded-invoices')

            imported_data = dataset.load(data, format='xlsx')

            main_table_resource.import_data(imported_data,
                                            dry_run=False,
                                            raise_errors=True,
                                            file_name=tmp_storage.name, user=request.user)
            tmp_storage.remove()
            # issuer_views.get_issuer_data(request.user)
            issuer_views.get_receiver_data(request.user)
            import_data_to_invoice(request.user)
            messages.success(request, 'Data is imported Successfully')
            return redirect('/tax/list/uploaded-invoices')

        else:
            messages.error(request, 'Invalid Excel Sheet ' +
                           str(result.base_errors))
            return redirect('/tax/list/uploaded-invoices')
    except zipfile.BadZipfile as e:
        # e is ---> File is not a zip file
        print('Exception occurred while uplaoding a file --> ', e)
        messages.error(request, 'Please, make sure file is saved correctly.')
        return redirect('/tax/list/uploaded-invoices')


def save_submission_response(invoice_id, submission_id, status):
    '''
    :param invoice_id: the id of the invoice to save its submission (db id)
    :param submission_id: the submission id coming from submitting an invoice
    :param status: the status is not None in case the submission id is null else the status is None
    :return: no return
    TODO the function should return if save is successful or not
    '''
    invoice = InvoiceHeader.objects.get(id=invoice_id)
    try:
        # if an old submission already exists update it
        old_submission = Submission.objects.get(invoice__id=invoice_id)
        old_submission.subm_id = submission_id
        if submission_id is None or status == "Invalid":
            old_submission.subm_id = None
            old_submission.subm_uuid = None
            old_submission.document_count = None
            old_submission.date_time_received = None
            old_submission.over_all_status = status
        old_submission.save()
    except Submission.DoesNotExist:
        submission_obj = Submission(
            invoice=invoice,
            subm_id=submission_id,
            over_all_status=status,
        )
        submission_obj.save()
    # if submission id is not None , call a function to check the submission of the invoice from gov api
    if submission_id is not None:
        # wait sometime until the status is updated at the gov side
        time.sleep(10)
        get_submission_response(submission_id)


def update_invoice_doc_version(invoice_id, version):
    """
    update invoice document version to user choice
    :param invoice_id: to get the certain invoice
    :param version: to know whether to update or no
    :return:
    """
    invoice_header = InvoiceHeader.objects.get(id=invoice_id)
    if invoice_header.document_type_version != version:
        invoice_header.document_type_version = version
        invoice_header.save()


@login_required(login_url='home:user-login')
@is_issuer
def submit_invoice(request, invoice_id, version=None):
    """
    This function is used to submit an invoice to the governmental api, it calls another function to
    save the submission response
    :param version:
    :param request: the request from the user
    :param invoice_id: the id of the invoice to be submitted (database id)
    :return: redirects to the page that lists all invoices
    """
    if version:
        update_invoice_doc_version(invoice_id=invoice_id, version=version)
    else:
        version = InvoiceHeader.objects.get(id=invoice_id).document_type_version
    # function that gets the invoice data in JSON format
    generated_invoice = Invoicegeneration(invoice_id=invoice_id).get_one_invoice()
    print('wooooow')
    invoice_as_str = simplejson.dumps(generated_invoice)  # by:ahd hozayen, we used simplejson to decode Decimal fields
    print('invoice ', invoice_as_str)
    if version == '1.0':
        jar = call_java.java_func(invoice_as_str, "Dreem", "08268939")  # send invoice_as_str to jar file to sign it.
        from_bytes_to_good_str = jar.decode("utf-8")
        from_str_to_json = json.loads(json.dumps(from_bytes_to_good_str))
        response = send_data_by_version(data=from_str_to_json)
    elif version == '0.9':
        print('version: ', version)
        response = send_data_by_version(data=invoice_as_str)
    else:
        response = ''
        print("#### Wrong Version ####")
    # if token is expired
    # TODO need to save the token in a session

    print(response)
    over_all_status = None
    # in case of network error
    if response is None:
        submissionId = None
        over_all_status = "Network Error"

    else:
        response_json = response.json()
        print('response json: ', response_json)
        submissionId = response_json['submissionId']

    # case of invalid invoice with submission id is null
    if submissionId is None and response is not None:
        over_all_status = "Invalid"

    # used to save the submission id
    save_submission_response(invoice_id, submissionId, status=over_all_status)
    return redirect('taxManagement:get-all-invoice-headers')


##### get all invoices ######
@is_issuer
def get_all_invoice_headers(request):
    invoice_headers = InvoiceHeader.objects.filter(issuer=request.user.issuer)
    count = 0
    for invoice_header in invoice_headers:
        submissions = Submission.objects.filter(invoice=invoice_header).last()
        invoice_headers[count].submissions = submissions
        count += 1
    context = {
        "invoice_headers": invoice_headers
    }
    return render(request, 'upload-invoice.html', context)


@is_issuer
def get_decument_detail_after_submit(request, internal_id):
    submission = Submission.objects.get(invoice__id=internal_id)
    if submission.subm_uuid is not None:
        response = get_document_details(submission_uuid=submission.subm_uuid)

        validation_steps = response.json(
        )['validationResults']['validationSteps']
        header_errors = []
        lines_errors = []
        general_errors = []
        for validation_step in validation_steps:
            if validation_step['status'] == 'Invalid':
                inner_errors = validation_step['error']['innerError']
                for inner_error in inner_errors:
                    if inner_error['propertyPath'].startswith('invoiceLine'):
                        lines_errors.append(inner_error['error'])
                    elif inner_error['propertyPath'].startswith('document'):
                        header_errors.append(inner_error['error'])
                    else:
                        general_errors.append(inner_error['error'])

        get_doc_context = {
            "response_json": response.json(),
            'header_errors': header_errors,
            'lines_errors': lines_errors,
            'other_errors': general_errors,
        }
        return render(request, 'doc-detail.html', get_doc_context)
    else:
        return redirect('taxManagement:list-eta-invoice')


@is_issuer
def list_eta_invoice(request):
    eta_invoice_list = Submission.objects.all()
    eta_context = {
        "eta_invoice_list": eta_invoice_list,
    }
    return render(request, 'eta-invoice.html', eta_context)


def resubmit(request, invoice_id):
    submit_invoice(request, invoice_id)
    return redirect("taxManagement:list-eta-invoice")


def calculate_line_total(invoice_line_id, tax_calculator):
    invoice_line = InvoiceLine.objects.get(id=invoice_line_id)
    t3_amount = tax_calculator.t3
    t4_amounts = tax_calculator.t4
    t1_amount = tax_calculator.t1
    t2_amount = tax_calculator.t2
    total_non_taxable_fees = tax_calculator.total_non_taxable_fees
    line_total = invoice_line.netTotal + invoice_line.totalTaxableFees + total_non_taxable_fees + \
                 t1_amount + t2_amount + t3_amount - t4_amounts - invoice_line.itemsDiscount
    invoice_line.total = line_total
    invoice_line.save()


@login_required(login_url='home:user-login')
def import_data_from_db(request):
    issuer = Issuer.objects.get(id=request.user.issuer.id)
    db_credintials = IssuerOracleDB.objects.get(issuer=issuer, is_active=True)
    address = db_credintials.ip_address
    port = db_credintials.port_number
    service_nm = db_credintials.service_number
    username = db_credintials.username
    password = db_credintials.password
    connection_class = OracleConnection(
        address, port, service_nm, username, password)
    data = connection_class.get_data_from_db()
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
        # Make sure issuer address already exists already exists before import
        issuer_address = Address.objects.filter(issuer=issuer)[0]
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
            signature_value="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hkiG9w0BBwUxgiZNBIImSSJJU1NVRVIiIkFERFJFU1MiIkJSQU5DSElEIiIwIiJDT1VOVFJZIiJFRyIiR09WRVJOQVRFIiJDYWlybyIiUkVHSU9OQ0lUWSIiTmFzciBDaXR5IiJTVFJFRVQiIjU4MCBDbGVtZW50aW5hIEtleSIiQlVJTERJTkdOVU1CRVIiIkJsZGcuIDAiIlBPU1RBTENPREUiIjY4MDMwIiJGTE9PUiIiMSIiUk9PTSIiMTIzIiJMQU5ETUFSSyIiNzY2MCBNZWxvZHkgVHJhaWwiIkFERElUSU9OQUxJTkZPUk1BVElPTiIiYmVzaWRlIFRvd25oYWxsIiJUWVBFIiJCIiJJRCIiMTAwMzI0OTMyIiJOQU1FIiJEcmVlbSIiUkVDRUlWRVIiIkFERFJFU1MiIkNPVU5UUlkiIkVHIiJHT1ZFUk5BVEUiIkVneXB0IiJSRUdJT05DSVRZIiJNdWZhemF0IGFsIElzbWx5YWgiIlNUUkVFVCIiNTgwIENsZW1lbnRpbmEgS2V5IiJCVUlMRElOR05VTUJFUiIiQmxkZy4gMCIiUE9TVEFMQ09ERSIiNjgwMzAiIkZMT09SIiIxIiJST09NIiIxMjMiIkxBTkRNQVJLIiI3NjYwIE1lbG9keSBUcmFpbCIiQURESVRJT05BTElORk9STUFUSU9OIiJiZXNpZGUgVG93bmhhbGwiIlRZUEUiIkIiIklEIiIzMTM3MTc5MTkiIk5BTUUiIlJlY2VpdmVyIiJET0NVTUVOVFRZUEUiIkkiIkRPQ1VNRU5UVFlQRVZFUlNJT04iIjEuMCIiREFURVRJTUVJU1NVRUQiIjIwMjEtMDItMTRUMDI6MDQ6NDVaIiJUQVhQQVlFUkFDVElWSVRZQ09ERSIiMTA3OSIiSU5URVJOQUxJRCIiQVItMDAwMjIiIlBVUkNIQVNFT1JERVJSRUZFUkVOQ0UiIlAtMjMzLUE2Mzc1IiJQVVJDSEFTRU9SREVSREVTQ1JJUFRJT04iInB1cmNoYXNlIE9yZGVyIGRlc2NyaXB0aW9uIiJTQUxFU09SREVSUkVGRVJFTkNFIiIxMjMxIiJTQUxFU09SREVSREVTQ1JJUFRJT04iIlNhbGVzIE9yZGVyIGRlc2NyaXB0aW9uIiJQUk9GT1JNQUlOVk9JQ0VOVU1CRVIiIlNvbWVWYWx1ZSIiUEFZTUVOVCIiQkFOS05BTUUiIlNvbWVWYWx1ZSIiQkFOS0FERFJFU1MiIlNvbWVWYWx1ZSIiQkFOS0FDQ09VTlROTyIiU29tZVZhbHVlIiJCQU5LQUNDT1VOVElCQU4iIiIiU1dJRlRDT0RFIiIiIlRFUk1TIiJTb21lVmFsdWUiIklOVk9JQ0VMSU5FUyIiSU5WT0lDRUxJTkVTIiJERVNDUklQVElPTiIiRnJ1aXR5IE1hY2hpbmUiIklURU1UWVBFIiJFR1MiIklURU1DT0RFIiJFRy0xMDAzMjQ5MzItMTExMTEiIlVOSVRUWVBFIiJFQSIiUVVBTlRJVFkiIjcuMDAwMDAiIklOVEVSTkFMQ09ERSIiRlNQTTAwMSIiU0FMRVNUT1RBTCIiNjYyLjkwMDAwIiJUT1RBTCIiMjIyMC4wODkxNCIiVkFMVUVESUZGRVJFTkNFIiI3LjAwMDAwIiJUT1RBTFRBWEFCTEVGRUVTIiI2MTguNjkyMTIiIk5FVFRPVEFMIiI2NDkuNjQyMDAiIklURU1TRElTQ09VTlQiIjUuMDAwMDAiIlVOSVRWQUxVRSIiQ1VSUkVOQ1lTT0xEIiJVU0QiIkFNT1VOVEVHUCIiOTQuNzAwMDAiIkFNT1VOVFNPTEQiIjQuNzM1MDAiIkNVUlJFTkNZRVhDSEFOR0VSQVRFIiIyMC4wMDAwMCIiRElTQ09VTlQiIlJBVEUiIjIiIkFNT1VOVCIiMTMuMjU4MDAiIlRBWEFCTEVJVEVNUyIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMSIiQU1PVU5UIiIyMDQuNjc2MzkiIlNVQlRZUEUiIlYwMDEiIlJBVEUiIjE0LjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQyIiJBTU9VTlQiIjE1Ni42NDAwOSIiU1VCVFlQRSIiVGJsMDEiIlJBVEUiIjEyIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQzIiJBTU9VTlQiIjMwLjAwMDAwIiJTVUJUWVBFIiJUYmwwMiIiUkFURSIiMC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUNCIiQU1PVU5UIiIzMi4yMzIxMCIiU1VCVFlQRSIiVzAwMSIiUkFURSIiNS4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUNSIiQU1PVU5UIiI5MC45NDk4OCIiU1VCVFlQRSIiU1QwMSIiUkFURSIiMTQuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDYiIkFNT1VOVCIiNjAuMDAwMDAiIlNVQlRZUEUiIlNUMDIiIlJBVEUiIjAuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDciIkFNT1VOVCIiNjQuOTY0MjAiIlNVQlRZUEUiIkVudDAxIiJSQVRFIiIxMC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUOCIiQU1PVU5UIiI5MC45NDk4OCIiU1VCVFlQRSIiUkQwMSIiUkFURSIiMTQuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDkiIkFNT1VOVCIiNzcuOTU3MDQiIlNVQlRZUEUiIlNDMDEiIlJBVEUiIjEyLjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQxMCIiQU1PVU5UIiI2NC45NjQyMCIiU1VCVFlQRSIiTW4wMSIiUkFURSIiMTAuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDExIiJBTU9VTlQiIjkwLjk0OTg4IiJTVUJUWVBFIiJNSTAxIiJSQVRFIiIxNC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTIiIkFNT1VOVCIiNzcuOTU3MDQiIlNVQlRZUEUiIk9GMDEiIlJBVEUiIjEyLjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQxMyIiQU1PVU5UIiI2NC45NjQyMCIiU1VCVFlQRSIiU1QwMyIiUkFURSIiMTAuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDE0IiJBTU9VTlQiIjkwLjk0OTg4IiJTVUJUWVBFIiJTVDA0IiJSQVRFIiIxNC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTUiIkFNT1VOVCIiNzcuOTU3MDQiIlNVQlRZUEUiIkVudDAzIiJSQVRFIiIxMi4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTYiIkFNT1VOVCIiNjQuOTY0MjAiIlNVQlRZUEUiIlJEMDMiIlJBVEUiIjEwLjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQxNyIiQU1PVU5UIiI2NC45NjQyMCIiU1VCVFlQRSIiU0MwMyIiUkFURSIiMTAuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDE4IiJBTU9VTlQiIjkwLjk0OTg4IiJTVUJUWVBFIiJNbjAzIiJSQVRFIiIxNC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTkiIkFNT1VOVCIiNzcuOTU3MDQiIlNVQlRZUEUiIk1JMDMiIlJBVEUiIjEyLjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQyMCIiQU1PVU5UIiI2NC45NjQyMCIiU1VCVFlQRSIiT0YwMyIiUkFURSIiMTAuMDAiIklOVk9JQ0VMSU5FUyIiREVTQ1JJUFRJT04iIkVHLTEwMDMyNDkzMi0wMDIiIklURU1UWVBFIiJFR1MiIklURU1DT0RFIiJFRy0xMDAzMjQ5MzItMDAyIiJVTklUVFlQRSIiRUEiIlFVQU5USVRZIiI1LjAwMDAwIiJJTlRFUk5BTENPREUiIkZTUE0wMDIiIlNBTEVTVE9UQUwiIjk0Ny4wMDAwMCIiVE9UQUwiIjMxMjMuNTEzMjMiIlZBTFVFRElGRkVSRU5DRSIiNy4wMDAwMCIiVE9UQUxUQVhBQkxFRkVFUyIiODU4LjEzMTYwIiJORVRUT1RBTCIiOTI4LjA2MDAwIiJJVEVNU0RJU0NPVU5UIiI1LjAwMDAwIiJVTklUVkFMVUUiIkNVUlJFTkNZU09MRCIiRVVSIiJBTU9VTlRFR1AiIjE4OS40MDAwMCIiQU1PVU5UU09MRCIiMTAuMDAwMDAiIkNVUlJFTkNZRVhDSEFOR0VSQVRFIiIxOC45NDAwMCIiRElTQ09VTlQiIlJBVEUiIjIiIkFNT1VOVCIiMTguOTQwMDAiIlRBWEFCTEVJVEVNUyIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMSIiQU1PVU5UIiIyODUuODc2NDQiIlNVQlRZUEUiIlYwMDEiIlJBVEUiIjE0LjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQyIiJBTU9VTlQiIjIxOC43ODI5OSIiU1VCVFlQRSIiVGJsMDEiIlJBVEUiIjEyIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQzIiJBTU9VTlQiIjMwLjAwMDAwIiJTVUJUWVBFIiJUYmwwMiIiUkFURSIiMC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUNCIiQU1PVU5UIiI0Ni4xNTMwMCIiU1VCVFlQRSIiVzAwMSIiUkFURSIiNS4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUNSIiQU1PVU5UIiIxMjkuOTI4NDAiIlNVQlRZUEUiIlNUMDEiIlJBVEUiIjE0LjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQ2IiJBTU9VTlQiIjYwLjAwMDAwIiJTVUJUWVBFIiJTVDAyIiJSQVRFIiIwLjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQ3IiJBTU9VTlQiIjkyLjgwNjAwIiJTVUJUWVBFIiJFbnQwMSIiUkFURSIiMTAuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDgiIkFNT1VOVCIiMTI5LjkyODQwIiJTVUJUWVBFIiJSRDAxIiJSQVRFIiIxNC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUOSIiQU1PVU5UIiIxMTEuMzY3MjAiIlNVQlRZUEUiIlNDMDEiIlJBVEUiIjEyLjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQxMCIiQU1PVU5UIiI5Mi44MDYwMCIiU1VCVFlQRSIiTW4wMSIiUkFURSIiMTAuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDExIiJBTU9VTlQiIjEyOS45Mjg0MCIiU1VCVFlQRSIiTUkwMSIiUkFURSIiMTQuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDEyIiJBTU9VTlQiIjExMS4zNjcyMCIiU1VCVFlQRSIiT0YwMSIiUkFURSIiMTIuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDEzIiJBTU9VTlQiIjkyLjgwNjAwIiJTVUJUWVBFIiJTVDAzIiJSQVRFIiIxMC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTQiIkFNT1VOVCIiMTI5LjkyODQwIiJTVUJUWVBFIiJTVDA0IiJSQVRFIiIxNC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTUiIkFNT1VOVCIiMTExLjM2NzIwIiJTVUJUWVBFIiJFbnQwMyIiUkFURSIiMTIuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDE2IiJBTU9VTlQiIjkyLjgwNjAwIiJTVUJUWVBFIiJSRDAzIiJSQVRFIiIxMC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTciIkFNT1VOVCIiOTIuODA2MDAiIlNVQlRZUEUiIlNDMDMiIlJBVEUiIjEwLjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQxOCIiQU1PVU5UIiIxMjkuOTI4NDAiIlNVQlRZUEUiIk1uMDMiIlJBVEUiIjE0LjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQxOSIiQU1PVU5UIiIxMTEuMzY3MjAiIlNVQlRZUEUiIk1JMDQiIlJBVEUiIjEyLjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQyMCIiQU1PVU5UIiI5Mi44MDYwMCIiU1VCVFlQRSIiT0YwMyIiUkFURSIiMTAuMDAiIklOVk9JQ0VMSU5FUyIiREVTQ1JJUFRJT04iIkVHLTEwMDMyNDkzMi0wMDMiIklURU1UWVBFIiJFR1MiIklURU1DT0RFIiJFRy0xMDAzMjQ5MzItMDAzIiJVTklUVFlQRSIiRUEiIlFVQU5USVRZIiI2LjU3MjY1IiJJTlRFUk5BTENPREUiIkZTUE0wMDMiIlNBTEVTVE9UQUwiIjE0NDUuOTgzMDAiIlRPVEFMIiI0NTIyLjQxNzcwIiJWQUxVRURJRkZFUkVOQ0UiIjMuMDAwMDAiIlRPVEFMVEFYQUJMRUZFRVMiIjEyMjguOTMyNjQiIk5FVFRPVEFMIiIxMzU5LjIyNDAyIiJJVEVNU0RJU0NPVU5UIiI0LjAwMDAwIiJVTklUVkFMVUUiIkNVUlJFTkNZU09MRCIiVVNEIiJBTU9VTlRFR1AiIjIyMC4wMDAwMCIiQU1PVU5UU09MRCIiMTEuMDAwMDAiIkNVUlJFTkNZRVhDSEFOR0VSQVRFIiIyMC4wMDAwMCIiRElTQ09VTlQiIlJBVEUiIjYiIkFNT1VOVCIiODYuNzU4OTgiIlRBWEFCTEVJVEVNUyIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMSIiQU1PVU5UIiI0MTAuOTk3MzYiIlNVQlRZUEUiIlYwMDEiIlJBVEUiIjE0LjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQyIiJBTU9VTlQiIjMxNC41Mzg4MCIiU1VCVFlQRSIiVGJsMDEiIlJBVEUiIjEyIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQzIiJBTU9VTlQiIjMwLjAwMDAwIiJTVUJUWVBFIiJUYmwwMiIiUkFURSIiMC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUNCIiQU1PVU5UIiI2Ny43NjEyMCIiU1VCVFlQRSIiVzAwMSIiUkFURSIiNS4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUNSIiQU1PVU5UIiIxOTAuMjkxMzYiIlNVQlRZUEUiIlNUMDEiIlJBVEUiIjE0LjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQ2IiJBTU9VTlQiIjYwLjAwMDAwIiJTVUJUWVBFIiJTVDAyIiJSQVRFIiIwLjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQ3IiJBTU9VTlQiIjEzNS45MjI0MCIiU1VCVFlQRSIiRW50MDEiIlJBVEUiIjEwLjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQ4IiJBTU9VTlQiIjE5MC4yOTEzNiIiU1VCVFlQRSIiUkQwMSIiUkFURSIiMTQuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDkiIkFNT1VOVCIiMTYzLjEwNjg4IiJTVUJUWVBFIiJTQzAxIiJSQVRFIiIxMi4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTAiIkFNT1VOVCIiMTM1LjkyMjQwIiJTVUJUWVBFIiJNbjAxIiJSQVRFIiIxMC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTEiIkFNT1VOVCIiMTkwLjI5MTM2IiJTVUJUWVBFIiJNSTAxIiJSQVRFIiIxNC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTIiIkFNT1VOVCIiMTYzLjEwNjg4IiJTVUJUWVBFIiJPRjAxIiJSQVRFIiIxMi4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTMiIkFNT1VOVCIiMTM1LjkyMjQwIiJTVUJUWVBFIiJTVDAzIiJSQVRFIiIxMC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTQiIkFNT1VOVCIiMTkwLjI5MTM2IiJTVUJUWVBFIiJTVDA0IiJSQVRFIiIxNC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTUiIkFNT1VOVCIiMTYzLjEwNjg4IiJTVUJUWVBFIiJFbnQwMyIiUkFURSIiMTIuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDE2IiJBTU9VTlQiIjEzNS45MjI0MCIiU1VCVFlQRSIiUkQwMyIiUkFURSIiMTAuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDE3IiJBTU9VTlQiIjEzNS45MjI0MCIiU1VCVFlQRSIiU0MwMyIiUkFURSIiMTAuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDE4IiJBTU9VTlQiIjE5MC4yOTEzNiIiU1VCVFlQRSIiTW4wMyIiUkFURSIiMTQuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDE5IiJBTU9VTlQiIjE2My4xMDY4OCIiU1VCVFlQRSIiTUkwNCIiUkFURSIiMTIuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDIwIiJBTU9VTlQiIjEzNS45MjI0MCIiU1VCVFlQRSIiT0YwMyIiUkFURSIiMTAuMDAiIklOVk9JQ0VMSU5FUyIiREVTQ1JJUFRJT04iIkVHLTEwMDMyNDkzMi0wMDQiIklURU1UWVBFIiJFR1MiIklURU1DT0RFIiJFRy0xMDAzMjQ5MzItMDA0IiJVTklUVFlQRSIiRUEiIlFVQU5USVRZIiI5LjAwMDAwIiJJTlRFUk5BTENPREUiIkZTUE0wMDQiIlNBTEVTVE9UQUwiIjEzNjMuNjgwMDAiIlRPVEFMIiI0MjIxLjg2NTM1IiJWQUxVRURJRkZFUkVOQ0UiIjguMDAwMDAiIlRPVEFMVEFYQUJMRUZFRVMiIjExNTAuNjcxMjgiIk5FVFRPVEFMIiIxMjY4LjIyMjQwIiJJVEVNU0RJU0NPVU5UIiIxMS4wMDAwMCIiVU5JVFZBTFVFIiJDVVJSRU5DWVNPTEQiIkVVUiIiQU1PVU5URUdQIiIxNTEuNTIwMDAiIkFNT1VOVFNPTEQiIjguMDAwMDAiIkNVUlJFTkNZRVhDSEFOR0VSQVRFIiIxOC45NDAwMCIiRElTQ09VTlQiIlJBVEUiIjciIkFNT1VOVCIiOTUuNDU3NjAiIlRBWEFCTEVJVEVNUyIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMSIiQU1PVU5UIiIzODUuMjQwOTMiIlNVQlRZUEUiIlYwMDEiIlJBVEUiIjE0LjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQyIiJBTU9VTlQiIjI5NC44MjcyNCIiU1VCVFlQRSIiVGJsMDEiIlJBVEUiIjEyIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQzIiJBTU9VTlQiIjMwLjAwMDAwIiJTVUJUWVBFIiJUYmwwMiIiUkFURSIiMC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUNCIiQU1PVU5UIiI2Mi44NjExMiIiU1VCVFlQRSIiVzAwMSIiUkFURSIiNS4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUNSIiQU1PVU5UIiIxNzcuNTUxMTQiIlNVQlRZUEUiIlNUMDEiIlJBVEUiIjE0LjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQ2IiJBTU9VTlQiIjYwLjAwMDAwIiJTVUJUWVBFIiJTVDAyIiJSQVRFIiIwLjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQ3IiJBTU9VTlQiIjEyNi44MjIyNCIiU1VCVFlQRSIiRW50MDEiIlJBVEUiIjEwLjAwIiJUQVhBQkxFSVRFTVMiIlRBWFRZUEUiIlQ4IiJBTU9VTlQiIjE3Ny41NTExNCIiU1VCVFlQRSIiUkQwMSIiUkFURSIiMTQuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDkiIkFNT1VOVCIiMTUyLjE4NjY5IiJTVUJUWVBFIiJTQzAxIiJSQVRFIiIxMi4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTAiIkFNT1VOVCIiMTI2LjgyMjI0IiJTVUJUWVBFIiJNbjAxIiJSQVRFIiIxMC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTEiIkFNT1VOVCIiMTc3LjU1MTE0IiJTVUJUWVBFIiJNSTAxIiJSQVRFIiIxNC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTIiIkFNT1VOVCIiMTUyLjE4NjY5IiJTVUJUWVBFIiJPRjAxIiJSQVRFIiIxMi4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTMiIkFNT1VOVCIiMTI2LjgyMjI0IiJTVUJUWVBFIiJTVDAzIiJSQVRFIiIxMC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTQiIkFNT1VOVCIiMTc3LjU1MTE0IiJTVUJUWVBFIiJTVDA0IiJSQVRFIiIxNC4wMCIiVEFYQUJMRUlURU1TIiJUQVhUWVBFIiJUMTUiIkFNT1VOVCIiMTUyLjE4NjY5IiJTVUJUWVBFIiJFbnQwMyIiUkFURSIiMTIuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDE2IiJBTU9VTlQiIjEyNi44MjIyNCIiU1VCVFlQRSIiUkQwMyIiUkFURSIiMTAuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDE3IiJBTU9VTlQiIjEyNi44MjIyNCIiU1VCVFlQRSIiU0MwMyIiUkFURSIiMTAuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDE4IiJBTU9VTlQiIjE3Ny41NTExNCIiU1VCVFlQRSIiTW4wMyIiUkFURSIiMTQuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDE5IiJBTU9VTlQiIjE1Mi4xODY2OSIiU1VCVFlQRSIiTUkwNCIiUkFURSIiMTIuMDAiIlRBWEFCTEVJVEVNUyIiVEFYVFlQRSIiVDIwIiJBTU9VTlQiIjEyNi44MjIyNCIiU1VCVFlQRSIiT0YwMyIiUkFURSIiMTAuMDAiIlRPVEFMRElTQ09VTlRBTU9VTlQiIjIxNC40MTQ1OCIiVE9UQUxTQUxFU0FNT1VOVCIiNDQxOS41NjMwMCIiTkVUQU1PVU5UIiI0MjA1LjE0ODQyIiJUQVhUT1RBTFMiIlRBWFRPVEFMUyIiVEFYVFlQRSIiVDEiIkFNT1VOVCIiMTI4Ni43OTExMiIiVEFYVE9UQUxTIiJUQVhUWVBFIiJUMiIiQU1PVU5UIiI5ODQuNzg5MTIiIlRBWFRPVEFMUyIiVEFYVFlQRSIiVDMiIkFNT1VOVCIiMTIwLjAwMDAwIiJUQVhUT1RBTFMiIlRBWFRZUEUiIlQ0IiJBTU9VTlQiIjIwOS4wMDc0MiIiVEFYVE9UQUxTIiJUQVhUWVBFIiJUNSIiQU1PVU5UIiI1ODguNzIwNzgiIlRBWFRPVEFMUyIiVEFYVFlQRSIiVDYiIkFNT1VOVCIiMjQwLjAwMDAwIiJUQVhUT1RBTFMiIlRBWFRZUEUiIlQ3IiJBTU9VTlQiIjQyMC41MTQ4NCIiVEFYVE9UQUxTIiJUQVhUWVBFIiJUOCIiQU1PVU5UIiI1ODguNzIwNzgiIlRBWFRPVEFMUyIiVEFYVFlQRSIiVDkiIkFNT1VOVCIiNTA0LjYxNzgxIiJUQVhUT1RBTFMiIlRBWFRZUEUiIlQxMCIiQU1PVU5UIiI0MjAuNTE0ODQiIlRBWFRPVEFMUyIiVEFYVFlQRSIiVDExIiJBTU9VTlQiIjU4OC43MjA3OCIiVEFYVE9UQUxTIiJUQVhUWVBFIiJUMTIiIkFNT1VOVCIiNTA0LjYxNzgxIiJUQVhUT1RBTFMiIlRBWFRZUEUiIlQxMyIiQU1PVU5UIiI0MjAuNTE0ODQiIlRBWFRPVEFMUyIiVEFYVFlQRSIiVDE0IiJBTU9VTlQiIjU4OC43MjA3OCIiVEFYVE9UQUxTIiJUQVhUWVBFIiJUMTUiIkFNT1VOVCIiNTA0LjYxNzgxIiJUQVhUT1RBTFMiIlRBWFRZUEUiIlQxNiIiQU1PVU5UIiI0MjAuNTE0ODQiIlRBWFRPVEFMUyIiVEFYVFlQRSIiVDE3IiJBTU9VTlQiIjQyMC41MTQ4NCIiVEFYVE9UQUxTIiJUQVhUWVBFIiJUMTgiIkFNT1VOVCIiNTg4LjcyMDc4IiJUQVhUT1RBTFMiIlRBWFRZUEUiIlQxOSIiQU1PVU5UIiI1MDQuNjE3ODEiIlRBWFRPVEFMUyIiVEFYVFlQRSIiVDIwIiJBTU9VTlQiIjQyMC41MTQ4NCIiVE9UQUxBTU9VTlQiIjE0MDgyLjg4NTQyIiJFWFRSQURJU0NPVU5UQU1PVU5UIiI1LjAwMDAwIiJUT1RBTElURU1TRElTQ09VTlRBTU9VTlQiIjI1LjAwMDAwIjANBgkqhkiG9w0BAQEFAASCAQB4RS/P5UYIOouJq2sGLss0U1P+Z9oza9z0bbbhobIaY01tSdqKH07fqfDqLNlnvNIykaPrdgCiGaqMg8cTwAzgNrt/TDKW8p4eSJs5D6NnKuoWZEmVGGeOyoqBcdvyqNLTXPQQz9T0k8pj/DQBM8gLVcdAqIW1VWzFp3/bwGjFpTLmQ9W5AJ+/tdiz5vcBlDxPy66OI3hLjD3UU+KWRsLH6fEsc6VO0bKbFIV7b1xxWrh+RK9t6kAe4DBkBDRKfwVnbKTS24Rc+jkjDWWfYk6tTGLqt38APbxPzBPjXHRPI9j9xQmeT57Dr8uMVFxpCXAaRML1ngqNAMTiP1v07oXoAAAAAAAA"
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
        calculate_all_invoice_lines(header_obj)
        header_totals(header_obj)
        header_tax_total = HeaderTaxTotal(
            header=header_obj, tax=tax_main_type, total=invoice['TAX_AMOUNT'])
        header_tax_total.save()

    return redirect('taxManagement:get-all-invoice-headers')


def header_totals(header):
    header.calculate_header_sales_total()
    header.calculate_items_discount()
    header.calculate_discount_amount()
    header.calculate_net_amount()
    header.calculate_total_amount()


def calculate_all_invoice_lines(header_obj):
    invoice_lines = header_obj.lines.all()
    for line_obj in invoice_lines:
        line_obj.get_amount_egp()
        line_obj.calculate_sales_total()
        line_obj.calculate_discount_amount()
        line_obj.calculate_net_total()
        tax_calculator = InoviceTaxLineCalculator(line_obj)
        tax_calculator.calculate_all_taxes_amount()
        calculate_line_total(line_obj.id, tax_calculator)


@is_issuer
def view_invoice(request, invoice_id):
    invoice_header = InvoiceHeader.objects.get(id=invoice_id)
    invoice_lines = InvoiceLine.objects.filter(invoice_header=invoice_header)
    context = {
        "invoice_header": invoice_header,
        "invoice_lines": invoice_lines,
        "page_title": _("View Invoice")
    }
    return render(request, 'view-invoice.html', context)


@is_issuer
def create_new_invoice_header(request):
    ''' 
        date : 10/03/2021
        author : Mamdouh
        purpose : create new invoice and save it to database
    '''
    header_form = InvoiceHeaderForm(issuer=request.user.issuer)
    if request.method == 'POST':
        header_form = InvoiceHeaderForm(issuer=request.user.issuer, data=request.POST)
        if header_form.is_valid():
            header_obj = header_form.save(commit=False)
            header_obj.issuer = request.user.issuer
            header_obj.created_by = request.user
            header_obj.save()
            print(header_obj.id)
            return redirect('taxManagement:create-invoice-line', invoice_id=header_obj.id)

    context = {
        'header_form': header_form,
        "page_title": _("Create Invoice Header"),
    }

    return render(request, 'create-invoice-header.html', context)


def load_receiver_addresses(request):
    receiver_id = request.GET.get('receiver')
    addresses = Address.objects.filter(receiver=receiver_id)
    return render(request, 'receiver-addresses-dropdown.html', {'addresses': addresses})


def load_issuer_addresses(request):
    addresses = Address.objects.filter(issuer=request.user.issuer)
    return render(request, 'issuer-addresses-dropdown.html', {'addresses': addresses})


@is_issuer
def create_new_invoice_line(request, invoice_id):
    ''' 
        date : 10/03/2021
        author : Mamdouh
        purpose : create new invoice and save it to database
    '''
    line_form = InvoiceLineForm()
    tax_line_form = TaxLineInlineForm()
    header = InvoiceHeader.objects.get(id=invoice_id)

    if request.method == 'POST':
        line_form = InvoiceLineForm(request.POST)
        tax_line_form = TaxLineInlineForm(request.POST)
        if line_form.is_valid():
            line_obj = line_form.save(commit=False)
            line_obj.invoice_header = header
            line_obj.created_by = request.user
            line_obj.save()
            tax_line_form = TaxLineInlineForm(request.POST, instance=line_obj)

            if tax_line_form.is_valid():
                tax_line_obj = tax_line_form.save(commit=False)
                for obj in tax_line_obj:
                    obj.created_by = request.user
                    obj.save()
                    calculate_all_invoice_lines(header)
                    header_totals(header)
                if 'Save And Exit' in request.POST:
                    return redirect('taxManagement:view-invoice', invoice_id=invoice_id)
                elif 'Save And Add' in request.POST:
                    return redirect('taxManagement:create-invoice-line', invoice_id=invoice_id)

    context = {
        'line_form': line_form,
        'tax_line_form': tax_line_form,
        "page_title": _("Create Invoice Line")
    }

    return render(request, 'create-invoice-line.html', context)


def refresh_submission_status(request, submission_id):
    submission = get_submission_response(submission_id)
    print(submission)
    return redirect('taxManagement:get-all-invoice-headers')


def update_invoice_status(request, invoice_id, status):
    """
    update invoice status to verified or canceled internally,
    update it according to api response after submission
    :param request:
    :return:
    by: amira
    """
    try:
        InvoiceHeader.objects.filter(id=invoice_id).update(invoice_status=status)
    except Exception as e:
        print('An error occurred in update status -> ', e)
    return redirect('taxManagement:get-all-invoice-headers')


def export_empty_invoice_temp(request):
    """
    download empty excel file
    :param request:
    :return:
    by: amira
    """
    invoice_resource = MainTableResource()
    dataset = invoice_resource.export(queryset=MainTable.objects.none())
    response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="invoice_template.xlsx"'
    return response


def cancel_document_form(request, doc_uuid):
    """
    cancel document and specifying cancellation reason
    :param request:
    :param doc_uuid: uuid of document
    :return:
    by: amira
    date: 11/4/2021
    """
    if request.method == 'POST':
        cancel_reason = request.POST['cancel_reason']
        cancel_body = {
            "status": "cancelled",
            "reason": cancel_reason
        }
        cancel_body_json = json.dumps(cancel_body)
        response = send_cancellation_request(doc_uuid=doc_uuid, data=cancel_body_json)
        if response.status_code == 200:
            update_submission_and_invoice_status(doc_uuid=doc_uuid)
            messages.success(request, _('Your invoice is cancelled successfully.'))
            return redirect('taxManagement:list-eta-invoice')
        else:
            messages.error(request, _('Something went wrong'))
            return redirect('taxManagement:list-eta-invoice')

    context = {
        'uuid': doc_uuid,
    }
    return render(request, 'cancel_document_form.html', context)


def update_submission_and_invoice_status(doc_uuid):
    """
    update status value in submission model and invoice_status in invoiceHeader model
    :param doc_uuid:
    :return:
    by: amira
    date: 12/4/2021
    """
    submission = Submission.objects.get(subm_uuid=doc_uuid)
    invoice = InvoiceHeader.objects.get(id=submission.invoice_id)
    # when invoiced is cancelled from portal the invoice is cancelled locally
    submission.status = 'cancel'
    submission.save()
    invoice.invoice_status = 'cancel'
    invoice.save()
