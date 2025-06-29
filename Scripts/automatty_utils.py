"""
AutoMatty Utilities - Universal plugin path resolver and basic utilities
This file handles plugin discovery and basic setup - doesn't import other AutoMatty modules
"""
import unreal
import os
import sys

def get_automatty_scripts_path():
    """
    Get AutoMatty scripts path - works for both project and engine plugin installations
    Returns the first valid path found, prioritizing project over engine
    """
    possible_paths = [
        # Project plugins (highest priority)
        os.path.join(unreal.Paths.project_dir(), "Plugins", "AutoMatty", "Scripts"),
        # Engine plugins 
        os.path.join(unreal.Paths.engine_dir(), "Plugins", "AutoMatty", "Scripts"),
        # Alternative engine location (some UE versions)
        os.path.join(unreal.Paths.engine_plugins_dir(), "AutoMatty", "Scripts")
    ]
    
    for path in possible_paths:
        if os.path.exists(path) and os.path.isdir(path):
            return path
    
    # Fallback - log all attempted paths for debugging
    unreal.log_error("❌ AutoMatty scripts not found in any of these locations:")
    for path in possible_paths:
        unreal.log_error(f"   - {path}")
    
    return None

def setup_automatty_imports():
    """
    Setup AutoMatty imports - call this at the start of any script
    Returns True if successful, False if failed
    """
    scripts_path = get_automatty_scripts_path()
    
    if not scripts_path:
        unreal.log_error("❌ Failed to locate AutoMatty scripts directory")
        return False
    
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)  # Insert at beginning for priority
        unreal.log(f"📁 AutoMatty scripts loaded from: {scripts_path}")
    
    return True

def log_plugin_info():
    """Debug function to show plugin installation info"""
    scripts_path = get_automatty_scripts_path()
    
    if scripts_path:
        if "engine" in scripts_path.lower():
            install_type = "Engine Plugin (shared across projects)"
        else:
            install_type = "Project Plugin (this project only)"
        
        unreal.log(f"🔌 AutoMatty detected as: {install_type}")
        unreal.log(f"📁 Scripts location: {scripts_path}")
    else:
        unreal.log_error("❌ AutoMatty plugin not found!")

# Basic validation functions that don't require other AutoMatty imports
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