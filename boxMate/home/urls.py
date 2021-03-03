from django.urls import path
from home import views

app_name = 'home'

urlpatterns = [
    path('', views.home_page, name='homepage'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='user-login'),
    path('logout/', views.user_logout, name='logout'),

]


