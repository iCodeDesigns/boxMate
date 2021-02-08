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
from .models import MainTable, InvoiceHeader ,InvoiceLine , TaxTypes,TaxLine
from issuer.models import Issuer,Receiver
from codes.models import ActivityType , TaxSubtypes, TaxTypes
from rest_framework.decorators import api_view
from issuer.models import *
from codes.models import *
import pprint



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
    'signature_type', 'issuer_branch_id','receiver_building_num','receiver_floor','receiver_room').annotate(Count('internal_id'))
    for header in headers:
        issuer_address = Address.objects.get(branch_id=header['issuer_branch_id'])
        receiver_address = Address.objects.get(buildingNumber=header['receiver_building_num'], floor=header['receiver_floor'], room=header['receiver_room'])
        issuer = Issuer.objects.get(reg_num=header['issuer_registration_num'])
        receiver = Receiver.objects.get(reg_num=header['receiver_registration_num'])
        taxpayer_activity_code = ActivityType.objects.get(code=header['taxpayer_activity_code'])
        header_obj = InvoiceHeader(
            issuer = issuer,
            issuer_address = issuer_address,
            receiver = receiver,
            receiver_address = receiver_address,
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
                                                 file_name=tmp_storage.name, )
        tmp_storage.remove()

    else:
        print(result.base_errors)
        data = {"success": False, "error": {"code": 400, "message": "Invalid Excel sheet"}}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    data = {"success": True}
    return Response(data, status=status.HTTP_200_OK)


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
            "buildingNumber":buildingNumber,
            "postalCode": postalCode,
            "floor": floor,
            "room": room,
            "landmark": landmark,
            "additionalInformation": additionalInformation
                    }


def get_receiver_address(invoice_id):
    invoice = InvoiceHeader.objects.get(internal_id=invoice_id)
    address_id = invoice.receiver_address
    address = Address.objects.get(id=address_id.id)

    country_id = address.country
    country_code = CountryCode.objects.get(code=country_id.code)
    country = country_code.code

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
        "buildingNumber":buildingNumber,
        "postalCode": postalCode,
        "floor": floor,
        "room": room,
        "landmark":landmark,
        "additionalInformation":additionalInformation
            }
    


