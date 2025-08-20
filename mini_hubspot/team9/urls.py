from django.urls import path
from . import views  # import your views

urlpatterns = [
    path('', views.home, name='home'),  # '' route handled by home view
]
