from django.urls import path

from codes.api import views

app_name = 'codes'
urlpatterns = [
    path('activity-code/upload', views.activity_type_upload, name='upload-tax'),   
]