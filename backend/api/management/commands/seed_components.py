import os
import json
from django.core.management.base import BaseCommand
from django.core.files import File
from api.models import Component
from django.conf import settings

class Command(BaseCommand):
    help = 'Seeds the database with default components from frontend config'

    def handle(self, *args, **options):
        # Determine paths
        # backend/api/management/commands/seed_components.py
        # root is backend/
        
        base_dir = settings.BASE_DIR # backend/
        frontend_dir = os.path.abspath(os.path.join(base_dir, '..', 'web-frontend'))
        config_dir = os.path.join(frontend_dir, 'src', 'assets', 'config')
        assets_dir = os.path.join(frontend_dir, 'src', 'assets')

        items_path = os.path.join(config_dir, 'items.json')
        grips_path = os.path.join(config_dir, 'grips.json')

        self.stdout.write(f"Reading config from: {config_dir}")

        if not os.path.exists(items_path):
            self.stdout.write(self.style.ERROR(f"items.json not found at {items_path}"))
            return

        with open(items_path, 'r') as f:
            items_data = json.load(f)

        grips_map = {}
        if os.path.exists(grips_path):
            with open(grips_path, 'r') as f:
                grips_list = json.load(f)
                for g in grips_list:
                    key = (g.get('category'), g.get('component'))
                    grips_map[key] = g

        # Counter for s_no generation if needed
        # We try to maintain stable s_no if possible, or just generate new ones
        
        count = 0
        
        for category, components in items_data.items():
            for comp_name, comp_data in components.items():
                count += 1
                
                # Prepare s_no
                # Ideally check if exists
                # We use specific format e.g. CAT-001
                # But to avoid collision let's use a systematic approach or slug
                s_no_candidate = f"{category[:3].upper()}-{count:03d}"
                
                # Check if component exists by Name AND Category (parent)
                existing = Component.objects.filter(name=comp_name, parent=category).first()
                
                if existing:
                    component = existing
                    self.stdout.write(f"Updating {comp_name}...")
                else:
                    component = Component(name=comp_name, parent=category)
                    component.s_no = s_no_candidate # Set initial s_no
                
                # Update fields
                component.parent = category # Ensure correct
                component.object = comp_data.get('object', '')
                
                # Grips
                grip_entry = grips_map.get((category, comp_name))
                if grip_entry:
                    component.grips = grip_entry.get('grips', [])
                    component.legend = grip_entry.get('default_label', '').split('-')[0] if grip_entry.get('default_label') else comp_data.get('legend', '')
                    # Extract suffix if possible from default_label e.g. C-01-A/B
                    # comp_data might not have suffix in items.json based on view, but let's check
                    # items.json didn't show suffix field. grips.json has default_label "C-01-A/B"
                    # So suffix is "A/B" if present
                    
                    lbl = grip_entry.get('default_label', '')
                    parts = lbl.split('-')
                    if len(parts) > 2:
                        component.suffix = parts[-1]
                    else:
                        component.suffix = ""
                        
                    # Legend is usually the first part
                    if len(parts) > 0:
                        component.legend = parts[0]

                else:
                    # Fallback if no grips entry
                    component.grips = comp_data.get('grips', [])
                    component.legend = comp_data.get('legend', '')
                    component.suffix = comp_data.get('suffix', '')

                # Handle Images
                # Path in json: "./assets/toolbar/..."
                # Real path: src/assets/toolbar/...
                
                icon_rel = comp_data.get('icon', '')
                svg_rel = comp_data.get('svg', '')
                
                def get_real_path(rel_path):
                    if rel_path.startswith('./assets/'):
                        return os.path.join(frontend_dir, 'src', rel_path[2:]) # remove ./
                    return None

                icon_path = get_real_path(icon_rel)
                svg_path = get_real_path(svg_rel)

                if icon_path and os.path.exists(icon_path):
                    with open(icon_path, 'rb') as f:
                        component.png.save(os.path.basename(icon_path), File(f), save=False)
                
                if svg_path and os.path.exists(svg_path):
                    with open(svg_path, 'rb') as f:
                        component.svg.save(os.path.basename(svg_path), File(f), save=False)

                component.save()
                self.stdout.write(self.style.SUCCESS(f"Saved {comp_name}"))

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {count} components"))
