from django.urls import path
# Remove this import since we're using custom view:
# from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('token/refresh/', views.token_refresh, name='token_refresh'),  # Use your custom view
]