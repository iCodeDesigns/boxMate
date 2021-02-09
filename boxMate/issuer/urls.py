from django.urls import path

from issuer import views

app_name = 'issuer'

urlpatterns = [
    path('create/', views.add_issuer, name='create-issuer'),
    path('list/', views.IssuerListView.as_view(), name='list-issuers'),
    path('list/uploaded-invoices', views.list_uploaded_invoice, name='list-uploaded-invoices'),
]
