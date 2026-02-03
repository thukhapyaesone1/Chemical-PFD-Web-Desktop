from importlib.resources import path
from django.contrib import admin
from .models import Project, Component, CanvasState, Connection
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
import zipfile
from django.contrib import admin, messages
import tempfile
import os,csv,json
from django.core.files import File

# -----------------------------
# Project Admin
# -----------------------------
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user", "created_at")
    search_fields = ("name", "user__username")
    list_filter = ("created_at",)


# -----------------------------
# Component Admin
# -----------------------------
@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ("id","s_no", "name")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("upload-zip/", self.admin_site.admin_view(self.upload_zip), name="component_upload_zip"),
        ]
        return custom_urls + urls

    def upload_zip(self, request):
        if request.method == "POST":
            zip_file = request.FILES.get("zip_file")
            if not zip_file or not zip_file.name.endswith(".zip"):
                messages.error(request, "Please upload a valid ZIP file.")
                return redirect("admin:component_upload_zip")

            # Create temp directory to extract ZIP
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(zip_file) as zf:
                    zf.extractall(temp_dir)
                
                # Find components folder (case insensitive)
                components_dir = None
                for item in os.listdir(temp_dir):
                    if os.path.isdir(os.path.join(temp_dir, item)) and item.lower() == "components":
                        components_dir = os.path.join(temp_dir, item)
                        break
                
                if not components_dir:
                    messages.error(request, "Components folder not found in ZIP.")
                    return redirect("admin:component_upload_zip")
                
                # Find CSV file
                csv_file = None
                for item in os.listdir(components_dir):
                    if item.lower().endswith('.csv'):
                        csv_file = os.path.join(components_dir, item)
                        break
                
                if not csv_file:
                    messages.error(request, "CSV file not found in components folder.")
                    return redirect("admin:component_upload_zip")
                
                # Map folder names to actual paths
                folder_map = {}
                for item in os.listdir(components_dir):
                    item_path = os.path.join(components_dir, item)
                    if os.path.isdir(item_path):
                        folder_map[item.lower()] = item_path
                
                # Check required folders
                required_folders = ['svg', 'png']
                missing_folders = [f for f in required_folders if f not in folder_map]
                
                if missing_folders:
                    messages.error(request, f"Missing folders: {', '.join(missing_folders)}")
                    return redirect("admin:component_upload_zip")
                
                svg_dir = folder_map['svg']
                png_dir = folder_map['png']

                with open(csv_file, newline="", encoding="utf-8-sig") as csvfile:
                    reader = csv.DictReader(csvfile)
                    success_count = 0
                    update_count = 0
                    create_count = 0
                    
                    for row in reader:
                        component_name = row.get("name")
                        s_no = row.get("s_no")
                        
                        # Skip rows without name or s_no
                        if not component_name or not s_no:
                            messages.warning(request, f"Skipping row missing name or s_no: {row}")
                            continue
                        
                        svg_path = os.path.join(svg_dir, f"{component_name}.svg")
                        png_path = os.path.join(png_dir, f"{component_name}.png")
                        
                        try:
                            # Check if component with this s_no already exists
                            existing_component = Component.objects.filter(s_no=s_no).first()
                            grips = row.get("grips")  # from CSV
                            if grips:
                                try:
                                    print("Grips data:", grips)
                                    grips = json.loads(grips)
                                except json.JSONDecodeError:
                                    print(f"Invalid JSON format for grips in component '{component_name}'. Setting grips to empty list.")
                                    grips = []

                            else:
                                grips = []
                            
                            if existing_component:
                                # Update existing component
                                component = existing_component
                                component.parent = row.get("parent", component.parent)
                                component.name = component_name
                                component.legend = row.get("legend", component.legend)
                                component.suffix = row.get("suffix", component.suffix)
                                component.object = row.get("object", component.object)
                                component.grips =  grips
                                update_count += 1
                            else:
                                # Create new component
                                component = Component(
                                    s_no=s_no,
                                    parent=row.get("parent"),
                                    name=component_name,
                                    legend=row.get("legend"),
                                    suffix=row.get("suffix"),
                                    object=row.get("object"),
                                    grips= grips,
                                )
                                create_count += 1
                            
                            # Update SVG if file exists
                            if os.path.exists(svg_path):
                                # Delete old SVG file if exists
                                if component.svg and hasattr(component.svg, 'name'):
                                    old_svg_path = component.svg.path
                                    if os.path.exists(old_svg_path):
                                        os.remove(old_svg_path)
                                
                                with open(svg_path, "rb") as f:
                                    component.svg.save(f"{component_name}.svg", File(f), save=False)
                            
                            # Update PNG if file exists
                            if os.path.exists(png_path):
                                # Delete old PNG file if exists
                                if component.png and hasattr(component.png, 'name'):
                                    old_png_path = component.png.path
                                    if os.path.exists(old_png_path):
                                        os.remove(old_png_path)
                                
                                with open(png_path, "rb") as f:
                                    component.png.save(f"{component_name}.png", File(f), save=False)
                            
                            component.save()
                            success_count += 1
                            
                        except Exception as e:
                            messages.warning(request, f"Error saving component '{component_name}': {str(e)}")
                
                if success_count > 0:
                    message = f"Successfully processed {success_count} components"
                    if update_count > 0:
                        message += f" (Updated: {update_count}"
                    if create_count > 0:
                        if update_count > 0:
                            message += f", Created: {create_count}"
                        else:
                            message += f" (Created: {create_count}"
                    if update_count > 0 or create_count > 0:
                        message += ")"
                    messages.success(request, message)
                return redirect("admin:api_component_changelist")

        return render(request, "admin/api/component/upload_zip.html")

# -----------------------------
# ProjectComponent Admin
# -----------------------------
@admin.register(CanvasState)
class CanvasStateAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "component", "label", "sequence")
    search_fields = ("label", "project__name", "component__name")
    list_filter = ("project", "component")

    # Show project name
    def project_name(self, obj):
        return obj.project.name
    project_name.short_description = "Project"

    # Show component name
    def component_name(self, obj):
        return obj.component.name
    component_name.short_description = "Component"

@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ("id", "sourceItemId", "targetItemId")
