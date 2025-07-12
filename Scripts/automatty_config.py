"""
AutoMatty Configuration and Utilities - Clean Version
Centralized config with UI integration and button functions
"""
import unreal
import os
import sys
import re

def ensure_unreal_qt():
    """Auto-install unreal_qt if missing"""
    try:
        import unreal_qt
        return True
    except ImportError:
        unreal.log("📦 Installing unreal-qt dependency...")
        
        # Auto-install using UE's pip
        import subprocess
        import sys
        import os
        
        # Get UE's Python executable
        python_exe = sys.executable
        
        try:
            # Install unreal-qt
            result = subprocess.run([
                python_exe, "-m", "pip", "install", "unreal-qt"
            ], capture_output=True, text=True, check=True)
            
            unreal.log("✅ unreal-qt installed successfully!")
            return True
            
        except subprocess.CalledProcessError as e:
            unreal.log_error(f"❌ Failed to install unreal-qt: {e}")
            unreal.log_error("💡 Manual install: Run this in cmd as admin:")
            unreal.log_error(f'   cd "{os.path.dirname(python_exe)}"')
            unreal.log_error(f'   python.exe -m pip install unreal-qt')
            return False
# =================================================
# ADD THESE FUNCTIONS TO automatty_config.py
# =================================================

def show_error_dialog(title, message, details=None):
    """Show user-friendly error dialog"""
    try:
        from PySide6.QtWidgets import QMessageBox
        
        msg = QMessageBox()
        msg.setWindowTitle(f"AutoMatty - {title}")
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        
        if details:
            msg.setInformativeText(details)
        
        msg.exec_()
    except:
        # Fallback to console if Qt fails
        unreal.log_error(f"❌ {title}: {message}")
        if details:
            unreal.log_error(f"   {details}")

def show_success_dialog(title, message, details=None):
    """Show success notification"""
    try:
        from PySide6.QtWidgets import QMessageBox
        
        msg = QMessageBox()
        msg.setWindowTitle(f"AutoMatty - {title}")
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        
        if details:
            msg.setInformativeText(details)
        
        msg.exec_()
    except:
        unreal.log(f"✅ {title}: {message}")

def show_material_selection_dialog():
    """Show dialog when no material instances found"""
    try:
        from PySide6.QtWidgets import QMessageBox
        
        msg = QMessageBox()
        msg.setWindowTitle("AutoMatty Material Editor")
        msg.setIcon(QMessageBox.Information)
        msg.setText("No Material Instances Found")
        msg.setInformativeText(
            "The selected mesh has regular Materials, but the editor works best with Material Instances.\n\n"
            "Would you like to create Material Instances from the existing materials?"
        )
        
        create_btn = msg.addButton("Create Instances", QMessageBox.AcceptRole)
        cancel_btn = msg.addButton("Cancel", QMessageBox.RejectRole)
        help_btn = msg.addButton("What's the difference?", QMessageBox.HelpRole)
        
        msg.exec_()
        
        if msg.clickedButton() == create_btn:
            return "create"
        elif msg.clickedButton() == help_btn:
            return "help"
        else:
            return "cancel"
    except:
        unreal.log_warning("⚠️ No Material Instances found. Select mesh with Material Instances.")
        return "cancel"

def show_help_dialog():
    """Explain Materials vs Material Instances"""
    try:
        from PySide6.QtWidgets import QMessageBox
        
        msg = QMessageBox()
        msg.setWindowTitle("Materials vs Material Instances")
        msg.setIcon(QMessageBox.Information)
        msg.setText("What's the difference?")
        msg.setInformativeText(
            "• Materials: Master templates (changes affect everything using them)\n"
            "• Material Instances: Editable copies with parameters\n\n"
            "The Material Editor can edit both, but Material Instances are safer "
            "because changes only affect that specific instance."
        )
        msg.exec_()
    except:
        unreal.log("💡 Materials = master templates, Material Instances = safe copies to edit")

def check_for_regular_materials(selected_actors):
    """Check if actors have regular materials (not instances)"""
    regular_materials = []
    
    for actor in selected_actors:
        if isinstance(actor, (unreal.StaticMeshActor, unreal.SkeletalMeshActor)):
            mesh_component = None
            
            if isinstance(actor, unreal.StaticMeshActor):
                mesh_component = actor.get_component_by_class(unreal.StaticMeshComponent)
            else:
                mesh_component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
            
            if mesh_component:
                num_materials = mesh_component.get_num_materials()
                
                for i in range(num_materials):
                    material = mesh_component.get_material(i)
                    if isinstance(material, unreal.Material):  # Regular material, not instance
                        regular_materials.append({
                            'name': material.get_name(),
                            'instance': material,
                            'slot': i,
                            'actor': actor.get_name()
                        })
    
    return regular_materials

def validate_material_options(checkboxes):
    """Validate material creation options for conflicts"""
    conflicts = []
    
    # Check triplanar + custom UV conflicts
    if checkboxes.get('use_triplanar') and checkboxes.get('use_custom_uvs'):
        conflicts.append({
            'type': 'triplanar_uv',
            'message': 'Triplanar mapping and custom UVs cannot be used together',
            'solution': 'Choose either Triplanar OR custom UVs, not both'
        })
    
    # Add more validations as needed...
    
    return conflicts

