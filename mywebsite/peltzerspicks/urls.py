
from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home, name='peltzerspicks-home'),    #Home 
    path('predictions/', views.Predictions, name='peltzerspicks-predictions'),  # Predictions page
    path('team/', views.meet_the_team, name='peltzerspicks-meet-the-team'),  # Team Page
]