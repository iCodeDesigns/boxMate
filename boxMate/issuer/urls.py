from django.urls import path

from issuer import views

app_name = 'issuer'

urlpatterns = [
    path('list/uploaded-invoices', views.list_uploaded_invoice, name='list-uploaded-invoices'),
    path('create/issuer', views.create_issuer, name='create-issuer'),
    path('create/tax/<int:issuer_id>', views.create_issuer_tax_view, name='create-tax'),
    path('create/issuer/tax', views.create_issuer_tax, name='create-issuer-tax'), #ajax
    path('issuer/<int:issuer_id>', views.view_issuer, name='view-issuer'),
    path('issuerDB/create' , views.issuer_oracle_DB_create , name='create-issuer-db-connection'),
    path('issuerDB/list' , views.issuer_oracle_DB_list , name = 'list-issuer-db-connection'),
    path('issuerDB/update/<int:id>' , views.issuer_oracle_DB_update , name = 'update-issuer-db-connection'),


]
    
