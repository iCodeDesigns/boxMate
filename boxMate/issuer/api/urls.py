from django.urls import path

from issuer.api import views

urlpatterns = [
    path('create/', views.add_issuer, name='create-issuer'),
    path('list/', views.IssuerListView.as_view(), name='list-issuers'),
]
