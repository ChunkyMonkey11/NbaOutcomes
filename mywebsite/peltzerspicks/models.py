from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class TeamMember(models.Model):
    name = models.CharField(max_length=100)  # A column to store the team member's name (up to 100 characters)
    role = models.CharField(max_length=120)  # A column for the team member's role (e.g., 'Developer')
    github = models.URLField(blank=True, null=True)  # Optional Twitter handle as a URL
    linkedin = models.URLField(blank=True, null=True)  # Optional LinkedIn profile as a URL

    def __str__(self):
        return self.name









"""
IMPORTANT LOOK LATER
The Model Class Prediction is used to create a database
that stores the information for the daily NBA predictions.
The data fields for model being defined below which repersent 
collumns in database table. Each field has common types. 
"""
# class Prediction(models.Model):
#     date = models.DateField()
#     matchup = models.CharField(max_length=255)
#     yahoo_total = models.FloatField()
#     yahoo_spread = models.FloatField()
#     predicted_total = models.FloatField()
#     predicted_spread = models.FloatField()
#     favored_team = models.CharField(max_length=100)

#     def __str__(self):
#         return f"{self.matchup} - {self.date}"