def get_invoice_header(invoice_id):
    # will return  {
    #                 "documentType": "I",
    #             "documentTypeVersion": "0.9",
    #             "dateTimeIssued": "2020-11-11T02:04:45Z",
    #             "taxpayerActivityCode": "4620",
    #             "internalID": "IID1",
    #             "purchaseOrderReference": "P-233-A6375",
    #             "purchaseOrderDescription": "purchase Order description",
    #             "salesOrderReference": "1231",
    #             "salesOrderDescription": "Sales Order description",
    #             "proformaInvoiceNumber": "SomeValue",
    #             "payment": {
    #                 "bankName": "SomeValue",
    #                 "bankAddress": "SomeValue",
    #                 "bankAccountNo": "SomeValue",
    #                 "bankAccountIBAN": "",
    #                 "swiftCode": "",
    #                 "terms": "SomeValue"
    #             },
    #             "delivery": {
    #                 "approach": "SomeValue",
    #                 "packaging": "SomeValue",
    #                 "dateValidity": "2020-09-28T09:30:10Z",
    #                 "exportPort": "SomeValue",
    #                 "countryOfOrigin": "LS",
    #                 "grossWeight": 10.59100,
    #                 "netWeight": 20.58700,
    #                 "terms": "SomeValue"
    #             },
    #             "totalDiscountAmount": 214.41458,
    #             "totalSalesAmount": 4419.56300,
    #             "netAmount": 4205.14842,
    #             "taxTotals": [
    #                 {
    #                     "taxType": "T1",
    #                     "amount": 1286.79112
    #                 },
    #                 {
    #                     "taxType": "T2",
    #                     "amount": 984.78912
    #                 }
    #             ],
    #             "totalAmount": 14082.88542,
    #             "extraDiscountAmount": 5.00000,
    #             "totalItemsDiscountAmount": 25.00000,
    #             "signatures": [
    #                 {
    #                     "signatureType": "I",
    #                     "value": "MIII0QYJKoZIhvcNAQcCoIIIwjCCCL4CAQMxDTALBglghkgBZQMEAgEwCwYJKoZIhvcNAQcFoIIGDzCCBgswggPzoAMCAQICEB7WHdVfBczn8ZiawvdzGP0wDQYJKoZIhvcNAQELBQAwRDELMAkGA1UEBhMCRUcxFDASBgNVBAoTC0VneXB0IFRydXN0MR8wHQYDVQQDExZFZ3lwdCBUcnVzdCBTZWFsaW5nIENBMB4XDTIwMDkyODAwMDAwMFoXDTIxMDkyODIzNTk1OVowggFYMRgwFgYDVQRhDA9WQVRFRy02NzQ4NTk1NDUxIjAgBgNVBAsMGVRBWCBJRCAtIDIyNTUwMDAwODExMDAwMTAxJTAjBgNVBAsMHE5hdGlvbmFsIElEIC0gMjcxMDExMjIxMDEzNzQxcTBvBgNVBAoMaNi02LHZg9mHINin2YTYtdmI2YHZiiDZhNmE2KrYrNin2LHZhyDZiNin2YTYqtmI2LHZitiv2KfYqiDYudio2K/Yp9mE2LnYstmK2LIg2KfYqNix2KfZh9mK2YUg2KfZhNi12YjZgdmKMXEwbwYDVQQDDGjYtNix2YPZhyDYp9mE2LXZiNmB2Yog2YTZhNiq2KzYp9ix2Ycg2YjYp9mE2KrZiNix2YrYr9in2Kog2LnYqNiv2KfZhNi52LLZitiyINin2KjYsdin2YfZitmFINin2YTYtdmI2YHZijELMAkGA1UEBhMCRUcwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCccO0oSnJjeL3Ebf8pLON\u002Br2dUrn3o9y8pdxOLEV\u002BLcmVBYlM2fY01jk6vU4BLmPFoYBclwD/smbtrXvXMQeeTH\u002B/2z8VZrDrsZwx3GpF5Auu0k/eruUrGN1W8LqSkMsCcIgseODTbjkn9tACdtFkYkrbnmqRuA9Cxc0kenscYTvtj4iUVjmJSnUK32c41kGQYmXyBCyfMKcxGFiF8\u002Bogg74CELrtVJfYA3toFGieRrD2JM\u002BziqbxfwjjtYayMHg\u002BPaOH06Qh/3JW/FyeQyRm3HYgxKxEGSMtPJAw/PsfqvsWOP5cGhgzPtsqQHyRCupLmSbYrS0dXg6/ZF1FAPyirAgMBAAGjgeIwgd8wCQYDVR0TBAIwADBQBgNVHR8ESTBHMEWgQ6BBhj9odHRwOi8vbXBraWNybC5lZ3lwdHRydXN0LmNvbS9FZ3lwdFRydXN0U2VhbGluZ0NBL0xhdGVzdENSTC5jcmwwCwYDVR0PBAQDAgbAMB0GA1UdDgQWBBSgbTpnmRnzk7m07ys9uTcWvVGzkDAfBgNVHSMEGDAWgBS15KC43nSgLTbHhRpk/f8aINUKwzARBglghkgBhvhCAQEEBAMCB4AwIAYDVR0RBBkwF4EVZXllaGlhQGVneXB0dHJ1c3QuY29tMA0GCSqGSIb3DQEBCwUAA4ICAQC7wmdpRtWiIuQsokfjUl3pruOsX7NBU46h\u002B\u002BWReQR/ceEcdzDRBVqwM7FKsTZy3/i6ACSE9MUMpMUPgtR\u002BneBq1cuknFSqhgQmnOa8mG2/nUjISNhyrcrnFSYrmJyBxT2wOO8xwtLDA2PQJIdG/n1Xn6YxwU7gbB0NApPmORhMfD1S6KINzvTj1D/EIpMaKzg7DC4wYgR2UbO8dFvNgaNtze/GRks7xQC4KMJ9udaf0JBOzyvuGtjzsB\u002B69XG0t68WVXyTIqxBZKVVU4jqG9JZdKhCHgr2P2G4nEJxTiXf3cl6iemdC1JezaoGW5FEph/wFqswiP05TVQdLOB9EkurvdrBF6sY8Xbk/2st5FvG9uAUuyQjzUETA/As4Clqr9dNirT6OVzWhI06S8CTgOONXwWTx9CjCoc\u002BERx8ce20YgVipZnKfz2MRy3bCF37\u002BCOgNyPNXy/bneFlSKEpMPYUKk5jt2z3G/I9gyozaXVGZ3sFjxHu0UX5fuiP7xknmPDdSi\u002BMwEfnh8EApgSvPlY7RLWQU8A2cUqWrCOvvuQfc2C5VG8CBP\u002BldOZt54OXSfEnx2841bTyKJGP86NvAZOTN9wFKoyhBztN9FmhG69IWbtsxdit2pbgCofh751MsN1Zbp9JerLwBxrmcEmUZfwSvE8ojOipxaszLKzg1SO7QTGCAogwggKEAgEBMFgwRDELMAkGA1UEBhMCRUcxFDASBgNVBAoTC0VneXB0IFRydXN0MR8wHQYDVQQDExZFZ3lwdCBUcnVzdCBTZWFsaW5nIENBAhAe1h3VXwXM5/GYmsL3cxj9MAsGCWCGSAFlAwQCAaCCAQUwGAYJKoZIhvcNAQkDMQsGCSqGSIb3DQEHBTAcBgkqhkiG9w0BCQUxDxcNMjAxMTAzMTAwMTQ4WjAvBgkqhkiG9w0BCQQxIgQgUt/GoPN5xkeHpV4L5olwuicaAObCbf0ORKgN4O260CIwgZkGCyqGSIb3DQEJEAIvMYGJMIGGMIGDMIGABCD6bb7asgHoS/gNVKpFneOpR/9uWobTYwah5r9IQzH\u002BcTBcMEigRjBEMQswCQYDVQQGEwJFRzEUMBIGA1UEChMLRWd5cHQgVHJ1c3QxHzAdBgNVBAMTFkVneXB0IFRydXN0IFNlYWxpbmcgQ0ECEB7WHdVfBczn8ZiawvdzGP0wCwYJKoZIhvcNAQEBBIIBAC3gpQ0ldw5TCYHG0rNMGveNtoC2vRWk7EXjPCYQJS11fkBnZ6VWAgcFtJrBHzv0x81Ik6ngvXlrl/bmB0yCm71yLcL4iBFRvB1CQ8nBlnrx24xD2OQPC\u002Bjza/7yt/y747kaJgoOcmP5Q7k92vtnIxdO\u002BX0SI3Jb9\u002BuByvJEZZTFHnjXie4gKLyR2HZqHB2VLf/scBTe2\u002BzxQx3p3Hn15Sh7Muufw0ARpZkuiT5haskusdGRF2JEsHtGX/X57JmXzHdOms/mDusbg4Mee2tLT\u002B67Bnz8FAX8qTMD8oCtOdfQaKQDhyyCsqxeLUMJ5oM28ZA/Ncf\u002BMlmVl0\u002BHKkGS13c="
    #                 }
    #             ]
    #         }
    pass


