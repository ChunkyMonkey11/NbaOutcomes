from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home, name='peltzerspicks-home'),
    path('team/', views.meet_the_team, name='peltzerspicks-meet-the-team'),
]