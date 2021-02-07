from import_export.widgets import ForeignKeyWidget
from import_export import resources, fields
from .models import *


class MainTableResource(resources.ModelResource):
    class Meta:
        model = MainTable

    #issuer
    issuer_type = fields.Field(
        column_name='type', 
        attribute='issuer_type',)  
  
    issuer_registration_num = fields.Field(
         column_name='issuer_registration_num', 
         attribute='issuer_registration_num',) 

    issuer_name = fields.Field(
        column_name='name', 
        attribute='issuer_name',) 
  
    issuer_building_num = fields.Field(
        column_name='buildingNumber', 
        attribute='issuer_building_num',) 

    issuer_room = fields.Field(
        column_name='room', 
        attribute='issuer_room',) 

    issuer_floor = fields.Field(
        column_name='floor', 
        attribute='issuer_floor',) 

    issuer_street = fields.Field(
        column_name='street', 
        attribute='issuer_street',) 

    issuer_land_mark = fields.Field(
        column_name='landmark', 
        attribute='issuer_land_mark',) 

    issuer_additional_information = fields.Field(
        column_name='additionalInformation', 
        attribute='issuer_additional_information',) 

    issuer_governate = fields.Field(
        column_name='governate', 
        attribute='issuer_governate',) 

    issuer_region_city = fields.Field(
        column_name='regionCity', 
        attribute='issuer_region_city',) 

    issuer_postal_code = fields.Field(
        column_name='postalCode', 
        attribute='issuer_postal_code',) 

    issuer_country = fields.Field(
        column_name='country', 
        attribute='issuer_country',) 

    issuer_branch_id = fields.Field(
        column_name='branchID', 
        attribute='issuer_branch_id',) 

    #receiver
    receiver_type = fields.Field(
        column_name='type2', 
        attribute='receiver_type',)  
  
    receiver_registration_num = fields.Field(
        column_name='id3', 
        attribute='receiver_registration_num',) 

    receiver_name = fields.Field(
        column_name='name4', 
        attribute='receiver_name',) 
  
    receiver_building_num = fields.Field(
        column_name='buildingNumber5', 
        attribute='receiver_building_num',) 

    receiver_room = fields.Field(
        column_name='room6', 
        attribute='receiver_room',) 

    receiver_floor = fields.Field(
        column_name='floor7', 
        attribute='receiver_floor',) 

    receiver_street = fields.Field(
        column_name='street8', 
        attribute='receiver_street',) 

    receiver_land_mark = fields.Field(
        column_name='landmark9', 
        attribute='receiver_land_mark',) 

    receiver_additional_information = fields.Field(
        column_name='additionalInformation10', 
        attribute='receiver_additional_information',) 

    receiver_governate = fields.Field(
        column_name='governate11', 
        attribute='receiver_governate',) 

    receiver_region_city = fields.Field(
        column_name='regionCity12', 
        attribute='receiver_region_city',) 

    receiver_postal_code = fields.Field(
        column_name='postalCode13', 
        attribute='receiver_postal_code',) 

    receiver_country = fields.Field(
        column_name='country14', 
        attribute='receiver_country',) 

    #core
    document_type = fields.Field(
        column_name='documentType', 
        attribute='document_type',)  
  
    document_type_version = fields.Field(
        column_name='documentTypeVersion', 
        attribute='document_type_version',) 

    date_time_issued = fields.Field(
        column_name='dateTimeIssued', 
        attribute='date_time_issued',) 
  
    taxpayer_activity_code = fields.Field(
        column_name='taxpayerActivityCode', 
        attribute='taxpayer_activity_code',) 

    purchase_order_reference = fields.Field(
        column_name='purchaseOrderReference', 
        attribute='purchase_order_reference',) 

    purchase_order_description = fields.Field(
        column_name='purchaseOrderDescription', 
        attribute='purchase_order_description',) 

    sales_order_description = fields.Field(
        column_name='salesOrderDescription', 
        attribute='sales_order_description',) 

    sales_order_reference = fields.Field(
        column_name='salesOrderReference', 
        attribute='sales_order_reference',) 

    proforma_invoice_number = fields.Field(
        column_name='proformaInvoiceNumber', 
        attribute='proforma_invoice_number',) 

    total_sales_amount = fields.Field(
        column_name='totalSalesAmount', 
        attribute='total_sales_amount',) 

    total_discount_amount = fields.Field(
        column_name='totalDiscountAmount', 
        attribute='total_discount_amount',) 

    net_amount = fields.Field(
        column_name='netAmount', 
        attribute='net_amount',) 

    sales_order_description = fields.Field(
        column_name='salesOrderDescription', 
        attribute='sales_order_description',) 

    sales_order_reference = fields.Field(
        column_name='salesOrderReference', 
        attribute='sales_order_reference',) 

    proforma_invoice_number = fields.Field(
        column_name='proformaInvoiceNumber', 
        attribute='proforma_invoice_number',) 

    total_amount = fields.Field(
        column_name='totalAmount', 
        attribute='total_amount',) 

    total_items_discount_amount = fields.Field(
        column_name='totalItemsDiscountAmount', 
        attribute='total_items_discount_amount',) 

    extra_discount_amount = fields.Field(
        column_name='extraDiscountAmount', 
        attribute='extra_discount_amount',) 

    internal_id = fields.Field(
        column_name='internalID', 
        attribute='internal_id',) 

    #Payment
    bank_name = fields.Field(
        column_name='bankName', 
        attribute='bank_name',) 

    bank_address = fields.Field(
        column_name='bankAddress', 
        attribute='bank_address',) 

    bank_account_no = fields.Field(
        column_name='bankAccountNo', 
        attribute='bank_account_no',) 

    bank_account_iban = fields.Field(
        column_name='bankAccountIBAN', 
        attribute='bank_account_iban',) 

    swift_code = fields.Field(
        column_name='swiftCode', 
        attribute='swift_code',)  
  
    payment_terms = fields.Field(
        column_name='terms', 
        attribute='payment_terms',) 

    #Delivery
    approach = fields.Field(
        column_name='approach', 
        attribute='approach',) 
  
    packaging = fields.Field(
        column_name='packaging', 
        attribute='packaging',) 

    date_validity = fields.Field(
        column_name='dateValidity', 
        attribute='date_validity',) 

    export_port = fields.Field(
        column_name='exportPort', 
        attribute='export_port',) 

    country_of_origin = fields.Field(
        column_name='countryOfOrigin', 
        attribute='country_of_origin',) 

    gross_weight = fields.Field(
        column_name='grossWeight', 
        attribute='gross_weight',) 

    delivery_terms = fields.Field(
        column_name='terms15', 
        attribute='delivery_terms',) 

    net_weight = fields.Field(
        column_name='netWeight', 
        attribute='net_weight',) 

    #Signature
    signature_type = fields.Field(
        column_name='signatureType', 
        attribute='signature_type',) 

    signature_value = fields.Field(
        column_name='value', 
        attribute='signature_value',) 
  
    #Tax Total
    taxt_type = fields.Field(
        column_name='taxType18', 
        attribute='taxt_type',) 

    tax_amount = fields.Field(
        column_name='amount19', 
        attribute='tax_amount',) 

    #Invoice Line
    description = fields.Field(
        column_name='description', 
        attribute='description',)  
  

    item_type = fields.Field(
        column_name='itemType', 
        attribute='item_type',) 


    item_code = fields.Field(
        column_name='itemCode', 
        attribute='item_code',) 
  


    unit_type = fields.Field(
        column_name='unitType', 
        attribute='unit_type',) 


    quantity = fields.Field(
        column_name='quantity', 
        attribute='quantity',) 

    sales_total = fields.Field(
        column_name='salesTotal', 
        attribute='sales_total',) 
    

    internal_code = fields.Field(
        column_name='internalCode', 
        attribute='internal_code',) 
     
    
    items_discount = fields.Field(
        column_name='itemsDiscount', 
        attribute='items_discount',) 
       


    net_total = fields.Field(
        column_name='netTotal', 
        attribute='net_total',) 
       
    total_taxable_fees = fields.Field(
        column_name='totalTaxableFees', 
        attribute='total_taxable_fees',) 
       
    value_difference = fields.Field(
        column_name='valueDifference', 
        attribute='value_difference',) 
       
    total = fields.Field(
        column_name='total', 
        attribute='total',) 

        #Value
    currency_sold = fields.Field(
        column_name='currencySold', 
        attribute='currency_sold',) 

    amount_sold = fields.Field(
        column_name='amountSold', 
        attribute='amount_sold',) 

    amount_egp = fields.Field(
        column_name='amountEGP', 
        attribute='amount_egp',) 

    
    currency_exchange_rate = fields.Field(
        column_name='currencyExchangeRate', 
        attribute='currency_exchange_rate',) 

     #Discount  
    discount_rate = fields.Field(
        column_name='dISCOUNTrate', 
        attribute='discount_rate',) 

    discount_amount = fields.Field(
        column_name='DISCOUNT amount', 
        attribute='discount_amount',) 

     #Taxable Item

    taxt_item_type = fields.Field(
        column_name='taxType', 
        attribute='taxt_item_type',) 

    tax_item_amount = fields.Field(
        column_name='amount16', 
        attribute='tax_item_amount',) 


    tax_item_subtype = fields.Field(
        column_name='subType', 
        attribute='tax_item_subtype',)  
  

    tax_item_rate = fields.Field(
        column_name='rate17', 
        attribute='tax_item_rate',) 



