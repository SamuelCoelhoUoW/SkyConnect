# teams/tests.py
# Author: Samuel Coelho (w2078214)
# Test cases for the Teams app - covering functionality
# as per Week 9 and Week 10 module materials

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Department, Team, TeamMember, Repository, Dependency


class TeamModelTestCase(TestCase):
    """Test that models are created and stored correctly in the database"""

    def setUp(self):
        """Set up test data — runs before every test method"""
        self.department = Department.objects.create(
            name='Engineering',
            description='Core engineering department'
        )
        self.team = Team.objects.create(
            name='Cloud Infrastructure',
            department=self.department,
            manager='Kevin Matsuura',
            manager_role='Cloud Manager',
            location='London, UK',
            status='active',
            email='cloud@sky.com'
        )
        self.member = TeamMember.objects.create(
            team=self.team,
            name='Emily Parker',
            role='engineer',
            job_title='Cloud Engineer',
            email='emily.parker@sky.com',
            phone='07700 900125'
        )
        self.repo = Repository.objects.create(
            team=self.team,
            name='Infrastructure as Code',
            description='Core cloud resource definitions'
        )

    def test_department_created_correctly(self):
        """Test department is saved to database with correct name"""
        self.assertEqual(self.department.name, 'Engineering')

    def test_team_created_correctly(self):
        """Test team is saved with correct name and status"""
        self.assertEqual(self.team.name, 'Cloud Infrastructure')
        self.assertEqual(self.team.status, 'active')

    def test_team_linked_to_department(self):
        """Test ForeignKey relationship between team and department"""
        self.assertEqual(self.team.department.name, 'Engineering')

    def test_member_linked_to_team(self):
        """Test ForeignKey relationship between member and team"""
        self.assertEqual(self.member.team.name, 'Cloud Infrastructure')

    def test_repository_linked_to_team(self):
        """Test ForeignKey relationship between repository and team"""
        self.assertEqual(self.repo.team.name, 'Cloud Infrastructure')

    def test_team_member_count(self):
        """Test that member count reflects database correctly"""
        self.assertEqual(self.team.members.count(), 1)

    def test_team_repository_count(self):
        """Test that repository count reflects database correctly"""
        self.assertEqual(self.team.repositories.count(), 1)


class TeamViewTestCase(TestCase):
    """Test that pages load correctly and require login"""

    def setUp(self):
        """Set up test user and test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
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

    def test_team_list_redirects_if_not_logged_in(self):
        """Test that unauthenticated users cannot access the teams page"""
        response = self.client.get(reverse('team_list'))
        self.assertEqual(response.status_code, 302)

    def test_team_list_loads_when_logged_in(self):
        """Test that the team list page loads successfully for logged in users"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('team_list'))
        self.assertEqual(response.status_code, 200)

    def test_team_list_shows_teams(self):
        """Test that teams appear in the team list page"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('team_list'))
        self.assertContains(response, 'Cloud Infrastructure')

    def test_team_detail_redirects_if_not_logged_in(self):
        """Test that unauthenticated users cannot access team detail page"""
        response = self.client.get(
            reverse('team_detail', args=[self.team.id])
        )
        self.assertEqual(response.status_code, 302)

    def test_team_detail_loads_when_logged_in(self):
        """Test that the team detail page loads successfully"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('team_detail', args=[self.team.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_team_detail_shows_team_name(self):
        """Test that team name appears on the detail page"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('team_detail', args=[self.team.id])
        )
        self.assertContains(response, 'Cloud Infrastructure')

    def test_team_detail_shows_overview_tab_by_default(self):
        """Test that overview tab is active by default"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('team_detail', args=[self.team.id])
        )
        self.assertContains(response, 'About the Team')


class TeamSearchTestCase(TestCase):
    """Test search and filter functionality"""

    def setUp(self):
        """Set up test user and multiple teams for search testing"""
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

    def test_search_returns_matching_team(self):
        """Test that searching for a team name returns the correct result"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('team_list'), {'search': 'Cloud'}
        )
        self.assertContains(response, 'Cloud Infrastructure')
        self.assertNotContains(response, 'Frontend Development')

    def test_search_with_no_results(self):
        """Test that searching for a non-existent team returns no results"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('team_list'), {'search': 'NonExistentTeam'}
        )
        self.assertNotContains(response, 'Cloud Infrastructure')
        self.assertNotContains(response, 'Frontend Development')

    def test_department_filter(self):
        """Test that department filter returns correct teams"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('team_list'),
            {'department': self.department.id}
        )
        self.assertContains(response, 'Cloud Infrastructure')

class TeamDependencyTestCase(TestCase):
    """Test upstream and downstream dependency functionality"""

    def setUp(self):
        """Set up two teams with a dependency between them"""
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

    def test_dependency_created_correctly(self):
        """Test dependency is saved to database with correct type"""
        self.assertEqual(self.dependency.dependency_type, 'upstream')

    def test_dependency_links_correct_teams(self):
        """Test dependency correctly links from_team and to_team"""
        self.assertEqual(self.dependency.from_team.name, 'Frontend Development')
        self.assertEqual(self.dependency.to_team.name, 'Cloud Infrastructure')

    def test_dependency_appears_on_detail_page(self):
        """Test dependency shows on the team detail dependencies tab"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('team_detail', args=[self.team2.id]),
            {'tab': 'dependencies'}
        )
        self.assertContains(response, 'Cloud Infrastructure')

    def test_upstream_filter_shows_correct_dependency(self):
        """Test that filtering by upstream shows the correct dependency"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('team_detail', args=[self.team2.id]),
            {'tab': 'dependencies', 'dep': 'upstream'}
        )
        self.assertContains(response, 'Cloud Infrastructure')

    def test_downstream_filter_shows_no_results(self):
        """Test that filtering by downstream returns nothing when none exist"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('team_detail', args=[self.team2.id]),
            {'tab': 'dependencies', 'dep': 'downstream'}
        )
        self.assertNotContains(response, 'Cloud Infrastructure')

class IntegrationTestCase(TestCase):
    """Test overall application integration between Teams and Messages"""

    def setUp(self):
        """Set up test user for integration testing"""
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

    def test_login_redirects_to_team_list(self):
        """Test that successful login redirects to the Teams page"""
        response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/teams/')

    def test_teams_page_accessible_after_login(self):
        """Test Teams page loads after authentication"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/teams/')
        self.assertEqual(response.status_code, 200)

    def test_navigation_from_teams_to_messages(self):
        """Test that base template contains link to messages page"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/teams/')
        self.assertContains(response, '/messages/')

    def test_admin_accessible_to_superuser(self):
        """Test that admin panel is accessible to superuser"""
        admin_user = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            email='admin@test.com'
        )
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)

    def test_signup_then_login_flow(self):
        """Test user can sign up and then log in successfully"""
        self.client.post('/signup/', {
            'email': 'newuser@test.com',
            'username': 'newuser',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        })
        response = self.client.post('/login/', {
            'username': 'newuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)