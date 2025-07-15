"""
AutoMatty Material Builder - COMPLETE FIXED VERSION
Clean dictionary-driven approach with proper triplanar support
"""
import unreal
from automatty_config import AutoMattyConfig
from automatty_utils import AutoMattyUtils

# ========================================
# CONFIGURATION DICTIONARIES - FIXED
# ========================================

# Material coordinate layouts - FIXED SPACING
COORD_LAYOUTS = {
    "orm": {
        "Color": (-1400, -100),
        "ORM": (-1400, -400),
        "Normal": (-1400, -800),
        "Emission": (-1400, -1200),
    },
    "split": {
        "Color": (-1400, -100),
        "Roughness": (-1400, -400),
        "Metallic": (-1400, -800),
        "Normal": (-1400, -1200),
        "Emission": (-1400, -1600),
    },
    "environment_simple": {
        "ColorA": (-1600, -200),
        "ColorB": (-1600, -300),
        "NormalA": (-1600, -400),
        "NormalB": (-1600, -500),
        "RoughnessA": (-1600, -600),
        "RoughnessB": (-1600, -700),
        "MetallicA": (-1600, -800),
        "MetallicB": (-1600, -900),
    },
    "environment_advanced": {
        "ColorA": (-1800, -200),
        "NormalA": (-1800, -300),
        "RoughnessA": (-1800, -400),
        "MetallicA": (-1800, -500),
        "ColorB": (-1800, -700),
        "NormalB": (-1800, -800),
        "RoughnessB": (-1800, -900),
        "MetallicB": (-1800, -1000),
    }
}

# Parameter groups for UI organization
PARAM_GROUPS = {
    "Color": ["color", "brightness", "contrast", "hue", "tint"],
    "Roughness": ["roughness", "rough"],
    "Metallic": ["metal", "metallic", "metalness"],
    "Normal": ["normal", "norm", "nrm"],
    "Displacement": ["height", "displacement", "disp"],
    "Emission": ["emission", "emissive", "glow"],
    "Environment": ["blend", "mask", "mix", "env"],
    "Texture Variation": ["variation", "random", "var"],
    "UV Controls": ["uv", "scale", "tiling"]
}

# Material functions library
MATERIAL_FUNCTIONS = {
    "world_aligned_texture": "/Engine/Functions/Engine_MaterialFunctions01/Texturing/WorldAlignedTexture",
    "world_aligned_normal": "/Engine/Functions/Engine_MaterialFunctions01/Texturing/WorldAlignedNormal",
    "texture_variation": "/Engine/Functions/Engine_MaterialFunctions03/Texturing/TextureVariation",
    "hue_shift": "/Engine/Functions/Engine_MaterialFunctions02/HueShift",
    "remap_value": "/Engine/Functions/Engine_MaterialFunctions03/Math/RemapValueRange"
}

# Control parameter configurations - FIXED
CONTROL_PARAMS = {
    "brightness": {"default": 1.0, "group": "Color", "range": (0.0, 5.0)},
    "color_contrast": {"default": 1.0, "group": "Color", "range": (0.0, 5.0)},
    "roughness_contrast": {"default": 1.0, "group": "Roughness", "range": (0.0, 5.0)},  # ADDED
    "hue_shift": {"default": 0.0, "group": "Color", "range": (-1.0, 1.0)},
    "roughness_min": {"default": 0.0, "group": "Roughness", "range": (0.0, 1.0)},
    "roughness_max": {"default": 1.0, "group": "Roughness", "range": (0.0, 1.0)},
    "metal_intensity": {"default": 0.0, "group": "Metallic", "range": (0.0, 1.0)},
    "emission_intensity": {"default": 0.0, "group": "Emission", "range": (0.0, 10.0)},
    "displacement_intensity": {"default": 0.1, "group": "Displacement", "range": (0.0, 10.0)},
    "scale": {"default": 1.0, "group": "UV Controls", "range": (0.01, 100.0)},  # RENAMED from uv_scale
    "mfp_scale": {"default": 0.0, "group": "SSS", "range": (0.0, 10.0)},  # CHANGED from 1.0 to 0.0
    "second_roughness": {"default": 0.5, "group": "Roughness", "range": (0.0, 1.0)},
    "second_roughness_weight": {"default": 0.0, "group": "Roughness", "range": (0.0, 1.0)},
    "mix_scale": {"default": 0.001, "group": "Advanced Mixing", "range": (0.0001, 1.0)}
}