def get_invoice_lines(invoice_id):
    # for every line it will call the function get_taxable_lines(invoice_line_id)
    # will return
    #               [
    #                 {
    #                     "description": "Computer1",
    #                     "itemType": "GPC",
    #                     "itemCode": "10003752",
    #                     "unitType": "EA",
    #                     "quantity": 7.00000,
    #                     "internalCode": "IC0",
    #                     "salesTotal": 662.90000,
    #                     "total": 2220.08914,
    #                     "valueDifference": 7.00000,
    #                     "totalTaxableFees": 618.69212,
    #                     "netTotal": 649.64200,
    #                     "itemsDiscount": 5.00000,
    #                     "unitValue": {
    #                         "currencySold": "USD",
    #                         "amountEGP": 94.70000,
    #                         "amountSold": 4.73500,
    #                         "currencyExchangeRate": 20.00000
    #                     },
    #                     "discount": {
    #                         "rate": 2,
    #                         "amount": 13.25800
    #                     },
    #                     "taxableItems": [
    #                             {
    #                                 "taxType": "T1",
    #                                 "amount": 385.24093,
    #                                 "subType": "T1",
    #                                 "rate": 14.00
    #                             },
    #                             {
    #                                 "taxType": "T2",
    #                                 "amount": 294.82724,
    #                                 "subType": "T2",
    #                                 "rate": 12
    #                             }
    #                           ]

    #                  }
    #                ]
    pass


def get_taxable_lines(invoice_line_id):
    # will return [
    #                             {
    #                                 "taxType": "T1",
    #                                 "amount": 204.67639,
    #                                 "subType": "T1",
    #                                 "rate": 14.00
    #                             },
    #                             {
    #                                 "taxType": "T2",
    #                                 "amount": 156.64009,
    #                                 "subType": "T2",
    #                                 "rate": 12
    #                             },
    #                             {
    #                                 "taxType": "T3",
    #                                 "amount": 30.00000,
    #                                 "subType": "T3",
    #                                 "rate": 0.00
    #                             },
    #                             {
    #                                 "taxType": "T4",
    #                                 "amount": 32.23210,
    #                                 "subType": "T4",
    #                                 "rate": 5.00
    #                             }
    #                         }
    #                      ]

    pass


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
    invoice.update(invoice_lines)
    print(invoice)


