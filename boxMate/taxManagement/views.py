from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from taxManagement.resources import MainTableResource
from tablib import Dataset
from django.conf import settings
from taxManagement.tmp_storage import TempFolderStorage
from django.db.models import Count
from .models import MainTable, InvoiceHeader ,InvoiceLine , TaxTypes,TaxLine
from issuer.models import Issuer,Receiver
from codes.models import ActivityType , TaxSubtypes, TaxTypes
from rest_framework.decorators import api_view


TMP_STORAGE_CLASS = getattr(settings, 'IMPORT_EXPORT_TMP_STORAGE_CLASS',
                            TempFolderStorage)


def write_to_tmp_storage(import_file):
    tmp_storage = TMP_STORAGE_CLASS()
    data = bytes()
    for chunk in import_file.chunks():
        data += chunk

    tmp_storage.save(data, 'rb')
    return tmp_storage




# @api_view(['POST', ])
def import_data_to_invoice():
    #### to be tested ####
    headers = MainTable.objects.values('document_type','document_type_version',
    'date_time_issued','taxpayer_activity_code','internal_id',
    'purchase_order_reference','purchase_order_description','sales_order_reference',
    'sales_order_description','proforma_invoice_number','total_sales_amount',
    'total_discount_amount','net_amount','total_amount','total_items_discount_amount',
    'extra_discount_amount','issuer_registration_num','receiver_registration_num',
    'signature_type').annotate(Count('internal_id'))
    for header in headers:
        issuer = Issuer.objects.get(reg_num=header['issuer_registration_num'])
        receiver = Receiver.objects.get(reg_num=header['receiver_registration_num'])
        taxpayer_activity_code = ActivityType.objects.get(code=header['taxpayer_activity_code'])
        header_obj = InvoiceHeader(
            issuer = issuer,
            receiver = receiver,
            document_type = header['document_type'],
            document_type_version =header['document_type_version'],
            date_time_issued = header['date_time_issued'],
            taxpayer_activity_code=taxpayer_activity_code,
            internal_id = header['internal_id'],
            purchase_order_reference = header['purchase_order_reference'],
            purchase_order_description = header['purchase_order_description'],
            sales_order_reference = header['sales_order_reference'],
            sales_order_description = header['sales_order_description'],
            proforma_invoice_number = header['proforma_invoice_number'],
            total_sales_amount = header['total_sales_amount'],
            total_discount_amount = header['total_discount_amount'],
            net_amount = header['net_amount'],
            extra_discount_amount = header['extra_discount_amount'],
            total_items_discount_amount = header['total_items_discount_amount'],
            total_amount = header['total_amount'],
            signature= header['signature_type']
        )
        header_obj.save()
        ####### create lines per invoice header #######
        lines = MainTable.objects.values('description','item_code','item_type',
        'unit_type','quantity', 'sales_total','currency_sold','amount_egp',
        'amount_sold','currency_exchange_rate','total','value_difference',
        'total_taxable_fees','items_discount','net_total','discount_rate',
        'discount_amount','internal_code').annotate(Count('item_code'))
        for line in lines:
            line_obj = InvoiceLine(
                invoice_header=header_obj,
                description = line['description'],
                itemType = line['item_type'],
                itemCode = line['item_code'],
                unitType = line['unit_type'],
                quantity = line['quantity'],
                currencySold = line['currency_sold'],
                amountEGP = line['amount_egp'],
                amountSold = line['amount_sold'],
                currencyExchangeRate = line['currency_exchange_rate'],
                salesTotal = line['sales_total'],
                total = line['total'],
                valueDifference = line['value_difference'],
                totalTaxableFees = line['total_taxable_fees'],
                itemsDiscount = line['items_discount'],
                netTotal = line['net_total'],
                rate = line['discount_rate'],
                amount = line['discount_amount'],
                internalCode = line['internal_code'],
            )
            line_obj.save()
            ##### create tax lines per invoice line #####
            tax_types = MainTable.objects.values('taxt_item_type','tax_item_amount',
            'tax_item_subtype','tax_item_rate').annotate(Count('internal_id')).annotate(Count('item_code'))
            for tax_type in tax_types:
                tax_main_type = TaxTypes.objects.get(code = tax_type['taxt_item_type'])
                tax_subtype = TaxSubtypes.objects.get(code = tax_type['tax_item_subtype'])
                tax_type_obj = TaxLine(
                    invoice_line=line_obj,
                    taxType = tax_main_type,
                    subType = tax_subtype,
                    amount = tax_type['tax_item_amount'],
                    rate = tax_type['tax_item_rate']
                )
                tax_type_obj.save()
# Create your views here.
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
                                                 file_name=tmp_storage.name,)
        tmp_storage.remove()

    else:
        print(result.base_errors)
        data = {"success": False, "error": {"code": 400, "message": "Invalid Excel sheet"}}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    data = {"success": True}
    return Response(data, status=status.HTTP_200_OK)

