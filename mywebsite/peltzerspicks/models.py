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
    yahoo_total = models.FloatField(null=True, blank=True)
    yahoo_spread = models.FloatField(null=True, blank=True)
    predicted_total = models.FloatField(null=True, blank=True)
    predicted_spread = models.FloatField()
    

    def __str__(self):
        return f"{self.matchup} - {self.date}"
