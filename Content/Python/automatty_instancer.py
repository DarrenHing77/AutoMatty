"""
AutoMatty Material Instancer - Updated Version
Smart material instance creation with environment + height map + texture variation support
"""
import unreal
from automatty_config import AutoMattyConfig, AutoMattyUtils


def create_material_instance():
    """
    Main function - creates smart material instance with auto-detection including texture variation
    Works with: import textures, content browser selection, or folder selection
    """
    # Get selected material
    selected_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    materials = [asset for asset in selected_assets if isinstance(asset, unreal.Material)]
    
    if len(materials) != 1:
        unreal.log_error("❌ Select exactly one Material asset")
        return None
    
    base_material = materials[0]
    unreal.log(f"🔧 Base material: {base_material.get_name()}")
    
    # Try different texture sources in order of preference
    textures = _get_textures_from_selection(selected_assets)
    
    if not textures:
        # No textures in selection, try importing
        textures = _import_textures()
    
    if not textures:
        # Still no textures, try recent folder
        textures = _get_textures_from_folder()
    
    if not textures:
        unreal.log_error("❌ No textures found. Try: selecting textures, importing, or setting texture path")
        return None
    
    unreal.log(f"🎯 Found {len(textures)} textures")
    
    # Create the instance
    return _create_instance(base_material, textures)

def _get_textures_from_selection(selected_assets):
    """Get textures from current content browser selection"""
    textures = [asset for asset in selected_assets if isinstance(asset, unreal.Texture2D)]
    if textures:
        unreal.log(f"📋 Using {len(textures)} textures from selection")
    return textures

def _import_textures():
    """Import textures using dialog"""
    unreal.log("📁 Opening import dialog...")
    texture_path = AutoMattyConfig.get_custom_texture_path()
    
    atools = unreal.AssetToolsHelpers.get_asset_tools()
    imported = atools.import_assets_with_dialog(texture_path)
    
    if not imported:
        return []
    
    textures = [asset for asset in imported if isinstance(asset, unreal.Texture2D)]
    if textures:
        unreal.log(f"📦 Imported {len(textures)} textures")
    return textures

def _get_textures_from_folder():
    """Get textures from configured material folder"""
    material_path = AutoMattyConfig.get_custom_material_path()
    
    asset_paths = unreal.EditorAssetLibrary.list_assets(material_path, recursive=False)
    textures = []
    
    for asset_path in asset_paths:
        asset = unreal.EditorAssetLibrary.load_asset(asset_path)
        if isinstance(asset, unreal.Texture2D):
            textures.append(asset)
    
    if textures:
        unreal.log(f"📂 Found {len(textures)} textures in {material_path}")
    return textures

def _create_instance(base_material, textures):
    """Create the actual material instance"""
    # Get paths and naming
    material_path = AutoMattyConfig.get_custom_material_path()
    instance_name, target_folder = AutoMattyUtils.generate_smart_instance_name(
        base_material, textures, material_path
    )
    
    # Analyze material capabilities
    texture_params = unreal.MaterialEditingLibrary.get_texture_parameter_names(base_material)
    has_height = "Height" in texture_params
    has_variation = "VariationHeightMap" in texture_params  # NEW - check for texture variation
    is_environment = _is_environment_material(texture_params)
    # Check for UDIM sets first
    
    #udim_sets = detect_udim_sets(textures)
    #if udim_sets:
    #    unreal.log(f"🗺️ Found {len(udim_sets)} UDIM sets")
    #    # Use first texture from each UDIM set for matching
    #    textures = [group[0] for group in udim_sets.values()]
    #
    #if is_environment:
    #    unreal.log("🌍 Environment material detected")
    #if has_height:
    #    unreal.log("🏔️ Height displacement supported")
    #if has_variation:
    #    unreal.log("🎲 Texture variation supported")
    
    # Match textures to parameters
    matched_textures = _match_textures(textures, has_height, is_environment, has_variation)
    
    if not matched_textures:
        unreal.log_warning("⚠️ No matching textures found")
        return None
    
    # Create the instance
    atools = unreal.AssetToolsHelpers.get_asset_tools()
    mic_factory = unreal.MaterialInstanceConstantFactoryNew()
    instance = atools.create_asset(
        instance_name, target_folder,
        unreal.MaterialInstanceConstant, mic_factory
    )
    
    unreal.MaterialEditingLibrary.set_material_instance_parent(instance, base_material)
    unreal.log(f"🎉 Created instance: {instance.get_name()}")
    
    # Apply textures
    applied_count = _apply_textures(instance, matched_textures)
    
    # Save
    unreal.EditorAssetLibrary.save_asset(instance.get_path_name())
    unreal.log(f"🏆 Applied {applied_count} textures successfully")
    
    return instance

def _is_environment_material(texture_params):
    """Check if material has environment A/B parameters"""
    env_indicators = ['ColorA', 'ColorB', 'NormalA', 'NormalB', 'RoughnessA', 'RoughnessB']
    return any(param in texture_params for param in env_indicators)

