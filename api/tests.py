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
