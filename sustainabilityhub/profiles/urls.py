from django.urls import path
from .views import ProfileDetailView, ProfileEditView


app_name = 'profiles'
urlpatterns = [
path('me/edit/', ProfileEditView.as_view(), name='edit'),
path('<str:username>/', ProfileDetailView.as_view(), name='detail'),
]