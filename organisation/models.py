# Author: Ar-rahim Mozumdar w2063830

from django.db import models
from teams.models import Team


class TeamType(models.Model):
    name  = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#1CB3FE',
                             help_text='Hex colour e.g. #1CB3FE')

    def __str__(self):
        return self.name


class TeamTypeAssignment(models.Model):
    team      = models.OneToOneField(Team, on_delete=models.CASCADE,
                                     related_name='type_assignment')
    team_type = models.ForeignKey(TeamType, on_delete=models.SET_NULL,
                                  null=True, blank=True,
                                  related_name='assignments')

    def __str__(self):
        return f"{self.team.name} → {self.team_type}"

    class Meta:
        verbose_name        = 'Team type assignment'
        verbose_name_plural = 'Team type assignments'
