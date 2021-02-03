from django.contrib.auth.models import User
from django.db import models
from issuer.models import Issuer, Receiver
from codes.models import ActivityType

# Create your models here.
from codes.models import TaxSubtypes, TaxTypes
from django.utils import timezone


class InvoiceHeader(models.Model):
    issuer = models.ForeignKey(Issuer, on_delete=models.CASCADE ,null=True,blank=True)
    receiver = models.ForeignKey(Receiver, on_delete=models.CASCADE,null=True,blank=True)
    document_type = models.CharField(max_length=2,
                                     choices=[('i', 'invoice')], default='i',null=True,blank=True)
    document_type_version = models.CharField(max_length=8,
                                             choices=[('1.0', '1.0')], default='1.0',null=True,blank=True)

    date_time_issued = models.DateTimeField(default=timezone.now,null=True,blank=True)
    taxpayer_activity_code = models.ForeignKey(ActivityType, on_delete=models.CASCADE,null=True,blank=True)
    internal_id = models.CharField(max_length=50,null=True,blank=True)
    purchase_order_reference = models.CharField(max_length=50,null=True,blank=True)
    purchase_order_description = models.CharField(max_length=100,null=True,blank=True)
    sales_order_reference = models.CharField(max_length=50,null=True,blank=True)
    sales_order_description = models.CharField(max_length=100,null=True,blank=True)
    proforma_invoice_number = models.CharField(max_length=50,null=True,blank=True)
    total_sales_amount = models.DecimalField(decimal_places=5, max_digits=20,null=True,blank=True)
    total_discount_amount = models.DecimalField(decimal_places=5, max_digits=20,null=True,blank=True)
    net_amount = models.DecimalField(decimal_places=5, max_digits=20,null=True,blank=True)
    extra_discount_amount = models.DecimalField(decimal_places=5, max_digits=20,null=True,blank=True)
    total_items_discount_amount = models.DecimalField(decimal_places=5, max_digits=20,null=True,blank=True)
    total_amount = models.DecimalField(decimal_places=5, max_digits=20,null=True,blank=True)
    signature = models.TextField(null=True,blank=True)

    def __str__(self):
        return self.issuer + ' ' + self.receiver + ' ' + self.date_time_issued


class InvoiceLine(models.Model):
    invoice_header = models.ForeignKey(InvoiceHeader, on_delete=models.CASCADE, )
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
        return self.itemCode + ' ' + self.total


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
        return self.invoice_line.itemCode + ' ' + self.taxType
