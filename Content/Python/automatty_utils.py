"""
AutoMatty Utilities - Simplified for UE Plugin Architecture
No path discovery needed - UE handles it automatically!
"""
import unreal
import re
from automatty_config import AutoMattyConfig

# That's it! No complex path discovery needed.
# UE automatically adds Plugin/Content/Python/ to sys.path

def setup_automatty_imports():
    """
    Setup AutoMatty imports - now just a compatibility function
    Returns True (always works with proper plugin structure)
    """
    unreal.log("📁 AutoMatty using UE's automatic Python plugin system")
    return True

def log_plugin_info():
    """Debug function to show plugin installation info"""
    unreal.log("🔌 AutoMatty using UE5 native Python plugin architecture")
    unreal.log("📁 Scripts auto-loaded from Plugin/Content/Python/")

# Basic validation functions
def validate_unreal_path(path):
    """Validate that a path starts with /Game/ or /Engine/"""
    if not path:
        return False
    return path.startswith(("/Game/", "/Engine/"))

def ensure_game_path(path):
    """Ensure path starts with /Game/ prefix"""
    if not path:
        return "/Game/"
    
    path = path.strip()
    if not path.startswith("/Game/"):
        # Remove leading slash if present
        path = path.lstrip("/")
        path = f"/Game/{path}"

    return path


class AutoMattyUtils:
    """Helper utilities used across the plugin"""

    @staticmethod
    def is_substrate_enabled():
        try:
            temp_mat = unreal.Material()
            lib = unreal.MaterialEditingLibrary
            temp_node = lib.create_material_expression(
                temp_mat, unreal.MaterialExpressionSubstrateSlabBSDF, 0, 0
            )
            return temp_node is not None
        except Exception:
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
            if path.lower().endswith("DefaultNormal"):
                return unreal.EditorAssetLibrary.load_asset(path)
        return None

    @staticmethod
    def extract_material_base_name(textures):
        if not textures:
            return "Material"

        first_texture = textures[0].get_name()
        base_name = first_texture

        base_name = re.sub(r"\.(jpg|png|tga|exr|hdr|tiff)$", "", base_name, flags=re.IGNORECASE)
        base_name = re.sub(r"_(?:10\d{2}|<udim>)", "", base_name, flags=re.IGNORECASE)
        base_name = re.sub(r"_(?:srgb|linear|rec709|aces)", "", base_name, flags=re.IGNORECASE)
        base_name = re.sub(r"_(?:\d+k|\d{3,4})$", "", base_name, flags=re.IGNORECASE)

        texture_types = [
            "color", "colour", "albedo", "diffuse", "basecolor", "base_color",
            "normal", "norm", "nrm", "bump", "roughness", "rough", "gloss",
            "metallic", "metalness", "metal", "specular", "spec",
            "occlusion", "ao", "ambient_occlusion", "orm", "rma", "mas",
            "height", "displacement", "disp", "emission", "emissive", "glow",
            "blend", "mask", "mix",
        ]

        type_pattern = r"_(?:" + "|".join(texture_types) + r")(?:_.*)?$"
        base_name = re.sub(type_pattern, "", base_name, flags=re.IGNORECASE)
        base_name = re.sub(r"_+$", "", base_name)
        base_name = re.sub(r"_v?\d+$", "", base_name)

        if not base_name or len(base_name) < 2:
            fallback = re.split(r"[_\-\.]", first_texture)[0]
            base_name = fallback if fallback else "Material"

        if not re.match(r"^[a-zA-Z]", base_name):
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
