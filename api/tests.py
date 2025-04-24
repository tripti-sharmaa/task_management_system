import logging
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User, Project, Task, Comment
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)

class TaskManagementSystemTests(APITestCase):

    def setUp(self):
        """Set up test data for the tests."""
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="adminpass",
            name="Admin User",
            role="Admin"
        )
        self.project_manager = User.objects.create_user(
            email="manager@example.com",
            password="managerpass",
            name="Project Manager",
            role="Project Manager"
        )
        self.developer = User.objects.create_user(
            email="developer@example.com",
            password="devpass",
            name="Developer",
            role="Developer"
        )

        self.project = Project.objects.create(
            name="Test Project",
            description="A test project",
            start_date="2025-04-01",
            end_date="2025-04-30",
            manager=self.project_manager
        )
        self.project.members.add(self.developer)

        self.task = Task.objects.create(
            title="Test Task",
            description="A test task",
            status="Pending",
            priority="Medium",
            project=self.project,
            assigned_to=self.developer
        )

        self.comment = Comment.objects.create(
            content="Test Comment",
            author=self.developer,
            task=self.task
        )

    def authenticate(self, user):
        """Authenticate a user and set the authorization header."""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_user_login_and_authentication(self):
        """Test user login and authentication status."""
        print("\n--- Testing user login and authentication ---")
        response = self.client.post('/api/auth/login/', {
            'email': 'admin@example.com',
            'password': 'adminpass'
        })
        print("Request: POST /api/auth/login/", {
            'email': 'admin@example.com',
            'password': 'adminpass'
        })
        print("Response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

        # Use the token to check authentication status
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')
        auth_response = self.client.get('/api/auth/')
        print("Request: GET /api/auth/")
        print("Response:", auth_response.status_code, auth_response.data)
        self.assertEqual(auth_response.status_code, status.HTTP_200_OK)
        self.assertEqual(auth_response.data['message'], 'Welcome Back!')

    def test_project_crud_operations(self):
        """Test CRUD operations for projects."""
        print("\n--- Testing project CRUD operations ---")
        self.authenticate(self.admin_user)

        # Create a new project
        response = self.client.post('/api/projects/', {
            'name': 'New Project',
            'description': 'A new test project',
            'start_date': '2025-05-01',
            'end_date': '2025-05-31',
            'manager': self.project_manager.id,
            'members': [self.developer.id]
        })
        print("Request: POST /api/projects/", {
            'name': 'New Project',
            'description': 'A new test project',
            'start_date': '2025-05-01',
            'end_date': '2025-05-31',
            'manager': self.project_manager.id,
            'members': [self.developer.id]
        })
        print("Response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Retrieve the project
        project_id = response.data['id']
        response = self.client.get(f'/api/projects/{project_id}/')
        print(f"Request: GET /api/projects/{project_id}/")
        print("Response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Update the project
        response = self.client.put(f'/api/projects/{project_id}/', {
            'name': 'Updated Project',
            'description': 'An updated test project',
            'start_date': '2025-05-01',
            'end_date': '2025-05-31',
            'manager': self.project_manager.id,
            'members': [self.developer.id]
        })
        print(f"Request: PUT /api/projects/{project_id}/", {
            'name': 'Updated Project',
            'description': 'An updated test project',
            'start_date': '2025-05-01',
            'end_date': '2025-05-31',
            'manager': self.project_manager.id,
            'members': [self.developer.id]
        })
        print("Response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Delete the project
        response = self.client.delete(f'/api/projects/{project_id}/')
        print(f"Request: DELETE /api/projects/{project_id}/")
        print("Response:", response.status_code)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_task_crud_operations(self):
        """Test CRUD operations for tasks."""
        print("\n--- Testing task CRUD operations ---")
        self.authenticate(self.project_manager)

        # Create a new task
        response = self.client.post('/api/tasks/', {
            'title': 'New Task',
            'description': 'A new test task',
            'status': 'Pending',
            'priority': 'High',
            'project': self.project.id,
            'assigned_to': self.developer.id
        })
        print("Request: POST /api/tasks/", {
            'title': 'New Task',
            'description': 'A new test task',
            'status': 'Pending',
            'priority': 'High',
            'project': self.project.id,
            'assigned_to': self.developer.id
        })
        print("Response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Retrieve the task
        task_id = response.data['id']
        response = self.client.get(f'/api/tasks/{task_id}/')
        print(f"Request: GET /api/tasks/{task_id}/")
        print("Response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Update the task
        response = self.client.put(f'/api/tasks/{task_id}/', {
            'title': 'Updated Task',
            'description': 'An updated test task',
            'status': 'In Progress',
            'priority': 'Medium',
            'project': self.project.id,
            'assigned_to': self.developer.id
        })
        print(f"Request: PUT /api/tasks/{task_id}/", {
            'title': 'Updated Task',
            'description': 'An updated test task',
            'status': 'In Progress',
            'priority': 'Medium',
            'project': self.project.id,
            'assigned_to': self.developer.id
        })
        print("Response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Delete the task
        response = self.client.delete(f'/api/tasks/{task_id}/')
        print(f"Request: DELETE /api/tasks/{task_id}/")
        print("Response:", response.status_code)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_comment_crud_operations(self):
        """Test CRUD operations for comments."""
        print("\n--- Testing comment CRUD operations ---")
        self.authenticate(self.developer)

        # Create a new comment
        response = self.client.post('/api/comments/', {
            'content': 'New Comment',
            'task': self.task.id
        })
        print("Request: POST /api/comments/", {
            'content': 'New Comment',
            'task': self.task.id
        })
        print("Response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Retrieve the comment
        comment_id = response.data['id']
        response = self.client.get(f'/api/comments/{comment_id}/')
        print(f"Request: GET /api/comments/{comment_id}/")
        print("Response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Update the comment
        response = self.client.put(f'/api/comments/{comment_id}/', {
            'content': 'Updated Comment',
            'task': self.task.id
        })
        print(f"Request: PUT /api/comments/{comment_id}/", {
            'content': 'Updated Comment',
            'task': self.task.id
        })
        print("Response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Delete the comment
        response = self.client.delete(f'/api/comments/{comment_id}/')
        print(f"Request: DELETE /api/comments/{comment_id}/")
        print("Response:", response.status_code)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

class RoleBasedAccessTests(APITestCase):
    """
    Test role-based access control for different user roles across all endpoints.
    """

    def setUp(self):
        """Set up test data for the tests."""
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="adminpass",
            name="Admin User",
            role="Admin"
        )
        self.project_manager = User.objects.create_user(
            email="manager@example.com",
            password="managerpass",
            name="Project Manager",
            role="Project Manager"
        )
        self.developer = User.objects.create_user(
            email="developer@example.com",
            password="devpass",
            name="Developer",
            role="Developer"
        )
        self.client_user = User.objects.create_user(
            email="client@example.com",
            password="clientpass",
            name="Client User",
            role="Client"
        )

        self.project = Project.objects.create(
            name="Test Project",
            description="A test project",
            start_date="2025-04-01",
            end_date="2025-04-30",
            manager=self.project_manager
        )
        self.project.members.add(self.developer)

        self.task = Task.objects.create(
            title="Test Task",
            description="A test task",
            status="Pending",
            priority="Medium",
            project=self.project,
            assigned_to=self.developer
        )

        self.comment = Comment.objects.create(
            content="Test Comment",
            author=self.developer,
            task=self.task
        )

    def authenticate(self, user):
        """Authenticate a user and set the authorization header."""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_admin_access(self):
        """Test that Admin has full access to all endpoints."""
        print("\n--- Testing Admin access ---")
        self.authenticate(self.admin_user)

        # Users
        response = self.client.get('/api/users/')
        print("Request: GET /api/users/")
        print("Response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Projects
        response = self.client.get('/api/projects/')
        print("Request: GET /api/projects/")
        print("Response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Tasks
        response = self.client.get('/api/tasks/')
        print("Request: GET /api/tasks/")
        print("Response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Comments
        response = self.client.get('/api/comments/')
        print("Request: GET /api/comments/")
        print("Response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_project_manager_access(self):
        """Test that Project Manager has restricted access to user management but full access to projects and tasks they manage."""
        print("\n--- Testing Project Manager access ---")
        self.authenticate(self.project_manager)

        # Users
        response = self.client.get('/api/users/')
        print("Request: GET /api/users/")
        print("Response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Projects
        response = self.client.get('/api/projects/')
        print("Request: GET /api/projects/")
        print("Response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Tasks
        response = self.client.get('/api/tasks/')
        print("Request: GET /api/tasks/")
        print("Response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Comments
        response = self.client.get('/api/comments/')
        print("Request: GET /api/comments/")
        print("Response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_developer_access(self):
        """Test that Developer has restricted access to user and project management but access to tasks and comments assigned to them."""
        print("\n--- Testing Developer access ---")
        self.authenticate(self.developer)

        # Users
        response = self.client.get('/api/users/')
        print("Request: GET /api/users/")
        print("Response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Projects
        response = self.client.get('/api/projects/')
        print("Request: GET /api/projects/")
        print("Response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Tasks
        response = self.client.get('/api/tasks/')
        print("Request: GET /api/tasks/")
        print("Response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Comments
        response = self.client.get('/api/comments/')
        print("Request: GET /api/comments/")
        print("Response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_client_access(self):
        """Test that Client has restricted access to user management but can view projects and tasks they are associated with."""
        print("\n--- Testing Client access ---")
        self.authenticate(self.client_user)

        # Users
        response = self.client.get('/api/users/')
        print("Request: GET /api/users/")
        print("Response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Projects
        response = self.client.get('/api/projects/')
        print("Request: GET /api/projects/")
        print("Response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Tasks
        response = self.client.get('/api/tasks/')
        print("Request: GET /api/tasks/")
        print("Response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Comments
        response = self.client.get('/api/comments/')
        print("Request: GET /api/comments/")
        print("Response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class TaggingTests(APITestCase):
    """
    Test tagging functionality for projects, tasks, and comments.
    """

    def setUp(self):
        """Set up test data for the tests."""
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="adminpass",
            name="Admin User",
            role="Admin"
        )
        self.project_manager = User.objects.create_user(
            email="manager@example.com",
            password="managerpass",
            name="Project Manager",
            role="Project Manager"
        )
        self.developer = User.objects.create_user(
            email="developer@example.com",
            password="devpass",
            name="Developer",
            role="Developer"
        )

        self.project = Project.objects.create(
            name="Test Project",
            description="A test project",
            start_date="2025-04-01",
            end_date="2025-04-30",
            manager=self.project_manager
        )

        self.task = Task.objects.create(
            title="Test Task",
            description="A test task",
            status="Pending",
            priority="Medium",
            project=self.project,
            assigned_to=self.developer
        )

        self.comment = Comment.objects.create(
            content="Test Comment",
            author=self.developer,
            task=self.task
        )

    def authenticate(self, user):
        """Authenticate a user and set the authorization header."""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_tag_users_to_project(self):
        """Test tagging users to a project."""
        print("\n--- Testing tagging users to a project ---")
        self.authenticate(self.admin_user)

        response = self.client.put(f'/api/projects/{self.project.id}/', {
            'name': self.project.name,
            'description': self.project.description,
            'start_date': self.project.start_date,
            'end_date': self.project.end_date,
            'manager': self.project_manager.id,
            'members': [self.developer.id]
        })
        print(f"Request: PUT /api/projects/{self.project.id}/")
        print("Response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.developer.id, response.data['members'])

    def test_tag_tasks_to_project_and_users(self):
        """Test tagging tasks to projects and users."""
        print("\n--- Testing tagging tasks to projects and users ---")
        self.authenticate(self.admin_user)

        response = self.client.post('/api/tasks/', {
            'title': 'New Task',
            'description': 'A new test task',
            'status': 'Pending',
            'priority': 'High',
            'project': self.project.id,
            'assigned_to': self.developer.id
        })
        print("Request: POST /api/tasks/")
        print("Response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['project'], self.project.id)
        self.assertEqual(response.data['assigned_to'], self.developer.id)

    def test_tag_comments_to_project_and_tasks(self):
        """Test tagging comments to projects and tasks."""
        print("\n--- Testing tagging comments to projects and tasks ---")
        self.authenticate(self.developer)

        response = self.client.post('/api/comments/', {
            'content': 'New Comment',
            'task': self.task.id
        })
        print("Request: POST /api/comments/")
        print("Response:", response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['task'], self.task.id)
        self.assertIsNone(response.data['project'])
