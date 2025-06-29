"""
AutoMatty Material Instance Creator - Smart material instance creation with universal plugin support
"""
import unreal

# Setup AutoMatty imports
try:
    from automatty_utils import setup_automatty_imports
    if not setup_automatty_imports():
        raise ImportError("Failed to setup AutoMatty imports")
    from automatty_config import AutoMattyConfig, AutoMattyUtils
except ImportError as e:
    unreal.log_error(f"❌ AutoMatty import failed: {e}")
    # Don't continue if imports fail
    raise

def create_material_instance_smart():
    """
    Enhanced material instance creator with smart naming and custom paths
    """
    
    # 1) Validate selected material
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    materials = [asset for asset in selected_assets if isinstance(asset, unreal.Material)]
    
    if len(materials) != 1:
        unreal.log_error("❌ Select exactly one Material asset.")
        return
    
    base_mat = materials[0]
    unreal.log(f"🔧 Base material: {base_mat.get_name()}")

    # 2) Get custom material path from UI settings
    material_path = AutoMattyConfig.get_custom_material_path()
    texture_import_path = AutoMattyConfig.get_custom_texture_path()

    unreal.log(f"📁 Using material path: {material_path}")
    
    # 3) Import textures with dialog
    atools = unreal.AssetToolsHelpers.get_asset_tools()
    imported = atools.import_assets_with_dialog(texture_import_path)
    if not imported:
        unreal.log("⚠️ No assets imported. Aborting.")
        return

    # 4) Filter to just textures
    textures = [obj for obj in imported if isinstance(obj, unreal.Texture2D)]
    if not textures:
        unreal.log_warning("⚠️ No textures imported.")
        return

    unreal.log(f"🎯 Found {len(textures)} textures")

    # 5) Use smart naming to generate instance name
    instance_name, target_folder = AutoMattyUtils.generate_smart_instance_name(
        base_mat, textures, material_path
    )
    
    unreal.log(f"🧠 Smart instance name: {instance_name}")

    # 6) Use config utility to match textures
    matched_textures = AutoMattyUtils.match_textures_to_params(textures)
    
    if not matched_textures:
        unreal.log_warning("⚠️ No matching textures found for material parameters.")
        return

    # 7) Determine workflow
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

    # 8) Create the Material Instance with smart naming
    mic_factory = unreal.MaterialInstanceConstantFactoryNew()
    instance = atools.create_asset(
        instance_name, target_folder,
        unreal.MaterialInstanceConstant, mic_factory
    )
    unreal.MaterialEditingLibrary.set_material_instance_parent(instance, base_mat)
    unreal.log(f"🎉 Created smart instance: {instance.get_name()}")

    # 9) Apply matched textures
    applied_count = 0
    for param in to_set:
        texture = matched_textures.get(param)
        if texture:
            try:
                unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
                    instance, param, texture
                )
                unreal.log(f"✅ Set '{param}' → {texture.get_name()}")
                applied_count += 1
            except Exception as e:
                unreal.log_warning(f"⚠️ Failed to set {param}: {str(e)}")

    # 10) Save it
    unreal.EditorAssetLibrary.save_asset(instance.get_path_name())
    unreal.log(f"💾 Saved instance at {instance.get_path_name()}")
    unreal.log(f"🏆 Successfully applied {applied_count} textures to {instance.get_name()}")
    
    return instance

