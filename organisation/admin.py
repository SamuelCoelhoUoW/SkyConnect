# Author: Ar-rahim Mozumdar w2063830

from django.contrib import admin
from .models import TeamType, TeamTypeAssignment


@admin.register(TeamType)
class TeamTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')


@admin.register(TeamTypeAssignment)
class TeamTypeAssignmentAdmin(admin.ModelAdmin):
    list_display  = ('team', 'team_type')
    list_filter   = ('team_type',)
    search_fields = ('team__name',)
    # Lets you assign types to many teams quickly from one screen
    list_editable = ('team_type',)