# ========================================
# MATERIAL BUILDER CLASS
# ========================================

class SubstrateMaterialBuilder:
    """Clean, dictionary-driven material builder"""
    
    def __init__(self, custom_paths=None):
        self.config = AutoMattyConfig()
        if custom_paths:
            self._override_paths(custom_paths)
        
        self.lib = unreal.MaterialEditingLibrary
        self.atools = unreal.AssetToolsHelpers.get_asset_tools()
        self.default_normal = AutoMattyUtils.find_default_normal()
    
    def _override_paths(self, custom_paths):
        """Override default paths with user-provided ones"""
        for key, value in custom_paths.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
    
    # ========================================
    # PUBLIC MATERIAL CREATION METHODS
    # ========================================
    
    def create_orm_material(self, base_name=None, custom_path=None, **features):
        """Create ORM material with features"""
        return self._create_material("orm", base_name, custom_path, **features)
    
    def create_split_material(self, base_name=None, custom_path=None, **features):
        """Create Split material with features"""
        return self._create_material("split", base_name, custom_path, **features)
    
    def create_environment_material(self, base_name=None, custom_path=None, **features):
        """Create Environment material with features"""
        env_type = "environment_advanced" if features.get('use_adv_env') else "environment_simple"
        return self._create_material(env_type, base_name, custom_path, **features)
    
    # ========================================
    # CORE MATERIAL CREATION LOGIC
    # ========================================
    
    def _create_material(self, material_type, base_name, custom_path, **features):
        """Unified material creation method"""
        if not AutoMattyUtils.is_substrate_enabled():
            unreal.log_error("❌ Substrate is not enabled in project settings!")
            return None
        
        # Generate name and path
        name, folder = self._generate_material_name(material_type, base_name, custom_path, features)
        
        # Create material asset
        material = self.atools.create_asset(name, folder, unreal.Material, unreal.MaterialFactoryNew())
        
        # Configure tessellation for nanite
        if features.get('use_nanite'):
            material.set_editor_property("enable_tessellation", True)
        
        # Build the material graph
        self._build_material_graph(material, material_type, features)
        
        # Finalize
        self.lib.recompile_material(material)
        unreal.EditorAssetLibrary.save_loaded_asset(material)
        
        # Log success
        feature_names = [k.replace('use_', '') for k, v in features.items() if v]
        feature_text = f" ({', '.join(feature_names)})" if feature_names else ""
        unreal.log(f"✅ {material_type.upper()} material '{name}'{feature_text} created")
        
        return material
    
    def _generate_material_name(self, material_type, base_name, custom_path, features):
        """Generate material name based on type and features"""
        if base_name is None:
            prefix = AutoMattyConfig.get_custom_material_prefix()
            type_map = {
                "orm": "ORM",
                "split": "Split", 
                "environment_simple": "Environment",
                "environment_advanced": "AdvEnvironment"
            }
            base_name = f"{prefix}_{type_map.get(material_type, material_type.title())}"
        
        folder = custom_path or AutoMattyConfig.get_custom_material_path()
        name = AutoMattyUtils.get_next_asset_name(base_name, folder)
        
        return name, folder
    
    # ========================================
    # MATERIAL GRAPH BUILDING
    # ========================================
    
    def _build_material_graph(self, material, material_type, features):
        """Build material graph based on type and features"""
        
        # Get coordinate layout
        coords = COORD_LAYOUTS[material_type].copy()
        
        # Add height coordinates if nanite enabled
        if features.get('use_nanite'):
            self._add_height_coordinates(coords, material_type)
        
        # Setup UV system (variation + scaling) - FIXED FOR TRIPLANAR
        uv_output = self._setup_uv_system(material, features)
        
        # Create texture samples
        samples = self._create_texture_samples(material, coords, features, uv_output)
        
        # Build material graph based on type
        if material_type.startswith("environment"):
            self._build_environment_graph(material, material_type, samples, features)
        else:
            self._build_standard_graph(material, material_type, samples, features)
    
    def _add_height_coordinates(self, coords, material_type):
        """Add height map coordinates for nanite displacement"""
        if material_type == "environment_simple":
            coords.update({"HeightA": (-1600, -1000), "HeightB": (-1600, -1100)})
        elif material_type == "environment_advanced":
            coords.update({"HeightA": (-1800, -600), "HeightB": (-1800, -1100)})
        else:
            coords["Height"] = (-1400, -1000)
        
        unreal.log(f"🏔️ Added Height parameters for {material_type} nanite displacement")
    
    # ========================================
    # UV SYSTEM SETUP - FIXED FOR TRIPLANAR
    # ========================================
    
    def _setup_uv_system(self, material, features):
        """Setup UV coordinates with optional scaling and variation - FIXED FOR TRIPLANAR"""
        
        if features.get('use_triplanar'):
            # For triplanar, use world position instead of texture coordinates
            world_pos = self.lib.create_material_expression(material, unreal.MaterialExpressionWorldPosition, -2000, -50)
            
            # Scale parameter (renamed from uv_scale to just scale)
            scale_param = self._create_control_parameter(material, "scale", -2000, -100)
            
            # Scale the world position
            scale_multiply = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, -1900, -75)
            self.lib.connect_material_expressions(world_pos, "", scale_multiply, "A")
            self.lib.connect_material_expressions(scale_param, "", scale_multiply, "B")
            
            # Apply texture variation if enabled
            if features.get('use_tex_var'):
                return self._setup_texture_variation(material, scale_multiply)
            
            return scale_multiply
        else:
            # Standard UV coordinates for non-triplanar
            tex_coords = self.lib.create_material_expression(material, unreal.MaterialExpressionTextureCoordinate, -2000, -50)
            
            # Scale parameter
            scale_param = self._create_control_parameter(material, "scale", -2000, -100)
            
            # Scale the UVs
            uv_multiply = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, -1900, -75)
            self.lib.connect_material_expressions(tex_coords, "", uv_multiply, "A")
            self.lib.connect_material_expressions(scale_param, "", uv_multiply, "B")
            
            # Apply texture variation if enabled
            if features.get('use_tex_var'):
                return self._setup_texture_variation(material, uv_multiply)
            
            return uv_multiply
    
    def _setup_texture_variation(self, material, uv_input):
        """Setup texture variation system - FIXED"""
        unreal.log(f"🎲 Setting up texture variation system")
        
        # Variation height map parameter - FIXED: use texture object instead of texture sample
        var_height_param = self.lib.create_material_expression(material, unreal.MaterialExpressionTextureObjectParameter, -1900, -150)
        var_height_param.set_editor_property("parameter_name", "VariationHeightMap")
        var_height_param.set_editor_property("group", "Texture Variation")
        
        # Random rotation/scale switch - FIXED: use StaticBoolParameter instead of StaticSwitchParameter
        random_switch = self.lib.create_material_expression(material, unreal.MaterialExpressionStaticBoolParameter, -1900, -200)
        random_switch.set_editor_property("parameter_name", "RandomRotationScale")
        random_switch.set_editor_property("default_value", True)
        random_switch.set_editor_property("group", "Texture Variation")
        
        # TextureVariation function
        texture_var_func = self._create_material_function(material, "texture_variation", -1700, -125)
        
        if texture_var_func:
            self.lib.connect_material_expressions(uv_input, "", texture_var_func, "UVs")
            self.lib.connect_material_expressions(var_height_param, "", texture_var_func, "Heightmap")
            self.lib.connect_material_expressions(random_switch, "", texture_var_func, "Random Rotation and Scale")
            unreal.log(f"✅ Texture variation function connected")
            return texture_var_func
        else:
            unreal.log_error(f"❌ TextureVariation function not found")
            return uv_input
    
    # ========================================
    # TEXTURE SAMPLE CREATION - FIXED FOR TRIPLANAR
    # ========================================
    
    def _create_texture_samples(self, material, coords, features, uv_output):
        """Create all texture samples for the material"""
        samples = {}
        
        for param_name, (x, y) in coords.items():
            if features.get('use_triplanar'):
                samples[param_name] = self._create_triplanar_sample(material, param_name, x, y, uv_output)
            else:
                samples[param_name] = self._create_regular_sample(material, param_name, x, y, uv_output)
        
        return samples
    
    def _create_triplanar_sample(self, material, param_name, x, y, uv_output):
        """Create triplanar texture sample - FIXED"""
        # Texture object parameter
        texture_param = self.lib.create_material_expression(material, unreal.MaterialExpressionTextureObjectParameter, x - 200, y)
        texture_param.set_editor_property("parameter_name", param_name)
        texture_param.set_editor_property("group", self._get_param_group(param_name))
        
        # Choose appropriate world-aligned function
        func_name = "world_aligned_normal" if "Normal" in param_name else "world_aligned_texture"
        world_align_func = self._create_material_function(material, func_name, x, y)
        
        if world_align_func:
            self.lib.connect_material_expressions(texture_param, "", world_align_func, "TextureObject")
            # FIXED: Connect world position to WorldPosition pin
            if uv_output:
                self.lib.connect_material_expressions(uv_output, "", world_align_func, "WorldPosition")
            
            emoji = "🏔️" if "Height" in param_name else "🔺"
            unreal.log(f"{emoji} Triplanar setup: {param_name}")
            return (world_align_func, "XYZ Texture")
        else:
            unreal.log_error(f"❌ World-aligned function not found for {param_name}")
            return self._create_regular_sample(material, param_name, x, y, uv_output)
    
    def _create_regular_sample(self, material, param_name, x, y, uv_output):
        """Create regular texture sample"""
        node = self.lib.create_material_expression(material, unreal.MaterialExpressionTextureSampleParameter2D, x, y)
        node.set_editor_property("parameter_name", param_name)
        node.set_editor_property("group", self._get_param_group(param_name))
        
        # Set sampler type based on parameter
        if "Normal" in param_name:
            node.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
            if self.default_normal:
                node.set_editor_property("texture", self.default_normal)
        elif "Height" in param_name:
            node.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_GRAYSCALE)
        
        # Connect variation UVs if available
        if uv_output:
            self.lib.connect_material_expressions(uv_output, "", node, "UVs")
            unreal.log(f"🎲 Connected variation UVs to {param_name}")
        
        return node
    
    def _get_param_group(self, param_name):
        """Get parameter group for UI organization"""
        param_lower = param_name.lower()
        for group, keywords in PARAM_GROUPS.items():
            if any(keyword in param_lower for keyword in keywords):
                return group
        return "Other"
    
    # ========================================
    # STANDARD MATERIAL GRAPH
    # ========================================
    
    def _build_standard_graph(self, material, material_type, samples, features):
        """Build standard material graph (ORM/Split)"""
        
        # Color processing chain
        color_final = self._build_color_chain(material, samples, material_type)
        
        # Roughness processing - FIXED: added contrast control
        roughness_final = self._build_roughness_chain(material, samples, material_type, features)
        
        # Metallic processing
        metallic_final = self._build_metallic_chain(material, samples, material_type)
        
        # AO processing (ORM only)
        ao_final = self._build_ao_chain(material, samples, material_type) if material_type == "orm" else None
        
        # Emission processing
        emission_final = self._build_emission_chain(material, samples)
        
        # SSS processing
        mfp_final = self._build_sss_chain(material, color_final)
        
        # Displacement (nanite)
        displacement_final = self._build_displacement_chain(material, samples, features)
        
        # Create and connect substrate slab - FIXED SPACING
        self._create_substrate_slab(material, {
            "diffuse": color_final,
            "roughness": roughness_final,
            "metallic": metallic_final,
            "normal": samples.get("Normal"),
            "ao": ao_final,
            "emission": emission_final,
            "mfp": mfp_final,
            "displacement": displacement_final
        }, features)
    
    def _build_color_chain(self, material, samples, material_type):
        """Build color processing chain"""
        base_color = samples["Color"]
        
        # Brightness
        brightness_param = self._create_control_parameter(material, "brightness", -1100, -100)
        brightness_multiply = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, -900, -150)
        self._connect_sample(base_color, brightness_multiply, "A")
        self.lib.connect_material_expressions(brightness_param, "", brightness_multiply, "B")
        
        # Contrast
        contrast_param = self._create_control_parameter(material, "color_contrast", -1100, -150)
        color_power = self.lib.create_material_expression(material, unreal.MaterialExpressionPower, -750, -150)
        self.lib.connect_material_expressions(brightness_multiply, "", color_power, "Base")
        self.lib.connect_material_expressions(contrast_param, "", color_power, "Exp")
        
        # Hue shift
        hue_param = self._create_control_parameter(material, "hue_shift", -1100, -200)
        hue_shift = self._create_material_function(material, "hue_shift", -600, -150)
        
        if hue_shift:
            self.lib.connect_material_expressions(color_power, "", hue_shift, "Texture")
            self.lib.connect_material_expressions(hue_param, "", hue_shift, "Hue Shift Percentage")
            return hue_shift
        
        return color_power
    
    def _build_roughness_chain(self, material, samples, material_type, features):
        """Build roughness processing chain - FIXED: added contrast control"""
        # Get roughness input
        if material_type == "orm":
            rough_mask = self.lib.create_material_expression(material, unreal.MaterialExpressionComponentMask, -1100, -350)
            rough_mask.set_editor_property("r", False)
            rough_mask.set_editor_property("g", True)
            rough_mask.set_editor_property("b", False)
            rough_mask.set_editor_property("a", False)
            self._connect_sample(samples["ORM"], rough_mask, "")
            roughness_input = rough_mask
        else:
            roughness_input = samples["Roughness"]
        
        # Roughness contrast - NEW
        rough_contrast_param = self._create_control_parameter(material, "roughness_contrast", -1100, -400)
        rough_contrast = self.lib.create_material_expression(material, unreal.MaterialExpressionPower, -900, -400)
        self._connect_sample(roughness_input, rough_contrast, "Base")
        self.lib.connect_material_expressions(rough_contrast_param, "", rough_contrast, "Exp")
        
        # Remap roughness range
        rough_min = self._create_control_parameter(material, "roughness_min", -1100, -450)
        rough_max = self._create_control_parameter(material, "roughness_max", -1100, -500)
        
        remap_rough = self._create_material_function(material, "remap_value", -700, -450)
        if remap_rough:
            self.lib.connect_material_expressions(rough_contrast, "", remap_rough, "Input")
            self.lib.connect_material_expressions(rough_min, "", remap_rough, "Target Low")
            self.lib.connect_material_expressions(rough_max, "", remap_rough, "Target High")
            return remap_rough
        
        return rough_contrast
    
    def _build_metallic_chain(self, material, samples, material_type):
        """Build metallic processing chain"""
        # Get metallic input
        if material_type == "orm":
            metal_mask = self.lib.create_material_expression(material, unreal.MaterialExpressionComponentMask, -1100, -550)
            metal_mask.set_editor_property("r", False)
            metal_mask.set_editor_property("g", False)
            metal_mask.set_editor_property("b", True)
            metal_mask.set_editor_property("a", False)
            self._connect_sample(samples["ORM"], metal_mask, "")
            metallic_input = metal_mask
        else:
            metallic_input = samples["Metallic"]
        
        # Metal intensity
        metal_intensity = self._create_control_parameter(material, "metal_intensity", -1100, -600)
        metal_final = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, -700, -550)
        self._connect_sample(metallic_input, metal_final, "A")
        self.lib.connect_material_expressions(metal_intensity, "", metal_final, "B")
        
        return metal_final
    
    def _build_ao_chain(self, material, samples, material_type):
        """Build ambient occlusion chain (ORM only)"""
        if material_type != "orm":
            return None
            
        ao_mask = self.lib.create_material_expression(material, unreal.MaterialExpressionComponentMask, -1100, -650)
        ao_mask.set_editor_property("r", True)
        ao_mask.set_editor_property("g", False)
        ao_mask.set_editor_property("b", False)
        ao_mask.set_editor_property("a", False)
        self._connect_sample(samples["ORM"], ao_mask, "")
        
        return ao_mask
    
    def _build_emission_chain(self, material, samples):
        """Build emission processing chain"""
        emission_intensity = self._create_control_parameter(material, "emission_intensity", -1100, -700)
        emission_final = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, -700, -650)
        self._connect_sample(samples["Emission"], emission_final, "A")
        self.lib.connect_material_expressions(emission_intensity, "", emission_final, "B")
        
        return emission_final
    
    def _build_sss_chain(self, material, color_input):
        """Build subsurface scattering chain"""
        mfp_color = self.lib.create_material_expression(material, unreal.MaterialExpressionVectorParameter, -1100, -750)
        mfp_color.set_editor_property("parameter_name", "MFPColor")
        mfp_color.set_editor_property("default_value", unreal.LinearColor(1.0, 0.5, 0.3, 1.0))
        mfp_color.set_editor_property("group", "SSS")
        
        use_diffuse_switch = self.lib.create_material_expression(material, unreal.MaterialExpressionStaticSwitchParameter, -700, -750)
        use_diffuse_switch.set_editor_property("parameter_name", "UseDiffuseAsMFP")
        use_diffuse_switch.set_editor_property("default_value", True)
        use_diffuse_switch.set_editor_property("group", "SSS")
        
        mfp_scale = self._create_control_parameter(material, "mfp_scale", -1100, -800)
        
        self.lib.connect_material_expressions(color_input, "", use_diffuse_switch, "True")
        self.lib.connect_material_expressions(mfp_color, "", use_diffuse_switch, "False")
        
        return {"switch": use_diffuse_switch, "scale": mfp_scale}
    
    def _build_displacement_chain(self, material, samples, features):
        """Build displacement chain for nanite"""
        if not features.get('use_nanite') or "Height" not in samples:
            return None
        
        displacement_intensity = self._create_control_parameter(material, "displacement_intensity", -1100, -850)
        displacement_multiply = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, -700, -800)
        self._connect_sample(samples["Height"], displacement_multiply, "A")
        self.lib.connect_material_expressions(displacement_intensity, "", displacement_multiply, "B")
        
        unreal.log(f"🏔️ Nanite displacement setup complete")
        return displacement_multiply
    
    # ========================================
    # ENVIRONMENT MATERIAL GRAPH
    # ========================================
    
    def _build_environment_graph(self, material, material_type, samples, features):
        """Build environment material graph"""
        if material_type == "environment_advanced":
            self._build_advanced_environment(material, samples, features)
        else:
            self._build_simple_environment(material, samples, features)
    
    def _build_simple_environment(self, material, samples, features):
        """Build simple environment with lerps"""
        # Blend mask
        blend_mask = self.lib.create_material_expression(material, unreal.MaterialExpressionTextureSampleParameter2D, -1600, -100)
        blend_mask.set_editor_property("parameter_name", "BlendMask")
        blend_mask.set_editor_property("group", "Environment")
        
        # Create lerps for each channel
        lerps = {}
        lerp_configs = [
            ("color", "ColorA", "ColorB", -1200, -250),
            ("normal", "NormalA", "NormalB", -1200, -450),
            ("roughness", "RoughnessA", "RoughnessB", -1200, -650),
            ("metallic", "MetallicA", "MetallicB", -1200, -850)
        ]
        
        # Add height lerp if nanite enabled
        if features.get('use_nanite') and "HeightA" in samples and "HeightB" in samples:
            lerp_configs.append(("height", "HeightA", "HeightB", -1200, -1050))
        
        for name, input_a, input_b, x, y in lerp_configs:
            if input_a in samples and input_b in samples:
                lerp = self.lib.create_material_expression(material, unreal.MaterialExpressionLinearInterpolate, x, y)
                self._connect_sample(samples[input_a], lerp, "A")
                self._connect_sample(samples[input_b], lerp, "B")
                self.lib.connect_material_expressions(blend_mask, "", lerp, "Alpha")
                lerps[name] = lerp
        
        # Color controls
        brightness_param = self._create_control_parameter(material, "brightness", -900, -200)
        brightness_multiply = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, -750, -250)
        self.lib.connect_material_expressions(lerps["color"], "", brightness_multiply, "A")
        self.lib.connect_material_expressions(brightness_param, "", brightness_multiply, "B")
        
        # Displacement
        displacement_final = None
        if features.get('use_nanite') and "height" in lerps:
            displacement_intensity = self._create_control_parameter(material, "displacement_intensity", -900, -1000)
            displacement_multiply = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, -750, -1050)
            self.lib.connect_material_expressions(lerps["height"], "", displacement_multiply, "A")
            self.lib.connect_material_expressions(displacement_intensity, "", displacement_multiply, "B")
            displacement_final = displacement_multiply
        
        # Create substrate slab - FIXED SPACING
        self._create_substrate_slab(material, {
            "diffuse": brightness_multiply,
            "normal": lerps.get("normal"),
            "roughness": lerps.get("roughness"),
            "metallic": lerps.get("metallic"),
            "displacement": displacement_final
        }, features)
    
    def _build_advanced_environment(self, material, samples, features):
        """Build advanced environment with dual slabs"""
        # Create slabs A and B
        slab_a = self.lib.create_material_expression(material, unreal.MaterialExpressionSubstrateSlabBSDF, -1400, -350)
        slab_b = self.lib.create_material_expression(material, unreal.MaterialExpressionSubstrateSlabBSDF, -1400, -750)
        
        # Connect slab A
        self._connect_sample(samples["ColorA"], slab_a, "Diffuse Albedo")
        self._connect_sample(samples["NormalA"], slab_a, "Normal")
        self._connect_sample(samples["RoughnessA"], slab_a, "Roughness")
        self._connect_sample(samples["MetallicA"], slab_a, "F0")
        
        # Connect slab B
        self._connect_sample(samples["ColorB"], slab_b, "Diffuse Albedo")
        self._connect_sample(samples["NormalB"], slab_b, "Normal")
        self._connect_sample(samples["RoughnessB"], slab_b, "Roughness")
        self._connect_sample(samples["MetallicB"], slab_b, "F0")
        
        # World-space mixing pattern
        mixing_pattern = self._create_world_space_mixing(material)
        
        # Displacement for advanced environment
        displacement_final = None
        if features.get('use_nanite') and "HeightA" in samples and "HeightB" in samples:
            height_lerp = self.lib.create_material_expression(material, unreal.MaterialExpressionLinearInterpolate, -1200, -1150)
            self._connect_sample(samples["HeightA"], height_lerp, "A")
            self._connect_sample(samples["HeightB"], height_lerp, "B")
            self.lib.connect_material_expressions(mixing_pattern, "", height_lerp, "Alpha")
            
            displacement_intensity = self._create_control_parameter(material, "displacement_intensity", -1400, -1200)
            displacement_multiply = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, -1000, -1150)
            self.lib.connect_material_expressions(height_lerp, "", displacement_multiply, "A")
            self.lib.connect_material_expressions(displacement_intensity, "", displacement_multiply, "B")
            displacement_final = displacement_multiply
        
        # Substrate horizontal mixing
        substrate_mix = self.lib.create_material_expression(material, unreal.MaterialExpressionSubstrateHorizontalMixing, -1000, -550)
        self.lib.connect_material_expressions(slab_a, "", substrate_mix, "Background")
        self.lib.connect_material_expressions(slab_b, "", substrate_mix, "Foreground")
        self.lib.connect_material_expressions(mixing_pattern, "", substrate_mix, "Mix")
        
        # Connect to material output - FIXED SPACING
        self.lib.connect_material_property(substrate_mix, "", unreal.MaterialProperty.MP_FRONT_MATERIAL)
        
        # Connect displacement
        if displacement_final:
            self._connect_displacement(material, displacement_final)
    
    def _create_world_space_mixing(self, material):
        """Create world-space mixing pattern"""
        world_pos = self.lib.create_material_expression(material, unreal.MaterialExpressionWorldPosition, -1600, -100)
        
        # Extract Z component
        component_mask = self.lib.create_material_expression(material, unreal.MaterialExpressionComponentMask, -1500, -100)
        component_mask.set_editor_property("r", False)
        component_mask.set_editor_property("g", False)
        component_mask.set_editor_property("b", True)
        component_mask.set_editor_property("a", False)
        self.lib.connect_material_expressions(world_pos, "", component_mask, "")
        
        # Scale
        scale_param = self._create_control_parameter(material, "mix_scale", -1600, -150)
        scale_multiply = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, -1400, -125)
        self.lib.connect_material_expressions(component_mask, "", scale_multiply, "A")
        self.lib.connect_material_expressions(scale_param, "", scale_multiply, "B")
        
        # Frac for tiling
        frac_node = self.lib.create_material_expression(material, unreal.MaterialExpressionFrac, -1300, -125)
        self.lib.connect_material_expressions(scale_multiply, "", frac_node, "")
        
        return frac_node
    
    # ========================================
    # SUBSTRATE SLAB CREATION - FIXED SPACING
    # ========================================
    
    def _create_substrate_slab(self, material, connections, features):
        """Create and connect substrate slab - FIXED: better spacing to avoid overlap"""
        slab = self.lib.create_material_expression(material, unreal.MaterialExpressionSubstrateSlabBSDF, -400, -400)
        
        # Connect inputs
        connection_map = {
            "diffuse": "Diffuse Albedo",
            "roughness": "Roughness", 
            "metallic": "F0",
            "normal": "Normal",
            "ao": "AmbientOcclusion",
            "emission": "Emissive Color"
        }
        
        for key, pin in connection_map.items():
            if connections.get(key):
                self._connect_sample(connections[key], slab, pin)
        
        # Connect SSS
        if connections.get("mfp"):
            mfp = connections["mfp"]
            self.lib.connect_material_expressions(mfp["switch"], "", slab, "SSS MFP")
            self.lib.connect_material_expressions(mfp["scale"], "", slab, "SSS MFP Scale")
        
        # Connect second roughness
        if features.get('use_second_roughness'):
            second_rough = self._create_control_parameter(material, "second_roughness", -700, -450)
            second_weight = self._create_control_parameter(material, "second_roughness_weight", -700, -500)
            self.lib.connect_material_expressions(second_rough, "", slab, "Second Roughness")
            self.lib.connect_material_expressions(second_weight, "", slab, "Second Roughness Weight")
        
        # Connect to output - FIXED: more spacing to avoid overlap
        self.lib.connect_material_property(slab, "", unreal.MaterialProperty.MP_FRONT_MATERIAL)
        
        # Connect displacement
        if connections.get("displacement"):
            self._connect_displacement(material, connections["displacement"])
    
    def _connect_displacement(self, material, displacement_node):
        """Connect displacement with fallbacks"""
        displacement_properties = [
            unreal.MaterialProperty.MP_DISPLACEMENT,
            unreal.MaterialProperty.MP_TESSELLATION_MULTIPLIER,
            unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET
        ]
        
        for prop in displacement_properties:
            try:
                self.lib.connect_material_property(displacement_node, "", prop)
                prop_name = str(prop).split('.')[-1]
                unreal.log(f"🏔️ Connected displacement to {prop_name}")
                break
            except AttributeError:
                continue
    
    # ========================================
    # UTILITY METHODS
    # ========================================
    
    def _create_control_parameter(self, material, param_key, x, y):
        """Create control parameter with config-driven settings"""
        config = CONTROL_PARAMS.get(param_key, {"default": 1.0, "group": "Other"})
        
        param = self.lib.create_material_expression(material, unreal.MaterialExpressionScalarParameter, x, y)
        param.set_editor_property("parameter_name", param_key.replace('_', '').title())
        param.set_editor_property("default_value", config["default"])
        param.set_editor_property("group", config["group"])
        
        return param
    
    def _create_material_function(self, material, func_key, x, y):
        """Create material function call"""
        func_path = MATERIAL_FUNCTIONS.get(func_key)
        if not func_path:
            unreal.log_error(f"❌ Unknown function key: {func_key}")
            return None
        
        func_asset = unreal.EditorAssetLibrary.load_asset(func_path)
        if not func_asset:
            unreal.log_error(f"❌ Function not found: {func_path}")
            return None
        
        func_call = self.lib.create_material_expression(material, unreal.MaterialExpressionMaterialFunctionCall, x, y)
        func_call.set_editor_property("material_function", func_asset)
        
        return func_call
    
    def _connect_sample(self, sample, target_node, target_input):
        """Connect sample (handles both regular and triplanar)"""
        if isinstance(sample, tuple):
            source_node, output_pin = sample
            self.lib.connect_material_expressions(source_node, output_pin, target_node, target_input)
        else:
            self.lib.connect_material_expressions(sample, "", target_node, target_input)

# ========================================
# CONVENIENCE FUNCTIONS
# ========================================

def create_orm_material(**kwargs):
    """Create basic ORM material"""
    builder = SubstrateMaterialBuilder()
    return builder.create_orm_material(**kwargs)

def create_split_material(**kwargs):
    """Create basic Split material"""
    builder = SubstrateMaterialBuilder()
    return builder.create_split_material(**kwargs)

def create_environment_material(**kwargs):
    """Create basic Environment material"""
    builder = SubstrateMaterialBuilder()
    return builder.create_environment_material(**kwargs)

if __name__ == "__main__":
    create_orm_material()
