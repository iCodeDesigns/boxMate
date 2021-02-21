from django.urls import path

from codes.api import views


app_name = 'codes'

urlpatterns = [
    path('activity/create/', views.add_activity_code, name='create-act'),
    path('activity/list/', views.ActivityListView.as_view(), name='list-act'),

]