import unreal
import os

def repath_material_instances():
    """
    Repath textures in selected material instances to new folder
    Uses dialog to select target folder
    """
    import sys
    proj_dir = unreal.Paths.project_dir()
    scripts_path = os.path.join(proj_dir, "Plugins", "AutoMatty", "Scripts")
    if scripts_path not in sys.path:
        sys.path.append(scripts_path)
    
    from automatty_config import AutoMattyConfig, AutoMattyUtils
    
    # 1) Validate selection
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    instances = [asset for asset in selected_assets if isinstance(asset, unreal.MaterialInstanceConstant)]
    
    if not instances:
        unreal.log_error("❌ Select some material instances first")
        return
    
    unreal.log(f"🎯 Found {len(instances)} material instances")
    
    # 2) Get target folder via import dialog
    unreal.log("📁 Navigate to your new texture folder in the import dialog...")
    atools = unreal.AssetToolsHelpers.get_asset_tools()
    imported = atools.import_assets_with_dialog("/Game/Textures")
    
    if not imported:
        unreal.log("⚠️ No target folder selected. Aborting.")
        return
    
    # Extract folder path from imported asset
    first_asset_path = imported[0].get_path_name()
    target_folder = '/'.join(first_asset_path.split('/')[:-1])
    unreal.log(f"🎯 Target folder: {target_folder}")
    
    # 3) Use imported textures directly
    target_textures = [asset for asset in imported if isinstance(asset, unreal.Texture2D)]
    
    if not target_textures:
        unreal.log_error(f"❌ No textures in imported assets")
        return
    
    unreal.log(f"🔍 Found {len(target_textures)} imported textures")
    
    # 4) Remap each instance
    total_remapped = 0
    for instance in instances:
        unreal.log(f"🔧 Processing {instance.get_name()}...")
        
        # Get the parent material
        parent_material = instance.get_editor_property('parent')
        
        if not parent_material:
            unreal.log_warning(f"  ⚠️ No parent material found for {instance.get_name()}")
            continue
        
        # Get texture parameter names from the parent material
        texture_params = unreal.MaterialEditingLibrary.get_texture_parameter_names(parent_material)
        
        remapped_count = 0
        
        for param_name in texture_params:
            current_texture = unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value(instance, param_name)
            
            if current_texture:
                new_texture = find_best_match(current_texture, target_textures)
                
                if new_texture:
                    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(instance, param_name, new_texture)
                    unreal.log(f"  ✅ {param_name}: {current_texture.get_name()} → {new_texture.get_name()}")
                    remapped_count += 1
                else:
                    unreal.log_warning(f"  ⚠️ No match for {param_name}: {current_texture.get_name()}")
        
        if remapped_count > 0:
            unreal.EditorAssetLibrary.save_asset(instance.get_path_name())
            total_remapped += remapped_count
    
    unreal.log(f"🏆 Remapped {total_remapped} textures total")

def find_best_match(current_texture, target_textures):
    """Smart texture matching with multiple strategies"""
    import re
    current_name = current_texture.get_name().lower()
    
    # 1. Exact match
    for tex in target_textures:
        if tex.get_name().lower() == current_name:
            return tex
    
    # 2. Version-agnostic match (remove _v001, _v002, etc.)
    clean_current = re.sub(r'_v\d+$', '', current_name)
    for tex in target_textures:
        clean_target = re.sub(r'_v\d+$', '', tex.get_name().lower())
        if clean_target == clean_current:
            return tex
    
    # 3. Type-based matching (Color → BaseColor, etc.)
    from automatty_config import AutoMattyConfig
    patterns = AutoMattyConfig.TEXTURE_PATTERNS
    
    current_type = None
    for tex_type, pattern in patterns.items():
        if pattern.search(current_name):
            current_type = tex_type
            break
    
    if current_type:
        for tex in target_textures:
            for tex_type, pattern in patterns.items():
                if tex_type == current_type and pattern.search(tex.get_name().lower()):
                    return tex
    
    return None

# Execute
if __name__ == "__main__":
    repath_material_instances()