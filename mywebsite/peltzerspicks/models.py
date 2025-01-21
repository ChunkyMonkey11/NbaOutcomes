from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

"""
To do for TeamMember Database.
    Along with fields below alter database and code so that each members headshot is printed.

"""
# Creating TeamMember database
class TeamMember(models.Model):
    name = models.CharField(max_length=100)  # A column to store the team member's name (up to 100 characters)
    role = models.CharField(max_length=120)  # A column for the team member's role (e.g., 'Developer')
    image = models.ImageField(upload_to='team_members/', blank=True, null=True)  # Profile image
    github = models.URLField(blank=True, null=True)  # Optional Twitter handle as a URL
    linkedin = models.URLField(blank=True, null=True)  # Optional LinkedIn profile as a URL

    # Need to figure out what magic method does
    def __str__(self):
        return self.name


"""
IMPORTANT LOOK LATER
The Model Class Prediction is used to create a database
that stores the information for the daily NBA predictions.
The data fields for model being defined below which repersent 
collumns in database table. Each field has common types. 
"""

"""
Finish this
To recreate the working model above but to store predictions here are some instructions.
1. Uncomment code below
2. Push make migrations then --> Push Migrations
3. From there figure out a way to make code.py always run and how to make those predictions store in game.
    Get help from Adrien for above.
"""
