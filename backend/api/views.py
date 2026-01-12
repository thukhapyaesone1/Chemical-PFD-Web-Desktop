from django.shortcuts import render
from django.http import Http404
from .models import Component, Project, CanvasState, Connection
from .serializers import ComponentSerializer, ProjectSerializer,CanvasStateSerializer, ConnectionSerializer
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
        # Don't pass user here
        project = serializer.save()
        return Response({
            "message": "Project created",
            "project": self.get_serializer(project).data
        }, status=status.HTTP_201_CREATED)

class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            return Response({
                "status": "error",
                "message": "Project not found"
            }, status=status.HTTP_404_NOT_FOUND)
        return super().handle_exception(exc)

    # -----------------------------
    # RETRIEVE
    # -----------------------------
    def retrieve(self, request, *args, **kwargs):
        project = self.get_object()

        # Project detail
        project_data = ProjectSerializer(project).data

        # Canvas items (nodes)
        canvas_items = (
            CanvasState.objects
            .filter(project=project)
            .select_related("component")
            .order_by("sequence")
        )

        items_data = CanvasStateSerializer(canvas_items, many=True).data

        # Connections (edges)
        connections = Connection.objects.filter(
            sourceItemId__project=project
        )

        connections_data = ConnectionSerializer(connections, many=True).data

        # Sequence counter (next available)
        sequence_counter = (
            canvas_items.last().sequence + 1
            if canvas_items.exists()
            else 0
        )
        response_data = project_data
        response_data["status"] = "success"
        response_data["canvas_state"] = {
                "items": items_data,
                "connections": connections_data,
                "sequence_counter": sequence_counter
            }

        return Response(response_data, status=status.HTTP_200_OK)

    # UPDATE (project only)
    def update(self, request, *args, **kwargs):
        partial =True

        project = self.get_object()

        # Update Project fields
        serializer = self.get_serializer(
            project,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Update CanvasState items
        canvas_state = request.data.get("canvas_state", {})
        items = canvas_state.get("items", [])
        connections = canvas_state.get("connections", [])

        for item in items:
            unique_id = item.get("id")
            print("Unique ID:", unique_id)
            if not unique_id:
                return Response({
                    'status': 'error',
                    'message': f'Temporary ID is required for canvas item'
                }, status=status.HTTP_400_BAD_REQUEST)
            if not item.get("component") or item["component"].get("id") is None:
                # component missing OR component.id missing
                return Response({
                    'status': 'error',
                    'message': f'Component ID is required for canvas item with temporary ID {unique_id}'
                }, status=status.HTTP_400_BAD_REQUEST)

            CanvasState.objects.update_or_create(
                id=unique_id,
                defaults={
                    "project": project,
                    "component_id": item.get("component", {}).get("id") if item.get("component") else None,
                    "label": item.get("label"),
                    "x": item.get("x"),
                    "y": item.get("y"),
                    "width": item.get("width"),
                    "height": item.get("height"),
                    "rotation": item.get("rotation", 0),
                    "scaleX": item.get("scaleX", 1),
                    "scaleY": item.get("scaleY", 1),
                    "sequence": item.get("sequence", 0)
                }
            )

        # Update Connections
        for conn in connections:
            conn_id = conn.get("id")
            source_id = conn.get("sourceItemId")
            target_id = conn.get("targetItemId")

            if not source_id or not target_id:
                continue

            Connection.objects.update_or_create(
                id=conn_id,
                defaults={
                    "sourceItemId_id": source_id,
                    "sourceGripIndex": conn.get("sourceGripIndex", 0),
                    "targetItemId_id": target_id,
                    "targetGripIndex": conn.get("targetGripIndex", 0),
                    "waypoints": conn.get("waypoints", [])
                }
            )

        # Prepare response
        project.refresh_from_db()
        canvas_items = CanvasState.objects.filter(project=project)
        canvas_items_data = CanvasStateSerializer(canvas_items, many=True).data
        connection_data = ConnectionSerializer(
            Connection.objects.filter(sourceItemId__project=project),
            many=True
        ).data

        response_data = ProjectSerializer(project).data
        response_data["status"] = "success"
        response_data["canvas_state"] = {
            "items": canvas_items_data,
            "connections": connection_data,
            "sequence_counter": canvas_items.last().sequence + 1 if canvas_items.exists() else 0
        } 
        return Response(response_data, status=status.HTTP_200_OK)



    # DELETE
    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        project.delete()

        return Response({
            "status": "success",
            "message": "Project deleted successfully"
        }, status=status.HTTP_200_OK)