def _match_textures(textures, include_height=False, is_environment=False, include_variation=False):
    """Smart texture matching with environment, height, and texture variation support"""
    import re
    
    patterns = AutoMattyConfig.TEXTURE_PATTERNS.copy()
    matched = {}
    
    if is_environment:
        # Environment material matching
        matched = _match_environment_textures(textures, patterns, include_variation)
    else:
        # Standard material matching
        for texture in textures:
            name = texture.get_name().lower()
            for param_type, pattern in patterns.items():
                # Skip Height matching if not supported
                if param_type == "Height" and not include_height:
                    continue
                    
                if param_type not in matched and pattern.search(name):
                    matched[param_type] = texture
                    emoji = "🏔️" if param_type == "Height" else "✅"
                    unreal.log(f"{emoji} Matched '{texture.get_name()}' → {param_type}")
                    break
        
        # Handle texture variation height map for standard materials
        if include_variation and "Height" not in matched and "Height" in patterns:
            # Look for any height-like texture that could be used for variation
            for texture in textures:
                name = texture.get_name().lower()
                if patterns["Height"].search(name) and texture not in matched.values():
                    matched["VariationHeightMap"] = texture
                    unreal.log(f"🎲 Matched '{texture.get_name()}' → VariationHeightMap")
                    break
    
    return matched

def _match_environment_textures(textures, patterns, include_variation=False):
    """Match textures for environment materials (A/B sets + blend mask + variation)"""
    matched = {}
    
    # Environment patterns
    env_patterns = {
        "ColorA": patterns["Color"],
        "ColorB": patterns["Color"],
        "NormalA": patterns["Normal"],
        "NormalB": patterns["Normal"],
        "RoughnessA": patterns["Roughness"],
        "RoughnessB": patterns["Roughness"],
        "MetallicA": patterns["Metallic"],
        "MetallicB": patterns["Metallic"],
        "BlendMask": patterns["BlendMask"],
    }
    
    # First pass: explicit A/B markers
    for texture in textures:
        name = texture.get_name().lower()
        
        for param, pattern in env_patterns.items():
            if param in matched:
                continue
                
            if not pattern.search(name):
                continue
            
            # Check for explicit markers
            if param.endswith('A'):
                if any(marker in name for marker in ['_a_', '_a.', '_01_', '_1_', 'first', 'primary']):
                    matched[param] = texture
                    unreal.log(f"🌍 Matched '{texture.get_name()}' → {param} (explicit A)")
            elif param.endswith('B'):
                if any(marker in name for marker in ['_b_', '_b.', '_02_', '_2_', 'second', 'secondary']):
                    matched[param] = texture
                    unreal.log(f"🌍 Matched '{texture.get_name()}' → {param} (explicit B)")
            elif param == "BlendMask":
                matched[param] = texture
                unreal.log(f"🌍 Matched '{texture.get_name()}' → {param}")
    
    # Second pass: assign remaining textures to A first, then B
    for texture in textures:
        if texture in matched.values():
            continue
            
        name = texture.get_name().lower()
        for base_type in ["Color", "Normal", "Roughness", "Metallic"]:
            if base_type in patterns and patterns[base_type].search(name):
                param_a = f"{base_type}A"
                param_b = f"{base_type}B"
                
                if param_a not in matched:
                    matched[param_a] = texture
                    unreal.log(f"🌍 Matched '{texture.get_name()}' → {param_a} (fallback)")
                    break
                elif param_b not in matched:
                    matched[param_b] = texture
                    unreal.log(f"🌍 Matched '{texture.get_name()}' → {param_b} (fallback)")
                    break
    
    # Handle texture variation for environment materials
    if include_variation:
        # Look for height textures that haven't been matched yet
        for texture in textures:
            if texture in matched.values():
                continue
            
            name = texture.get_name().lower()
            if patterns["Height"].search(name):
                matched["VariationHeightMap"] = texture
                unreal.log(f"🎲 Environment matched '{texture.get_name()}' → VariationHeightMap")
                break
    
    return matched

def _apply_textures(instance, matched_textures):
    """Apply matched textures to material instance"""
    applied_count = 0
    
    for param_name, texture in matched_textures.items():
        try:
            unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
                instance, param_name, texture
            )
            
            # Emoji based on parameter type
            if param_name == "Height":
                emoji = "🏔️"
            elif param_name == "VariationHeightMap":
                emoji = "🎲"
            elif param_name.endswith(('A', 'B')) or param_name == "BlendMask":
                emoji = "🌍"
            else:
                emoji = "✅"
            
            unreal.log(f"{emoji} Set '{param_name}' → {texture.get_name()}")
            applied_count += 1
            
        except Exception as e:
            unreal.log_warning(f"⚠️ Failed to set {param_name}: {str(e)}")
    
    return applied_count

# Execute when called directly
if __name__ == "__main__":
    create_material_instance()