from django.urls import path

from taxManagement.api import views

app_name = 'tax'
urlpatterns = [
    path('upload/', views.upload_excel_sheet, name='upload-tax'),
    path('invoice-headers/' , views.get_all_invoice_headers , name='get-all-invoice-headers'),
    path('subm_list/', views.submission_list, name='submission-list'),
]