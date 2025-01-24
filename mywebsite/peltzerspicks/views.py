from django.shortcuts import render
from django.http import HttpResponse
from .models import TeamMember
from .models import Prediction

def Home(request):
    """
    View function for rendering the home page.

    This function takes an HTTP request and returns an HTTP response 
    that renders the 'home.html' template from the 'peltzerspicks/templates' directory.
    """

    return render(request, 'peltzerspicks/home.html')


def Predictions(request):
    """
    View function for rendering the predictions page.

    This function takes an HTTP request and returns an HTTP response 
    that renders the 'predictions.html' template from the 'peltzerspicks/templates' directory.
    """
    predictions = Prediction.objects.all() 
    
    return render(request, 'peltzerspicks/predictions.html', {'predictions': predictions})  # ✅ Pass as a dict


def meet_the_team(request):
    """
    View function for rendering the team page.

    This function takes an HTTP request and returns an HTTP response 
    that renders the 'meet_the_team.html' template from the 'peltzerspicks/templates' directory.
    """
    # Fetch all team members from the TeamMember Model
    team = TeamMember.objects.all()

    # Pass the team data to the teampage template.
    return render(request, 'peltzerspicks/meet_the_team.html', {'team': team})



    