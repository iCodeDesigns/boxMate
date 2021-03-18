from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.db.models.signals import pre_save
from django.dispatch import receiver
from issuer.models import Issuer, Receiver, Address
from codes.models import ActivityType
from codes.models import TaxSubtypes, TaxTypes
from datetime import datetime
from django.conf import settings
from currencies.models import Currency


# Create your models here.


class MainTable(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    # Core
    document_type = models.CharField(max_length=20, blank=True, null=True)
    document_type_version = models.CharField(max_length=20, blank=True, null=True)
    date_time_issued = models.DateTimeField(blank=True, null=True)
    taxpayer_activity_code = models.CharField(max_length=20, blank=True, null=True)
    internal_id = models.CharField(max_length=20, blank=True, null=True)
    purchase_order_reference = models.CharField(max_length=55, blank=True, null=True)
    purchase_order_description = models.CharField(max_length=55, blank=True, null=True)
    sales_order_reference = models.CharField(max_length=20, blank=True, null=True)
    sales_order_description = models.CharField(max_length=20, blank=True, null=True)
    proforma_invoice_number = models.CharField(max_length=50, blank=True, null=True)
    total_sales_amount = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    total_discount_amount = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    net_amount = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    total_items_discount_amount = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    extra_discount_amount = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)

    # Issuer
    issuer_type = models.CharField(max_length=55, blank=True, null=True)
    issuer_registration_num = models.CharField(max_length=20, blank=True, null=True)
    issuer_name = models.CharField(max_length=55, blank=True, null=True)
    issuer_building_num = models.CharField(max_length=55, blank=True, null=True)
    issuer_room = models.CharField(max_length=20, blank=True, null=True)
    issuer_floor = models.CharField(max_length=29, blank=True, null=True)
    issuer_street = models.CharField(max_length=55, blank=True, null=True)
    issuer_land_mark = models.CharField(max_length=55, blank=True, null=True)
    issuer_additional_information = models.CharField(max_length=55, blank=True, null=True)
    issuer_governate = models.CharField(max_length=55, blank=True, null=True)
    issuer_region_city = models.CharField(max_length=55, blank=True, null=True)
    issuer_postal_code = models.CharField(max_length=20, blank=True, null=True)
    issuer_country = models.CharField(max_length=20, blank=True, null=True)
    issuer_branch_id = models.CharField(max_length=20, blank=True, null=True)

    # Receiver
    receiver_type = models.CharField(max_length=55, blank=True, null=True)
    receiver_registration_num = models.CharField(max_length=20, blank=True, null=True)
    receiver_name = models.CharField(max_length=55, blank=True, null=True)
    receiver_building_num = models.CharField(max_length=55, blank=True, null=True)
    receiver_room = models.CharField(max_length=20, blank=True, null=True)
    receiver_floor = models.CharField(max_length=5, blank=True, null=True)
    receiver_street = models.CharField(max_length=55, blank=True, null=True)
    receiver_land_mark = models.CharField(max_length=55, blank=True, null=True)
    receiver_additional_information = models.CharField(max_length=55, blank=True, null=True)
    receiver_governate = models.CharField(max_length=55, blank=True, null=True)
    receiver_region_city = models.CharField(max_length=55, blank=True, null=True)
    receiver_postal_code = models.CharField(max_length=20, blank=True, null=True)
    receiver_country = models.CharField(max_length=20, blank=True, null=True)

    # Payment
    bank_name = models.CharField(max_length=20, blank=True, null=True)
    bank_address = models.CharField(max_length=20, blank=True, null=True)
    bank_account_no = models.CharField(max_length=55, blank=True, null=True)
    bank_account_iban = models.CharField(max_length=55, blank=True, null=True)
    swift_code = models.CharField(max_length=20, blank=True, null=True)
    payment_terms = models.CharField(max_length=20, blank=True, null=True)

    # Delivery
    approach = models.CharField(max_length=20, blank=True, null=True)
    packaging = models.CharField(max_length=20, blank=True, null=True)
    date_validity = models.DateTimeField(blank=True, null=True)
    export_port = models.CharField(max_length=55, blank=True, null=True)
    country_of_origin = models.CharField(max_length=55, blank=True, null=True)
    gross_weight = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    net_weight = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    delivery_terms = models.CharField(max_length=55, blank=True, null=True)

    # Tax Total
    taxt_type = models.CharField(max_length=55, blank=True, null=True)
    tax_amount = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)

    # Signature
    signature_type = models.CharField(max_length=55, blank=True, null=True)
    signature_value = models.CharField(max_length=200, blank=True, null=True)

    # Invoice Line
    description = models.CharField(max_length=55, blank=True, null=True)
    item_type = models.CharField(max_length=20, blank=True, null=True)
    item_code = models.CharField(max_length=55, blank=True, null=True)
    unit_type = models.CharField(max_length=20, blank=True, null=True)
    quantity = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    sales_total = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    internal_code = models.CharField(max_length=20, blank=True, null=True)
    items_discount = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    net_total = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    total_taxable_fees = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    value_difference = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    total = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    # Value
    currency_sold = models.CharField(max_length=20, blank=True, null=True)
    amount_sold = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    amount_egp = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    currency_exchange_rate = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    # Discount
    discount_rate = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    # Taxable Item
    taxt_item_type = models.CharField(max_length=55, blank=True, null=True)
    tax_item_amount = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    tax_item_subtype = models.CharField(max_length=55, blank=True, null=True)
    tax_item_rate = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)


