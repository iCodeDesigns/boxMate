from django.urls import path

from taxManagement import views

app_name = 'taxManagement'
urlpatterns = [
    path('upload/', views.upload_excel_sheet, name='upload-tax'),
    path('subm_list/', views.submission_list, name='submission-list'),
    path('list/uploaded-invoices' , views.get_all_invoice_headers , name='get-all-invoice-headers'),
    # path('invoice-headers/' , views.get_all_invoice_headers , name='get-all-invoice-headers')
    path('list/eta-invoice/', views.list_eta_invoice, name='list-eta-invoice'),
    path('test/', views.submit_invoice),

] 