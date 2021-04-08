from decimal import Decimal
from taxManagement.models import (MainTable, InvoiceHeader, InvoiceLine, TaxTypes, TaxLine, Signature, Submission,
                                  HeaderTaxTotal)
from issuer.models import (Issuer, Receiver, Address)
from codes.models import (ActivityType, TaxSubtypes, TaxTypes, CountryCode)
from issuer import views as issuer_views


class Invoicegeneration:
    """
    name : Invoice generation class
    made by : ahd hozayen
    date : 7-Mar-2021
    purpose : this class used to organize the way of generating Invoice JSON file.
    """

    def __init__(self, invoice_id):
        self.invoice_id = invoice_id

    def get_issuer_address(self):
        invoice = InvoiceHeader.objects.get(id=self.invoice_id)
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

    def get_issuer_body(self):
        invoice = InvoiceHeader.objects.get(id=self.invoice_id)
        issuer_id = invoice.issuer
        issuer = Issuer.objects.get(id=issuer_id.id)

        type = issuer.type
        reg_num = issuer.reg_num
        name = issuer.name

        address = self.get_issuer_address()

        return {
            "address": address,
            "type": type,
            "id": reg_num,
            "name": name,
        }

    def get_receiver_address(self):
        invoice = InvoiceHeader.objects.get(id=self.invoice_id)
        address_id = invoice.receiver_address
        print("###", address_id)
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

    def get_receiver_body(self):
        invoice = InvoiceHeader.objects.get(id=self.invoice_id)
        receiver_id = invoice.receiver
        receiver = Receiver.objects.get(id=receiver_id.id)

        type = receiver.type
        reg_num = receiver.reg_num
        name = receiver.name

        address = self.get_receiver_address()

        return {
            "address": address,
            "type": type,
            "id": reg_num,
            "name": name,
        }

    def get_invoice_header(self):
        invoice_header = InvoiceHeader.objects.get(id=self.invoice_id)
        signatures = Signature.objects.filter(invoice_header=invoice_header)
        taxtotals = HeaderTaxTotal.objects.filter(header=invoice_header)
        tax_total_list = []
        for total in taxtotals:
            tax_total_object = {
                "taxType": total.tax.code,
                "amount": Decimal(format(total.total, '.5f'))
            }
            tax_total_list.append(tax_total_object)
        signature_list = []
        for signature in signatures:
            signature_obj = {
                "signatureType": signature.signature_type,
                "value": signature.signature_value
            }
            signature_list.append(signature_obj)

        # amira test
        invoice_lines = self.get_invoice_lines()

        data = {
            "documentType": invoice_header.document_type,
            "documentTypeVersion": invoice_header.document_type_version,
            "dateTimeIssued": "2021-04-07T15:37:51Z",
            # "dateTimeIssued": datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + "Z",     # commented by ahd due to server errors with dat format.
            "taxpayerActivityCode": invoice_header.taxpayer_activity_code.code,
            "internalID": invoice_header.internal_id,
            "purchaseOrderReference": invoice_header.purchase_order_reference,
            "purchaseOrderDescription": invoice_header.purchase_order_description,
            "salesOrderReference": invoice_header.sales_order_description,
            "salesOrderDescription": invoice_header.sales_order_description,
            "proformaInvoiceNumber": invoice_header.proforma_invoice_number,
            # payment
            "payment": {
                "bankName": "",
                "bankAddress": "",
                "bankAccountNo": "",
                "bankAccountIBAN": "",
                "swiftCode": "",
                "terms": ""
            },
            #invoicelines
            "invoiceLines": invoice_lines,
            "totalDiscountAmount": Decimal(format(invoice_header.total_discount_amount, '.5f')),
            "totalSalesAmount": Decimal(format(invoice_header.total_sales_amount, '.5f')),
            "netAmount": Decimal(format(invoice_header.net_amount, '.5f')),
            "taxTotals": tax_total_list,
            "totalAmount": Decimal(format(invoice_header.total_amount, '.5f')),
            "extraDiscountAmount": Decimal(format(invoice_header.extra_discount_amount, '.5f')),
            "totalItemsDiscountAmount": Decimal(format(invoice_header.total_items_discount_amount, '.5f')),
            "signatures": signature_list
        }
        print('signature: ', data)
        return data

    def get_taxable_lines(self, invoice_line_id):
        tax_lines = TaxLine.objects.filter(invoice_line__id=invoice_line_id)
        tax_lines_list = []
        if len(tax_lines) != 0:
            for line in tax_lines:
                tax_line = {"taxType": line.taxType.code, "amount": Decimal(format(line.amount, '.5f')),
                            "subType": line.subType.code, "rate": Decimal(format(line.rate, '.2f'))}
                tax_lines_list.append(tax_line)
        return tax_lines_list

    def get_invoice_lines(self):
        invoice_lines = InvoiceLine.objects.filter(
            invoice_header__id=self.invoice_id)
        invoice_lines_list = []
        for line in invoice_lines:
            if line.amountSold:
                amountSold = Decimal(format(line.amountSold, '.5f'))
            else:
                amountSold = Decimal(format(0, '.5f'))
            if line.currencyExchangeRate:
                currencyExchangeRate = Decimal(format(line.currencyExchangeRate, '.5f'))
            else:
                currencyExchangeRate = Decimal(format(0, '.5f'))
            invoice_line = {
                "description": line.description,
                "itemType": line.itemType,
                "itemCode": line.itemCode,
                "unitType": line.unitType,
                "quantity": Decimal(line.quantity),
                "internalCode": line.internalCode,
                "salesTotal": Decimal(format(line.salesTotal, '.5f')),
                "total": Decimal(format(line.total, '.5f')),
                "valueDifference": Decimal(format(line.valueDifference, '.5f')),
                "totalTaxableFees": Decimal(format(line.totalTaxableFees, '.5f')),
                "netTotal": Decimal(format(line.netTotal, '.5f')),
                "itemsDiscount": Decimal(format(line.itemsDiscount, '.5f')),
                "unitValue": {
                    "amountEGP": Decimal(format(line.amountEGP, '.5f')),
                    "amountSold": amountSold,
                    "currencyExchangeRate": currencyExchangeRate,
                    "currencySold": line.currencySold.code},
                "discount": {"rate": Decimal(format(line.rate, '.2f')),
                             "amount": Decimal(format(line.amount, '.5f'))
                             }
            }

            taxable_lines = self.get_taxable_lines(line.id)
            invoice_line.update({"taxableItems": taxable_lines})
            invoice_lines_list.append(invoice_line)
        print('lines: ', invoice_lines_list)
        return invoice_lines_list

    def get_one_invoice(self):
        issuer_body = self.get_issuer_body()
        receiver_body = self.get_receiver_body()
        invoice_header = self.get_invoice_header()
        # invoice_lines = self.get_invoice_lines()

        invoice = {

            "issuer": issuer_body,
            "receiver": receiver_body,

        }
        doc = {
            "documents": []
        }
        # invoice.update({"invoiceLines": invoice_lines})
        invoice.update(invoice_header)
        doc["documents"] = [invoice]

        print('invoice: ', type(invoice))
        return doc
