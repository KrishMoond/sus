from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('admin-users/', views.admin_users, name='admin_users'),
    path('create-user/', views.create_user, name='create_user'),
    path('delete-user/<int:pk>/', views.delete_user, name='delete_user'),
    path('warn-user/<int:pk>/', views.warn_user, name='warn_user'),
    path('user-warnings/<int:pk>/', views.user_warnings, name='user_warnings'),
    path('toggle-user/<int:pk>/', views.toggle_user_status, name='toggle_user_status'),
    path('user-detail/<int:pk>/', views.user_detail, name='user_detail'),
    path('my-warnings/', views.my_warnings, name='my_warnings'),
]