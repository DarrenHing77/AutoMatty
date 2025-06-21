import unreal
import os

def create_material_instance_smart():
    """
    Enhanced material instance creator using modular config
    """
    
    # Set up imports after path configuration
    import sys
    proj_dir = unreal.Paths.project_dir()
    scripts_path = os.path.join(proj_dir, "Plugins", "AutoMatty", "Scripts")
    if scripts_path not in sys.path:
        sys.path.append(scripts_path)
    
    from automatty_config import AutoMattyConfig, AutoMattyUtils
    
    # 1) Validate selected material
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    materials = [asset for asset in selected_assets if isinstance(asset, unreal.Material)]
    
    if len(materials) != 1:
        unreal.log_error("❌ Select exactly one Material asset.")
        return
    
    base_mat = materials[0]
    unreal.log(f"🔧 Base material: {base_mat.get_name()}")

    # 2) Use config for paths
    texture_path = AutoMattyConfig.DEFAULT_TEXTURE_PATH
    material_path = AutoMattyConfig.DEFAULT_MATERIAL_PATH
    
    # 3) Import textures with dialog
    atools = unreal.AssetToolsHelpers.get_asset_tools()
    imported = atools.import_assets_with_dialog(texture_path)
    if not imported:
        unreal.log("⚠️ No assets imported. Aborting.")
        return

    # 4) Filter to just textures
    textures = [obj for obj in imported if isinstance(obj, unreal.Texture2D)]
    if not textures:
        unreal.log_warning("⚠️ No textures imported.")
        return

    # 5) Use config utility to match textures
    matched_textures = AutoMattyUtils.match_textures_to_params(textures)
    
    if not matched_textures:
        unreal.log_warning("⚠️ No matching textures found for material parameters.")
        return

    # 6) Determine workflow
    split_keys = {"Occlusion", "Roughness", "Metallic"}
    has_split = any(k in matched_textures for k in split_keys)
    has_orm = "ORM" in matched_textures

    if has_split:
        to_set = ["Color", "Normal", "Occlusion", "Roughness", "Metallic"]
        workflow = "split"
    elif has_orm:
        to_set = ["Color", "Normal", "ORM"]
        workflow = "orm"
    else:
        to_set = list(matched_textures.keys())
        workflow = "basic"
    
    unreal.log(f"🎯 Detected workflow: {workflow}")

    # 7) Create the Material Instance with versioning
    inst_name = f"{base_mat.get_name()}_Inst"
    
    # Check if it exists and version if needed
    full_path = f"{material_path}/{inst_name}"
    if unreal.EditorAssetLibrary.does_asset_exist(full_path):
        inst_name = AutoMattyUtils.get_next_asset_name(
            f"{base_mat.get_name()}_Inst", material_path
        )
    
    mic_factory = unreal.MaterialInstanceConstantFactoryNew()
    instance = atools.create_asset(
        inst_name, material_path,
        unreal.MaterialInstanceConstant, mic_factory
    )
    unreal.MaterialEditingLibrary.set_material_instance_parent(instance, base_mat)
    unreal.log(f"🎉 Created instance: {instance.get_name()}")

    # 8) Apply matched textures
    for param in to_set:
        texture = matched_textures.get(param)
        if texture:
            try:
                unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
                    instance, param, texture
                )
                unreal.log(f"✅ Set '{param}' → {texture.get_name()}")
            except Exception as e:
                unreal.log_warning(f"⚠️ Failed to set {param}: {str(e)}")

    # 9) Save it
    unreal.EditorAssetLibrary.save_asset(instance.get_path_name())
    unreal.log(f"💾 Saved instance at {instance.get_path_name()}")

# Execute the function when called directly
if __name__ == "__main__":
    create_material_instance_smart()