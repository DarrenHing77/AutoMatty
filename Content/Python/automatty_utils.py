"""
AutoMatty Utilities - Simplified for UE Plugin Architecture
No path discovery needed - UE handles it automatically!
"""
import unreal

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