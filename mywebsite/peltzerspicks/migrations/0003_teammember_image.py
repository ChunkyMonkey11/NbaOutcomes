# Generated by Django 5.1.4 on 2025-01-16 23:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("peltzerspicks", "0002_teammember_delete_prediction"),
    ]

    operations = [
        migrations.AddField(
            model_name="teammember",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="team_members/"),
        ),
    ]
