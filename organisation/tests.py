# Author: Ar-rahim Mozumdar w2063830
# Test cases for the Organisation app


from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from teams.models import Department, Team, Dependency
from .models import TeamType, TeamTypeAssignment


class TeamTypeModelTestCase(TestCase):
    """Test that TeamType and TeamTypeAssignment models work correctly"""

    def setUp(self):
        """Set up test data — runs before every test method"""
        self.team_type = TeamType.objects.create(
            name='Backend',
            color='#116B98'
        )
        self.department = Department.objects.create(
            name='Engineering'
        )
        self.team = Team.objects.create(
            name='Cloud Infrastructure',
            department=self.department,
            manager='Kevin Matsuura',
            status='active'
        )
        self.assignment = TeamTypeAssignment.objects.create(
            team=self.team,
            team_type=self.team_type
        )

    def test_team_type_created_correctly(self):
        """Test TeamType is saved with correct name and colour"""
        self.assertEqual(self.team_type.name, 'Backend')
        self.assertEqual(self.team_type.color, '#116B98')

    def test_team_type_str(self):
        """Test TeamType __str__ returns its name"""
        self.assertEqual(str(self.team_type), 'Backend')

    def test_team_type_assignment_created(self):
        """Test TeamTypeAssignment links a team to a type correctly"""
        self.assertEqual(self.assignment.team.name, 'Cloud Infrastructure')
        self.assertEqual(self.assignment.team_type.name, 'Backend')

    def test_team_type_assignment_str(self):
        """Test TeamTypeAssignment __str__ returns readable string"""
        self.assertIn('Cloud Infrastructure', str(self.assignment))
        self.assertIn('Backend', str(self.assignment))

    def test_one_assignment_per_team(self):
        """Test that a team can only have one TeamTypeAssignment (OneToOne)"""
        from django.db import IntegrityError
        with self.assertRaises(Exception):
            TeamTypeAssignment.objects.create(
                team=self.team,
                team_type=self.team_type
            )

    def test_assignment_accessible_from_team(self):
        """Test reverse relation — team.type_assignment gives correct type"""
        self.assertEqual(self.team.type_assignment.team_type.name, 'Backend')

    def test_deleting_team_deletes_assignment(self):
        """Test CASCADE — deleting a team removes its assignment"""
        self.team.delete()
        self.assertEqual(TeamTypeAssignment.objects.count(), 0)

    def test_deleting_type_nullifies_assignment(self):
        """Test SET_NULL — deleting a TeamType sets assignment.team_type to None"""
        self.team_type.delete()
        self.assignment.refresh_from_db()
        self.assertIsNone(self.assignment.team_type)


class OrganisationViewTestCase(TestCase):
    """Test that the organisation page loads correctly and requires login"""

    def setUp(self):
        """Set up test user and basic data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.department = Department.objects.create(name='Engineering')
        self.team = Team.objects.create(
            name='Cloud Infrastructure',
            department=self.department,
            manager='Kevin Matsuura',
            status='active'
        )

    def test_organisation_redirects_if_not_logged_in(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(reverse('organisation'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response['Location'])

    def test_organisation_loads_when_logged_in(self):
        """Test that organisation page returns 200 for authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('organisation'))
        self.assertEqual(response.status_code, 200)

    def test_organisation_shows_team_in_context(self):
        """Test that the teams_with_meta context contains our test team"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('organisation'))
        teams = [item['team'] for item in response.context['teams_with_meta']]
        self.assertIn(self.team, teams)

    def test_organisation_contains_department_in_context(self):
        """Test that departments are passed to the template context"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('organisation'))
        self.assertIn(self.department, response.context['departments'])

    def test_organisation_default_view_is_network(self):
        """Test that the default view mode is network"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('organisation'))
        self.assertEqual(response.context['view_mode'], 'network')

    def test_nodes_json_in_context(self):
        """Test that nodes_json is populated and is valid JSON"""
        import json
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('organisation'))
        nodes = json.loads(response.context['nodes_json'])
        self.assertIsInstance(nodes, list)
        self.assertGreater(len(nodes), 0)

    def test_node_contains_correct_team_name(self):
        """Test that the graph node label matches the team name"""
        import json
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('organisation'))
        nodes = json.loads(response.context['nodes_json'])
        labels = [n['label'] for n in nodes]
        self.assertIn('Cloud Infrastructure', labels)

    def test_grid_view_mode(self):
        """Test switching to grid view via query parameter"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('organisation'), {'view': 'grid'})
        self.assertEqual(response.context['view_mode'], 'grid')


