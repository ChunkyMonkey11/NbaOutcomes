from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home, name='peltzerspicks-home'),
    path('about/', views.about, name='peltzerspicks-about'),
]