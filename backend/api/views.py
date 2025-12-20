from django.shortcuts import render
from django.http import Http404
from .models import Component, Project, ProjectComponent
from .serializers import ComponentSerializer, ProjectSerializer, ProjectComponentSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser


@api_view(['GET'])
@permission_classes([AllowAny])
def hello_world(request):
    return Response({"message": "Hello from DRF!"})

class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password required"},
                            status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"},
                            status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password)
        )
        return Response({"message": "User registered successfully", "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }},
         status=status.HTTP_201_CREATED)

class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

class MyTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
class ComponentListView(generics.ListCreateAPIView):
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    ordering_fields = ['s_no', 'name', 'legend']
    ordering = ['s_no']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({"components": serializer.data}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        component = serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

class ComponentDetailView(generics.RetrieveAPIView):
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'


class ComponentByNameView(generics.RetrieveAPIView):
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer
    permission_classes = [AllowAny]
    lookup_field = 'name'

class ProjectListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "projects": serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = serializer.save(user=request.user)
        return Response({
            "message": "Project created",
            "project": self.get_serializer(project).data
        }, status=status.HTTP_201_CREATED)

class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            return Response({
                "status": "error",
                "message": "Project not found"
            }, status=status.HTTP_404_NOT_FOUND)

        return super().handle_exception(exc)

    def retrieve(self, request, *args, **kwargs):
        project = self.get_object()
        serializer = self.get_serializer(project)

        project_components = ProjectComponent.objects.filter(
            project=project
        ).select_related("component")

        pc_serializer = ProjectComponentSerializer(project_components, many=True)
        project_data = serializer.data
        project_data["components"] = pc_serializer.data

        return Response({
            "status": "success",
            "project": project_data
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False) 
        project = self.get_object()

        serializer = self.get_serializer(
            project, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        components = request.data.get("components", [])
        for component_data in components:
            component_id = component_data.get("component_id")
            component_unique_id = component_data.get("component_unique_id")
            connections = component_data.get("connections", {})

            if not component_id or not component_unique_id:
                continue

            project_component, created = ProjectComponent.objects.update_or_create(
                project=project,
                component_id=component_id,
                defaults={
                    "component_unique_id": component_unique_id,
                    "connections": connections
                }
            )
        project.refresh_from_db()

        project_components = ProjectComponent.objects.filter(
            project=project
        ).select_related("component")

        pc_serializer = ProjectComponentSerializer(project_components, many=True)
        project_data = serializer.data
        project_data["components"] = pc_serializer.data

        return Response({
            "status": "success",
            "message": "Project updated successfully",
            "project": project_data
        }, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        project = self.get_object()  # 404 if not owned by user
        project.delete()
        return Response({
            "status": "success",
            "message": "Project deleted successfully"
        }, status=status.HTTP_200_OK)
