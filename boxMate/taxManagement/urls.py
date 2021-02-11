from django.urls import path

from taxManagement import views

app_name = 'taxManagement'
urlpatterns = [
    path('upload/', views.upload_excel_sheet, name='upload-tax'),
    path('subm_list/', views.submission_list, name='submission-list'),
    path('list/uploaded-invoices' , views.get_all_invoice_headers , name='get-all-invoice-headers'),
    # path('invoice-headers/' , views.get_all_invoice_headers , name='get-all-invoice-headers')
    path('list/eta-invoice/', views.list_eta_invoice, name='list-eta-invoice'),
    path('submit-invoice/<slug:invoice_id>', views.submit_invoice , name='submit-invoice'),
    path('document-detail/<slug:doc_uuid>/', views.get_decument_detail_after_submit , name='dec-detail'),
    path('upload-excel-sheet/' , views.upload_excel_sheet, name='upload-excel-sheet')

] 