class OrganisationFilterTestCase(TestCase):
    """Test filtering and search functionality"""

    def setUp(self):
        """Set up two departments, two teams, and a team type"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.dept1 = Department.objects.create(name='Engineering')
        self.dept2 = Department.objects.create(name='Product')

        self.team1 = Team.objects.create(
            name='Cloud Infrastructure',
            department=self.dept1,
            manager='Kevin Matsuura',
            status='active'
        )
        self.team2 = Team.objects.create(
            name='Design Systems',
            department=self.dept2,
            manager='Priya Nair',
            status='active'
        )
        self.team3 = Team.objects.create(
            name='Platform Reliability',
            department=self.dept1,
            manager='Sarah Ross',
            status='inactive'
        )
        self.team_type = TeamType.objects.create(name='Backend', color='#116B98')
        TeamTypeAssignment.objects.create(team=self.team1, team_type=self.team_type)

    def _get_team_names(self, response):
        return [item['team'].name for item in response.context['teams_with_meta']]

    def test_filter_by_department(self):
        """Test that department filter returns only teams in that department"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('organisation'), {'department': self.dept1.id})
        names = self._get_team_names(response)
        self.assertIn('Cloud Infrastructure', names)
        self.assertIn('Platform Reliability', names)
        self.assertNotIn('Design Systems', names)

    def test_filter_by_status_active(self):
        """Test that status filter returns only active teams"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('organisation'), {'status': 'active'})
        names = self._get_team_names(response)
        self.assertIn('Cloud Infrastructure', names)
        self.assertNotIn('Platform Reliability', names)

    def test_filter_by_team_type(self):
        """Test that team type filter returns only assigned teams"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('organisation'), {'team_type': self.team_type.id})
        names = self._get_team_names(response)
        self.assertIn('Cloud Infrastructure', names)
        self.assertNotIn('Design Systems', names)
        self.assertNotIn('Platform Reliability', names)

    def test_search_by_team_name(self):
        """Test that searching by team name returns correct result"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('organisation'), {'search': 'Cloud'})
        names = self._get_team_names(response)
        self.assertIn('Cloud Infrastructure', names)
        self.assertNotIn('Design Systems', names)

    def test_search_by_manager_name(self):
        """Test that searching by manager name returns their teams"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('organisation'), {'search': 'Priya'})
        names = self._get_team_names(response)
        self.assertIn('Design Systems', names)
        self.assertNotIn('Cloud Infrastructure', names)

    def test_search_by_department_name(self):
        """Test that searching by department name returns all teams in it"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('organisation'), {'search': 'Product'})
        names = self._get_team_names(response)
        self.assertIn('Design Systems', names)

    def test_search_no_results(self):
        """Test that searching for non-existent term returns empty list"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('organisation'), {'search': 'ZZZnonexistent'})
        names = self._get_team_names(response)
        self.assertEqual(len(names), 0)

    def test_combined_department_and_status_filter(self):
        """Test that combining department and status filters both apply"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('organisation'), {
            'department': self.dept1.id, 'status': 'active'
        })
        names = self._get_team_names(response)
        self.assertIn('Cloud Infrastructure', names)
        self.assertNotIn('Platform Reliability', names)
        self.assertNotIn('Design Systems', names)

    def test_selected_dept_in_context_when_filtered(self):
        """Test that selected_dept is set in context when department is filtered"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('organisation'), {'department': self.dept1.id})
        self.assertIsNotNone(response.context['selected_dept'])
        self.assertEqual(response.context['selected_dept'].name, 'Engineering')

    def test_selected_dept_none_when_no_filter(self):
        """Test that selected_dept is None when no department is selected"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('organisation'))
        self.assertIsNone(response.context['selected_dept'])


class OrganisationDependencyTestCase(TestCase):
    """Test that dependencies between teams are shown correctly on the map"""

    def setUp(self):
        """Set up two teams with an upstream dependency"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.department = Department.objects.create(name='Engineering')
        self.team1 = Team.objects.create(
            name='Cloud Infrastructure',
            department=self.department,
            manager='Kevin Matsuura',
            status='active'
        )
        self.team2 = Team.objects.create(
            name='Frontend Development',
            department=self.department,
            manager='Alex Santos',
            status='active'
        )
        self.dependency = Dependency.objects.create(
            from_team=self.team2,
            to_team=self.team1,
            dependency_type='upstream',
            description='Frontend depends on cloud infrastructure'
        )

    def test_edges_json_contains_dependency(self):
        """Test that the edges_json context includes the dependency arrow"""
        import json
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('organisation'))
        edges = json.loads(response.context['edges_json'])
        self.assertGreater(len(edges), 0)

    def test_upstream_count_on_team_meta(self):
        """Test that upstream_count is correct for the dependent team"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('organisation'))
        meta = {item['team'].name: item for item in response.context['teams_with_meta']}
        self.assertEqual(meta['Frontend Development']['upstream_count'], 1)

    def test_downstream_count_on_source_team(self):
        """Test that downstream_count is correct for the depended-on team"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('organisation'))
        meta = {item['team'].name: item for item in response.context['teams_with_meta']}
        self.assertEqual(meta['Cloud Infrastructure']['downstream_count'], 0)

    def test_upstream_teams_list_correct(self):
        """Test that upstream_teams contains the correct team object"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('organisation'))
        meta = {item['team'].name: item for item in response.context['teams_with_meta']}
        upstream_names = [t.name for t in meta['Frontend Development']['upstream_teams']]
        self.assertIn('Cloud Infrastructure', upstream_names)


class OrganisationDataJsonTestCase(TestCase):
    """Test the AJAX data endpoint used by the map refresh button"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.department = Department.objects.create(name='Engineering')
        self.team = Team.objects.create(
            name='Cloud Infrastructure',
            department=self.department,
            manager='Kevin Matsuura',
            status='active'
        )

    def test_data_endpoint_redirects_if_not_logged_in(self):
        """Test that AJAX endpoint also requires authentication"""
        response = self.client.get(reverse('organisation_data'))
        self.assertEqual(response.status_code, 302)

    def test_data_endpoint_returns_json(self):
        """Test that /organisation/data/ returns valid JSON"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('organisation_data'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_data_endpoint_contains_nodes_and_edges(self):
        """Test that the JSON response contains nodes and edges keys"""
        import json
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('organisation_data'))
        data = json.loads(response.content)
        self.assertIn('nodes', data)
        self.assertIn('edges', data)

    def test_data_endpoint_node_has_required_fields(self):
        """Test that each node has id, label, department, and manager"""
        import json
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('organisation_data'))
        data = json.loads(response.content)
        node = data['nodes'][0]
        for field in ['id', 'label', 'department', 'manager']:
            self.assertIn(field, node)

    def test_data_endpoint_filter_by_department(self):
        """Test that the data endpoint respects the department filter"""
        import json
        dept2 = Department.objects.create(name='Product')
        Team.objects.create(
            name='Design Systems', department=dept2,
            manager='Priya Nair', status='active'
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('organisation_data'), {'department': self.department.id}
        )
        data = json.loads(response.content)
        labels = [n['label'] for n in data['nodes']]
        self.assertIn('Cloud Infrastructure', labels)
        self.assertNotIn('Design Systems', labels)


class OrganisationIntegrationTestCase(TestCase):
    """Integration tests — organisation module working with the rest of the app"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.department = Department.objects.create(name='Engineering')
        self.team = Team.objects.create(
            name='Cloud Infrastructure',
            department=self.department,
            manager='Kevin Matsuura',
            status='active'
        )

    def test_organisation_accessible_after_login(self):
        """Test organisation page accessible after standard login flow"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/organisation/')
        self.assertEqual(response.status_code, 200)

    def test_teams_created_in_teams_app_appear_in_org_map(self):
        """Test teams created via the teams app show on the organisation map"""
        import json
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('organisation'))
        nodes = json.loads(response.context['nodes_json'])
        labels = [n['label'] for n in nodes]
        self.assertIn('Cloud Infrastructure', labels)

    def test_organisation_link_in_navigation(self):
        """Test that the base template contains a link to the organisation page"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/organisation/')
        self.assertContains(response, '/organisation/')

    def test_team_type_colour_used_in_node(self):
        """Test that assigning a TeamType changes the node colour in graph data"""
        import json
        team_type = TeamType.objects.create(name='Backend', color='#FF0000')
        TeamTypeAssignment.objects.create(team=self.team, team_type=team_type)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('organisation'))
        nodes = json.loads(response.context['nodes_json'])
        node = next(n for n in nodes if n['label'] == 'Cloud Infrastructure')
        self.assertEqual(node['color']['background'], '#FF0000')

