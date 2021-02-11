from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from issuer.models import Issuer, Receiver, Address
from codes.models import ActivityType
from codes.models import TaxSubtypes, TaxTypes
from datetime import datetime


# Create your models here.


class MainTable(models.Model):
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
    receiver = models.ForeignKey(Receiver, on_delete=models.CASCADE, null=True, blank=True)
    receiver_address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True,
                                         related_name="receiver_address")
    document_type = models.CharField(max_length=2,
                                     choices=[('i', 'invoice')], default='i', null=True, blank=True)
    document_type_version = models.CharField(max_length=8,
                                             choices=[('1.0', '1.0'), ('0.9', '0.9')], default='1.0', null=True,
                                             blank=True)

    date_time_issued = models.DateTimeField(default=datetime.now()
                                            , null=True, blank=True)
    taxpayer_activity_code = models.ForeignKey(ActivityType, on_delete=models.CASCADE, null=True, blank=True)
    internal_id = models.CharField(max_length=50, null=True, blank=True)
    purchase_order_reference = models.CharField(max_length=50, null=True, blank=True)
    purchase_order_description = models.CharField(max_length=100, null=True, blank=True)
    sales_order_reference = models.CharField(max_length=50, null=True, blank=True)
    sales_order_description = models.CharField(max_length=100, null=True, blank=True)
    proforma_invoice_number = models.CharField(max_length=50, null=True, blank=True)
    total_sales_amount = models.DecimalField(decimal_places=5, max_digits=20, null=True, blank=True)
    total_discount_amount = models.DecimalField(decimal_places=5, max_digits=20, null=True, blank=True)
    net_amount = models.DecimalField(decimal_places=5, max_digits=20, null=True, blank=True)
    extra_discount_amount = models.DecimalField(decimal_places=5, max_digits=20, null=True, blank=True)
    total_items_discount_amount = models.DecimalField(decimal_places=5, max_digits=20, null=True, blank=True)
    total_amount = models.DecimalField(decimal_places=5, max_digits=20, null=True, blank=True)

    def __str__(self):
        return str(self.issuer.name + ' ' + self.receiver.name)

    def calculate_total_sales(self):
        self.total_sales_amount = 0
        for line in self.lines.all():
            print(line)
            self.total_sales_amount = self.total_sales_amount + line.salesTotal

    def calculate_total_item_discount(self):
        self.total_discount_amount = 0
        for line in self.lines.all():
            self.total_discount_amount = (
                self.total_discount_amount + line.amount if line.amount is not None else self.total_discount_amount)

    def calculate_net_total(self):
        self.net_amount = 0
        for line in self.lines.all():
            self.net_amount = self.net_amount + line.netTotal


class Signature(models.Model):
    invoice_header = models.ForeignKey(InvoiceHeader, on_delete=models.CASCADE, related_name='signatures')
    signature_type = models.CharField(max_length=20, null=True, blank=True)
    signature_value = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.signature_type


class InvoiceLine(models.Model):
    invoice_header = models.ForeignKey(InvoiceHeader, on_delete=models.CASCADE, related_name="lines")
    description = models.CharField(max_length=250, blank=True, null=True)
    itemType = models.CharField(max_length=50, blank=True, null=True, help_text='Must be of GPC format')
    itemCode = models.CharField(max_length=50, blank=True, null=True, help_text='Must be of GS1 code')
    unitType = models.CharField(max_length=50, blank=True, null=True, help_text='A code from unitype table')
    quantity = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True)
    currencySold = models.CharField(max_length=10, blank=True, null=True, help_text='Currency code used from ISO 4217.')
    amountEGP = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True)
    amountSold = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True,
                                     help_text='Mandatory if currencySold <> EGP.')
    currencyExchangeRate = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True,
                                               help_text='Exchange rate of the Egyptian bank on the day of invoicing '
                                                         'used to convert currency sold to the value of currency EGP. '
                                                         'Mandatory if currencySold is not EGP. Should be valid '
                                                         'decimal with max 5 decimal digits.')
    salesTotal = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True,
                                     help_text='Total amount for the invoice line considering quantity and unit price '
                                               'in EGP (with excluded factory amounts if they are present for '
                                               'specific types in documents).')
    total = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True,
                                help_text='Total amount for the invoice line after adding all pricing items, taxes, '
                                          'removing discounts.')
    valueDifference = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True,
                                          help_text='Value difference when selling goods already taxed (accepts +/- '
                                                    'numbers), e.g., factory value based.')
    totalTaxableFees = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True,
                                           help_text='Total amount of additional taxable fees to be used in final tax '
                                                     'calculation.')
    itemsDiscount = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True,
                                        help_text='Non-taxable items discount.')
    netTotal = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True,
                                   help_text='Total amount for the invoice line after applying discount.')
    rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                               help_text='Optional: discount percentage rate applied. Must be from 0 to 100.')
    amount = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True,
                                 help_text='Optional: amount of discount provided to customer for this item. Should '
                                           'be smaller or equal to value Total. If percentage specified should be '
                                           'valid amount calculated from total by applying discount percentage. ')
    internalCode = models.CharField(max_length=50, blank=True, null=True,
                                    help_text='Optional: Internal code used for the product being sold – can be used '
                                              'to simplify references back to existing solution.')
    created_at = models.DateField(auto_now_add=True, null=True, blank=True)
    last_updated_at = models.DateField(null=True, auto_now=True, auto_now_add=False, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                   related_name="line_created_by")
    last_updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.itemCode

    def calculate_sales_total(self):
        if self.amountSold is not None:
            self.salesTotal = self.quantity * self.amountSold
        else:
            self.salesTotal = self.quantity * self.amountEGP

    def calculate_discount_amount(self):
        if self.rate is not None:
            self.amount = self.rate * self.salesTotal / 100

    def calculate_net_total(self):
        if self.amount is not None:
            self.netTotal = self.salesTotal - self.amount
        else:
            self.netTotal = self.salesTotal


class TaxLine(models.Model):
    invoice_line = models.ForeignKey(InvoiceLine, on_delete=models.CASCADE, related_name='tax_lines')
    taxType = models.ForeignKey(TaxTypes, on_delete=models.CASCADE, null=True, blank=True)
    subType = models.ForeignKey(TaxSubtypes, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True)
    rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True, null=True, blank=True)
    last_updated_at = models.DateField(null=True, auto_now=True, auto_now_add=False, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                   related_name="tax_line_created_by")
    last_updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.invoice_line.itemCode + ' ' + self.taxType.code)


class Submission(models.Model):
    invoice = models.ForeignKey(InvoiceHeader, on_delete=models.CASCADE, null=True, blank=True)
    subm_id = models.CharField(max_length=30, blank=True, null=True, unique=True)
    subm_uuid = models.CharField(max_length=100, blank=True, null=True,unique=True)
    document_count = models.IntegerField(blank=True, null=True)
    date_time_received = models.DateTimeField(blank=True, null=True)
    over_all_status = models.CharField(max_length=100, blank=True, null=True)



@receiver(pre_save, sender='taxManagement.InvoiceLine')
def update_total_line(sender, instance, **kwargs):
    instance.calculate_sales_total()
    instance.calculate_discount_amount()
    instance.calculate_net_total()
