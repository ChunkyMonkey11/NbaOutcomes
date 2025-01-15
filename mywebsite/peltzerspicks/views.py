from django.shortcuts import render
from django.http import HttpResponse
from .models import TeamMember


team = [
        {
            'name': 'Adrien Peltzer',
            'role': '   Model Developer',
            'about me': 'Hello I am Adrien...',
            'github': 'https://twitter.com/johndoe',
            'linkedin': 'https://linkedin.com/in/johndoe',
        },
        {
            'name': 'Revant Patel',
            'role': 'Developer',
            'about me': 'Hello I am Revant...',
            'github': 'https://twitter.com/janesmith',
            'linkedin': 'https://linkedin.com/in/janesmith',
        },
    ]

def Home(request):
    
    return render(request, 'peltzerspicks/home.html')

def meet_the_team(request):
    # Fetch all team members from the database
    team = TeamMember.objects.all()
    # Pass the team data to the template
    return render(request, 'peltzerspicks/meet_the_team.html', {'team': team})


    