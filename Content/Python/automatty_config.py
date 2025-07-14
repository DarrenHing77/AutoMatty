"""
AutoMatty Configuration - REFACTORED VERSION
Dictionary-driven config management, no more copy-paste hell
"""
import unreal
import os
import sys
import re
import json

# ========================================
# CONFIGURATION DICTIONARIES
# ========================================

# Settings configuration - drives all the UI/storage logic
SETTINGS_CONFIG = {
    "material_path": {
        "default": "/Game/Materials/AutoMatty",
        "widget_property": "MaterialPathInput",
        "description": "📁 Material Path",
        "validation": "path"
    },
    "texture_path": {
        "default": "/Game/Textures/AutoMatty", 
        "widget_property": "TexturePathInput",
        "description": "🖼️ Texture Path",
        "validation": "path"
    },
    "material_prefix": {
        "default": "M_AutoMatty",
        "widget_property": "MaterialPrefixInput", 
        "description": "🏷️ Material Prefix",
        "validation": "name"
    },
    "hotkey": {
        "default": "M",
        "widget_property": "HotkeyInput",
        "description": "⌨️ Hotkey",
        "validation": "hotkey"
    }
}

# Button actions configuration - drives all the create_* functions
BUTTON_ACTIONS = {
    "create_orm": {
        "module": "automatty_builder",
        "class": "SubstrateMaterialBuilder",
        "method": "create_orm_material",
        "description": "🔧 Creating ORM Material",
        "success_msg": "🎉 SUCCESS! Created ORM material",
        "get_features": True
    },
    "create_split": {
        "module": "automatty_builder", 
        "class": "SubstrateMaterialBuilder",
        "method": "create_split_material",
        "description": "🔧 Creating Split Material",
        "success_msg": "🎉 SUCCESS! Created Split material", 
        "get_features": True
    },
    "create_environment": {
        "module": "automatty_builder",
        "class": "SubstrateMaterialBuilder", 
        "method": "create_environment_material",
        "description": "🔧 Creating Environment Material",
        "success_msg": "🎉 SUCCESS! Created Environment material",
        "get_features": True
    },
    "create_instance": {
        "module": "automatty_instancer",
        "function": "create_material_instance", 
        "description": "🔧 Creating Smart Material Instance",
        "success_msg": "🎉 SUCCESS! Created material instance",
        "get_features": False
    },
    "repath_instances": {
        "module": "automatty_repather",
        "function": "repath_material_instances",
        "description": "🔧 Repathing Material Instances", 
        "success_msg": "🏆 Texture repathing completed",
        "get_features": False
    }
}

# Feature checkboxes configuration
FEATURE_CHECKBOXES = {
    "use_nanite": "UseNanite",
    "use_second_roughness": "UseSecondRoughness", 
    "use_adv_env": "UseAdvEnv",
    "use_triplanar": "UseTriplanar",
    "use_tex_var": "UseTexVar"
}

