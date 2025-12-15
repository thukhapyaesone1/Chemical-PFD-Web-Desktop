from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase
from api.models import Component, Project, ProjectComponent
from django.core.files.uploadedfile import SimpleUploadedFile


class RegisterAPITest(APITestCase):
    def test_register_user(self):
        url = reverse('auth_register')
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword123'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

class RefreshTokenAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123')
    def test_refresh_token(self):
        # First, obtain a token pair
        login_url = reverse('auth_login')
        login_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        refresh_token = login_response.data['refresh']

        # Now, refresh the token
        refresh_url = reverse('token_refresh')
        refresh_data = {
            'refresh': refresh_token
        }
        refresh_response = self.client.post(refresh_url, refresh_data, format='json')

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)

class LoginAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )
    
    def test_login_user(self):
        url = reverse('auth_login')
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

class ComponentListAPITest(APITestCase):
    def setUp(self):
        Component.objects.create(
            s_no='1',
            parent='',
            name='Resistor',
            legend='R',
            suffix='R',
            object='Object',
            grips='Grips'
        )
        Component.objects.create(
            s_no='2',
            parent='',
            name='Capacitor',
            legend='C',
            suffix='C',
            object='Object',
            grips='Grips'
        )
    
    def test_list_components(self):
        url = reverse('component-list')
        response = self.client.get(url, format='json')
        print("component response.data:", response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["components"]), 2)

class ProjectAPITest(APITestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123"
        )

        # Login and get token
        login_url = reverse("auth_login")
        login_response = self.client.post(login_url, {
            "username": "testuser",
            "password": "testpassword123"
        }, format="json")

        self.access_token = login_response.data["access"]

        # Authenticate client
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )

        # Create component
        self.component = Component.objects.create(
            s_no="1",
            parent="",
            name="Resistor",
            legend="R",
            suffix="Ω",
            object="Object",
            grips="Grips"
        )

        # Create project
        self.project = Project.objects.create(
            name="Test Project",
            user=self.user
        )

    # -----------------------------
    # LIST PROJECTS
    # -----------------------------
    def test_list_projects(self):
        url = reverse("project-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["projects"]), 1)

    # -----------------------------
    # CREATE PROJECT
    # -----------------------------
    def test_create_project(self):
        url = reverse("project-list")
        data = {
            "name": "New Project"
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(response.data["project"]["name"], "New Project")

    # -----------------------------
    # RETRIEVE PROJECT (NO COMPONENTS)
    # -----------------------------
    def test_retrieve_project(self):
        url = reverse("project-detail", args=[self.project.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["project"]["name"], "Test Project")
        self.assertEqual(response.data["project"]["components"], [])

    # -----------------------------
    # UPDATE PROJECT WITH COMPONENTS
    # -----------------------------
    def test_update_project_with_components(self):
        url = reverse("project-detail", args=[self.project.id])

        data = {
            "name": "Updated Project",
            "components": [
                {
                    "component_id": self.component.id,
                    "component_unique_id": "res_1",
                    "connections": {
                        "A": "5V",
                        "B": "GND"
                    }
                }
            ]
        }

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Project updated
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, "Updated Project")

        # Component relation created
        self.assertEqual(ProjectComponent.objects.count(), 1)

        pc = ProjectComponent.objects.first()
        self.assertEqual(pc.component_unique_id, "res_1")
        self.assertEqual(pc.connections["A"], "5V")

        # Response includes flattened component data
        components = response.data["project"]["components"]
        self.assertEqual(len(components), 1)
        self.assertEqual(components[0]["name"], "Resistor")
        self.assertEqual(components[0]["component_unique_id"], "res_1")

    # -----------------------------
    # UNAUTHORIZED ACCESS BLOCKED
    # -----------------------------
    def test_project_requires_auth(self):
        self.client.credentials()  # remove auth

        url = reverse("project-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