def create_material_instance_with_browser():
    """
    Alternative version using content browser selection instead of import
    """
    
    # Get selected assets from content browser
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    
    # Separate materials and textures
    materials = [asset for asset in selected_assets if isinstance(asset, unreal.Material)]
    textures = [asset for asset in selected_assets if isinstance(asset, unreal.Texture2D)]
    
    # Validate selection
    if len(materials) != 1:
        unreal.log_error("❌ Select exactly one Material asset")
        return
    
    if not textures:
        unreal.log_error("❌ Select some textures too, genius")
        return
    
    base_mat = materials[0]
    unreal.log(f"🔧 Base material: {base_mat.get_name()}")
    unreal.log(f"🎯 Found {len(textures)} selected textures")
    
    # Get custom path
    material_path = AutoMattyConfig.get_custom_material_path()
    
    # Generate smart instance name
    instance_name, target_folder = AutoMattyUtils.generate_smart_instance_name(
        base_mat, textures, material_path
    )
    
    # Match and apply textures (same logic as above)
    matched_textures = AutoMattyUtils.match_textures_to_params(textures)
    
    if not matched_textures:
        unreal.log_warning("⚠️ No matching textures found")
        return
    
    # Create instance
    atools = unreal.AssetToolsHelpers.get_asset_tools()
    mic_factory = unreal.MaterialInstanceConstantFactoryNew()
    instance = atools.create_asset(
        instance_name, target_folder,
        unreal.MaterialInstanceConstant, mic_factory
    )
    unreal.MaterialEditingLibrary.set_material_instance_parent(instance, base_mat)
    
    # Apply textures
    applied_count = 0
    for param, texture in matched_textures.items():
        try:
            unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
                instance, param, texture
            )
            unreal.log(f"✅ Set '{param}' → {texture.get_name()}")
            applied_count += 1
        except Exception as e:
            unreal.log_warning(f"⚠️ Failed to set {param}: {str(e)}")
    
    # Save
    unreal.EditorAssetLibrary.save_asset(instance.get_path_name())
    unreal.log(f"🏆 Created {instance.get_name()} with {applied_count} textures")
    
    return instance

def create_material_instance_from_recent():
    """
    Create instance from recently imported textures (good for drag-drop workflow)
    """
    
    # Get selected material
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    materials = [asset for asset in selected_assets if isinstance(asset, unreal.Material)]
    
    if len(materials) != 1:
        unreal.log_error("❌ Select exactly one Material asset")
        return
    
    base_mat = materials[0]
    
    # Find recently imported textures in the custom material path
    material_path = AutoMattyConfig.get_custom_material_path()
    
    # Get all textures in the material path
    asset_paths = unreal.EditorAssetLibrary.list_assets(material_path, recursive=False)
    textures = []
    
    for asset_path in asset_paths:
        asset = unreal.EditorAssetLibrary.load_asset(asset_path)
        if isinstance(asset, unreal.Texture2D):
            textures.append(asset)
    
    if not textures:
        unreal.log_error(f"❌ No textures found in {material_path}")
        return
    
    unreal.log(f"🔍 Found {len(textures)} textures in material folder")
    
    # Use the same logic as the main function
    instance_name, target_folder = AutoMattyUtils.generate_smart_instance_name(
        base_mat, textures, material_path
    )
    
    matched_textures = AutoMattyUtils.match_textures_to_params(textures)
    
    if not matched_textures:
        unreal.log_warning("⚠️ No matching textures found")
        return
    
    # Create and populate instance
    atools = unreal.AssetToolsHelpers.get_asset_tools()
    mic_factory = unreal.MaterialInstanceConstantFactoryNew()
    instance = atools.create_asset(
        instance_name, target_folder,
        unreal.MaterialInstanceConstant, mic_factory
    )
    unreal.MaterialEditingLibrary.set_material_instance_parent(instance, base_mat)
    
    # Apply textures
    applied_count = 0
    for param, texture in matched_textures.items():
        try:
            unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
                instance, param, texture
            )
            unreal.log(f"✅ Set '{param}' → {texture.get_name()}")
            applied_count += 1
        except Exception as e:
            unreal.log_warning(f"⚠️ Failed to set {param}: {str(e)}")
    
    unreal.EditorAssetLibrary.save_asset(instance.get_path_name())
    unreal.log(f"🏆 Created {instance.get_name()} with {applied_count} textures")
    
    return instance

# Legacy compatibility function
def create_material_instance_with_path():
    """Legacy function - redirects to smart version"""
    unreal.log_warning("⚠️ Using legacy function - consider updating to create_material_instance_smart()")
    return create_material_instance_smart()

# Execute the main function when called directly
if __name__ == "__main__":
    create_material_instance_smart()