# Validation patterns
VALIDATORS = {
    "path": lambda x: x.startswith("/Game/") if x else True,
    "name": lambda x: bool(x and re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', x)),
    "hotkey": lambda x: len(x) == 1 and x.isalpha() if x else True
}

# Texture matching patterns (moved from old config)
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

# ========================================
# CORE CONFIG CLASS
# ========================================

class AutoMattyConfig:
    """Clean, dictionary-driven configuration management"""
    
    @staticmethod
    def get_config_path():
        """Get config file path"""
        proj_dir = unreal.Paths.project_dir()
        config_dir = os.path.join(proj_dir, "Saved", "Config", "AutoMatty")
        return os.path.join(config_dir, "automatty_config.json")
    
    @staticmethod
    def load_config():
        """Load entire config as dict"""
        config_path = AutoMattyConfig.get_config_path()
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            unreal.log_warning(f"⚠️ Failed to load config: {e}")
        return {}
    
    @staticmethod
    def save_config(config_data):
        """Save entire config dict"""
        config_path = AutoMattyConfig.get_config_path()
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            return True
        except Exception as e:
            unreal.log_error(f"❌ Failed to save config: {e}")
            return False
    
    @staticmethod
    def get_setting(setting_key):
        """Get single setting with default fallback"""
        config = AutoMattyConfig.load_config()
        setting_config = SETTINGS_CONFIG.get(setting_key, {})
        return config.get(setting_key, setting_config.get("default", ""))
    
    @staticmethod
    def set_setting(setting_key, value):
        """Set single setting"""
        if setting_key not in SETTINGS_CONFIG:
            unreal.log_error(f"❌ Unknown setting: {setting_key}")
            return False
        
        # Validate
        setting_config = SETTINGS_CONFIG[setting_key]
        validator = VALIDATORS.get(setting_config.get("validation"))
        if validator and not validator(value):
            unreal.log_error(f"❌ Invalid {setting_key}: {value}")
            return False
        
        # Save
        config = AutoMattyConfig.load_config()
        config[setting_key] = value
        success = AutoMattyConfig.save_config(config)
        
        if success:
            desc = setting_config.get("description", setting_key)
            unreal.log(f"✅ {desc}: {value}")
        
        return success
    
    @staticmethod
    def validate_and_create_path(path):
        """Validate UE path and create folder"""
        if not path.startswith("/Game/"):
            unreal.log_warning(f"⚠️ Path should start with /Game/: {path}")
            return False
        
        try:
            unreal.EditorAssetLibrary.make_directory(path)
            unreal.log(f"✅ Ensured path exists: {path}")
            return True
        except Exception as e:
            unreal.log_error(f"❌ Failed to create path {path}: {str(e)}")
            return False

# ========================================
# LEGACY COMPATIBILITY METHODS
# ========================================

# Keep old method names for backward compatibility
AutoMattyConfig.get_custom_material_path = lambda: AutoMattyConfig.get_setting("material_path")
AutoMattyConfig.get_custom_texture_path = lambda: AutoMattyConfig.get_setting("texture_path") 
AutoMattyConfig.get_custom_material_prefix = lambda: AutoMattyConfig.get_setting("material_prefix")
AutoMattyConfig.set_custom_material_path = lambda x: AutoMattyConfig.set_setting("material_path", x)
AutoMattyConfig.set_custom_texture_path = lambda x: AutoMattyConfig.set_setting("texture_path", x)
AutoMattyConfig.set_custom_material_prefix = lambda x: AutoMattyConfig.set_setting("material_prefix", x)

# Export texture patterns for other modules
AutoMattyConfig.TEXTURE_PATTERNS = TEXTURE_PATTERNS

# ========================================
# WIDGET INTERACTION
# ========================================

class WidgetManager:
    """Centralized widget interaction"""
    
    @staticmethod
    def get_widget():
        """Get widget instance"""
        try:
            subsystem = unreal.get_editor_subsystem(unreal.EditorUtilitySubsystem)
            blueprint = unreal.EditorAssetLibrary.load_asset("/AutoMatty/EUW_AutoMatty")
            return subsystem.find_utility_widget_from_blueprint(blueprint) if blueprint else None
        except:
            return None
    
    @staticmethod
    def get_checkboxes():
        """Get all checkbox states"""
        widget = WidgetManager.get_widget()
        if not widget:
            return {key: False for key in FEATURE_CHECKBOXES.keys()}
        
        checkboxes = {}
        for feature_key, widget_property in FEATURE_CHECKBOXES.items():
            try:
                checkbox = widget.get_editor_property(widget_property)
                checkboxes[feature_key] = checkbox.is_checked() if checkbox else False
            except:
                checkboxes[feature_key] = False
        
        return checkboxes
    
    @staticmethod
    def load_settings_to_widget():
        """Load all settings into widget"""
        widget = WidgetManager.get_widget()
        if not widget:
            unreal.log_warning("⚠️ No widget found")
            return False
        
        success_count = 0
        for setting_key, config in SETTINGS_CONFIG.items():
            try:
                widget_property = config.get("widget_property")
                if widget_property:
                    input_widget = widget.get_editor_property(widget_property)
                    if input_widget:
                        value = AutoMattyConfig.get_setting(setting_key)
                        input_widget.set_text(str(value))
                        success_count += 1
            except Exception as e:
                unreal.log_warning(f"⚠️ Failed to load {setting_key}: {e}")
        
        unreal.log(f"📥 Loaded {success_count}/{len(SETTINGS_CONFIG)} settings")
        return success_count > 0
    
    @staticmethod
    def save_settings_from_widget():
        """Save all settings from widget"""
        widget = WidgetManager.get_widget()
        if not widget:
            unreal.log_error("❌ No widget found")
            return False
        
        success_count = 0
        for setting_key, config in SETTINGS_CONFIG.items():
            try:
                widget_property = config.get("widget_property")
                if widget_property:
                    input_widget = widget.get_editor_property(widget_property)
                    if input_widget:
                        value = str(input_widget.get_text()).strip()
                        if value:  # Only save non-empty values
                            if AutoMattyConfig.set_setting(setting_key, value):
                                success_count += 1
            except Exception as e:
                unreal.log_warning(f"⚠️ Failed to save {setting_key}: {e}")
        
        unreal.log(f"💾 Saved {success_count} settings")
        return success_count > 0

# ========================================
# BUTTON ACTION SYSTEM  
# ========================================

class ButtonActionManager:
    """Unified button action system"""
    
    @staticmethod
    def execute_action(action_key):
        """Execute any button action by key"""
        action_config = BUTTON_ACTIONS.get(action_key)
        if not action_config:
            unreal.log_error(f"❌ Unknown action: {action_key}")
            return False
        
        unreal.log(action_config["description"])
        
        try:
            # Import and reload module
            import importlib
            module_name = action_config["module"]
            module = importlib.import_module(module_name)
            importlib.reload(module)
            
            # Get features if needed
            kwargs = {}
            if action_config.get("get_features"):
                kwargs = WidgetManager.get_checkboxes()
            
            # Execute the action
            result = None
            if "class" in action_config:
                # Class method approach
                builder_class = getattr(module, action_config["class"])
                builder = builder_class()
                method = getattr(builder, action_config["method"])
                result = method(**kwargs)
            else:
                # Function approach  
                func = getattr(module, action_config["function"])
                result = func(**kwargs)
            
            # Log success
            if result:
                success_msg = action_config["success_msg"]
                if hasattr(result, 'get_name'):
                    success_msg += f": {result.get_name()}"
                unreal.log(success_msg)
                
                # Log features if applicable
                if kwargs:
                    features = [k.replace('use_', '') for k, v in kwargs.items() if v]
                    if features:
                        unreal.log(f"💡 Features: {', '.join(features)}")
            else:
                unreal.log("⚠️ Action completed but no result returned")
            
            return True
            
        except Exception as e:
            unreal.log_error(f"❌ Action failed: {e}")
            return False

# ========================================
# MATERIAL EDITOR INTEGRATION
# ========================================

def ensure_unreal_qt():
    """Auto-install unreal_qt if missing"""
    try:
        import unreal_qt
        return True
    except ImportError:
        unreal.log("📦 Installing unreal-qt dependency...")
        
        import subprocess
        python_exe = sys.executable
        
        try:
            result = subprocess.run([
                python_exe, "-m", "pip", "install", "unreal-qt"
            ], capture_output=True, text=True, check=True)
            
            unreal.log("✅ unreal-qt installed successfully!")
            return True
            
        except subprocess.CalledProcessError as e:
            unreal.log_error(f"❌ Failed to install unreal-qt: {e}")
            return False

def show_material_editor():
    """Show material editor with dependency handling"""
    try:
        if not ensure_unreal_qt():
            return False
        
        import unreal_qt
        unreal_qt.setup()
        
        import automatty_material_instance_editor
        import importlib
        importlib.reload(automatty_material_instance_editor)
        
        automatty_material_instance_editor.show_editor_for_selection()
        return True
        
    except Exception as e:
        unreal.log_error(f"❌ Material editor failed: {e}")
        return False

# ========================================
# MENU SYSTEM
# ========================================

@unreal.uclass()
class AutoMattyMenuScript(unreal.ToolMenuEntryScript):
    """Material Editor menu entry"""
    
    @unreal.ufunction(override=True)
    def execute(self, context):
        show_material_editor()

@unreal.uclass()  
class AutoMattyWidgetScript(unreal.ToolMenuEntryScript):
    """Main widget menu entry"""
    
    @unreal.ufunction(override=True)
    def execute(self, context):
        try:
            subsystem = unreal.get_editor_subsystem(unreal.EditorUtilitySubsystem)
            blueprint = unreal.EditorAssetLibrary.load_asset("/AutoMatty/EUW_AutoMatty")
            if blueprint:
                widget = subsystem.spawn_and_register_tab(blueprint)
                if widget:
                    unreal.log("🎯 AutoMatty widget opened!")
                else:
                    unreal.log_error("❌ Failed to spawn widget")
        except Exception as e:
            unreal.log_error(f"❌ Widget failed: {e}")

class MenuManager:
    """Menu registration management"""
    
    _menu_script = None
    _widget_script = None
    
    @staticmethod
    def register_menus():
        """Register both menu entries"""
        try:
            menus = unreal.ToolMenus.get()
            
            # Widget entry
            MenuManager._widget_script = AutoMattyWidgetScript()
            MenuManager._widget_script.init_entry(
                owner_name="AutoMatty",
                menu="LevelEditor.MainMenu.Tools",
                section="LevelEditorModules", 
                name="AutoMattyWidget",
                label="AutoMatty",
                tool_tip="Open AutoMatty main widget"
            )
            MenuManager._widget_script.register_menu_entry()
            
            # Editor entry
            MenuManager._menu_script = AutoMattyMenuScript()
            MenuManager._menu_script.init_entry(
                owner_name="AutoMatty",
                menu="LevelEditor.MainMenu.Tools",
                section="LevelEditorModules",
                name="AutoMattyMaterialEditor", 
                label="AutoMatty Material Editor",
                tool_tip="Open AutoMatty Material Instance Editor"
            )
            MenuManager._menu_script.register_menu_entry()
            
            menus.refresh_all_widgets()
            unreal.log("✅ AutoMatty menus registered!")
            return True
            
        except Exception as e:
            unreal.log_error(f"❌ Menu registration failed: {e}")
            return False
    
    @staticmethod
    def unregister_menus():
        """Unregister menu entries"""
        try:
            menus = unreal.ToolMenus.get()
            menus.unregister_owner_by_name("AutoMatty")
            menus.refresh_all_widgets()
            MenuManager._menu_script = None
            MenuManager._widget_script = None
            unreal.log("🗑️ AutoMatty menus unregistered")
            return True
        except Exception as e:
            unreal.log_error(f"❌ Menu unregistration failed: {e}")
            return False

# ========================================
# PUBLIC API FUNCTIONS (for widget buttons)
# ========================================

# Settings functions
def load_current_settings():
    """Load settings into widget"""
    return WidgetManager.load_settings_to_widget()

def apply_all_settings():
    """Save all settings from widget"""
    return WidgetManager.save_settings_from_widget()

# Material creation functions  
def create_orm_material():
    """Create ORM material"""
    return ButtonActionManager.execute_action("create_orm")

def create_split_material():
    """Create Split material"""
    return ButtonActionManager.execute_action("create_split")

def create_environment_material():
    """Create Environment material"""  
    return ButtonActionManager.execute_action("create_environment")

def create_material_instance():
    """Create material instance"""
    return ButtonActionManager.execute_action("create_instance")

def repath_material_instances():
    """Repath material instances"""
    return ButtonActionManager.execute_action("repath_instances")

# Legacy UI functions (for backward compatibility)
def ui_get_current_material_path():
    return AutoMattyConfig.get_setting("material_path")

def ui_set_custom_material_path(path):
    clean_path = path.strip()
    if clean_path.startswith("/All/Game/"):
        clean_path = clean_path.replace("/All/Game/", "/Game/", 1)
    elif not clean_path.startswith("/Game/") and clean_path:
        clean_path = f"/Game/{clean_path.lstrip('/')}"
    
    if clean_path and AutoMattyConfig.validate_and_create_path(clean_path):
        return AutoMattyConfig.set_setting("material_path", clean_path)
    return AutoMattyConfig.set_setting("material_path", "")

def ui_get_current_texture_path():
    return AutoMattyConfig.get_setting("texture_path")

def ui_set_custom_texture_path(path):
    clean_path = path.strip()
    if clean_path.startswith("/All/Game/"):
        clean_path = clean_path.replace("/All/Game/", "/Game/", 1) 
    elif not clean_path.startswith("/Game/") and clean_path:
        clean_path = f"/Game/{clean_path.lstrip('/')}"
    
    if clean_path and AutoMattyConfig.validate_and_create_path(clean_path):
        return AutoMattyConfig.set_setting("texture_path", clean_path)
    return AutoMattyConfig.set_setting("texture_path", "")

def ui_get_current_material_prefix():
    return AutoMattyConfig.get_setting("material_prefix")

def ui_set_custom_material_prefix(prefix):
    return AutoMattyConfig.set_setting("material_prefix", prefix.strip())

def ui_get_current_hotkey():
    return AutoMattyConfig.get_setting("hotkey")

def ui_set_hotkey(hotkey):
    return AutoMattyConfig.set_setting("hotkey", hotkey.strip().upper())

# ADD THESE FUNCTIONS TO automatty_config.py

# ========================================
# DIRECT UI TEXT HANDLING - NO FORMAT TEXT NODE NEEDED
# ========================================

def handle_material_path_changed(text_input):
    """Handle material path text change directly from EUW OnTextCommitted"""
    clean_path = str(text_input).strip()
    
    # Clean up common UE path issues
    if clean_path.startswith("/All/Game/"):
        clean_path = clean_path.replace("/All/Game/", "/Game/", 1)
    elif not clean_path.startswith("/Game/") and clean_path:
        clean_path = f"/Game/{clean_path.lstrip('/')}"
    
    # Validate and save
    if clean_path and AutoMattyConfig.validate_and_create_path(clean_path):
        AutoMattyConfig.set_setting("material_path", clean_path)
        unreal.log(f"✅ Material path updated: {clean_path}")
    elif clean_path:
        unreal.log_error(f"❌ Invalid material path: {clean_path}")
    
    return clean_path

def handle_texture_path_changed(text_input):
    """Handle texture path text change directly from EUW OnTextCommitted"""
    clean_path = str(text_input).strip()
    
    # Clean up common UE path issues
    if clean_path.startswith("/All/Game/"):
        clean_path = clean_path.replace("/All/Game/", "/Game/", 1)
    elif not clean_path.startswith("/Game/") and clean_path:
        clean_path = f"/Game/{clean_path.lstrip('/')}"
    
    # Validate and save
    if clean_path and AutoMattyConfig.validate_and_create_path(clean_path):
        AutoMattyConfig.set_setting("texture_path", clean_path)
        unreal.log(f"✅ Texture path updated: {clean_path}")
    elif clean_path:
        unreal.log_error(f"❌ Invalid texture path: {clean_path}")
    
    return clean_path

def handle_material_prefix_changed(text_input):
    """Handle material prefix text change directly from EUW OnTextCommitted"""
    clean_prefix = str(text_input).strip()
    
    if clean_prefix:
        AutoMattyConfig.set_setting("material_prefix", clean_prefix)
        unreal.log(f"✅ Material prefix updated: {clean_prefix}")
    
    return clean_prefix

def force_load_ui_settings():
    """Force load all settings into UI - call this when widget opens"""
    widget = WidgetManager.get_widget()
    if not widget:
        unreal.log_error("❌ No widget found for loading settings")
        return False
    
    success_count = 0
   # ADD THESE FUNCTIONS TO automatty_config.py

# ========================================
# DIRECT UI TEXT HANDLING - NO FORMAT TEXT NODE NEEDED
# ========================================

def handle_material_path_changed():
    """Handle material path text change - reads directly from widget"""
    widget = WidgetManager.get_widget()
    if not widget:
        return
    
    # Read text directly from the widget input field
    input_field = widget.get_editor_property("MaterialPathInput")
    if not input_field:
        return
        
    clean_path = str(input_field.get_text()).strip()
    
    # Clean up common UE path issues
    if clean_path.startswith("/All/Game/"):
        clean_path = clean_path.replace("/All/Game/", "/Game/", 1)
    elif not clean_path.startswith("/Game/") and clean_path:
        clean_path = f"/Game/{clean_path.lstrip('/')}"
    
    # Validate and save
    if clean_path and AutoMattyConfig.validate_and_create_path(clean_path):
        AutoMattyConfig.set_setting("material_path", clean_path)
        unreal.log(f"✅ Material path updated: {clean_path}")
    elif clean_path:
        unreal.log_error(f"❌ Invalid material path: {clean_path}")
    
    return clean_path

def handle_texture_path_changed():
    """Handle texture path text change - reads directly from widget"""
    widget = WidgetManager.get_widget()
    if not widget:
        return
    
    # Read text directly from the widget input field
    input_field = widget.get_editor_property("TexturePathInput")
    if not input_field:
        return
        
    clean_path = str(input_field.get_text()).strip()
    
    # Clean up common UE path issues
    if clean_path.startswith("/All/Game/"):
        clean_path = clean_path.replace("/All/Game/", "/Game/", 1)
    elif not clean_path.startswith("/Game/") and clean_path:
        clean_path = f"/Game/{clean_path.lstrip('/')}"
    
    # Validate and save
    if clean_path and AutoMattyConfig.validate_and_create_path(clean_path):
        AutoMattyConfig.set_setting("texture_path", clean_path)
        unreal.log(f"✅ Texture path updated: {clean_path}")
    elif clean_path:
        unreal.log_error(f"❌ Invalid texture path: {clean_path}")
    
    return clean_path

def handle_material_prefix_changed():
    """Handle material prefix text change - reads directly from widget"""
    widget = WidgetManager.get_widget()
    if not widget:
        return
    
    # Read text directly from the widget input field  
    input_field = widget.get_editor_property("MaterialPrefixInput")
    if not input_field:
        return
        
    clean_prefix = str(input_field.get_text()).strip()
    
    if clean_prefix:
        AutoMattyConfig.set_setting("material_prefix", clean_prefix)
        unreal.log(f"✅ Material prefix updated: {clean_prefix}")
    
    return clean_prefix

def force_load_ui_settings():
    """Force load all settings into UI - call this when widget opens"""
    widget = WidgetManager.get_widget()
    if not widget:
        unreal.log_error("❌ No widget found for loading settings")
        return False
    
    success_count = 0
    
    # Material Path
    try:
        material_path = AutoMattyConfig.get_setting("material_path")
        material_input = widget.get_editor_property("MaterialPathInput")
        if material_input and material_path:
            material_input.set_text(material_path)
            success_count += 1
            unreal.log(f"📥 Loaded material path: {material_path}")
    except Exception as e:
        unreal.log_warning(f"⚠️ Failed to load material path: {e}")
    
    # Texture Path  
    try:
        texture_path = AutoMattyConfig.get_setting("texture_path")
        texture_input = widget.get_editor_property("TexturePathInput")
        if texture_input and texture_path:
            texture_input.set_text(texture_path)
            success_count += 1
            unreal.log(f"📥 Loaded texture path: {texture_path}")
    except Exception as e:
        unreal.log_warning(f"⚠️ Failed to load texture path: {e}")
    
    # Material Prefix
    try:
        material_prefix = AutoMattyConfig.get_setting("material_prefix")
        prefix_input = widget.get_editor_property("MaterialPrefixInput")
        if prefix_input and material_prefix:
            prefix_input.set_text(material_prefix)
            success_count += 1
            unreal.log(f"📥 Loaded material prefix: {material_prefix}")
    except Exception as e:
        unreal.log_warning(f"⚠️ Failed to load material prefix: {e}")
    
    unreal.log(f"🎯 Force loaded {success_count} UI settings")
    return success_count > 0

# ========================================
# WIDGET STARTUP FUNCTION
# ========================================

def initialize_widget_on_startup():
    """Call this when the widget first opens to load all settings"""
    try:
        # Small delay to ensure widget is fully loaded
        import time
        time.sleep(0.1)
        
        # Force load all settings
        force_load_ui_settings()
        
        unreal.log("🚀 AutoMatty widget initialized with saved settings")
        return True
        
    except Exception as e:
        unreal.log_error(f"❌ Widget initialization failed: {e}")
        return False

# Utility classes for other modules
class AutoMattyUtils:
    """Utility functions"""
    
    @staticmethod
    def is_substrate_enabled():
        try:
            temp_mat = unreal.Material()
            lib = unreal.MaterialEditingLibrary
            temp_node = lib.create_material_expression(
                temp_mat, unreal.MaterialExpressionSubstrateSlabBSDF, 0, 0
            )
            return temp_node is not None
        except:
            return True
    
    @staticmethod 
    def get_next_asset_name(base_name, folder, prefix="v", pad=3):
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
        for path in unreal.EditorAssetLibrary.list_assets("/Engine", recursive=True, include_folder=False):
            if path.lower().endswith("defaultnormal"):
                return unreal.EditorAssetLibrary.load_asset(path)
        return None
    
    @staticmethod
    def extract_material_base_name(textures):
        if not textures:
            return "Material"
        
        first_texture = textures[0].get_name()
        base_name = first_texture
        
        # Remove common suffixes
        base_name = re.sub(r'\.(jpg|png|tga|exr|hdr|tiff)$', '', base_name, flags=re.IGNORECASE)
        base_name = re.sub(r'_(?:10\d{2}|<udim>)', '', base_name, flags=re.IGNORECASE)
        base_name = re.sub(r'_(?:srgb|linear|rec709|aces)', '', base_name, flags=re.IGNORECASE)
        base_name = re.sub(r'_(?:\d+k|\d{3,4})$', '', base_name, flags=re.IGNORECASE)
        
        texture_types = [
            'color', 'colour', 'albedo', 'diffuse', 'basecolor', 'base_color',
            'normal', 'norm', 'nrm', 'bump', 'roughness', 'rough', 'gloss',
            'metallic', 'metalness', 'metal', 'specular', 'spec',
            'occlusion', 'ao', 'ambient_occlusion', 'orm', 'rma', 'mas',
            'height', 'displacement', 'disp', 'emission', 'emissive', 'glow',
            'blend', 'mask', 'mix'
        ]
        
        type_pattern = r'_(?:' + '|'.join(texture_types) + r')(?:_.*)?$'
        base_name = re.sub(type_pattern, '', base_name, flags=re.IGNORECASE)
        base_name = re.sub(r'_+$', '', base_name)
        base_name = re.sub(r'_v?\d+$', '', base_name)
        
        if not base_name or len(base_name) < 2:
            fallback = re.split(r'[_\-\.]', first_texture)[0]
            base_name = fallback if fallback else "Material"
        
        if not re.match(r'^[a-zA-Z]', base_name):
            base_name = f"Mat_{base_name}"
        
        return base_name
    
    @staticmethod
    def generate_smart_instance_name(base_material, textures, custom_path=None):
        material_base = AutoMattyUtils.extract_material_base_name(textures)
        instance_name = f"M_{material_base}_Inst"
        
        folder = custom_path or AutoMattyConfig.get_setting("material_path")
        
        full_path = f"{folder}/{instance_name}"
        if unreal.EditorAssetLibrary.does_asset_exist(full_path):
            instance_name = AutoMattyUtils.get_next_asset_name(
                f"M_{material_base}_Inst", folder
            )
        
        return instance_name, folder

# Auto-setup
MenuManager.register_menus()
