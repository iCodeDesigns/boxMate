from django.urls import path

from taxManagement import views

app_name = 'tax'
urlpatterns = [
    path('upload/', views.upload_excel_sheet, name='upload-tax'),

]