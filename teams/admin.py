# teams/admin.py
# Author: Samuel Coelho (w2078214)

from django.contrib import admin
from .models import Department, Team, TeamMember, Repository, Dependency

admin.site.register(Department)
admin.site.register(Team)
admin.site.register(TeamMember)
admin.site.register(Repository)
admin.site.register(Dependency)