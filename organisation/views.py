import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from teams.models import Department, Team, Dependency
from .models import TeamType, TeamTypeAssignment

DEPT_COLORS = [
    '#116B98', '#1CB3FE', '#0a8a3a', '#9b59b6',
    '#e67e22', '#e74c3c', '#1abc9c', '#2c3e50',
]


def _dept_color_map():
    depts = list(Department.objects.all())
    return {d.id: DEPT_COLORS[i % len(DEPT_COLORS)] for i, d in enumerate(depts)}


def _type_assignment_map():
    """Return {team_id: TeamType} for all assigned teams."""
    return {
        a.team_id: a.team_type
        for a in TeamTypeAssignment.objects.select_related('team_type').all()
        if a.team_type
    }


def _team_color(team, dept_color_map, type_map):
    """Use TeamType colour if assigned, otherwise fall back to dept colour."""
    tt = type_map.get(team.id)
    if tt:
        return tt.color, tt.name
    return dept_color_map.get(team.department_id, '#1CB3FE'), None


def _build_graph(teams_qs, dept_color_map, type_map):
    team_ids = set(t.id for t in teams_qs)
    nodes, edges, seen = [], [], set()

    for team in teams_qs:
        color, type_name = _team_color(team, dept_color_map, type_map)
        nodes.append({
            'id': team.id, 'label': team.name,
            'color': {'background': color, 'border': color,
                      'highlight': {'background': '#0a5c7a', 'border': '#0a5c7a'}},
            'font': {'color': '#ffffff', 'size': 14},
            'shape': 'box', 'margin': 10,
            'department': team.department.name,
            'manager': team.manager,
            'type': type_name or team.department.name,
        })

    deps = Dependency.objects.filter(
        from_team__in=team_ids, to_team__in=team_ids
    ).select_related('from_team', 'to_team')

    for dep in deps:
        if dep.dependency_type == 'upstream':
            key = (dep.to_team_id, dep.from_team_id)
            if key not in seen:
                seen.add(key)
                edges.append({'from': dep.to_team_id, 'to': dep.from_team_id,
                               'arrows': 'to', 'color': {'color': '#888888'}})
        elif dep.dependency_type == 'downstream':
            key = (dep.from_team_id, dep.to_team_id)
            if key not in seen:
                seen.add(key)
                edges.append({'from': dep.from_team_id, 'to': dep.to_team_id,
                               'arrows': 'to', 'color': {'color': '#888888'}})
    return nodes, edges


@login_required
def organisation_view(request):
    departments = Department.objects.all()
    team_types  = TeamType.objects.all()
    dept_color_map = _dept_color_map()
    type_map       = _type_assignment_map()

    dept_legend = [(d, dept_color_map.get(d.id, '#1CB3FE')) for d in departments]
    type_legend = list(team_types)  

    dept_id    = request.GET.get('department', '')
    type_id    = request.GET.get('team_type', '')
    status_val = request.GET.get('status', '')
    search     = request.GET.get('search', '').strip()
    view_mode  = request.GET.get('view', 'network')

    teams = Team.objects.select_related('department').all()
    if dept_id:
        teams = teams.filter(department__id=dept_id)
    if status_val:
        teams = teams.filter(status=status_val)
    if type_id:
        assigned_ids = TeamTypeAssignment.objects.filter(
            team_type__id=type_id).values_list('team_id', flat=True)
        teams = teams.filter(id__in=assigned_ids)
    if search:
        teams = (
            teams.filter(name__icontains=search) |
            teams.filter(department__name__icontains=search) |
            teams.filter(manager__icontains=search)
        ).distinct()

    nodes, edges = _build_graph(teams, dept_color_map, type_map)

    teams_with_meta = []
    for team in teams:
        color, type_name = _team_color(team, dept_color_map, type_map)
        upstream_deps   = Dependency.objects.filter(from_team=team, dependency_type='upstream').select_related('to_team')
        downstream_deps = Dependency.objects.filter(from_team=team, dependency_type='downstream').select_related('to_team')
        teams_with_meta.append({
            'team':             team,
            'color':            color,
            'type_name':        type_name,
            'upstream_count':   upstream_deps.count(),
            'downstream_count': downstream_deps.count(),
            'upstream_teams':   [d.to_team for d in upstream_deps],
            'downstream_teams': [d.to_team for d in downstream_deps],
        })

    selected_dept = None
    if dept_id:
        try:
            selected_dept = Department.objects.get(id=dept_id)
            selected_dept.team_count_val = Team.objects.filter(department=selected_dept).count()
        except Department.DoesNotExist:
            pass

    context = {
        'departments':     departments,
        'team_types':      team_types,
        'dept_legend':     dept_legend,
        'type_legend':     type_legend,
        'status_choices':  Team.STATUS_CHOICES,
        'teams_with_meta': teams_with_meta,
        'nodes_json':      json.dumps(nodes),
        'edges_json':      json.dumps(edges),
        'dept_id':         dept_id,
        'type_id':         type_id,
        'status_val':      status_val,
        'search':          search,
        'view_mode':       view_mode,
        'selected_dept':   selected_dept,
    }
    return render(request, 'Organisation.html', context)


@login_required
def organisation_data_json(request):
    dept_id    = request.GET.get('department', '')
    type_id    = request.GET.get('team_type', '')
    status_val = request.GET.get('status', '')
    search     = request.GET.get('search', '').strip()
    dept_color_map = _dept_color_map()
    type_map       = _type_assignment_map()

    teams = Team.objects.select_related('department').all()
    if dept_id:
        teams = teams.filter(department__id=dept_id)
    if status_val:
        teams = teams.filter(status=status_val)
    if type_id:
        assigned_ids = TeamTypeAssignment.objects.filter(
            team_type__id=type_id).values_list('team_id', flat=True)
        teams = teams.filter(id__in=assigned_ids)
    if search:
        teams = (
            teams.filter(name__icontains=search) |
            teams.filter(department__name__icontains=search)
        ).distinct()

    nodes, edges = _build_graph(teams, dept_color_map, type_map)
    return JsonResponse({'nodes': nodes, 'edges': edges})
