from django.shortcuts import render

from django.db.models import Count
from .models import MainTable, InvoiceHeader ,InvoiceLine
from issuer.models import Issuer,Receiver
from codes.models import ActivityType
from rest_framework.decorators import api_view


@api_view(['POST', ])
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
        reciever = Receiver.objects.get(reg_num=header['receiver_registration_num'])
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
        lines = MainTable.objects.filter(invoice_header=header_obj)
        for line in lines:
            line_obj = InvoiceLine(
                invoice_header=header_obj,
                description = line.description,
                itemType = line.item_type,
                itemCode = line.item_code,
                unitType = line.unit_type,
                quantity = line.quantity,
                currencySold = line.currency_sold,
                amountEGP = line.amount_egp,
                amountSold = line.amount_sold,
                currencyExchangeRate = line.currency_exchange_rate,
                salesTotal = line.sales_total,
                total = line.total,
                valueDifference = line.value_difference,
                totalTaxableFees = line.total_taxable_fees,
                itemsDiscount = line.items_discount,
                netTotal = line.net_total,
                rate = line.rate,
                amount = line.amount,
                internalCode = line.internal_code,
            )
            line_obj.save()