class InvoiceHeader(models.Model):
    issuer = models.ForeignKey(Issuer, on_delete=models.CASCADE, null=True, blank=True)
    issuer_address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True,
                                       related_name="issuer_address")
    receiver = models.ForeignKey(Receiver, on_delete=models.CASCADE)
    receiver_address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True,
                                         related_name="receiver_address")
    document_type = models.CharField(max_length=2,
                                     choices=[('I', 'Invoice'),('C','Credit Memo'),('D','Debit Memo')], default='I')
    document_type_version = models.CharField(max_length=8,
                                             choices=[('1.0', '1.0'), ('0.9', '0.9')], default='1.0')

    date_time_issued = models.DateTimeField(default=datetime.now())
    taxpayer_activity_code = models.ForeignKey(ActivityType, on_delete=models.CASCADE)
    internal_id = models.CharField(max_length=50)
    purchase_order_reference = models.CharField(max_length=50, null=True, blank=True)
    purchase_order_description = models.CharField(max_length=100, null=True, blank=True)
    sales_order_reference = models.CharField(max_length=50, null=True, blank=True)
    sales_order_description = models.CharField(max_length=100, null=True, blank=True)
    proforma_invoice_number = models.CharField(max_length=50, null=True, blank=True)
    total_sales_amount = models.DecimalField(decimal_places=5, max_digits=20, null=True, blank=True, default=0.0)
    total_discount_amount = models.DecimalField(decimal_places=5, max_digits=20, null=True, blank=True, default=0.0)
    net_amount = models.DecimalField(decimal_places=5, max_digits=20, null=True, blank=True, default=0.0)
    extra_discount_amount = models.DecimalField(decimal_places=5, max_digits=20, null=True, blank=True, default=0.0)
    total_items_discount_amount = models.DecimalField(decimal_places=5, max_digits=20, null=True, blank=True,
                                                      default=0.0)
    total_amount = models.DecimalField(decimal_places=5, max_digits=20, null=True, blank=True, default=0.0)

    invoice_status = models.CharField(default='draft', max_length=15)

    class Meta:
        unique_together = ('issuer' , 'internal_id')

    def calculate_header_sales_total(self):
        sales_total = InvoiceLine.objects.filter(invoice_header=self).aggregate(sales_total=Sum("salesTotal"))[
            'sales_total']
        if sales_total is not None :
            self.total_sales_amount = sales_total
        else:
            self.total_sales_amount = 0
        self.save()


    def calculate_items_discount(self):
        items_discount = InvoiceLine.objects.filter(invoice_header=self).aggregate(itemsDiscount=Sum("itemsDiscount"))[
            'itemsDiscount']
        if items_discount is not None :
            self.total_items_discount_amount = items_discount
        else:
            self.total_items_discount_amount = 0
        self.save()


    def calculate_discount_amount(self):
        total_discount_amount =InvoiceLine.objects.filter(invoice_header=self).aggregate(discount_amount=Sum("amount"))[
                'discount_amount']
        if total_discount_amount is not None :
            self.total_discount_amount = total_discount_amount
        else:
            self.total_discount_amount = 0
        self.save()

    def calculate_net_amount(self):
        net_amount = InvoiceLine.objects.filter(invoice_header=self).aggregate(net_amount=Sum("netTotal"))[
            'net_amount']
        if net_amount is not None :
            self.net_amount = net_amount
        else:
            self.net_amount = 0
        self.save()

    def calculate_total_amount(self):
        total_amount = InvoiceLine.objects.filter(invoice_header=self).aggregate(total_amount=Sum("total"))[
            'total_amount']
        if total_amount and self.extra_discount_amount is not None:
            self.total_amount = total_amount - self.extra_discount_amount
        else:
            self.total_amount = 0
        self.save()


class Signature(models.Model):
    invoice_header = models.ForeignKey(InvoiceHeader, on_delete=models.CASCADE, related_name='signatures')
    signature_type = models.CharField(max_length=20, null=True, blank=True)
    signature_value = models.TextField(null=True, blank=True)


