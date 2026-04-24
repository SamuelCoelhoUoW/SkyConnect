# teams/views.py
# Author: Samuel Coelho (w2078214)
# Individual element - Team views for Sky Connect

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Team, Department, Dependency


@login_required
def team_list(request):
    """Display all teams with search and filter functionality"""
    teams = Team.objects.all()
    departments = Department.objects.all()

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        teams = teams.filter(
            Q(name__icontains=search_query) |
            Q(manager__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Department filter
    department_filter = request.GET.get('department', '')
    if department_filter:
        teams = teams.filter(department__id=department_filter)

    # Sort
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'name':
        teams = teams.order_by('name')
    elif sort_by == 'department':
        teams = teams.order_by('department__name')

    return render(request, 'teams/team_list.html', {
        'teams': teams,
        'departments': departments,
        'search_query': search_query,
        'department_filter': department_filter,
        'sort_by': sort_by,
    })


@login_required
def team_detail(request, team_id):
    """Display a single team's full profile with tabs"""
    team = get_object_or_404(Team, id=team_id)
    members = team.members.all()
    repositories = team.repositories.all()
    dependencies = Dependency.objects.filter(from_team=team)

    # Tab selection
    active_tab = request.GET.get('tab', 'overview')

    return render(request, 'teams/team_detail.html', {
        'team': team,
        'members': members,
        'repositories': repositories,
        'dependencies': dependencies,
        'active_tab': active_tab,
    })