def submit_invoice():
    data = {
        "documents": [
            {
                "issuer": {
                    "address": {
                        "branchID": "0",
                        "country": "EG",
                        "governate": "Cairo",
                        "regionCity": "Nasr City",
                        "street": "580 Clementina Key",
                        "buildingNumber": "Bldg. 0",
                        "postalCode": "68030",
                        "floor": "1",
                        "room": "123",
                        "landmark": "7660 Melody Trail",
                        "additionalInformation": "beside Townhall"
                    },
                    "type": "B",
                    "id": "113317713",
                    "name": "Issuer Company"
                },
                "receiver": {
                    "address": {
                        "country": "EG",
                        "governate": "Egypt",
                        "regionCity": "Mufazat al Ismlyah",
                        "street": "580 Clementina Key",
                        "buildingNumber": "Bldg. 0",
                        "postalCode": "68030",
                        "floor": "1",
                        "room": "123",
                        "landmark": "7660 Melody Trail",
                        "additionalInformation": "beside Townhall"
                    },
                    "type": "B",
                    "id": "313717919",
                    "name": "Receiver"
                },
                "documentType": "I",
                "documentTypeVersion": "0.9",
                "dateTimeIssued": "2020-11-11T02:04:45Z",
                "taxpayerActivityCode": "4620",
                "internalID": "IID1",
                "purchaseOrderReference": "P-233-A6375",
                "purchaseOrderDescription": "purchase Order description",
                "salesOrderReference": "1231",
                "salesOrderDescription": "Sales Order description",
                "proformaInvoiceNumber": "SomeValue",
                "payment": {
                    "bankName": "SomeValue",
                    "bankAddress": "SomeValue",
                    "bankAccountNo": "SomeValue",
                    "bankAccountIBAN": "",
                    "swiftCode": "",
                    "terms": "SomeValue"
                },
                "delivery": {
                    "approach": "SomeValue",
                    "packaging": "SomeValue",
                    "dateValidity": "2020-09-28T09:30:10Z",
                    "exportPort": "SomeValue",
                    "countryOfOrigin": "LS",
                    "grossWeight": 10.59100,
                    "netWeight": 20.58700,
                    "terms": "SomeValue"
                },
                "invoiceLines": [
                    {
                        "description": "Computer1",
                        "itemType": "GPC",
                        "itemCode": "10003752",
                        "unitType": "EA",
                        "quantity": 7.00000,
                        "internalCode": "IC0",
                        "salesTotal": 662.90000,
                        "total": 2220.08914,
                        "valueDifference": 7.00000,
                        "totalTaxableFees": 618.69212,
                        "netTotal": 649.64200,
                        "itemsDiscount": 5.00000,
                        "unitValue": {
                            "currencySold": "USD",
                            "amountEGP": 94.70000,
                            "amountSold": 4.73500,
                            "currencyExchangeRate": 20.00000
                        },
                        "discount": {
                            "rate": 2,
                            "amount": 13.25800
                        },
                        "taxableItems": [
                            {
                                "taxType": "T1",
                                "amount": 204.67639,
                                "subType": "T1",
                                "rate": 14.00
                            },
                            {
                                "taxType": "T2",
                                "amount": 156.64009,
                                "subType": "T2",
                                "rate": 12
                            },
                            {
                                "taxType": "T3",
                                "amount": 30.00000,
                                "subType": "T3",
                                "rate": 0.00
                            },
                            {
                                "taxType": "T4",
                                "amount": 32.23210,
                                "subType": "T4",
                                "rate": 5.00
                            },
                            {
                                "taxType": "T5",
                                "amount": 90.94988,
                                "subType": "T5",
                                "rate": 14.00
                            },
                            {
                                "taxType": "T6",
                                "amount": 60.00000,
                                "subType": "T6",
                                "rate": 0.00
                            },
                            {
                                "taxType": "T7",
                                "amount": 64.96420,
                                "subType": "T7",
                                "rate": 10.00
                            },
                            {
                                "taxType": "T8",
                                "amount": 90.94988,
                                "subType": "T8",
                                "rate": 14.00
                            },
                            {
                                "taxType": "T9",
                                "amount": 77.95704,
                                "subType": "T9",
                                "rate": 12.00
                            },
                            {
                                "taxType": "T10",
                                "amount": 64.96420,
                                "subType": "T10",
                                "rate": 10.00
                            },
                            {
                                "taxType": "T11",
                                "amount": 90.94988,
                                "subType": "T11",
                                "rate": 14.00
                            },
                            {
                                "taxType": "T12",
                                "amount": 77.95704,
                                "subType": "T12",
                                "rate": 12.00
                            },
                            {
                                "taxType": "T13",
                                "amount": 64.96420,
                                "subType": "T13",
                                "rate": 10.00
                            },
                            {
                                "taxType": "T14",
                                "amount": 90.94988,
                                "subType": "T14",
                                "rate": 14.00
                            },
                            {
                                "taxType": "T15",
                                "amount": 77.95704,
                                "subType": "T15",
                                "rate": 12.00
                            },
                            {
                                "taxType": "T16",
                                "amount": 64.96420,
                                "subType": "T16",
                                "rate": 10.00
                            },
                            {
                                "taxType": "T17",
                                "amount": 64.96420,
                                "subType": "T17",
                                "rate": 10.00
                            },
                            {
                                "taxType": "T18",
                                "amount": 90.94988,
                                "subType": "T18",
                                "rate": 14.00
                            },
                            {
                                "taxType": "T19",
                                "amount": 77.95704,
                                "subType": "T19",
                                "rate": 12.00
                            },
                            {
                                "taxType": "T20",
                                "amount": 64.96420,
                                "subType": "T20",
                                "rate": 10.00
                            }
                        ]
                    },
                    {
                        "description": "Computer2",
                        "itemType": "GPC",
                        "itemCode": "10001827",
                        "unitType": "EA",
                        "quantity": 5.00000,
                        "internalCode": "IC0",
                        "salesTotal": 947.00000,
                        "total": 3123.51323,
                        "valueDifference": 7.00000,
                        "totalTaxableFees": 858.13160,
                        "netTotal": 928.06000,
                        "itemsDiscount": 5.00000,
                        "unitValue": {
                            "currencySold": "EUR",
                            "amountEGP": 189.40000,
                            "amountSold": 10.00000,
                            "currencyExchangeRate": 18.94000
                        },
                        "discount": {
                            "rate": 2,
                            "amount": 18.94000
                        },
                        "taxableItems": [
                            {
                                "taxType": "T1",
                                "amount": 285.87644,
                                "subType": "T1",
                                "rate": 14.00
                            },
                            {
                                "taxType": "T2",
                                "amount": 218.78299,
                                "subType": "T2",
                                "rate": 12
                            },
                            {
                                "taxType": "T3",
                                "amount": 30.00000,
                                "subType": "T3",
                                "rate": 0.00
                            },
                            {
                                "taxType": "T4",
                                "amount": 46.15300,
                                "subType": "T4",
                                "rate": 5.00
                            },
                            {
                                "taxType": "T5",
                                "amount": 129.92840,
                                "subType": "T5",
                                "rate": 14.00
                            },
                            {
                                "taxType": "T6",
                                "amount": 60.00000,
                                "subType": "T6",
                                "rate": 0.00
                            },
                            {
                                "taxType": "T7",
                                "amount": 92.80600,
                                "subType": "T7",
                                "rate": 10.00
                            },
                            {
                                "taxType": "T8",
                                "amount": 129.92840,
                                "subType": "T8",
                                "rate": 14.00
                            },
                            {
                                "taxType": "T9",
                                "amount": 111.36720,
                                "subType": "T9",
                                "rate": 12.00
                            },
                            {
                                "taxType": "T10",
                                "amount": 92.80600,
                                "subType": "T10",
                                "rate": 10.00
                            },
                            {
                                "taxType": "T11",
                                "amount": 129.92840,
                                "subType": "T11",
                                "rate": 14.00
                            },
                            {
                                "taxType": "T12",
                                "amount": 111.36720,
                                "subType": "T12",
                                "rate": 12.00
                            },
                            {
                                "taxType": "T13",
                                "amount": 92.80600,
                                "subType": "T13",
                                "rate": 10.00
                            },
                            {
                                "taxType": "T14",
                                "amount": 129.92840,
                                "subType": "T14",
                                "rate": 14.00
                            },
                            {
                                "taxType": "T15",
                                "amount": 111.36720,
                                "subType": "T15",
                                "rate": 12.00
                            },
                            {
                                "taxType": "T16",
                                "amount": 92.80600,
                                "subType": "T16",
                                "rate": 10.00
                            },
                            {
                                "taxType": "T17",
                                "amount": 92.80600,
                                "subType": "T17",
                                "rate": 10.00
                            },
                            {
                                "taxType": "T18",
                                "amount": 129.92840,
                                "subType": "T18",
                                "rate": 14.00
                            },
                            {
                                "taxType": "T19",
                                "amount": 111.36720,
                                "subType": "T19",
                                "rate": 12.00
                            },
                            {
                                "taxType": "T20",
                                "amount": 92.80600,
                                "subType": "T20",
                                "rate": 10.00
                            }
                        ]
                    },
                    {
                        "description": "Computer3",
                        "itemType": "GPC",
                        "itemCode": "10001516",
                        "unitType": "EA",
                        "quantity": 6.57265,
                        "internalCode": "IC0",
                        "salesTotal": 1445.98300,
                        "total": 4522.41770,
                        "valueDifference": 3.00000,
                        "totalTaxableFees": 1228.93264,
                        "netTotal": 1359.22402,
                        "itemsDiscount": 4.00000,
                        "unitValue": {
                            "currencySold": "USD",
                            "amountEGP": 220.00000,
                            "amountSold": 11.00000,
                            "currencyExchangeRate": 20.00000
                        },
                        "discount": {
                            "rate": 6,
                            "amount": 86.75898
                        },
                        "taxableItems": [
                            {
                                "taxType": "T1",
                                "amount": 410.99736,
                                "subType": "T1",
                                "rate": 14.00
                            },
                            {
                                "taxType": "T2",
                                "amount": 314.53880,
                                "subType": "T2",
                                "rate": 12
                            },
                            {
                                "taxType": "T3",
                                "amount": 30.00000,
                                "subType": "T3",
                                "rate": 0.00
                            },
                            {
                                "taxType": "T4",
                                "amount": 67.76120,
                                "subType": "T4",
                                "rate": 5.00
                            },
                            {
                                "taxType": "T5",
                                "amount": 190.29136,
                                "subType": "T5",
                                "rate": 14.00
                            },
                            {
                                "taxType": "T6",
                                "amount": 60.00000,
                                "subType": "T6",
                                "rate": 0.00
                            },
                            {
                                "taxType": "T7",
                                "amount": 135.92240,
                                "subType": "T7",
                                "rate": 10.00
                            },
                            {
                                "taxType": "T8",
                                "amount": 190.29136,
                                "subType": "T8",
                                "rate": 14.00
                            },
                            {
                                "taxType": "T9",
                                "amount": 163.10688,
                                "subType": "T9",
                                "rate": 12.00
                            },
                            {
                                "taxType": "T10",
                                "amount": 135.92240,
                                "subType": "T10",
                                "rate": 10.00
                            },
                            {
                                "taxType": "T11",
                                "amount": 190.29136,
                                "subType": "T11",
                                "rate": 14.00
                            },
                            {
                                "taxType": "T12",
                                "amount": 163.10688,
                                "subType": "T12",
                                "rate": 12.00
                            },
                            {
                                "taxType": "T13",
                                "amount": 135.92240,
                                "subType": "T13",
                                "rate": 10.00
                            },
                            {
                                "taxType": "T14",
                                "amount": 190.29136,
                                "subType": "T14",
                                "rate": 14.00
                            },
                            {
                                "taxType": "T15",
                                "amount": 163.10688,
                                "subType": "T15",
                                "rate": 12.00
                            },
                            {
                                "taxType": "T16",
                                "amount": 135.92240,
                                "subType": "T16",
                                "rate": 10.00
                            },
                            {
                                "taxType": "T17",
                                "amount": 135.92240,
                                "subType": "T17",
                                "rate": 10.00
                            },
                            {
                                "taxType": "T18",
                                "amount": 190.29136,
                                "subType": "T18",
                                "rate": 14.00
                            },
                            {
                                "taxType": "T19",
                                "amount": 163.10688,
                                "subType": "T19",
                                "rate": 12.00
                            },
                            {
                                "taxType": "T20",
                                "amount": 135.92240,
                                "subType": "T20",
                                "rate": 10.00
                            }
                        ]
                    },
                    {
                        "description": "Computer4",
                        "itemType": "GPC",
                        "itemCode": "10007938",
                        "unitType": "EA",
                        "quantity": 9.00000,
                        "internalCode": "IC0",
                        "salesTotal": 1363.68000,
                        "total": 4221.86535,
                        "valueDifference": 8.00000,
                        "totalTaxableFees": 1150.67128,
                        "netTotal": 1268.22240,
                        "itemsDiscount": 11.00000,
                        "unitValue": {
                            "currencySold": "EUR",
                            "amountEGP": 151.52000,
                            "amountSold": 8.00000,
                            "currencyExchangeRate": 18.94000
                        },
                        "discount": {
                            "rate": 7,
                            "amount": 95.45760
                        },
                        "taxableItems": [
                            {
                                "taxType": "T1",
                                "amount": 385.24093,
                                "subType": "T1",
                                "rate": 14.00
                            },
                            {
                                "taxType": "T2",
                                "amount": 294.82724,
                                "subType": "T2",
                                "rate": 12
                            },
                            {
                                "taxType": "T3",
                                "amount": 30.00000,
                                "subType": "T3",
                                "rate": 0.00
                            },
                            {
                                "taxType": "T4",
                                "amount": 62.86112,
                                "subType": "T4",
                                "rate": 5.00
                            },
                            {
                                "taxType": "T5",
                                "amount": 177.55114,
                                "subType": "T5",
                                "rate": 14.00
                            },
                            {
                                "taxType": "T6",
                                "amount": 60.00000,
                                "subType": "T6",
                                "rate": 0.00
                            },
                            {
                                "taxType": "T7",
                                "amount": 126.82224,
                                "subType": "T7",
                                "rate": 10.00
                            },
                            {
                                "taxType": "T8",
                                "amount": 177.55114,
                                "subType": "T8",
                                "rate": 14.00
                            },
                            {
                                "taxType": "T9",
                                "amount": 152.18669,
                                "subType": "T9",
                                "rate": 12.00
                            },
                            {
                                "taxType": "T10",
                                "amount": 126.82224,
                                "subType": "T10",
                                "rate": 10.00
                            },
                            {
                                "taxType": "T11",
                                "amount": 177.55114,
                                "subType": "T11",
                                "rate": 14.00
                            },
                            {
                                "taxType": "T12",
                                "amount": 152.18669,
                                "subType": "T12",
                                "rate": 12.00
                            },
                            {
                                "taxType": "T13",
                                "amount": 126.82224,
                                "subType": "T13",
                                "rate": 10.00
                            },
                            {
                                "taxType": "T14",
                                "amount": 177.55114,
                                "subType": "T14",
                                "rate": 14.00
                            },
                            {
                                "taxType": "T15",
                                "amount": 152.18669,
                                "subType": "T15",
                                "rate": 12.00
                            },
                            {
                                "taxType": "T16",
                                "amount": 126.82224,
                                "subType": "T16",
                                "rate": 10.00
                            },
                            {
                                "taxType": "T17",
                                "amount": 126.82224,
                                "subType": "T17",
                                "rate": 10.00
                            },
                            {
                                "taxType": "T18",
                                "amount": 177.55114,
                                "subType": "T18",
                                "rate": 14.00
                            },
                            {
                                "taxType": "T19",
                                "amount": 152.18669,
                                "subType": "T19",
                                "rate": 12.00
                            },
                            {
                                "taxType": "T20",
                                "amount": 126.82224,
                                "subType": "T20",
                                "rate": 10.00
                            }
                        ]
                    }
                ],
                "totalDiscountAmount": 214.41458,
                "totalSalesAmount": 4419.56300,
                "netAmount": 4205.14842,
                "taxTotals": [
                    {
                        "taxType": "T1",
                        "amount": 1286.79112
                    },
                    {
                        "taxType": "T2",
                        "amount": 984.78912
                    },
                    {
                        "taxType": "T3",
                        "amount": 120.00000
                    },
                    {
                        "taxType": "T4",
                        "amount": 209.00742
                    },
                    {
                        "taxType": "T5",
                        "amount": 588.72078
                    },
                    {
                        "taxType": "T6",
                        "amount": 240.00000
                    },
                    {
                        "taxType": "T7",
                        "amount": 420.51484
                    },
                    {
                        "taxType": "T8",
                        "amount": 588.72078
                    },
                    {
                        "taxType": "T9",
                        "amount": 504.61781

                    },
                    {
                        "taxType": "T10",
                        "amount": 420.51484
                    },
                    {
                        "taxType": "T11",
                        "amount": 588.72078
                    },
                    {
                        "taxType": "T12",
                        "amount": 504.61781
                    },
                    {
                        "taxType": "T13",
                        "amount": 420.51484

                    },
                    {
                        "taxType": "T14",
                        "amount": 588.72078
                    },
                    {
                        "taxType": "T15",
                        "amount": 504.61781
                    },
                    {
                        "taxType": "T16",
                        "amount": 420.51484
                    },
                    {
                        "taxType": "T17",
                        "amount": 420.51484
                    },
                    {
                        "taxType": "T18",
                        "amount": 588.72078
                    },
                    {
                        "taxType": "T19",
                        "amount": 504.61781
                    },
                    {
                        "taxType": "T20",
                        "amount": 420.51484
                    }
                ],
                "totalAmount": 14082.88542,
                "extraDiscountAmount": 5.00000,
                "totalItemsDiscountAmount": 25.00000,
                "signatures": [
                    {
                        "signatureType": "I",
                        "value": "MIII0QYJKoZIhvcNAQcCoIIIwjCCCL4CAQMxDTALBglghkgBZQMEAgEwCwYJKoZIhvcNAQcFoIIGDzCCBgswggPzoAMCAQICEB7WHdVfBczn8ZiawvdzGP0wDQYJKoZIhvcNAQELBQAwRDELMAkGA1UEBhMCRUcxFDASBgNVBAoTC0VneXB0IFRydXN0MR8wHQYDVQQDExZFZ3lwdCBUcnVzdCBTZWFsaW5nIENBMB4XDTIwMDkyODAwMDAwMFoXDTIxMDkyODIzNTk1OVowggFYMRgwFgYDVQRhDA9WQVRFRy02NzQ4NTk1NDUxIjAgBgNVBAsMGVRBWCBJRCAtIDIyNTUwMDAwODExMDAwMTAxJTAjBgNVBAsMHE5hdGlvbmFsIElEIC0gMjcxMDExMjIxMDEzNzQxcTBvBgNVBAoMaNi02LHZg9mHINin2YTYtdmI2YHZiiDZhNmE2KrYrNin2LHZhyDZiNin2YTYqtmI2LHZitiv2KfYqiDYudio2K/Yp9mE2LnYstmK2LIg2KfYqNix2KfZh9mK2YUg2KfZhNi12YjZgdmKMXEwbwYDVQQDDGjYtNix2YPZhyDYp9mE2LXZiNmB2Yog2YTZhNiq2KzYp9ix2Ycg2YjYp9mE2KrZiNix2YrYr9in2Kog2LnYqNiv2KfZhNi52LLZitiyINin2KjYsdin2YfZitmFINin2YTYtdmI2YHZijELMAkGA1UEBhMCRUcwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCccO0oSnJjeL3Ebf8pLON\u002Br2dUrn3o9y8pdxOLEV\u002BLcmVBYlM2fY01jk6vU4BLmPFoYBclwD/smbtrXvXMQeeTH\u002B/2z8VZrDrsZwx3GpF5Auu0k/eruUrGN1W8LqSkMsCcIgseODTbjkn9tACdtFkYkrbnmqRuA9Cxc0kenscYTvtj4iUVjmJSnUK32c41kGQYmXyBCyfMKcxGFiF8\u002Bogg74CELrtVJfYA3toFGieRrD2JM\u002BziqbxfwjjtYayMHg\u002BPaOH06Qh/3JW/FyeQyRm3HYgxKxEGSMtPJAw/PsfqvsWOP5cGhgzPtsqQHyRCupLmSbYrS0dXg6/ZF1FAPyirAgMBAAGjgeIwgd8wCQYDVR0TBAIwADBQBgNVHR8ESTBHMEWgQ6BBhj9odHRwOi8vbXBraWNybC5lZ3lwdHRydXN0LmNvbS9FZ3lwdFRydXN0U2VhbGluZ0NBL0xhdGVzdENSTC5jcmwwCwYDVR0PBAQDAgbAMB0GA1UdDgQWBBSgbTpnmRnzk7m07ys9uTcWvVGzkDAfBgNVHSMEGDAWgBS15KC43nSgLTbHhRpk/f8aINUKwzARBglghkgBhvhCAQEEBAMCB4AwIAYDVR0RBBkwF4EVZXllaGlhQGVneXB0dHJ1c3QuY29tMA0GCSqGSIb3DQEBCwUAA4ICAQC7wmdpRtWiIuQsokfjUl3pruOsX7NBU46h\u002B\u002BWReQR/ceEcdzDRBVqwM7FKsTZy3/i6ACSE9MUMpMUPgtR\u002BneBq1cuknFSqhgQmnOa8mG2/nUjISNhyrcrnFSYrmJyBxT2wOO8xwtLDA2PQJIdG/n1Xn6YxwU7gbB0NApPmORhMfD1S6KINzvTj1D/EIpMaKzg7DC4wYgR2UbO8dFvNgaNtze/GRks7xQC4KMJ9udaf0JBOzyvuGtjzsB\u002B69XG0t68WVXyTIqxBZKVVU4jqG9JZdKhCHgr2P2G4nEJxTiXf3cl6iemdC1JezaoGW5FEph/wFqswiP05TVQdLOB9EkurvdrBF6sY8Xbk/2st5FvG9uAUuyQjzUETA/As4Clqr9dNirT6OVzWhI06S8CTgOONXwWTx9CjCoc\u002BERx8ce20YgVipZnKfz2MRy3bCF37\u002BCOgNyPNXy/bneFlSKEpMPYUKk5jt2z3G/I9gyozaXVGZ3sFjxHu0UX5fuiP7xknmPDdSi\u002BMwEfnh8EApgSvPlY7RLWQU8A2cUqWrCOvvuQfc2C5VG8CBP\u002BldOZt54OXSfEnx2841bTyKJGP86NvAZOTN9wFKoyhBztN9FmhG69IWbtsxdit2pbgCofh751MsN1Zbp9JerLwBxrmcEmUZfwSvE8ojOipxaszLKzg1SO7QTGCAogwggKEAgEBMFgwRDELMAkGA1UEBhMCRUcxFDASBgNVBAoTC0VneXB0IFRydXN0MR8wHQYDVQQDExZFZ3lwdCBUcnVzdCBTZWFsaW5nIENBAhAe1h3VXwXM5/GYmsL3cxj9MAsGCWCGSAFlAwQCAaCCAQUwGAYJKoZIhvcNAQkDMQsGCSqGSIb3DQEHBTAcBgkqhkiG9w0BCQUxDxcNMjAxMTAzMTAwMTQ4WjAvBgkqhkiG9w0BCQQxIgQgUt/GoPN5xkeHpV4L5olwuicaAObCbf0ORKgN4O260CIwgZkGCyqGSIb3DQEJEAIvMYGJMIGGMIGDMIGABCD6bb7asgHoS/gNVKpFneOpR/9uWobTYwah5r9IQzH\u002BcTBcMEigRjBEMQswCQYDVQQGEwJFRzEUMBIGA1UEChMLRWd5cHQgVHJ1c3QxHzAdBgNVBAMTFkVneXB0IFRydXN0IFNlYWxpbmcgQ0ECEB7WHdVfBczn8ZiawvdzGP0wCwYJKoZIhvcNAQEBBIIBAC3gpQ0ldw5TCYHG0rNMGveNtoC2vRWk7EXjPCYQJS11fkBnZ6VWAgcFtJrBHzv0x81Ik6ngvXlrl/bmB0yCm71yLcL4iBFRvB1CQ8nBlnrx24xD2OQPC\u002Bjza/7yt/y747kaJgoOcmP5Q7k92vtnIxdO\u002BX0SI3Jb9\u002BuByvJEZZTFHnjXie4gKLyR2HZqHB2VLf/scBTe2\u002BzxQx3p3Hn15Sh7Muufw0ARpZkuiT5haskusdGRF2JEsHtGX/X57JmXzHdOms/mDusbg4Mee2tLT\u002B67Bnz8FAX8qTMD8oCtOdfQaKQDhyyCsqxeLUMJ5oM28ZA/Ncf\u002BMlmVl0\u002BHKkGS13c="
                    }
                ]
            }
        ]
    }
    auth_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjBGOTkyNkZFQTUyOTgxRjZDMjBENUMzNUQ0NjUxMzAzQ0QzQzBFMzIiLCJ0eXAiOiJhdCtqd3QiLCJ4NXQiOiJENWttX3FVcGdmYkNEVncxMUdVVEE4MDhEakkifQ.eyJuYmYiOjE2MTI0NDc2ODksImV4cCI6MTYxMjQ1MTI4OSwiaXNzIjoiaHR0cHM6Ly9pZC5wcmVwcm9kLmV0YS5nb3YuZWciLCJhdWQiOiJJbnZvaWNpbmdBUEkiLCJjbGllbnRfaWQiOiI1NDc0MTNhNC03OWVlLTQ3MTUtODUzMC1hN2RkYmUzOTI4NDgiLCJJbnRlcm1lZElkIjoiMCIsIkludGVybWVkUklOIjoiIiwiSW50ZXJtZWRFbmZvcmNlZCI6IjIiLCJuYW1lIjoiMTAwMzI0OTMyOjU0NzQxM2E0LTc5ZWUtNDcxNS04NTMwLWE3ZGRiZTM5Mjg0OCIsInNpZCI6ImJjYTAxNjc4LTk1OWEtNjUyZC0zMjc4LWM3ZTAwYzQwNTkxZSIsInByZWZlcnJlZF91c2VybmFtZSI6IkRyZWVtRVJQU3lzdGVtIiwiVGF4SWQiOiIxMDYzMCIsIlRheFJpbiI6IjEwMDMyNDkzMiIsIlByb2ZJZCI6IjIxODc4IiwiSXNUYXhBZG1pbiI6IjAiLCJJc1N5c3RlbSI6IjEiLCJOYXRJZCI6IiIsInNjb3BlIjpbIkludm9pY2luZ0FQSSJdfQ.qGf71fWwKR6O6TXPkTYZMMG3ybMVnMpFC08vB-6qYwGeRPpLXwU8S3CkzbWCiz6aMMkCf5h6hr9dycFh7hWS5c-pBd70gA5bTWyycMrKhCssvrLYrHf0rssEDPoBf5V3i1XLAUN83pl7B1tlEoy8QFOhIO0K6fqZpu5-ZY6HZHYbQO6ZdmS_Y1EpRQge8a1-O8mX_Jt11qupBZInjkKiQvDnAthO8_DpwDkM1-bJxVkIcGa0f5Umck7joSGglBUKT089-azh2PRjyorrjvqhcEMMc7aYYOlxYQwT9TnB6RFdzV235Y9PzV57ia8o2J6DbdakXJhcIEXfLXtujAP3Ig"
    url = 'https://api.preprod.invoicing.eta.gov.eg/api/v1/documentsubmissions'
    response = requests.post(url, verify=False,
                             headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + auth_token},
                             json=data)
    return response
