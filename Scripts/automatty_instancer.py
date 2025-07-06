"""
AutoMatty Material Instance Creator with Environment Material Support - Smart material instance creation with universal plugin support
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
    Enhanced material instance creator with environment material support, smart naming, custom paths, and height map support
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

    # 6) Check material capabilities
    texture_params = unreal.MaterialEditingLibrary.get_texture_parameter_names(base_mat)
    has_height_param = "Height" in texture_params
    
    # 7) Detect material type
    is_environment = any(param.endswith('A') or param.endswith('B') for param in texture_params if param.startswith(('Color', 'Normal', 'Roughness', 'Metallic')))
    material_type = "environment" if is_environment else None
    
    if is_environment:
        unreal.log(f"🌍 Detected environment material with A/B texture sets")
    
    # 8) Use enhanced texture matching
    matched_textures = _match_textures_enhanced(
        textures, 
        include_height=has_height_param,
        material_type=material_type
    )
    
    if not matched_textures:
        unreal.log_warning("⚠️ No matching textures found for material parameters.")
        return

    # 9) Determine workflow and log findings
    if is_environment:
        workflow = "environment"
        to_set = list(matched_textures.keys())
        unreal.log(f"🌍 Environment workflow detected")
    else:
        # Standard material workflow detection
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

    # 10) Create the Material Instance with smart naming
    mic_factory = unreal.MaterialInstanceConstantFactoryNew()
    instance = atools.create_asset(
        instance_name, target_folder,
        unreal.MaterialInstanceConstant, mic_factory
    )
    unreal.MaterialEditingLibrary.set_material_instance_parent(instance, base_mat)
    unreal.log(f"🎉 Created smart instance: {instance.get_name()}")

    # 11) Apply matched textures
    applied_count = 0
    for param in to_set:
        texture = matched_textures.get(param)
        if texture:
            try:
                unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
                    instance, param, texture
                )
                param_emoji = "🏔️" if param == "Height" else "🌍" if param.endswith(('A', 'B')) or param == "BlendMask" else "✅"
                unreal.log(f"{param_emoji} Set '{param}' → {texture.get_name()}")
                applied_count += 1
            except Exception as e:
                unreal.log_warning(f"⚠️ Failed to set {param}: {str(e)}")

    # 12) Save it
    unreal.EditorAssetLibrary.save_asset(instance.get_path_name())
    unreal.log(f"💾 Saved instance at {instance.get_path_name()}")
    unreal.log(f"🏆 Successfully applied {applied_count} textures to {instance.get_name()}")
    
    return instance

def _match_textures_enhanced(textures, include_height=False, material_type=None):
    """
    Enhanced texture matching with environment material support
    """
    import re
    
    # Standard patterns
    patterns = AutoMattyConfig.TEXTURE_PATTERNS
    
    # Filter patterns based on include_height flag
    if not include_height and "Height" in patterns:
        patterns = {k: v for k, v in patterns.items() if k != "Height"}
    
    found = {}
    
    # Handle environment materials with A/B texture sets
    if material_type == "environment":
        # Environment materials need A/B sets plus BlendMask
        env_patterns = {
            "ColorA": patterns["Color"],
            "ColorB": patterns["Color"], 
            "NormalA": patterns["Normal"],
            "NormalB": patterns["Normal"],
            "RoughnessA": patterns["Roughness"],
            "RoughnessB": patterns["Roughness"],
            "MetallicA": patterns["Metallic"],
            "MetallicB": patterns["Metallic"],
            "BlendMask": re.compile(r"(?:^|[_\W])(?:blend|mask|mix)(?:$|[_\W])", re.IGNORECASE),
        }
        
        # Try to intelligently assign A/B based on filename hints
        for tex in textures:
            name = tex.get_name().lower()
            
            # Check for explicit A/B markers first
            for param, pattern in env_patterns.items():
                if param not in found:
                    # For A textures, look for 'a', '01', 'first', etc.
                    if param.endswith('A'):
                        if pattern.search(name) and any(marker in name for marker in ['_a_', '_a.', '_01_', '_1_', 'first', 'primary']):
                            found[param] = tex
                            unreal.log(f"Matched '{tex.get_name()}' -> {param} (explicit A marker)")
                            break
                    # For B textures, look for 'b', '02', 'second', etc.
                    elif param.endswith('B'):
                        if pattern.search(name) and any(marker in name for marker in ['_b_', '_b.', '_02_', '_2_', 'second', 'secondary']):
                            found[param] = tex
                            unreal.log(f"Matched '{tex.get_name()}' -> {param} (explicit B marker)")
                            break
                    # BlendMask
                    elif param == "BlendMask":
                        if pattern.search(name):
                            found[param] = tex
                            unreal.log(f"Matched '{tex.get_name()}' -> {param}")
                            break
        
        # Fallback: assign remaining textures to A set first, then B set
        for tex in textures:
            if tex in found.values():
                continue  # Already assigned
                
            name = tex.get_name().lower()
            for base_type in ["Color", "Normal", "Roughness", "Metallic"]:
                if base_type in patterns and patterns[base_type].search(name):
                    # Assign to A first, then B
                    param_a = f"{base_type}A"
                    param_b = f"{base_type}B"
                    
                    if param_a not in found:
                        found[param_a] = tex
                        unreal.log(f"Matched '{tex.get_name()}' -> {param_a} (fallback)")
                        break
                    elif param_b not in found:
                        found[param_b] = tex
                        unreal.log(f"Matched '{tex.get_name()}' -> {param_b} (fallback)")
                        break
    else:
        # Standard material matching (existing logic)
        for tex in textures:
            name = tex.get_name().lower()
            for param, pattern in patterns.items():
                if param not in found and pattern.search(name):
                    found[param] = tex
                    unreal.log(f"Matched '{tex.get_name()}' -> {param}")
                    break
    
    return found

def create_material_instance_with_browser():
    """
    Alternative version using content browser selection instead of import with height map and environment support
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
    
    # Check for capabilities and material type
    texture_params = unreal.MaterialEditingLibrary.get_texture_parameter_names(base_mat)
    has_height_param = "Height" in texture_params
    is_environment = any(param.endswith('A') or param.endswith('B') for param in texture_params if param.startswith(('Color', 'Normal', 'Roughness', 'Metallic')))
    material_type = "environment" if is_environment else None
    
    if is_environment:
        unreal.log(f"🌍 Detected environment material with A/B texture sets")
    
    # Match and apply textures
    matched_textures = _match_textures_enhanced(textures, include_height=has_height_param, material_type=material_type)
    
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
            param_emoji = "🏔️" if param == "Height" else "🌍" if param.endswith(('A', 'B')) or param == "BlendMask" else "✅"
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
    Create instance from recently imported textures with height map and environment support (good for drag-drop workflow)
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
    
    # Check capabilities and material type
    texture_params = unreal.MaterialEditingLibrary.get_texture_parameter_names(base_mat)
    has_height_param = "Height" in texture_params
    is_environment = any(param.endswith('A') or param.endswith('B') for param in texture_params if param.startswith(('Color', 'Normal', 'Roughness', 'Metallic')))
    material_type = "environment" if is_environment else None
    
    if is_environment:
        unreal.log(f"🌍 Detected environment material with A/B texture sets")
    
    matched_textures = _match_textures_enhanced(textures, include_height=has_height_param, material_type=material_type)
    
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
            param_emoji = "🏔️" if param == "Height" else "🌍" if param.endswith(('A', 'B')) or param == "BlendMask" else "✅"
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