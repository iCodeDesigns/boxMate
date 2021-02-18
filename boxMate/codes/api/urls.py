from django.urls import path

from codes.api import views

app_name = 'codes'
urlpatterns = [
    path('activity-code/upload', views.activity_type_upload, name='upload-activity-code'),
    path('tax-type/upload', views.tax_type_upload, name='upload-tax-type'),   
    path('tax-subtype/upload', views.tax_subtype_upload, name='upload-tax-subtype'),   
    path('unit-type/upload', views.unit_type_upload, name='upload-unit-type'),   
    path('country-code/upload', views.country_code_upload, name='upload-country-code'),   


]