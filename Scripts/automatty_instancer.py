"""
AutoMatty Material Instance Creator with Height Map Support - Smart material instance creation with universal plugin support
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
    Enhanced material instance creator with smart naming, custom paths, and height map support
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

    # 6) Check if material has height/displacement support (nanite)
    has_height_param = _material_has_height_parameter(base_mat)
    
    # 7) Use config utility to match textures (include height if material supports it)
    matched_textures = AutoMattyUtils.match_textures_to_params(textures, include_height=has_height_param)
    
    if not matched_textures:
        unreal.log_warning("⚠️ No matching textures found for material parameters.")
        return

    # 8) Determine workflow and log height map detection
    split_keys = {"Occlusion", "Roughness", "Metallic"}
    has_split = any(k in matched_textures for k in split_keys)
    has_orm = "ORM" in matched_textures
    has_height = "Height" in matched_textures

    if has_split:
        to_set = ["Color", "Normal", "Occlusion", "Roughness", "Metallic", "Emission"]
        workflow = "split"
    elif has_orm:
        to_set = ["Color", "Normal", "ORM", "Emission"]
        workflow = "orm"
    else:
        to_set = list(matched_textures.keys())
        workflow = "basic"
    
    # Add height if available and material supports it
    if has_height and has_height_param:
        to_set.append("Height")
        unreal.log(f"🏔️ Height map detected and will be applied")
    elif has_height and not has_height_param:
        unreal.log_warning(f"⚠️ Height map found but material doesn't support displacement")
    
    unreal.log(f"🎯 Detected workflow: {workflow}")

    # 9) Create the Material Instance with smart naming
    mic_factory = unreal.MaterialInstanceConstantFactoryNew()
    instance = atools.create_asset(
        instance_name, target_folder,
        unreal.MaterialInstanceConstant, mic_factory
    )
    unreal.MaterialEditingLibrary.set_material_instance_parent(instance, base_mat)
    unreal.log(f"🎉 Created smart instance: {instance.get_name()}")

    # 10) Apply matched textures
    applied_count = 0
    for param in to_set:
        texture = matched_textures.get(param)
        if texture:
            try:
                unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
                    instance, param, texture
                )
                param_emoji = "🏔️" if param == "Height" else "✅"
                unreal.log(f"{param_emoji} Set '{param}' → {texture.get_name()}")
                applied_count += 1
            except Exception as e:
                unreal.log_warning(f"⚠️ Failed to set {param}: {str(e)}")

    # 11) Save it
    unreal.EditorAssetLibrary.save_asset(instance.get_path_name())
    unreal.log(f"💾 Saved instance at {instance.get_path_name()}")
    unreal.log(f"🏆 Successfully applied {applied_count} textures to {instance.get_name()}")
    
    return instance

def create_material_instance_with_browser():
    """
    Alternative version using content browser selection instead of import with height map support
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
        unreal.log_error("❌ Select some textures too")
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
    
    # Check for height support
    has_height_param = _material_has_height_parameter(base_mat)
    
    # Match and apply textures (same logic as above)
    matched_textures = AutoMattyUtils.match_textures_to_params(textures, include_height=has_height_param)
    
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
            param_emoji = "🏔️" if param == "Height" else "✅"
            unreal.log(f"{param_emoji} Set '{param}' → {texture.get_name()}")
            applied_count += 1
        except Exception as e:
            unreal.log_warning(f"⚠️ Failed to set {param}: {str(e)}")
    
    # Save
    unreal.EditorAssetLibrary.save_asset(instance.get_path_name())
    unreal.log(f"🏆 Created {instance.get_name()} with {applied_count} textures")
    
    return instance

def create_material_instance_from_recent():
    """
    Create instance from recently imported textures with height map support (good for drag-drop workflow)
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
    
    # Check for height support
    has_height_param = _material_has_height_parameter(base_mat)
    
    matched_textures = AutoMattyUtils.match_textures_to_params(textures, include_height=has_height_param)
    
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
            param_emoji = "🏔️" if param == "Height" else "✅"
            unreal.log(f"{param_emoji} Set '{param}' → {texture.get_name()}")
            applied_count += 1
        except Exception as e:
            unreal.log_warning(f"⚠️ Failed to set {param}: {str(e)}")
    
    unreal.EditorAssetLibrary.save_asset(instance.get_path_name())
    unreal.log(f"🏆 Created {instance.get_name()} with {applied_count} textures")
    
    return instance

def _material_has_height_parameter(material):
    """
    Check if a material has Height parameter (indicates nanite displacement support)
    """
    try:
        # Get all texture parameter names from the material
        texture_params = unreal.MaterialEditingLibrary.get_texture_parameter_names(material)
        
        # Check if Height parameter exists
        has_height = "Height" in texture_params
        
        if has_height:
            unreal.log(f"🏔️ Material '{material.get_name()}' supports height displacement")
        else:
            unreal.log(f"🚫 Material '{material.get_name()}' does not have height displacement")
        
        return has_height
        
    except Exception as e:
        unreal.log_warning(f"⚠️ Could not check material parameters: {str(e)}")
        return False

def _material_has_tessellation_enabled(material):
    """
    Check if a material has tessellation enabled (another indicator of nanite support)
    """
    try:
        # Check tessellation mode
        tessellation_mode = material.get_editor_property("d3d11_tessellation_mode")
        is_enabled = tessellation_mode != unreal.MaterialTessellationMode.MTM_NO_TESSELLATION
        
        if is_enabled:
            unreal.log(f"🔧 Material '{material.get_name()}' has tessellation enabled")
        
        return is_enabled
        
    except Exception as e:
        unreal.log_warning(f"⚠️ Could not check tessellation mode: {str(e)}")
        return False

# Legacy compatibility function
def create_material_instance_with_path():
    """Legacy function - redirects to smart version"""
    unreal.log_warning("⚠️ Using legacy function - consider updating to create_material_instance_smart()")
    return create_material_instance_smart()

# Execute the main function when called directly
if __name__ == "__main__":
    create_material_instance_smart()