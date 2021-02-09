from django.urls import path

from taxManagement import views

app_name = 'tax'
urlpatterns = [
    path('upload/', views.upload_excel_sheet, name='upload-tax'),
    path('subm_list/', views.submission_list, name='submission-list'),
    path('invoice-headers/' , views.get_all_invoice_headers , name='get-all-invoice-headers')

]