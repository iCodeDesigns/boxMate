from django.urls import path

from issuer import views

app_name = 'issuer'

urlpatterns = [
    path('list/uploaded-invoices', views.list_uploaded_invoice, name='list-uploaded-invoices'),
]
    
