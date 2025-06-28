import unreal
import re
import os

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
    
    # Texture matching patterns
    TEXTURE_PATTERNS = {
        "Color": re.compile(r"(colou?r|albedo|base[-_]?color|diffuse)", re.IGNORECASE),
        "Normal": re.compile(r"normal", re.IGNORECASE),
        "Occlusion": re.compile(r"(?:^|[_\W])(?:ao|occlusion)(?:$|[_\W])", re.IGNORECASE),
        "Roughness": re.compile(r"roughness", re.IGNORECASE),
        "Metallic": re.compile(r"metal(?:lic|ness)", re.IGNORECASE),
        "ORM": re.compile(r"(?:^|[_\W])orm(?:$|[_\W])|occlusion[-_]?roughness[-_]?metalness", re.IGNORECASE),
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
            import os
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
            import os
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
            import os
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
        import os
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
    """Utility functions for AutoMatty with enhanced smart naming"""
    
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
    def match_textures_to_params(textures, patterns=None):
        """Match texture list to material parameters"""
        if patterns is None:
            patterns = AutoMattyConfig.TEXTURE_PATTERNS
        
        found = {}
        for tex in textures:
            name = tex.get_name().lower()
            for param, pattern in patterns.items():
                if param not in found and pattern.search(name):
                    found[param] = tex
                    unreal.log(f"Matched '{tex.get_name()}' -> {param}")
                    break
        
        return found
    
    @staticmethod
    def extract_material_base_name(textures):
        """
        Extract base material name from texture list
        Examples:
        - ChrHead_color_1001_sRGB.jpg -> ChrHead
        - Wood_Planks_Normal.tga -> Wood_Planks  
        - MetalPanel_ORM_2K.exr -> MetalPanel
        """
        
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
        
        # Remove texture type suffixes (color, normal, orm, etc)
        texture_types = [
            'color', 'colour', 'albedo', 'diffuse', 'basecolor', 'base_color',
            'normal', 'norm', 'nrm', 'bump',
            'roughness', 'rough', 'gloss',
            'metallic', 'metalness', 'metal',
            'specular', 'spec',
            'occlusion', 'ao', 'ambient_occlusion',
            'orm', 'rma', 'mas',  # packed maps
            'height', 'displacement', 'disp',
            'emission', 'emissive', 'glow'
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
        """
        Generate smart instance name based on textures
        Returns: (instance_name, full_path)
        """
        
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

# UI Integration functions (call these from your Editor Utility Widget)
def ui_set_custom_material_path(path_string):
    """Called from UI when user sets custom material path"""
    if not path_string.strip():
        unreal.log("📁 Using default material path")
        AutoMattyConfig.set_custom_material_path("")
        return True
    
    # Clean up the path
    clean_path = path_string.strip()
    if not clean_path.startswith("/Game/"):
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
    
    # Clean up the path
    clean_path = path_string.strip()
    if not clean_path.startswith("/Game/"):
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

# Test function to validate naming
def test_naming_extraction():
    """Test the naming extraction with common patterns"""
    test_cases = [
        "ChrHead_color_1001_sRGB",
        "Wood_Planks_Normal_2K", 
        "MetalPanel_ORM_4K",
        "Fabric_Roughness_Linear",
        "Stone_Wall_Albedo_<udim>",
        "ComplexMaterial_BaseColor_v002_1001_sRGB",
        "SimpleRock_Color",
        "T_Ground_Mud_D"  # UE convention
    ]
    
    expected = [
        "ChrHead",
        "Wood_Planks", 
        "MetalPanel",
        "Fabric",
        "Stone_Wall",
        "ComplexMaterial",
        "SimpleRock",
        "Ground_Mud"
    ]
    
    for i, test in enumerate(test_cases):
        # Mock texture object
        class MockTexture:
            def __init__(self, name):
                self._name = name
            def get_name(self):
                return self._name
        
        result = AutoMattyUtils.extract_material_base_name([MockTexture(test)])
        print(f"'{test}' -> '{result}' (expected: '{expected[i]}')")

if __name__ == "__main__":
    test_naming_extraction()