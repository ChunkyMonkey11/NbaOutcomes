from django.db import models

class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=120)
    github = models.URLField(max_length=200, blank=True, null=True)
    linkedin = models.URLField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='team_members/', blank=True, null=True)

    def __str__(self):
        return self.name

class Prediction(models.Model):  # ✅ Ensure this class exists
    date = models.DateField(auto_now_add=True)
    matchup = models.CharField(max_length=255)
    yahoo_total = models.FloatField()
    yahoo_spread = models.FloatField()
    predicted_total = models.FloatField()
    predicted_spread = models.FloatField()
    favored_team = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.matchup} - {self.date}"
