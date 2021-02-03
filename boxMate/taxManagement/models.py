from django.db import models

# Create your models here.


class MainTable(models.Model):
#Core
    document_type = models.CharField(max_length=20)
    document_type_version = models.CharField(max_length=20)
    date_time_issued = models.DateTimeField()
    taxpayer_activity_code = models.CharField(max_length=20)
    internal_id = models.CharField(max_length=20)
    purchase_order_reference = models.CharField(max_length=55)
    purchase_order_description = models.CharField(max_length=55)
    sales_order_reference = models.CharField(max_length=20)
    sales_order_description = models.CharField(max_length=20)
    proforma_invoice_number = models.CharField(max_length=50)
    total_sales_amount =  models.DecimalField(max_digits=20,  decimal_places=10)
    total_discount_amount =  models.DecimalField(max_digits=20,  decimal_places=10)
    net_amount =  models.DecimalField(max_digits=20,  decimal_places=10)
    total_amount =  models.DecimalField(max_digits=20,  decimal_places=10)
    total_items_discount_amount = models.DecimalField(max_digits=20,  decimal_places=10)
    extra_discount_amount = models.DecimalField(max_digits=20,  decimal_places=10)

  
  
    
    #Issuer
    issuer_type = models.CharField(max_length=55)
    issuer_registration_num = models.CharField(max_length=20)
    issuer_name = models.CharField(max_length=55)
    issuer_building_num = models.CharField(max_length=55)
    issuer_room = models.CharField(max_length=20)
    issuer_floor = models.CharField(max_length=29)
    issuer_street = models.CharField(max_length=55)
    issuer_land_mark = models.CharField(max_length=55)
    issuer_additional_information = models.CharField(max_length=55)
    issuer_governate = models.CharField(max_length=55)
    issuer_region_city = models.CharField(max_length=55)
    issuer_postal_code = models.CharField(max_length=20)
    issuer_country = models.CharField(max_length=20)
    issuer_branch_id = models.CharField(max_length=20)

    #Receiver
    receiver_type = models.CharField(max_length=55)
    receiver_registration_num = models.CharField(max_length=20)
    receiver_name = models.CharField(max_length=55)
    receiver_building_num = models.CharField(max_length=55)
    receiver_room = models.CharField(max_length=20)
    receiver_floor = models.CharField(max_length=5)
    receiver_street = models.CharField(max_length=55)
    receiver_land_mark = models.CharField(max_length=55)
    receiver_additional_information = models.CharField(max_length=55)
    receiver_governate = models.CharField(max_length=55)
    receiver_region_city = models.CharField(max_length=55)
    receiver_postal_code = models.CharField(max_length=20)
    receiver_country = models.CharField(max_length=20)

    #Payment
    bank_name = models.CharField(max_length=20)
    bank_address = models.CharField(max_length=20)
    bank_account_no = models.CharField(max_length=55)
    bank_account_iban = models.CharField(max_length=55)
    swift_code = models.CharField(max_length=20)
    payment_terms = models.CharField(max_length=20)
     
    #Delivery
    approach = models.CharField(max_length=20)
    packaging = models.CharField(max_length=20)
    date_validity = models.DateTimeField()
    export_port = models.CharField(max_length=55)
    country_of_origin = models.CharField(max_length=55)
    gross_weight = models.DecimalField(max_digits=7,  decimal_places=6)
    net_weight = models.DecimalField(max_digits=7,  decimal_places=6)
    delivery_terms = models.CharField(max_length=55)

    #Tax Total
    taxt_type = models.CharField(max_length=55)
    tax_amount = models.DecimalField(max_digits=20,  decimal_places=10)
    
    #Signature
    signature_type = models.CharField(max_length=55)
    signature_value = models.CharField(max_length=200)

    #Invoice Line
    description = models.CharField(max_length=55)
    item_type = models.CharField(max_length=20)
    item_code = models.CharField(max_length=55)
    unit_type = models.CharField(max_length=20)
    quantity = models.DecimalField(max_digits=20,  decimal_places=10)
    sales_total = models.DecimalField(max_digits=20,  decimal_places=10)
    internal_code = models.CharField(max_length=20)
    items_discount = models.DecimalField(max_digits=20,  decimal_places=10)
    net_total = models.DecimalField(max_digits=20,  decimal_places=10)
    total_taxable_fees= models.DecimalField(max_digits=20,  decimal_places=10)
    value_difference = models.DecimalField(max_digits=20,  decimal_places=10)
    total = models.DecimalField(max_digits=20,  decimal_places=10)
    value_difference = models.DecimalField(max_digits=20,  decimal_places=10)
        #Value
    currency_sold = models.CharField(max_length=20)
    amount_sold =  models.DecimalField(max_digits=20,  decimal_places=10)
    amount_egp = models.DecimalField(max_digits=20,  decimal_places=10)
    currency_exchange_rate = models.DecimalField(max_digits=20,  decimal_places=10)
        #Discount
    discount_rate  =  models.DecimalField(max_digits=20,  decimal_places=10)
    discount_amount = models.DecimalField(max_digits=20,  decimal_places=10)
        #Taxable Item
    taxt_item_type = models.CharField(max_length=55)
    tax_item_amount = models.DecimalField(max_digits=20,  decimal_places=10)
    tax_item_subtype = models.CharField(max_length=55)
    tax_item_rate = models.DecimalField(max_digits=20,  decimal_places=10)

    





