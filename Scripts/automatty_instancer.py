import unreal
import os
from automatty_config import AutoMattyConfig, AutoMattyUtils

def create_material_instance_smart():
    """
    Enhanced material instance creator that:
    - Uses selected textures if available
    - Handles existing textures properly
    - Supports user path input
    - Checks for conflicts
    """
    
    # 1) Validate selected material
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    materials = [asset for asset in selected_assets if isinstance(asset, unreal.Material)]
    
    if len(materials) != 1:
        unreal.log_error("❌ Select exactly one Material asset.")
        return
    
    base_mat = materials[0]
    unreal.log(f"🔧 Base material: {base_mat.get_name()}")
    
    # 2) Check for already selected textures
    selected_textures = AutoMattyUtils.get_selected_textures()
    
    if selected_textures:
        unreal.log(f"📦 Found {len(selected_textures)} selected textures")
        textures_to_use = selected_textures
        import_needed = False
    else:
        unreal.log("📁 No textures selected - will prompt for import")
        import_needed = True
    
    # 3) Get destination paths (could be enhanced with proper UI)
    texture_path = AutoMattyUtils.get_user_path(
        "Texture destination:", 
        AutoMattyConfig.DEFAULT_TEXTURE_PATH
    )
    
    material_path = AutoMattyUtils.get_user_path(
        "Material instance destination:",
        AutoMattyConfig.DEFAULT_MATERIAL_PATH
    )
    
    # 4) Handle texture import if needed
    if import_needed:
        textures_to_use = handle_texture_import(texture_path)
        if not textures_to_use:
            unreal.log("⚠️ No textures to work with. Aborting.")
            return
    
    # 5) Match textures to parameters
    matched_textures = AutoMattyUtils.match_textures_to_params(textures_to_use)
    
    if not matched_textures:
        unreal.log_warning("⚠️ No matching textures found for material parameters.")
        return
    
    # 6) Determine material workflow
    workflow = determine_workflow(matched_textures)
    unreal.log(f"🎯 Detected workflow: {workflow}")
    
    # 7) Create the material instance
    instance = create_instance(base_mat, material_path)
    if not instance:
        return
    
    # 8) Apply textures to instance
    apply_textures_to_instance(instance, matched_textures, workflow)
    
    # 9) Save and finish
    unreal.EditorAssetLibrary.save_asset(instance.get_path_name())
    unreal.log(f"🎉 Material instance created: {instance.get_name()}")

def handle_texture_import(dest_path):
    """Handle texture importing with conflict resolution"""
    atools = unreal.AssetToolsHelpers.get_asset_tools()
    
    # Import with dialog
    imported = atools.import_assets_with_dialog(dest_path)
    if not imported:
        return []
    
    textures = []
    for asset in imported:
        if isinstance(asset, unreal.Texture2D):
            # Check if this texture already existed
            asset_name = asset.get_name()
            if AutoMattyUtils.asset_exists_in_project(asset_name, dest_path):
                choice = AutoMattyUtils.prompt_user_choice(
                    f"Texture '{asset_name}' already exists. Use existing or reload?",
                    ["Use Existing", "Reload", "Skip"]
                )
                
                if choice == "Use Existing":
                    existing_path = f"{dest_path}/{asset_name}"
                    textures.append(unreal.EditorAssetLibrary.load_asset(existing_path))
                elif choice == "Reload":
                    textures.append(asset)  # Use the newly imported one
                # Skip = don't add to list
            else:
                textures.append(asset)
    
    return textures

def determine_workflow(matched_textures):
    """Determine if we're using ORM packed or split textures"""
    split_keys = {"Occlusion", "Roughness", "Metallic"}
    has_split = any(k in matched_textures for k in split_keys)
    has_orm = "ORM" in matched_textures
    
    if has_split and has_orm:
        # User has both - prefer split for more control
        return "split"
    elif has_split:
        return "split"
    elif has_orm:
        return "orm"
    else:
        return "basic"

def create_instance(base_material, dest_path):
    """Create the material instance"""
    atools = unreal.AssetToolsHelpers.get_asset_tools()
    mic_factory = unreal.MaterialInstanceConstantFactoryNew()
    
    inst_name = f"{base_material.get_name()}_Inst"
    
    # Check for existing instance
    if AutoMattyUtils.asset_exists_in_project(inst_name, dest_path):
        choice = AutoMattyUtils.prompt_user_choice(
            f"Material instance '{inst_name}' already exists. Overwrite?",
            ["Overwrite", "Create New Version", "Cancel"]
        )
        
        if choice == "Cancel":
            return None
        elif choice == "Create New Version":
            inst_name = AutoMattyUtils.get_next_asset_name(
                f"{base_material.get_name()}_Inst", dest_path
            )
    
    # Create the instance
    instance = atools.create_asset(
        inst_name, dest_path, 
        unreal.MaterialInstanceConstant, mic_factory
    )
    
    unreal.MaterialEditingLibrary.set_material_instance_parent(instance, base_material)
    return instance

def apply_textures_to_instance(instance, matched_textures, workflow):
    """Apply matched textures to the material instance"""
    
    # Define parameter sets for different workflows
    if workflow == "split":
        params_to_set = ["Color", "Normal", "Occlusion", "Roughness", "Metallic"]
    elif workflow == "orm":
        params_to_set = ["Color", "Normal", "ORM"]
    else:
        params_to_set = list(matched_textures.keys())
    
    # Apply each texture
    for param in params_to_set:
        texture = matched_textures.get(param)
        if texture:
            try:
                unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
                    instance, param, texture
                )
                unreal.log(f"✅ Set '{param}' → {texture.get_name()}")
            except Exception as e:
                unreal.log_warning(f"⚠️ Failed to set {param}: {str(e)}")

# Execute the function
if __name__ == "__main__":
    create_material_instance_smart()