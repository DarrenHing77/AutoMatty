import unreal
import re

class AutoMattyConfig:
    """Centralized config for AutoMatty plugin"""
    
    # Default paths - can be overridden
    DEFAULT_MATERIAL_PATH = "/Game/Materials/AutoMatty"
    DEFAULT_TEXTURE_PATH = "/Game/Textures/AutoMatty"
    DEFAULT_FUNCTION_PATH = "/Game/Functions"
    
    # Material function names
    CHEAP_CONTRAST_FUNC = "CheapContrast"
    REMAP_VALUE_FUNC = "RemapValueRange"
    
    # Texture matching patterns
    TEXTURE_PATTERNS = {
        "Color": re.compile(r"(colou?r|albedo|base[-_]?color|diffuse)", re.IGNORECASE),
        "Normal": re.compile(r"normal", re.IGNORECASE),
        "Occlusion": re.compile(r"(?:^|[_\W])(?:ao|occlusion)(?:$|[_\W])", re.IGNORECASE),
        "Roughness": re.compile(r"roughness", re.IGNORECASE),
        "Metallic": re.compile(r"metal(?:lic|ness)", re.IGNORECASE),
        "ORM": re.compile(r"(?:^|[_\W])orm(?:$|[_\W])|occlusion[-_]?roughness[-_]?metalness", re.IGNORECASE),
    }

class AutoMattyUtils:
    """Utility functions for AutoMatty"""
    
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