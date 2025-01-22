# Register your models here.
from django.contrib import admin
from .models import TeamMember
from .models import Prediction

admin.site.register(TeamMember)
admin.site.register(Prediction)