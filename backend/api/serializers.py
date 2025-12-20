from rest_framework import serializers
from .models import Component, Project, ProjectComponent
import json



class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
class ComponentSerializer(serializers.ModelSerializer):
    svg_url = serializers.SerializerMethodField()
    png_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Component
        fields = '__all__'
    
        def to_internal_value(self, data):
            grips = data.get("grips")

            if isinstance(grips, str):
                try:
                    data["grips"] = json.loads(grips)
                except json.JSONDecodeError:
                    raise serializers.ValidationError({
                        "grips": "Invalid JSON format"
                    })

            return super().to_internal_value(data)
    
    def get_svg_url(self, obj):
        request = self.context.get('request')
        if obj.svg and hasattr(obj.svg, 'url'):
            if request:
                return request.build_absolute_uri(obj.svg.url)
            return obj.svg.url
        return None
    
    def get_png_url(self, obj):
        request = self.context.get('request')
        if obj.png and hasattr(obj.png, 'url'):
            if request:
                return request.build_absolute_uri(obj.png.url)
            return obj.png.url
        return None

class ProjectComponentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="component.id", read_only=True)
    s_no = serializers.CharField(source="component.s_no", read_only=True)
    parent = serializers.CharField(source="component.parent", read_only=True)
    name = serializers.CharField(source="component.name", read_only=True)
    svg = serializers.ImageField(source="component.svg", read_only=True)
    png = serializers.ImageField(source="component.png", read_only=True)
    object = serializers.CharField(source="component.object", read_only=True)
    legend = serializers.CharField(source="component.legend", read_only=True)
    suffix = serializers.CharField(source="component.suffix", read_only=True)
    grips = serializers.CharField(source="component.grips", read_only=True)

    class Meta:
        model = ProjectComponent
        fields = [
            "id",
            "s_no",
            "parent",
            "name",
            "svg",
            "png",
            "object",
            "legend",
            "suffix",
            "grips",
            "component_unique_id",
            "connections",
        ]