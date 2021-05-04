from django.urls import path

from taxManagement import views

app_name = 'taxManagement'
urlpatterns = [
    path('upload/', views.upload_excel_sheet, name='upload-tax'),
    path('list/uploaded-invoices', views.get_all_invoice_headers , name='get-all-invoice-headers'),
    path('connect/get-data', views.import_data_from_db , name='connect-oracle'),

    # path('invoice-headers/' , views.get_all_invoice_headers , name='get-all-invoice-headers')
    path('list/eta-invoice/', views.list_eta_invoice, name='list-eta-invoice'),
    path('submit-invoice/<slug:invoice_id>', views.submit_invoice , name='submit-invoice'),
    path('document-detail/<slug:internal_id>/', views.get_decument_detail_after_submit , name='dec-detail'),
    path('upload-excel-sheet/' , views.upload_excel_sheet, name='upload-excel-sheet'),
    path('resubmit-invoice/<slug:invoice_id>', views.resubmit, name='resubmit-invoice'),
    path('view-invoice/<slug:invoice_id>' , views.view_invoice , name = 'view-invoice'),
    path('create-invoice-header' , views.create_new_invoice_header , name='create-invoice-header'),
    path('create-invoice-line/<int:invoice_id>' , views.create_new_invoice_line , name='create-invoice-line'),
    path('refresh-submission-status/<slug:submission_id>' , views.refresh_submission_status , name='refresh-submission-status'),

    path('tax/change-invoice-status/<int:invoice_id>/<slug:status>', views.update_invoice_status, name="update-invoice-status"),

    path('export/invoice-template', views.export_empty_invoice_temp, name="export_excel_template"),

    path('ajax/load-addresses/', views.load_receiver_addresses, name='ajax_load_addresses'),

    path('cancel-invoice/<slug:doc_uuid>/', views.cancel_document_form, name="cancel_doc_form"),

    path('list/print-invoice/', views.list_print_invoice, name='list_print_invoice'),
    path('print-invoice/<slug:doc_uuid>', views.print_invoice, name='print_invoice'),


]