class OrganisationDependencyFilterTestCase(TestCase):
    """Test the Dependencies filter dropdown (Has Upstream / Has Downstream)."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.department = Department.objects.create(name='Engineering')

        # team_a has no dependencies at all
        self.team_a = Team.objects.create(
            name='Team A — No Deps',
            department=self.department,
            manager='Alice', status='active'
        )
        # team_b depends on team_c (team_b has upstream, team_c has downstream)
        self.team_b = Team.objects.create(
            name='Team B — Has Upstream',
            department=self.department,
            manager='Bob', status='active'
        )
        self.team_c = Team.objects.create(
            name='Team C — Has Downstream',
            department=self.department,
            manager='Carol', status='active'
        )
        Dependency.objects.create(
            from_team=self.team_b,
            to_team=self.team_c,
            dependency_type='upstream'
        )

    def _get_team_names(self, response):
        return [item['team'].name for item in response.context['teams_with_meta']]

    def test_upstream_filter_excludes_teams_without_upstream(self):
        """
        dep_filter=upstream, filtering by 'Has Upstream' should return only Team B
        and exclude Team A (no deps) and Team C (only downstream).
        """
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('organisation'), {'dep_filter': 'upstream'}
        )
        names = self._get_team_names(response)
        # Team A has no dependencies — should NOT appear
        self.assertNotIn('Team A — No Deps', names)
        # Team B has upstream — SHOULD appear
        self.assertIn('Team B — Has Upstream', names)

    def test_downstream_filter_excludes_teams_without_downstream(self):
        """
        dep_filter=downstream, filtering by 'Has Downstream' should return only Team C
        and exclude Team A (no deps) and Team B (only upstream).
        """
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('organisation'), {'dep_filter': 'downstream'}
        )
        names = self._get_team_names(response)
        # Team A has no dependencies — should NOT appear
        self.assertNotIn('Team A — No Deps', names)
        # Team C has downstream — SHOULD appear
        self.assertIn('Team C — Has Downstream', names)

    def test_upstream_filter_excludes_downstream_only_teams(self):
        """
        dep_filter=upstream, filtering by 'Has Upstream' should exclude Team C.
        Team C only has downstream (other teams depend on it), not upstream.
        It should be excluded when filtering by 'Has Upstream'.
        """
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('organisation'), {'dep_filter': 'upstream'}
        )
        names = self._get_team_names(response)
        self.assertNotIn('Team C — Has Downstream', names)
