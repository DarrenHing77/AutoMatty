# Add this to a new file: Scripts/automatty_repather.py

import unreal
import os
from automatty_config import AutoMattyConfig, AutoMattyUtils

def repath_material_instance_textures():
    """
    Repath textures in selected material instances to new folder
    Perfect for versioning up/down texture sets
    """
    
    # 1) Validate selection
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    instances = [asset for asset in selected_assets if isinstance(asset, unreal.MaterialInstanceConstant)]
    
    if not instances:
        unreal.log_error("❌ Select some material instances, genius")
        return
    
    unreal.log(f"🎯 Found {len(instances)} material instances")
    
    # 2) Prompt for new texture folder
    # This is the tricky part - UE doesn't have great folder picker support
    # Workaround: Use import dialog to let user navigate to folder
    atools = unreal.AssetToolsHelpers.get_asset_tools()
    
    # Fake import to get folder path (user cancels but we get the path)
    unreal.log("📁 Navigate to your new texture folder and cancel the import...")
    
    # Alternative: Hardcode common paths and let user choose
    texture_folders = [
        "/Game/Textures/Materials/v001",
        "/Game/Textures/Materials/v002", 
        "/Game/Textures/Materials/Latest",
        "/Game/Textures/NewSet"
    ]
    
    # For now, let's use a simple approach - user sets target path in config
    target_folder = "/Game/Textures/NewVersion"  # Make this configurable
    
    # 3) Get all textures in target folder
    target_assets = unreal.EditorAssetLibrary.list_assets(target_folder, recursive=False)
    target_textures = []
    
    for asset_path in target_assets:
        asset = unreal.EditorAssetLibrary.load_asset(asset_path)
        if isinstance(asset, unreal.Texture2D):
            target_textures.append(asset)
    
    if not target_textures:
        unreal.log_error(f"❌ No textures found in {target_folder}")
        return
    
    unreal.log(f"🔍 Found {len(target_textures)} textures in target folder")
    
    # 4) For each material instance, remap textures
    for instance in instances:
        unreal.log(f"🔧 Processing {instance.get_name()}...")
        
        # Get current texture parameters
        texture_params = unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_names(instance)
        
        remapped_count = 0
        for param_name in texture_params:
            current_texture = unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value(
                instance, param_name
            )
            
            if current_texture:
                # Find matching texture in target folder
                new_texture = find_matching_texture(current_texture, target_textures)
                
                if new_texture:
                    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
                        instance, param_name, new_texture
                    )
                    unreal.log(f"  ✅ {param_name}: {current_texture.get_name()} → {new_texture.get_name()}")
                    remapped_count += 1
                else:
                    unreal.log_warning(f"  ⚠️ No match found for {param_name}: {current_texture.get_name()}")
        
        if remapped_count > 0:
            unreal.EditorAssetLibrary.save_asset(instance.get_path_name())
            unreal.log(f"💾 Saved {instance.get_name()} with {remapped_count} remapped textures")

def find_matching_texture(current_texture, target_textures):
    """
    Find best matching texture in target folder
    Uses multiple strategies for matching
    """
    current_name = current_texture.get_name().lower()
    
    # Strategy 1: Exact name match
    for tex in target_textures:
        if tex.get_name().lower() == current_name:
            return tex
    
    # Strategy 2: Remove version suffixes and match
    # e.g., "Wood_Color_v001" matches "Wood_Color_v002"
    import re
    clean_current = re.sub(r'_v\d+$', '', current_name)
    
    for tex in target_textures:
        clean_target = re.sub(r'_v\d+$', '', tex.get_name().lower())
        if clean_target == clean_current:
            return tex
    
    # Strategy 3: Fuzzy matching by texture type
    # Extract texture type (Color, Normal, ORM, etc.)
    current_type = extract_texture_type(current_name)
    if current_type:
        base_name = extract_base_name(current_name)
        
        for tex in target_textures:
            target_name = tex.get_name().lower()
            target_type = extract_texture_type(target_name)
            target_base = extract_base_name(target_name)
            
            # Match if same type and similar base name
            if current_type == target_type and base_name in target_base:
                return tex
    
    return None

def extract_texture_type(texture_name):
    """Extract texture type from name (Color, Normal, ORM, etc.)"""
    patterns = AutoMattyConfig.TEXTURE_PATTERNS
    
    for tex_type, pattern in patterns.items():
        if pattern.search(texture_name):
            return tex_type
    return None

def extract_base_name(texture_name):
    """Extract base material name from texture"""
    # Remove common suffixes
    import re
    base = re.sub(r'_(color|normal|orm|rough|metal|ao|occlusion).*$', '', texture_name, flags=re.IGNORECASE)
    base = re.sub(r'_v\d+$', '', base)  # Remove version
    return base

def repath_with_folder_prompt():
    """
    Version with better folder selection
    """
    # Get user to select target folder by having them select any asset in it
    selected = unreal.EditorUtilityLibrary.get_selected_assets()
    
    if not selected:
        unreal.log_error("❌ Select an asset in your target texture folder first")
        return
    
    # Extract folder path from selected asset
    asset_path = selected[0].get_path_name()
    target_folder = '/'.join(asset_path.split('/')[:-1])  # Remove asset name
    
    unreal.log(f"🎯 Using target folder: {target_folder}")
    
    # Now select material instances and run the repath
    unreal.log("Now select your material instances and run this again...")
    # ... rest of repath logic

# Main execution
if __name__ == "__main__":
    repath_material_instance_textures()