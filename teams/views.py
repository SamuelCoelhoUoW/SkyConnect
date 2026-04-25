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
    active_tab = request.GET.get('tab', 'overview')

    # Members — filter by role if provided
    role_filter = request.GET.get('role', '')
    members = team.members.all()
    if role_filter:
        members = members.filter(role=role_filter)

    # Repositories — search and sort
    repo_sort = request.GET.get('repo_sort', 'updated')
    repo_search = request.GET.get('repo_search', '')
    repositories = team.repositories.all()
    if repo_search:
        repositories = repositories.filter(name__icontains=repo_search)
    if repo_sort == 'name':
        repositories = repositories.order_by('name')
    else:
        repositories = repositories.order_by('-updated_at')

    # Dependencies — filter by type if provided
    dep_filter = request.GET.get('dep', '')
    dependencies = Dependency.objects.filter(from_team=team)
    if dep_filter:
        dependencies = dependencies.filter(dependency_type=dep_filter)

    return render(request, 'teams/team_detail.html', {
        'team': team,
        'members': members,
        'repositories': repositories,
        'dependencies': dependencies,
        'active_tab': active_tab,
        'role_filter': role_filter,
        'dep_filter': dep_filter,
        'repo_sort': repo_sort,
        'repo_search': repo_search,
    })