def show_conflict_dialog(conflicts):
    """Show material creation conflicts"""
    try:
        from PySide6.QtWidgets import QMessageBox
        
        msg = QMessageBox()
        msg.setWindowTitle("AutoMatty - Material Creation Issues")
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Material creation has conflicts:")
        
        conflict_text = "\n\n".join([
            f"• {c['message']}\n  → {c['solution']}" 
            for c in conflicts
        ])
        
        msg.setInformativeText(conflict_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    except:
        for conflict in conflicts:
            unreal.log_error(f"❌ {conflict['message']}")
            unreal.log_error(f"   → {conflict['solution']}")

def show_material_editor():
    """Enhanced show material editor with error handling"""
    try:
        # Setup unreal-qt if needed
        import unreal_qt
        unreal_qt.setup()
        
        # Import and show the editor with enhanced error handling
        import automatty_material_instance_editor
        automatty_material_instance_editor.show_editor_for_selection()
        
    except ImportError:
        show_error_dialog(
            "Missing Dependency", 
            "unreal-qt is required for the Material Editor.",
            "Install it with: pip install unreal-qt"
        )
    except Exception as e:
        show_error_dialog("Material Editor Error", f"Failed to open editor: {e}")

def debug_selected_materials():
    """Debug function to see what materials are on selected mesh"""
    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    selected_actors = editor_actor_subsystem.get_selected_level_actors()
    
    unreal.log(f"🔍 Found {len(selected_actors)} selected actors")
    
    for actor in selected_actors:
        unreal.log(f"  Actor: {actor.get_name()} ({type(actor).__name__})")
        
        if isinstance(actor, (unreal.StaticMeshActor, unreal.SkeletalMeshActor)):
            if isinstance(actor, unreal.StaticMeshActor):
                mesh_component = actor.get_component_by_class(unreal.StaticMeshComponent)
            else:
                mesh_component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
            
            if mesh_component:
                num_materials = mesh_component.get_num_materials()
                unreal.log(f"    Materials: {num_materials}")
                
                for i in range(num_materials):
                    material = mesh_component.get_material(i)
                    if material:
                        mat_type = type(material).__name__
                        unreal.log(f"      Slot {i}: {material.get_name()} ({mat_type})")
                    else:
                        unreal.log(f"      Slot {i}: None")



# Setup AutoMatty path - do this first before any other imports
def setup_automatty_path():
    """Ensure AutoMatty scripts path is available"""
    possible_paths = [
        # Project plugins (highest priority)
        os.path.join(unreal.Paths.project_dir(), "Plugins", "AutoMatty", "Scripts"),
        # Engine plugins
        os.path.join(unreal.Paths.engine_dir(), "Plugins", "AutoMatty", "Scripts"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path) and os.path.isdir(path):
            if path not in sys.path:
                sys.path.insert(0, path)
            unreal.log(f"📁 AutoMatty scripts loaded from: {path}")
            return path
    
    unreal.log_error("❌ AutoMatty plugin not found in engine or project directories")
    return None

# Run setup immediately
setup_automatty_path()

# Now import AutoMatty modules
try:
    from automatty_utils import setup_automatty_imports
    setup_automatty_imports()
except ImportError as e:
    unreal.log_error(f"❌ Failed to import automatty_utils: {e}")


## RELOAD AND SHOWING INSTANCE EDITOR

def reload_material_editor():
    """Hot-reload the material editor without restarting UE"""
    import importlib
    try:
        import automatty_material_instance_editor
        importlib.reload(automatty_material_instance_editor)
        unreal.log("🔄 Material editor reloaded!")
        return automatty_material_instance_editor
    except Exception as e:
        unreal.log_error(f"❌ Reload failed: {e}")
        return None

def show_material_editor():
    """Show the material editor with current selection"""
    editor_module = reload_material_editor()
    if editor_module:
        editor_module.show_editor_for_selection()




class AutoMattyConfig:
    """Centralized config for AutoMatty plugin with UI integration"""
    
    # Default paths - can be overridden
    DEFAULT_MATERIAL_PATH = "/Game/Materials/AutoMatty"
    DEFAULT_TEXTURE_PATH = "/Game/Textures/AutoMatty"
    DEFAULT_FUNCTION_PATH = "/Game/Functions"
    DEFAULT_MATERIAL_PREFIX = "M_AutoMatty"
    
    # Material function names
    CHEAP_CONTRAST_FUNC = "CheapContrast"
    REMAP_VALUE_FUNC = "RemapValueRange"
    
    # UI settings for persistent storage
    UI_SETTINGS_SECTION = "AutoMattyPlugin"
    CUSTOM_MATERIAL_PATH_KEY = "CustomMaterialPath"
    CUSTOM_TEXTURE_PATH_KEY = "CustomTexturePath"
    CUSTOM_MATERIAL_PREFIX_KEY = "CustomMaterialPrefix"
    
    # Texture matching patterns - UPDATED WITH HEIGHT AND BLEND SUPPORT
    TEXTURE_PATTERNS = {
        "ORM": re.compile(r"(?:^|[_\W])orm(?:$|[_\W])|occlusion[-_]?roughness[-_]?metal(?:lic|ness)", re.IGNORECASE),
        "Color": re.compile(r"(colou?r|albedo|base[-_]?color|diffuse)", re.IGNORECASE),
        "Normal": re.compile(r"normal", re.IGNORECASE),
        "Occlusion": re.compile(r"(?:^|[_\W])(?:ao|occlusion)(?:$|[_\W])", re.IGNORECASE),
        "Roughness": re.compile(r"roughness", re.IGNORECASE),
        "Metallic": re.compile(r"metal(?:lic|ness)", re.IGNORECASE),
        "Height": re.compile(r"(?:^|[_\W])(?:height|disp|displacement)(?:$|[_\W])", re.IGNORECASE),
        "Emission": re.compile(r"(?:^|[_\W])(?:emission|emissive|glow)(?:$|[_\W])", re.IGNORECASE),
        "BlendMask": re.compile(r"(?:^|[_\W])(?:blend|mask|mix)(?:$|[_\W])", re.IGNORECASE),
    }
    
    @staticmethod
    def get_custom_material_path():
        """Get user-defined material path from config file"""
        config_file = AutoMattyConfig._get_config_file_path()
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    import json
                    config_data = json.load(f)
                    custom_path = config_data.get('material_path', '')
                    return custom_path if custom_path.strip() else AutoMattyConfig.DEFAULT_MATERIAL_PATH
        except Exception as e:
            unreal.log_warning(f"Could not read config: {e}")
        
        return AutoMattyConfig.DEFAULT_MATERIAL_PATH
    
    @staticmethod
    def set_custom_material_path(path):
        """Save custom material path to config file"""
        config_file = AutoMattyConfig._get_config_file_path()
        
        try:
            # Create config directory if needed
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            
            # Read existing config or create new
            config_data = {}
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    import json
                    config_data = json.load(f)
            
            # Update and save
            config_data['material_path'] = path
            with open(config_file, 'w') as f:
                import json
                json.dump(config_data, f, indent=2)
            
            unreal.log(f"📁 Custom material path set to: {path}")
        except Exception as e:
            unreal.log_error(f"Failed to save config: {e}")
    
    @staticmethod
    def get_custom_texture_path():
        """Get user-defined texture path from config file"""
        config_file = AutoMattyConfig._get_config_file_path()
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    import json
                    config_data = json.load(f)
                    custom_path = config_data.get('texture_path', '')
                    return custom_path if custom_path.strip() else AutoMattyConfig.DEFAULT_TEXTURE_PATH
        except Exception as e:
            unreal.log_warning(f"Could not read texture path config: {e}")
        
        return AutoMattyConfig.DEFAULT_TEXTURE_PATH
    
    @staticmethod
    def set_custom_texture_path(path):
        """Save custom texture path to config file"""
        config_file = AutoMattyConfig._get_config_file_path()
        
        try:
            # Create config directory if needed
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            
            # Read existing config or create new
            config_data = {}
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    import json
                    config_data = json.load(f)
            
            # Update and save
            config_data['texture_path'] = path
            with open(config_file, 'w') as f:
                import json
                json.dump(config_data, f, indent=2)
            
            unreal.log(f"🖼️ Custom texture path set to: {path}")
        except Exception as e:
            unreal.log_error(f"Failed to save texture path config: {e}")
    
    @staticmethod
    def get_custom_material_prefix():
        """Get user-defined material prefix from config file"""
        config_file = AutoMattyConfig._get_config_file_path()
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    import json
                    config_data = json.load(f)
                    return config_data.get('material_prefix', AutoMattyConfig.DEFAULT_MATERIAL_PREFIX)
        except Exception as e:
            unreal.log_warning(f"Could not read material prefix config: {e}")
        
        return AutoMattyConfig.DEFAULT_MATERIAL_PREFIX
    
    @staticmethod
    def set_custom_material_prefix(prefix):
        """Save custom material prefix to config file"""
        config_file = AutoMattyConfig._get_config_file_path()
        
        try:
            # Create config directory if needed
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            
            # Read existing config or create new
            config_data = {}
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    import json
                    config_data = json.load(f)
            
            # Update and save
            config_data['material_prefix'] = prefix
            with open(config_file, 'w') as f:
                import json
                json.dump(config_data, f, indent=2)
            
            unreal.log(f"🏷️ Material prefix set to: {prefix}")
        except Exception as e:
            unreal.log_error(f"Failed to save material prefix config: {e}")
    
    @staticmethod
    def _get_config_file_path():
        """Get the config file path"""
        proj_dir = unreal.Paths.project_dir()
        config_dir = os.path.join(proj_dir, "Saved", "Config", "AutoMatty")
        return os.path.join(config_dir, "automatty_config.json")
    
    @staticmethod
    def validate_and_create_path(path):
        """Validate path and create folder if needed"""
        if not path.startswith("/Game/"):
            unreal.log_warning(f"⚠️ Path should start with /Game/: {path}")
            return False
        
        # Create the folder structure if it doesn't exist
        try:
            # This will create the folder structure
            unreal.EditorAssetLibrary.make_directory(path)
            unreal.log(f"✅ Ensured path exists: {path}")
            return True
        except Exception as e:
            unreal.log_error(f"❌ Failed to create path {path}: {str(e)}")
            return False

class AutoMattyUtils:
    """Utility functions for AutoMatty with enhanced smart naming and environment support"""
    
    @staticmethod
    def get_user_path(prompt_text, default_path):
        """Get path from user with default fallback"""
        return default_path  # For now, return default
    
    @staticmethod
    def is_substrate_enabled():
        """Check if Substrate material system is enabled"""
        try:
            # Try creating a substrate node to test
            temp_mat = unreal.Material()
            lib = unreal.MaterialEditingLibrary
            temp_node = lib.create_material_expression(
                temp_mat, unreal.MaterialExpressionSubstrateSlabBSDF, 0, 0
            )
            return temp_node is not None
        except:
            unreal.log_warning("Could not determine Substrate status - assuming enabled")
            return True
    
    @staticmethod
    def get_next_asset_name(base_name, folder, prefix="v", pad=3):
        """Generate versioned asset name"""
        registry = unreal.AssetRegistryHelpers.get_asset_registry()
        assets = registry.get_assets_by_path(folder, recursive=False)
        pat = re.compile(rf"^{re.escape(base_name)}_{prefix}(\d{{{pad}}})$")
        max_idx = 0
        for ad in assets:
            m = pat.match(str(ad.asset_name))
            if m and int(m.group(1)) > max_idx:
                max_idx = int(m.group(1))
        return f"{base_name}_{prefix}{max_idx+1:0{pad}d}"
    
    @staticmethod
    def find_default_normal():
        """Find engine's default normal texture"""
        for path in unreal.EditorAssetLibrary.list_assets("/Engine", recursive=True, include_folder=False):
            if path.lower().endswith("defaultnormal"):
                return unreal.EditorAssetLibrary.load_asset(path)
        unreal.log_warning("Could not find DefaultNormal in /Engine")
        return None
    
    @staticmethod
    def check_material_function_exists(func_name, search_path=None):
        """Check if a material function exists"""
        if search_path is None:
            search_path = AutoMattyConfig.DEFAULT_FUNCTION_PATH
        
        func_path = f"{search_path}/{func_name}"
        return unreal.EditorAssetLibrary.does_asset_exist(func_path)
    
    @staticmethod
    def extract_material_base_name(textures):
        """Extract base material name from texture list"""
        
        if not textures:
            return "Material"
        
        # Get the first texture name to analyze
        first_texture = textures[0].get_name()
        
        # Remove common texture suffixes and patterns
        base_name = first_texture
        
        # Remove file extensions if somehow present
        base_name = re.sub(r'\.(jpg|png|tga|exr|hdr|tiff)$', '', base_name, flags=re.IGNORECASE)
        
        # Remove UDIM patterns (1001, 1002, etc or <udim>)
        base_name = re.sub(r'_(?:10\d{2}|<udim>)', '', base_name, flags=re.IGNORECASE)
        
        # Remove colorspace info (sRGB, Linear, etc)
        base_name = re.sub(r'_(?:srgb|linear|rec709|aces)', '', base_name, flags=re.IGNORECASE)
        
        # Remove resolution info (2K, 4K, 1024, etc)
        base_name = re.sub(r'_(?:\d+k|\d{3,4})$', '', base_name, flags=re.IGNORECASE)
        
        # Remove texture type suffixes (color, normal, orm, height, etc)
        texture_types = [
            'color', 'colour', 'albedo', 'diffuse', 'basecolor', 'base_color',
            'normal', 'norm', 'nrm', 'bump',
            'roughness', 'rough', 'gloss',
            'metallic', 'metalness', 'metal',
            'specular', 'spec',
            'occlusion', 'ao', 'ambient_occlusion',
            'orm', 'rma', 'mas',  # packed maps
            'height', 'displacement', 'disp',  # height/displacement maps
            'emission', 'emissive', 'glow',
            'blend', 'mask', 'mix'  # environment blend masks
        ]
        
        # Create pattern to match any texture type at the end
        type_pattern = r'_(?:' + '|'.join(texture_types) + r')(?:_.*)?$'
        base_name = re.sub(type_pattern, '', base_name, flags=re.IGNORECASE)
        
        # Clean up any trailing underscores or numbers
        base_name = re.sub(r'_+$', '', base_name)
        base_name = re.sub(r'_v?\d+$', '', base_name)  # Remove version numbers
        
        # If we stripped everything, use a fallback
        if not base_name or len(base_name) < 2:
            # Try to get something from the original name
            fallback = re.split(r'[_\-\.]', first_texture)[0]
            base_name = fallback if fallback else "Material"
        
        # Ensure it starts with a letter (UE naming convention)
        if not re.match(r'^[a-zA-Z]', base_name):
            base_name = f"Mat_{base_name}"
        
        return base_name
    
    @staticmethod
    def generate_smart_instance_name(base_material, textures, custom_path=None):
        """Generate smart instance name based on textures"""
        
        # Extract base name from textures
        material_base = AutoMattyUtils.extract_material_base_name(textures)
        
        # Create instance name
        instance_name = f"M_{material_base}_Inst"
        
        # Get the target folder
        if custom_path:
            folder = custom_path
        else:
            folder = AutoMattyConfig.get_custom_material_path()
        
        # Check for existing instances and version if needed
        full_path = f"{folder}/{instance_name}"
        if unreal.EditorAssetLibrary.does_asset_exist(full_path):
            instance_name = AutoMattyUtils.get_next_asset_name(
                f"M_{material_base}_Inst", folder
            )
        
        return instance_name, folder

# ========================================
# UI INTEGRATION FUNCTIONS
# ========================================

def ui_set_custom_material_path(path_string):
    """Called from UI when user sets custom material path"""
    if not path_string.strip():
        unreal.log("📁 Using default material path")
        AutoMattyConfig.set_custom_material_path("")
        return True
    
    # Clean up the path - handle content browser paths properly
    clean_path = path_string.strip()
    
    # Handle content browser paths that start with /All/Game/
    if clean_path.startswith("/All/Game/"):
        clean_path = clean_path.replace("/All/Game/", "/Game/", 1)
    # Handle paths that don't start with /Game/
    elif not clean_path.startswith("/Game/"):
        clean_path = f"/Game/{clean_path.lstrip('/')}"
    
    # Validate and set
    if AutoMattyConfig.validate_and_create_path(clean_path):
        AutoMattyConfig.set_custom_material_path(clean_path)
        return True
    else:
        return False


def ui_get_current_material_path():
    """Get current material path for UI display"""
    return AutoMattyConfig.get_custom_material_path()

def ui_set_custom_texture_path(path_string):
    """Called from UI when user sets custom texture path"""
    if not path_string.strip():
        unreal.log("🖼️ Using default texture path")
        AutoMattyConfig.set_custom_texture_path("")
        return True
    
    # Clean up the path - handle content browser paths properly
    clean_path = path_string.strip()
    
    # Handle content browser paths that start with /All/Game/
    if clean_path.startswith("/All/Game/"):
        clean_path = clean_path.replace("/All/Game/", "/Game/", 1)
    # Handle paths that don't start with /Game/
    elif not clean_path.startswith("/Game/"):
        clean_path = f"/Game/{clean_path.lstrip('/')}"
    
    # Validate and set
    if AutoMattyConfig.validate_and_create_path(clean_path):
        AutoMattyConfig.set_custom_texture_path(clean_path)
        return True
    else:
        return False

def ui_get_current_texture_path():
    """Get current texture path for UI display"""
    return AutoMattyConfig.get_custom_texture_path()

def ui_set_custom_material_prefix(prefix_string):
    """Called from UI when user sets custom material prefix"""
    clean_prefix = prefix_string.strip() or AutoMattyConfig.DEFAULT_MATERIAL_PREFIX
    AutoMattyConfig.set_custom_material_prefix(clean_prefix)
    return True

def ui_get_current_material_prefix():
    """Get current material prefix for UI display"""
    return AutoMattyConfig.get_custom_material_prefix()

# ========================================
# STREAMLINED UI FUNCTIONS
# ========================================

def get_widget():
    """Get the widget instance - one liner"""
    try:
        subsystem = unreal.get_editor_subsystem(unreal.EditorUtilitySubsystem)
        blueprint = unreal.EditorAssetLibrary.load_asset("/AutoMatty/EUW_AutoMatty")
        return subsystem.find_utility_widget_from_blueprint(blueprint) if blueprint else None
    except:
        return None

def apply_all_settings():
    """Apply ALL settings at once - one button to rule them all"""
    widget = get_widget()
    if not widget:
        unreal.log_error("❌ No widget found")
        return
    
    try:
        # Read all inputs
        prefix = str(widget.get_editor_property('MaterialPrefixInput').get_text()).strip()
        mat_path = str(widget.get_editor_property('MaterialPathInput').get_text()).strip()
        tex_path = str(widget.get_editor_property('TexturePathInput').get_text()).strip()
        
        # Apply all settings
        results = []
        if prefix:
            ui_set_custom_material_prefix(prefix)
            results.append(f"Prefix: {prefix}")
        if mat_path:
            ui_set_custom_material_path(mat_path)
            results.append(f"Material: {mat_path}")
        if tex_path:
            ui_set_custom_texture_path(tex_path)
            results.append(f"Texture: {tex_path}")
        
        if results:
            unreal.log(f"✅ Settings applied: {' | '.join(results)}")
        else:
            unreal.log("⚠️ No settings to apply")
            
    except Exception as e:
        unreal.log_error(f"❌ Settings failed: {e}")

def load_current_settings():
    """Load current settings into the widget inputs"""
    widget = get_widget()
    if not widget:
        unreal.log_warning("⚠️ No widget found for settings load")
        return
    
    try:
        # Set current values in the widget
        widget.get_editor_property('MaterialPrefixInput').set_text(ui_get_current_material_prefix())
        widget.get_editor_property('MaterialPathInput').set_text(ui_get_current_material_path())
        widget.get_editor_property('TexturePathInput').set_text(ui_get_current_texture_path())
        
        unreal.log("📥 Current settings loaded into UI")
        
    except Exception as e:
        unreal.log_error(f"❌ Load settings failed: {e}")

# Auto-save functions (for OnTextCommitted events)
def auto_save_prefix():
    widget = get_widget()
    if widget:
        try:
            prefix = str(widget.get_editor_property('MaterialPrefixInput').get_text()).strip()
            if prefix:
                ui_set_custom_material_prefix(prefix)
        except:
            pass

def auto_save_material_path():
    widget = get_widget()
    if widget:
        try:
            path = str(widget.get_editor_property('MaterialPathInput').get_text()).strip()
            if path:
                ui_set_custom_material_path(path)
        except:
            pass

def auto_save_texture_path():
    widget = get_widget()
    if widget:
        try:
            path = str(widget.get_editor_property('TexturePathInput').get_text()).strip()
            if path:
                ui_set_custom_texture_path(path)
        except:
            pass

# ========================================
# BUTTON FUNCTIONS - Material creation actions
# ========================================

def get_checkboxes():
    """Get checkbox states from widget - UPDATED WITH TEXTURE VARIATION"""
    checkboxes = {
        'use_nanite': False,
        'use_second_roughness': False,
        'use_adv_env': False,
        'use_triplanar': False,
        'use_tex_var': False  # NEW - texture variation toggle
    }
    
    try:
        widget = get_widget()
        if widget:
            nanite_checkbox = widget.get_editor_property("UseNanite")
            roughness_checkbox = widget.get_editor_property("UseSecondRoughness")
            adv_env_checkbox = widget.get_editor_property("UseAdvEnv")
            triplanar_checkbox = widget.get_editor_property("UseTriplanar")
            tex_var_checkbox = widget.get_editor_property("UseTexVar")  # NEW
            
            checkboxes['use_nanite'] = nanite_checkbox.is_checked() if nanite_checkbox else False
            checkboxes['use_second_roughness'] = roughness_checkbox.is_checked() if roughness_checkbox else False
            checkboxes['use_adv_env'] = adv_env_checkbox.is_checked() if adv_env_checkbox else False
            checkboxes['use_triplanar'] = triplanar_checkbox.is_checked() if triplanar_checkbox else False
            checkboxes['use_tex_var'] = tex_var_checkbox.is_checked() if tex_var_checkbox else False  # NEW
            
            unreal.log(f"✅ Checkboxes: Nanite={checkboxes['use_nanite']}, SecondRough={checkboxes['use_second_roughness']}, AdvEnv={checkboxes['use_adv_env']}, Triplanar={checkboxes['use_triplanar']}, TexVar={checkboxes['use_tex_var']}")
    except Exception as e:
        unreal.log_error(f"⚠️ Checkbox access failed: {e}")
    
    return checkboxes

def create_orm_material():
    """Create ORM material - UPDATED WITH UV SCALE AND TEXTURE VARIATION"""
    unreal.log("🔧 Creating ORM Material with UV scaling and variation support...")
    
    try:
        import importlib
        import automatty_builder
        importlib.reload(automatty_builder)
        from automatty_builder import SubstrateMaterialBuilder
        
        checkboxes = get_checkboxes()
        builder = SubstrateMaterialBuilder()
        
        material = builder.create_orm_material(
            use_second_roughness=checkboxes['use_second_roughness'],
            use_nanite=checkboxes['use_nanite'],
            use_triplanar=checkboxes['use_triplanar'],
            use_tex_var=checkboxes['use_tex_var']  # NEW
        )
        
        if material:
            features = []
            if checkboxes['use_second_roughness']: features.append("dual-roughness")
            if checkboxes['use_nanite']: features.append("nanite displacement")
            if checkboxes['use_triplanar']: features.append("triplanar mapping")
            if checkboxes['use_tex_var']: features.append("texture variation")  # NEW
            feature_text = f" with {', '.join(features)}" if features else ""
            unreal.log(f"🎉 SUCCESS! Created ORM material{feature_text}: {material.get_name()}")
            unreal.log(f"💡 UV scaling and texture variation now available on ALL material types!")
        else:
            unreal.log_error("❌ Failed to create ORM material")
            
    except Exception as e:
        unreal.log_error(f"❌ Error creating ORM material: {e}")

def create_split_material():
    """Create Split material - UPDATED WITH UV SCALE AND TEXTURE VARIATION"""
    unreal.log("🔧 Creating Split Material with UV scaling and variation support...")
    
    try:
        import importlib
        import automatty_builder
        importlib.reload(automatty_builder)
        from automatty_builder import SubstrateMaterialBuilder
        
        checkboxes = get_checkboxes()
        builder = SubstrateMaterialBuilder()
        
        material = builder.create_split_material(
            use_second_roughness=checkboxes['use_second_roughness'],
            use_nanite=checkboxes['use_nanite'],
            use_triplanar=checkboxes['use_triplanar'],
            use_tex_var=checkboxes['use_tex_var']  # NEW
        )
        
        if material:
            features = []
            if checkboxes['use_second_roughness']: features.append("dual-roughness")
            if checkboxes['use_nanite']: features.append("nanite displacement")
            if checkboxes['use_triplanar']: features.append("triplanar mapping")
            if checkboxes['use_tex_var']: features.append("texture variation")  # NEW
            feature_text = f" with {', '.join(features)}" if features else ""
            unreal.log(f"🎉 SUCCESS! Created Split material{feature_text}: {material.get_name()}")
            unreal.log(f"💡 UV scaling and texture variation now available on ALL material types!")
        else:
            unreal.log_error("❌ Failed to create Split material")
            
    except Exception as e:
        unreal.log_error(f"❌ Error creating Split material: {e}")

def create_environment_material():
    """Create Environment material - UPDATED WITH TEXTURE VARIATION"""
    unreal.log("🔧 Creating Environment Material...")
    
    try:
        import importlib
        import automatty_builder
        importlib.reload(automatty_builder)
        from automatty_builder import SubstrateMaterialBuilder
        
        checkboxes = get_checkboxes()
        builder = SubstrateMaterialBuilder()
        
        material = builder.create_environment_material(
            use_adv_env=checkboxes['use_adv_env'],
            use_triplanar=checkboxes['use_triplanar'],
            use_nanite=checkboxes['use_nanite'],
            use_tex_var=checkboxes['use_tex_var']  # NEW
        )
        
        if material:
            features = []
            if checkboxes['use_adv_env']: features.append("advanced-mixing")
            if checkboxes['use_triplanar']: features.append("triplanar")
            if checkboxes['use_nanite']: features.append("nanite")
            if checkboxes['use_tex_var']: features.append("texture-variation")  # NEW
            feature_text = f" ({', '.join(features)})" if features else ""
            unreal.log(f"🎉 SUCCESS! Created Environment material{feature_text}: {material.get_name()}")
            if checkboxes['use_adv_env']:
                unreal.log("💀 Your GPU will hate this advanced version")
        else:
            unreal.log_error("❌ Failed to create Environment material")
            
    except Exception as e:
        unreal.log_error(f"❌ Error creating Environment material: {e}")

def create_material_instance():
    """Create Material Instance"""
    unreal.log("🔧 Creating Smart Material Instance...")
    
    try:
        import importlib
        import automatty_instancer
        importlib.reload(automatty_instancer)
        from automatty_instancer import create_material_instance
        
        instance = create_material_instance()
        
        if instance:
            unreal.log(f"🎉 SUCCESS! Created material instance: {instance.get_name()}")
        else:
            unreal.log("⚠️ No instance created - check selection and textures")
            
    except Exception as e:
        unreal.log_error(f"❌ Error creating material instance: {e}")

def repath_material_instances():
    """Repath Material Instances"""
    unreal.log("🔧 Repathing Material Instances...")
    
    try:
        import importlib
        import automatty_repather
        importlib.reload(automatty_repather)
        from automatty_repather import repath_material_instances as repath_func
        
        repath_func()
        unreal.log("🏆 Texture repathing completed")
        
    except Exception as e:
        unreal.log_error(f"❌ Error repathing materials: {e}")




# ===========================================
# PROPER MENU ENTRY SCRIPT APPROACH
# ===========================================

@unreal.uclass()
class AutoMattyMenuScript(unreal.ToolMenuEntryScript):
    """Menu script for AutoMatty Material Editor"""
    
    @unreal.ufunction(override=True)
    def execute(self, context):
        """Execute when menu item is clicked or hotkey pressed"""
        try:
            import automatty_material_instance_editor
            automatty_material_instance_editor.show_editor_for_selection()
            unreal.log("🎯 AutoMatty Material Editor opened via menu/hotkey!")
        except Exception as e:
            unreal.log_error(f"❌ Failed to open AutoMatty editor: {e}")

class AutoMattyHotkeys:
    """Hotkey management using proper menu registration"""
    
    DEFAULT_HOTKEY = "M"
    _menu_script = None
    _widget_script = None  # NEW - for main widget
    
    @staticmethod
    def get_hotkey_from_config():
        """Get hotkey from config"""
        config_file = AutoMattyConfig._get_config_file_path()
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    import json
                    config_data = json.load(f)
                    return config_data.get('hotkey', AutoMattyHotkeys.DEFAULT_HOTKEY)
        except:
            pass
        return AutoMattyHotkeys.DEFAULT_HOTKEY
    
    @staticmethod
    def set_hotkey_in_config(hotkey):
        """Save hotkey to config"""
        config_file = AutoMattyConfig._get_config_file_path()
        try:
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            
            config_data = {}
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    import json
                    config_data = json.load(f)
            
            config_data['hotkey'] = hotkey.upper()
            
            with open(config_file, 'w') as f:
                import json
                json.dump(config_data, f, indent=2)
            
            unreal.log(f"⌨️ Hotkey saved: {hotkey}")
            return True
        except Exception as e:
            unreal.log_error(f"❌ Failed to save hotkey: {e}")
            return False

# ===========================================
# ADDITIONAL MENU SCRIPTS
# ===========================================

@unreal.uclass()
class AutoMattyWidgetScript(unreal.ToolMenuEntryScript):
    """Menu script for main AutoMatty EUW widget"""
    
    @unreal.ufunction(override=True)
    def execute(self, context):
        """Execute when menu item is clicked or hotkey pressed"""
        try:
            # Open the main AutoMatty widget
            subsystem = unreal.get_editor_subsystem(unreal.EditorUtilitySubsystem)
            blueprint = unreal.EditorAssetLibrary.load_asset("/AutoMatty/EUW_AutoMatty")
            
            if blueprint:
                widget = subsystem.spawn_and_register_tab(blueprint)
                if widget:
                    unreal.log("🎯 AutoMatty main widget opened via menu/hotkey!")
                else:
                    unreal.log_error("❌ Failed to spawn AutoMatty widget")
            else:
                unreal.log_error("❌ Could not load EUW_AutoMatty blueprint")
                
        except Exception as e:
            unreal.log_error(f"❌ Failed to open AutoMatty widget: {e}")

# ===========================================
# MENU REGISTRATION 
# ===========================================

def register_automatty_menu_entry():
    """Register BOTH AutoMatty menu entries that can be bound to hotkeys"""
    try:
        # Get the Tools menu
        menus = unreal.ToolMenus.get()
        tools_menu = menus.find_menu("LevelEditor.MainMenu.Tools")
        
        if not tools_menu:
            unreal.log_error("❌ Could not find Tools menu")
            return False
        
        # 1. MAIN WIDGET ENTRY
        widget_script = AutoMattyWidgetScript()
        widget_script.init_entry(
            owner_name="AutoMatty",
            menu="LevelEditor.MainMenu.Tools", 
            section="LevelEditorModules",
            name="AutoMattyWidget",
            label="AutoMatty",
            tool_tip="Open AutoMatty main widget"
        )
        widget_script.register_menu_entry()
        
        # 2. MATERIAL EDITOR ENTRY  
        editor_script = AutoMattyMenuScript()
        editor_script.init_entry(
            owner_name="AutoMatty",
            menu="LevelEditor.MainMenu.Tools", 
            section="LevelEditorModules", 
            name="AutoMattyMaterialEditor",
            label="AutoMatty Material Editor",
            tool_tip="Open AutoMatty Material Instance Editor"
        )
        editor_script.register_menu_entry()
        
        # Refresh menus
        menus.refresh_all_widgets()
        
        # Store references to prevent garbage collection
        AutoMattyHotkeys._menu_script = editor_script
        AutoMattyHotkeys._widget_script = widget_script
        
        unreal.log("✅ AutoMatty menu entries registered!")
        unreal.log("📋 Available in Tools menu:")
        unreal.log("   • AutoMatty (main widget)")
        unreal.log("   • AutoMatty Material Editor")
        unreal.log("📋 To set hotkeys:")
        unreal.log("1. Edit → Editor Preferences → Keyboard Shortcuts")
        unreal.log("2. Search 'AutoMatty' to find both commands")
        unreal.log("3. Set hotkeys (suggest: A for widget, M for editor)")
        
        return True
        
    except Exception as e:
        unreal.log_error(f"❌ Menu registration failed: {e}")
        return False

def unregister_automatty_menu():
    """Unregister AutoMatty menu entries"""
    try:
        menus = unreal.ToolMenus.get()
        menus.unregister_owner_by_name("AutoMatty")
        menus.refresh_all_widgets()
        AutoMattyHotkeys._menu_script = None
        AutoMattyHotkeys._widget_script = None  # Clear both references
        unreal.log("🗑️ AutoMatty menu entries unregistered")
        return True
    except Exception as e:
        unreal.log_error(f"❌ Menu unregistration failed: {e}")
        return False

# ===========================================
# ALTERNATIVE: CONSOLE COMMAND BACKUP
# ===========================================

def register_console_command():
    """Register console command as backup"""
    try:
        # Note: Console command registration in Python is limited
        # This is mainly for testing
        unreal.log("🎮 Console command fallback available")
        unreal.log("💡 Type in console: py automatty_config.open_editor_command()")
        return True
    except Exception as e:
        unreal.log_error(f"❌ Console command setup failed: {e}")
        return False

# ===========================================
# UI FUNCTIONS
# ===========================================

def ui_get_current_hotkey():
    """Get current hotkey for UI"""
    return AutoMattyHotkeys.get_hotkey_from_config()

def ui_set_hotkey(hotkey_string):
    """Set new hotkey"""
    clean_hotkey = hotkey_string.strip().upper()
    
    if not clean_hotkey:
        clean_hotkey = AutoMattyHotkeys.DEFAULT_HOTKEY
    
    if len(clean_hotkey) != 1 or not clean_hotkey.isalpha():
        unreal.log_error(f"❌ Invalid hotkey: {clean_hotkey}. Use A-Z")
        return False
    
    success = AutoMattyHotkeys.set_hotkey_in_config(clean_hotkey)
    if success:
        unreal.log(f"⌨️ Hotkey preference set to: {clean_hotkey}")
        unreal.log("💡 You still need to manually bind it in Editor Preferences")
        show_hotkey_instructions()
    
    return success

def show_hotkey_instructions():
    """Show instructions for manual hotkey setup"""
    hotkey = AutoMattyHotkeys.get_hotkey_from_config()
    unreal.log("📋 HOTKEY SETUP INSTRUCTIONS:")
    unreal.log("1. Edit → Editor Preferences → Keyboard Shortcuts")
    unreal.log("2. Search 'AutoMatty' to find both commands:")
    unreal.log("   • AutoMatty (main widget)")
    unreal.log("   • AutoMatty Material Editor")
    unreal.log("3. Click text field and set hotkeys")
    unreal.log("   💡 Suggestion: A for widget, M for editor")
    unreal.log("4. Click elsewhere to save")

def setup_hotkey_system():
    """Main setup function"""
    hotkey = AutoMattyHotkeys.get_hotkey_from_config()
    unreal.log(f"🔧 Setting up AutoMatty menu entry (hotkey: {hotkey})")
    
    # Register menu entry (this is what gets bound to hotkeys)
    if register_automatty_menu_entry():
        register_console_command()  # Backup method
        return True
    else:
        unreal.log_error("❌ Failed to setup menu entry")
        return False

def test_editor_directly():
    """Test opening editor without hotkey"""
    try:
        import automatty_material_instance_editor
        automatty_material_instance_editor.show_editor_for_selection()
        unreal.log("✅ Direct editor test worked!")
        return True
    except Exception as e:
        unreal.log_error(f"❌ Direct test failed: {e}")
        return False

def open_editor_command():
    """Simple function to open editor (for console/manual use)"""
    test_editor_directly()

def reload_menu_system():
    """Reload menu system for development"""
    unregister_automatty_menu()
    return setup_hotkey_system()

# ===========================================
# ENHANCED WIDGET INTEGRATION
# ===========================================

def apply_all_settings_with_hotkey():
    """Enhanced apply function that includes hotkey"""
    widget = get_widget()
    if not widget:
        unreal.log_error("❌ No widget found")
        return
    
    try:
        # Apply existing settings
        apply_all_settings()
        
        # Apply hotkey if field exists
        try:
            hotkey_input = widget.get_editor_property('HotkeyInput')
            if hotkey_input:
                hotkey = str(hotkey_input.get_text()).strip()
                if hotkey:
                    ui_set_hotkey(hotkey)
        except:
            pass  # Hotkey field doesn't exist yet
            
    except Exception as e:
        unreal.log_error(f"❌ Settings with hotkey failed: {e}")

def load_current_settings_with_hotkey():
    """Enhanced load function that includes hotkey"""
    load_current_settings()
    
    widget = get_widget()
    if widget:
        try:
            hotkey_input = widget.get_editor_property('HotkeyInput')
            if hotkey_input:
                hotkey_input.set_text(ui_get_current_hotkey())
        except:
            pass  # Hotkey field doesn't exist yet

# Auto-setup on import
setup_hotkey_system()