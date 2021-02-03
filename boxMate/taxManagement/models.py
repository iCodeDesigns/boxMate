from django.db import models
from issuer.models import Issuer,Reciever
from codes.models import ActivityType 

class InvoiceHeader(models.Model):
    issuer = models.ForeignKey(Issuer , on_delete=models.CASCADE)
    reciever = models.ForeignKey(Reciever , on_delete=models.CASCADE)
    document_type = models.CharField(max_length=2 ,
                                    choices=[('i','invoice')] , default='i')
    document_type_version = models.CharField(max_length=8, 
                                        choices=[('1.0','1.0')],default='1.0')
    
    date_time_issued = models.DateTimeField(auto_now_add=True)
    taxpayer_activity_code = models.ForeignKey(ActivityType , on_delete=models.CASCADE)
    internal_id = models.CharField(max_length=50)
    purchase_order_reference = models.CharField(max_length=50)
    purchase_order_description = models.CharField(max_length=100)
    sales_order_reference = models.CharField(max_length=50)
    sales_order_description = models.CharField(max_length=100)
    proforma_invoice_number = models.CharField(max_length=50)
    total_sales_amount = models.DecimalField(decimal_places=5,max_digits=20)
    total_discount_amount = models.DecimalField(decimal_places=5,max_digits=20)
    net_amount = models.DecimalField(decimal_places=5,max_digits=20)
    extra_discount_amount = models.DecimalField(decimal_places=5,max_digits=20)
    total_items_discount_amount	= models.DecimalField(decimal_places=5,max_digits=20)
    total_amount = models.DecimalField(decimal_places=5,max_digits=20)
    signature = models.TextField()
        