class InvoiceLine(models.Model):
    invoice_header = models.ForeignKey(InvoiceHeader, on_delete=models.CASCADE, related_name="lines")
    description = models.CharField(max_length=250)
    itemType = models.CharField(max_length=50, help_text='Must be of GPC format')
    itemCode = models.CharField(max_length=50, help_text='Must be of GS1 code')
    unitType = models.CharField(max_length=50, help_text='A code from unitype table')
    quantity = models.DecimalField(max_digits=20, decimal_places=5)
    currencySold = models.ForeignKey(Currency,on_delete=models.CASCADE)
    amountEGP = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True)
    amountSold = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True,
                                     help_text='Mandatory if currencySold <> EGP.')
    currencyExchangeRate = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True,
                                               help_text='Exchange rate of the Egyptian bank on the day of invoicing '
                                                         'used to convert currency sold to the value of currency EGP. '
                                                         'Mandatory if currencySold is not EGP. Should be valid '
                                                         'decimal with max 5 decimal digits.')
    salesTotal = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True, default=0.00000,
                                     help_text='Total amount for the invoice line considering quantity and unit price '
                                               'in EGP (with excluded factory amounts if they are present for '
                                               'specific types in documents).')
    total = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True, default=0.0,
                                help_text='Total amount for the invoice line after adding all pricing items, taxes, '
                                          'removing discounts.')
    valueDifference = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True, default=0.00000,
                                          help_text='Value difference when selling goods already taxed (accepts +/- '
                                                    'numbers), e.g., factory value based.')
    totalTaxableFees = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True, default=0.0,
                                           help_text='Total amount of additional taxable fees to be used in final tax '
                                                     'calculation.')
    itemsDiscount = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True, default=0.0,
                                        help_text='Non-taxable items discount.')
    netTotal = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True, default=0.0,
                                   help_text='Total amount for the invoice line after applying discount.')
    rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0.0,
                               help_text='Optional: discount percentage rate applied. Must be from 0 to 100.')
    amount = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True, default=0.0,
                                 help_text='Optional: amount of discount provided to customer for this item. Should '
                                           'be smaller or equal to value Total. If percentage specified should be '
                                           'valid amount calculated from total by applying discount percentage. ')
    internalCode = models.CharField(max_length=50,
                                    help_text='Optional: Internal code used for the product being sold – can be used '
                                              'to simplify references back to existing solution.')
    created_at = models.DateField(auto_now_add=True, null=True, blank=True)
    last_updated_at = models.DateField(null=True, auto_now=True, auto_now_add=False, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                                   related_name="line_created_by")
    last_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    # for TaxLine totals
    def get_amount_egp(self):
        if self.currencySold is not None:
            if self.currencySold.code != 'EGP':
                if self.amountSold and self.currencyExchangeRate is not None:
                    self.amountEGP = self.amountSold * self.currencyExchangeRate
                else:
                    self.amountEGP = 0
                self.save()
            else:
                if self.amountEGP is None:
                    self.amountEGP = 0

    def calculate_sales_total(self):
        if self.quantity and self.amountEGP is not None:
            self.salesTotal = self.quantity * self.amountEGP
        else:
            self.salesTotal = 0
        self.save()

    def calculate_discount_amount(self):
        if self.rate is not None:
            self.amount = (self.rate / 100) * self.salesTotal
        else:
            self.amount = 0
        self.save()

    def calculate_net_total(self):
        if self.amount is not None:
            self.netTotal = self.salesTotal - self.amount
        else:
            self.netTotal = self.salesTotal
        self.save()


class TaxLine(models.Model):
    invoice_line = models.ForeignKey(InvoiceLine, on_delete=models.CASCADE, related_name='tax_lines')
    taxType = models.ForeignKey(TaxTypes, on_delete=models.CASCADE, null=True, blank=True)
    subType = models.ForeignKey(TaxSubtypes, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True)
    rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True, null=True, blank=True)
    last_updated_at = models.DateField(null=True, auto_now=True, auto_now_add=False, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                                   related_name="tax_line_created_by")
    last_updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)


class Submission(models.Model):
    invoice = models.ForeignKey(InvoiceHeader, on_delete=models.CASCADE, null=True, blank=True)
    subm_id = models.CharField(max_length=30, blank=True, null=True, unique=True)
    subm_uuid = models.CharField(max_length=100, blank=True, null=True, unique=True)
    document_count = models.IntegerField(blank=True, null=True)
    date_time_received = models.DateTimeField(blank=True, null=True)
    over_all_status = models.CharField(max_length=100, blank=True, null=True)


class HeaderTaxTotal(models.Model):
    header = models.ForeignKey(InvoiceHeader, on_delete=models.CASCADE, null=True, blank=True)
    tax = models.ForeignKey(TaxTypes, on_delete=models.CASCADE, null=True, blank=True)
    total = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True)
