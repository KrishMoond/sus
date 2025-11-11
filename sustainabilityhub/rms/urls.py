from django.urls import path
from . import views

app_name = 'rms'

urlpatterns = [
    path('create/', views.create_report, name='create'),
    path('my-reports/', views.my_reports, name='my_reports'),
    path('admin/', views.admin_reports, name='admin_reports'),
    path('resolve/<int:pk>/', views.resolve_report, name='resolve'),
    path('feedback/', views.submit_feedback, name='feedback'),
    path('feedbacks/', views.view_feedbacks, name='view_feedbacks'),
]