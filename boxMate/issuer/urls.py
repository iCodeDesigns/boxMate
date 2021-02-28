from django.urls import path

from issuer import views

app_name = 'issuer'

urlpatterns = [
    path('list/uploaded-invoices', views.list_uploaded_invoice, name='list-uploaded-invoices'),
    path('create/issuer', views.create_issuer, name='create-issuer'),
    path('create/tax/<int:issuer_id>', views.create_issuer_view, name='create-tax'),
    path('create/issuer/tax', views.create_issuer_tax, name='create-issuer-tax'),
]
    
