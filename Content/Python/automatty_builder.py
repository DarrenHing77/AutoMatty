"""
AutoMatty Material Builder - SMART SPACING VERSION
No more hardcoded coordinates - everything auto-calculated
"""
import unreal
from automatty_config import AutoMattyConfig
from automatty_utils import AutoMattyUtils

# ========================================
# SMART SPACING SYSTEM
# ========================================

class NodeSpacer:
    """Auto-calculate node positions with proper spacing"""
    
    # Base spacing constants - adjust these to fix everything at once
    TEXTURE_SPACING_Y = 450      # Vertical spacing between texture samples
    PROCESSING_SPACING_Y = 200   # Vertical spacing between processing nodes
    CHAIN_SPACING_X = 300        # Horizontal spacing between processing chains
    PARAM_SPACING_Y = 80         # Vertical spacing between parameters
    
    # Base positions
    TEXTURE_BASE_X = -1400
    TEXTURE_BASE_Y = -100
    PROCESSING_BASE_X = -1100
    PROCESSING_BASE_Y = -100
    PARAM_BASE_X = -1100
    PARAM_BASE_Y = -100
    
    # UV system positions
    UV_BASE_X = -2000
    UV_BASE_Y = -50
    UV_SPACING_Y = 100
    
    @staticmethod
    def get_texture_coords(material_type):
        """Generate texture coordinates with proper spacing"""
        coords = {}
        y_offset = 0
        
        if material_type == "orm":
            texture_list = ["Color", "ORM", "Normal", "Emission"]
        elif material_type == "split":
            texture_list = ["Color", "Roughness", "Metallic", "Normal", "Emission"]
        elif material_type == "environment_simple":
            texture_list = ["ColorA", "ColorB", "NormalA", "NormalB", "RoughnessA", "RoughnessB", "MetallicA", "MetallicB"]
        elif material_type == "environment_advanced":
            texture_list = ["ColorA", "NormalA", "RoughnessA", "MetallicA", "ColorB", "NormalB", "RoughnessB", "MetallicB"]
        else:
            texture_list = ["Color", "Normal"]
        
        # Environment materials get pushed left more
        x_offset = -200 if "environment" in material_type else 0
        if material_type == "environment_advanced":
            x_offset = -400
        
        for texture_name in texture_list:
            coords[texture_name] = (
                NodeSpacer.TEXTURE_BASE_X + x_offset,
                NodeSpacer.TEXTURE_BASE_Y + y_offset
            )
            y_offset += NodeSpacer.TEXTURE_SPACING_Y
        
        return coords
    
    @staticmethod
    def get_processing_coords(chain_name, step_index=0):
        """Get coordinates for processing nodes"""
        chain_offsets = {
            "color": 0,
            "roughness": 1,
            "metallic": 2,
            "emission": 3,
            "sss": 4,
            "displacement": 5
        }
        
        chain_y_offset = chain_offsets.get(chain_name, 0) * (NodeSpacer.PROCESSING_SPACING_Y * 3)
        
        return (
            NodeSpacer.PROCESSING_BASE_X + (step_index * NodeSpacer.CHAIN_SPACING_X),
            NodeSpacer.PROCESSING_BASE_Y + chain_y_offset + (step_index * NodeSpacer.PROCESSING_SPACING_Y)
        )
    
    @staticmethod
    def get_param_coords(param_group, param_index):
        """Get coordinates for parameter nodes"""
        group_offsets = {
            "Color": 0,
            "Roughness": 1,
            "Metallic": 2,
            "Displacement": 3,
            "SSS": 4,
            "Environment": 5,
            "Texture Variation": 6,
            "UV Controls": 7
        }
        
        group_y_offset = group_offsets.get(param_group, 0) * (NodeSpacer.PARAM_SPACING_Y * 3)
        
        return (
            NodeSpacer.PARAM_BASE_X,
            NodeSpacer.PARAM_BASE_Y + group_y_offset + (param_index * NodeSpacer.PARAM_SPACING_Y)
        )
    
    @staticmethod
    def get_uv_coords(step_index):
        """Get coordinates for UV system nodes"""
        return (
            NodeSpacer.UV_BASE_X + (step_index * 100),
            NodeSpacer.UV_BASE_Y + (step_index * NodeSpacer.UV_SPACING_Y)
        )
    
    @staticmethod
    def add_height_coords(coords, material_type):
        """Add height coordinates using smart spacing"""
        # Find the last Y position and add spacing
        last_y = max(y for x, y in coords.values()) if coords else NodeSpacer.TEXTURE_BASE_Y
        height_y = last_y + NodeSpacer.TEXTURE_SPACING_Y
        
        if material_type == "environment_simple":
            coords.update({
                "HeightA": (NodeSpacer.TEXTURE_BASE_X - 200, height_y),
                "HeightB": (NodeSpacer.TEXTURE_BASE_X - 200, height_y + NodeSpacer.TEXTURE_SPACING_Y)
            })
        elif material_type == "environment_advanced":
            coords.update({
                "HeightA": (NodeSpacer.TEXTURE_BASE_X - 400, height_y),
                "HeightB": (NodeSpacer.TEXTURE_BASE_X - 400, height_y + NodeSpacer.TEXTURE_SPACING_Y)
            })
        else:
            coords["Height"] = (NodeSpacer.TEXTURE_BASE_X, height_y)

class ParameterManager:
    """Auto-positioning parameter manager"""
    
    def __init__(self):
        self.param_counters = {}  # Track parameter counts per group
    
    def create_parameter(self, material, lib, param_key, group="Other"):
        """Create parameter with auto-positioning"""
        if group not in self.param_counters:
            self.param_counters[group] = 0
        
        # Auto-calculate position based on group and count
        x, y = NodeSpacer.get_param_coords(group, self.param_counters[group])
        
        config = CONTROL_PARAMS.get(param_key, {"default": 1.0, "group": group})
        param = lib.create_material_expression(material, unreal.MaterialExpressionScalarParameter, x, y)
        param.set_editor_property("parameter_name", param_key.replace('_', '').title())
        param.set_editor_property("default_value", config["default"])
        param.set_editor_property("group", config["group"])
        
        self.param_counters[group] += 1
        return param

# ========================================
# CONTROL PARAMETERS CONFIG
# ========================================

CONTROL_PARAMS = {
    "brightness": {"default": 1.0, "group": "Color", "range": (0.0, 5.0)},
    "color_contrast": {"default": 1.0, "group": "Color", "range": (0.0, 5.0)},
    "roughness_contrast": {"default": 1.0, "group": "Roughness", "range": (0.0, 5.0)},
    "hue_shift": {"default": 0.0, "group": "Color", "range": (-1.0, 1.0)},
    "roughness_min": {"default": 0.0, "group": "Roughness", "range": (0.0, 1.0)},
    "roughness_max": {"default": 1.0, "group": "Roughness", "range": (0.0, 1.0)},
    "metal_intensity": {"default": 0.0, "group": "Metallic", "range": (0.0, 1.0)},
    "emission_intensity": {"default": 0.0, "group": "Emission", "range": (0.0, 10.0)},
    "displacement_intensity": {"default": 0.1, "group": "Displacement", "range": (0.0, 10.0)},
    "scale": {"default": 1.0, "group": "UV Controls", "range": (0.01, 100.0)},
    "mfp_scale": {"default": 0.0, "group": "SSS", "range": (0.0, 10.0)},
    "second_roughness": {"default": 0.5, "group": "Roughness", "range": (0.0, 1.0)},
    "second_roughness_weight": {"default": 0.0, "group": "Roughness", "range": (0.0, 1.0)},
    "mix_scale": {"default": 0.001, "group": "Environment", "range": (0.0001, 1.0)}
}

# Material functions library
MATERIAL_FUNCTIONS = {
    "world_aligned_texture": "/Engine/Functions/Engine_MaterialFunctions01/Texturing/WorldAlignedTexture",
    "world_aligned_normal": "/Engine/Functions/Engine_MaterialFunctions01/Texturing/WorldAlignedNormal",
    "texture_variation": "/Engine/Functions/Engine_MaterialFunctions03/Texturing/TextureVariation",
    "hue_shift": "/Engine/Functions/Engine_MaterialFunctions02/HueShift",
    "remap_value": "/Engine/Functions/Engine_MaterialFunctions03/Math/RemapValueRange"
}

# ========================================
# MATERIAL BUILDER CLASS
# ========================================

class SubstrateMaterialBuilder:
    """Smart spacing material builder"""
    
    def __init__(self, custom_paths=None):
        self.config = AutoMattyConfig()
        if custom_paths:
            self._override_paths(custom_paths)
        
        self.lib = unreal.MaterialEditingLibrary
        self.atools = unreal.AssetToolsHelpers.get_asset_tools()
        self.default_normal = AutoMattyUtils.find_default_normal()
        self.param_manager = ParameterManager()
        self.spacer = NodeSpacer()
    
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
        """Build material graph with smart spacing"""
        
        # Get smart coordinates
        coords = self.spacer.get_texture_coords(material_type)
        
        # Add height coordinates if nanite enabled
        if features.get('use_nanite'):
            self.spacer.add_height_coords(coords, material_type)
        
        # Setup UV system with smart spacing
        uv_output = self._setup_uv_system(material, features)
        
        # Create texture samples
        samples = self._create_texture_samples(material, coords, features, uv_output)
        
        # Build material graph based on type
        if material_type.startswith("environment"):
            self._build_environment_graph(material, material_type, samples, features)
        else:
            self._build_standard_graph(material, material_type, samples, features)
    
    # ========================================
    # UV SYSTEM SETUP
    # ========================================
    
    def _setup_uv_system(self, material, features):
        """Setup UV coordinates with smart spacing"""
        
        if features.get('use_triplanar'):
            # For triplanar, use world position instead of texture coordinates
            world_pos_coords = self.spacer.get_uv_coords(0)
            world_pos = self.lib.create_material_expression(material, unreal.MaterialExpressionWorldPosition, *world_pos_coords)
            
            # Scale parameter
            scale_param_coords = self.spacer.get_uv_coords(1)
            scale_param = self.param_manager.create_parameter(material, self.lib, "scale", "UV Controls")
            scale_param.set_editor_property("expression_x", scale_param_coords[0])
            scale_param.set_editor_property("expression_y", scale_param_coords[1])
            
            # Scale the world position
            scale_multiply_coords = self.spacer.get_uv_coords(2)
            scale_multiply = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, *scale_multiply_coords)
            self.lib.connect_material_expressions(world_pos, "", scale_multiply, "A")
            self.lib.connect_material_expressions(scale_param, "", scale_multiply, "B")
            
            # Apply texture variation if enabled
            if features.get('use_tex_var'):
                return self._setup_texture_variation(material, scale_multiply)
            
            return scale_multiply
        else:
            # Standard UV coordinates
            tex_coords_coords = self.spacer.get_uv_coords(0)
            tex_coords = self.lib.create_material_expression(material, unreal.MaterialExpressionTextureCoordinate, *tex_coords_coords)
            
            # Scale parameter
            scale_param = self.param_manager.create_parameter(material, self.lib, "scale", "UV Controls")
            
            # Scale the UVs
            uv_multiply_coords = self.spacer.get_uv_coords(2)
            uv_multiply = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, *uv_multiply_coords)
            self.lib.connect_material_expressions(tex_coords, "", uv_multiply, "A")
            self.lib.connect_material_expressions(scale_param, "", uv_multiply, "B")
            
            # Apply texture variation if enabled
            if features.get('use_tex_var'):
                return self._setup_texture_variation(material, uv_multiply)
            
            return uv_multiply
    
    def _setup_texture_variation(self, material, uv_input):
        """Setup texture variation system"""
        unreal.log(f"🎲 Setting up texture variation system")
        
        # Variation height map parameter
        var_height_coords = self.spacer.get_uv_coords(3)
        var_height_param = self.lib.create_material_expression(material, unreal.MaterialExpressionTextureObjectParameter, *var_height_coords)
        var_height_param.set_editor_property("parameter_name", "VariationHeightMap")
        var_height_param.set_editor_property("group", "Texture Variation")
        
        # Random rotation/scale switch
        random_switch_coords = self.spacer.get_uv_coords(4)
        random_switch = self.lib.create_material_expression(material, unreal.MaterialExpressionStaticBoolParameter, *random_switch_coords)
        random_switch.set_editor_property("parameter_name", "RandomRotationScale")
        random_switch.set_editor_property("default_value", True)
        random_switch.set_editor_property("group", "Texture Variation")
        
        # TextureVariation function
        texture_var_coords = self.spacer.get_uv_coords(5)
        texture_var_func = self._create_material_function(material, "texture_variation", *texture_var_coords)
        
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
    # TEXTURE SAMPLE CREATION
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
        """Create triplanar texture sample"""
        # Texture object parameter
        texture_param = self.lib.create_material_expression(material, unreal.MaterialExpressionTextureObjectParameter, x - 200, y)
        texture_param.set_editor_property("parameter_name", param_name)
        texture_param.set_editor_property("group", self._get_param_group(param_name))
        
        # Choose appropriate world-aligned function
        func_name = "world_aligned_normal" if "Normal" in param_name else "world_aligned_texture"
        world_align_func = self._create_material_function(material, func_name, x, y)
        
        if world_align_func:
            self.lib.connect_material_expressions(texture_param, "", world_align_func, "TextureObject")
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
        
        return node
    
    def _get_param_group(self, param_name):
        """Get parameter group for UI organization"""
        param_lower = param_name.lower()
        
        if any(keyword in param_lower for keyword in ["color", "brightness", "contrast", "hue", "tint"]):
            return "Color"
        elif any(keyword in param_lower for keyword in ["roughness", "rough"]):
            return "Roughness"
        elif any(keyword in param_lower for keyword in ["metal", "metallic", "metalness"]):
            return "Metallic"
        elif any(keyword in param_lower for keyword in ["normal", "norm", "nrm"]):
            return "Normal"
        elif any(keyword in param_lower for keyword in ["height", "displacement", "disp"]):
            return "Displacement"
        elif any(keyword in param_lower for keyword in ["emission", "emissive", "glow"]):
            return "Emission"
        elif any(keyword in param_lower for keyword in ["blend", "mask", "mix", "env"]):
            return "Environment"
        elif any(keyword in param_lower for keyword in ["variation", "random", "var"]):
            return "Texture Variation"
        elif any(keyword in param_lower for keyword in ["uv", "scale", "tiling"]):
            return "UV Controls"
        else:
            return "Other"
    
    # ========================================
    # STANDARD MATERIAL GRAPH
    # ========================================
    
    def _build_standard_graph(self, material, material_type, samples, features):
        """Build standard material graph with smart spacing"""
        
        # Processing chains with smart coordinates
        color_final = self._build_color_chain(material, samples, material_type)
        roughness_final = self._build_roughness_chain(material, samples, material_type, features)
        metallic_final = self._build_metallic_chain(material, samples, material_type)
        ao_final = self._build_ao_chain(material, samples, material_type) if material_type == "orm" else None
        emission_final = self._build_emission_chain(material, samples)
        mfp_final = self._build_sss_chain(material, color_final)
        displacement_final = self._build_displacement_chain(material, samples, features)
        
        # Create substrate slab with smart spacing
        slab_coords = self.spacer.get_processing_coords("slab", 0)
        self._create_substrate_slab(material, slab_coords, {
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
        """Build color processing chain with smart spacing"""
        base_color = samples["Color"]
        
        # Smart coordinates for color processing
        brightness_param = self.param_manager.create_parameter(material, self.lib, "brightness", "Color")
        brightness_coords = self.spacer.get_processing_coords("color", 0)
        brightness_multiply = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, *brightness_coords)
        self._connect_sample(base_color, brightness_multiply, "A")
        self.lib.connect_material_expressions(brightness_param, "", brightness_multiply, "B")
        
        # Contrast
        contrast_param = self.param_manager.create_parameter(material, self.lib, "color_contrast", "Color")
        contrast_coords = self.spacer.get_processing_coords("color", 1)
        color_power = self.lib.create_material_expression(material, unreal.MaterialExpressionPower, *contrast_coords)
        self.lib.connect_material_expressions(brightness_multiply, "", color_power, "Base")
        self.lib.connect_material_expressions(contrast_param, "", color_power, "Exp")
        
        # Hue shift
        hue_param = self.param_manager.create_parameter(material, self.lib, "hue_shift", "Color")
        hue_shift_coords = self.spacer.get_processing_coords("color", 2)
        hue_shift = self._create_material_function(material, "hue_shift", *hue_shift_coords)
        
        if hue_shift:
            self.lib.connect_material_expressions(color_power, "", hue_shift, "Texture")
            self.lib.connect_material_expressions(hue_param, "", hue_shift, "Hue Shift Percentage")
            return hue_shift
        
        return color_power
    
    def _build_roughness_chain(self, material, samples, material_type, features):
        """Build roughness processing chain with smart spacing"""
        # Get roughness input
        if material_type == "orm":
            rough_mask_coords = self.spacer.get_processing_coords("roughness", 0)
            rough_mask = self.lib.create_material_expression(material, unreal.MaterialExpressionComponentMask, *rough_mask_coords)
            rough_mask.set_editor_property("r", False)
            rough_mask.set_editor_property("g", True)
            rough_mask.set_editor_property("b", False)
            rough_mask.set_editor_property("a", False)
            self._connect_sample(samples["ORM"], rough_mask, "")
            roughness_input = rough_mask
        else:
            roughness_input = samples["Roughness"]
        
        # Roughness contrast
        rough_contrast_param = self.param_manager.create_parameter(material, self.lib, "roughness_contrast", "Roughness")
        rough_contrast_coords = self.spacer.get_processing_coords("roughness", 1)
        rough_contrast = self.lib.create_material_expression(material, unreal.MaterialExpressionPower, *rough_contrast_coords)
        self._connect_sample(roughness_input, rough_contrast, "Base")
        self.lib.connect_material_expressions(rough_contrast_param, "", rough_contrast, "Exp")
        
        # Remap roughness range
        rough_min = self.param_manager.create_parameter(material, self.lib, "roughness_min", "Roughness")
        rough_max = self.param_manager.create_parameter(material, self.lib, "roughness_max", "Roughness")
        
        remap_coords = self.spacer.get_processing_coords("roughness", 2)
        remap_rough = self._create_material_function(material, "remap_value", *remap_coords)
        if remap_rough:
            self.lib.connect_material_expressions(rough_contrast, "", remap_rough, "Input")
            self.lib.connect_material_expressions(rough_min, "", remap_rough, "Target Low")
            self.lib.connect_material_expressions(rough_max, "", remap_rough, "Target High")
            return remap_rough
        
        return rough_contrast
    
    def _build_metallic_chain(self, material, samples, material_type):
        """Build metallic processing chain with smart spacing"""
        # Get metallic input
        if material_type == "orm":
            metal_mask_coords = self.spacer.get_processing_coords("metallic", 0)
            metal_mask = self.lib.create_material_expression(material, unreal.MaterialExpressionComponentMask, *metal_mask_coords)
            metal_mask.set_editor_property("r", False)
            metal_mask.set_editor_property("g", False)
            metal_mask.set_editor_property("b", True)
            metal_mask.set_editor_property("a", False)
            self._connect_sample(samples["ORM"], metal_mask, "")
            metallic_input = metal_mask
        else:
            metallic_input = samples["Metallic"]
        
        # Metal intensity
        metal_intensity = self.param_manager.create_parameter(material, self.lib, "metal_intensity", "Metallic")
        metal_final_coords = self.spacer.get_processing_coords("metallic", 1)
        metal_final = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, *metal_final_coords)
        self._connect_sample(metallic_input, metal_final, "A")
        self.lib.connect_material_expressions(metal_intensity, "", metal_final, "B")
        
        return metal_final
    
    def _build_ao_chain(self, material, samples, material_type):
        """Build ambient occlusion chain"""
        if material_type != "orm":
            return None
            
        ao_mask_coords = self.spacer.get_processing_coords("ao", 0)
        ao_mask = self.lib.create_material_expression(material, unreal.MaterialExpressionComponentMask, *ao_mask_coords)
        ao_mask.set_editor_property("r", True)
        ao_mask.set_editor_property("g", False)
        ao_mask.set_editor_property("b", False)
        ao_mask.set_editor_property("a", False)
        self._connect_sample(samples["ORM"], ao_mask, "")
        
        return ao_mask
    
    def _build_emission_chain(self, material, samples):
        """Build emission processing chain with smart spacing"""
        emission_intensity = self.param_manager.create_parameter(material, self.lib, "emission_intensity", "Emission")
        emission_final_coords = self.spacer.get_processing_coords("emission", 0)
        emission_final = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, *emission_final_coords)
        self._connect_sample(samples["Emission"], emission_final, "A")
        self.lib.connect_material_expressions(emission_intensity, "", emission_final, "B")
        
        return emission_final
    
    def _build_sss_chain(self, material, color_input):
        """Build subsurface scattering chain with smart spacing"""
        mfp_color_coords = self.spacer.get_processing_coords("sss", 0)
        mfp_color = self.lib.create_material_expression(material, unreal.MaterialExpressionVectorParameter, *mfp_color_coords)
        mfp_color.set_editor_property("parameter_name", "MFPColor")
        mfp_color.set_editor_property("default_value", unreal.LinearColor(1.0, 0.5, 0.3, 1.0))
        mfp_color.set_editor_property("group", "SSS")
        
        use_diffuse_coords = self.spacer.get_processing_coords("sss", 1)
        use_diffuse_switch = self.lib.create_material_expression(material, unreal.MaterialExpressionStaticSwitchParameter, *use_diffuse_coords)
        use_diffuse_switch.set_editor_property("parameter_name", "UseDiffuseAsMFP")
        use_diffuse_switch.set_editor_property("default_value", True)
        use_diffuse_switch.set_editor_property("group", "SSS")
        
        mfp_scale = self.param_manager.create_parameter(material, self.lib, "mfp_scale", "SSS")
        
        self.lib.connect_material_expressions(color_input, "", use_diffuse_switch, "True")
        self.lib.connect_material_expressions(mfp_color, "", use_diffuse_switch, "False")
        
        return {"switch": use_diffuse_switch, "scale": mfp_scale}
    
    def _build_displacement_chain(self, material, samples, features):
        """Build displacement chain with smart spacing"""
        if not features.get('use_nanite') or "Height" not in samples:
            return None
        
        displacement_intensity = self.param_manager.create_parameter(material, self.lib, "displacement_intensity", "Displacement")
        displacement_coords = self.spacer.get_processing_coords("displacement", 0)
        displacement_multiply = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, *displacement_coords)
        self._connect_sample(samples["Height"], displacement_multiply, "A")
        self.lib.connect_material_expressions(displacement_intensity, "", displacement_multiply, "B")
        
        unreal.log(f"🏔️ Nanite displacement setup complete")
        return displacement_multiply
    
    # ========================================
    # ENVIRONMENT MATERIALS
    # ========================================
    
    def _build_environment_graph(self, material, material_type, samples, features):
        """Build environment material graph with smart spacing"""
        if material_type == "environment_advanced":
            self._build_advanced_environment(material, samples, features)
        else:
            self._build_simple_environment(material, samples, features)
    
    def _build_simple_environment(self, material, samples, features):
        """Build simple environment with smart spacing"""
        # Blend mask
        blend_mask_coords = self.spacer.get_processing_coords("environment", 0)
        blend_mask = self.lib.create_material_expression(material, unreal.MaterialExpressionTextureSampleParameter2D, *blend_mask_coords)
        blend_mask.set_editor_property("parameter_name", "BlendMask")
        blend_mask.set_editor_property("group", "Environment")
        
        # Create lerps with smart spacing
        lerps = {}
        lerp_configs = [
            ("color", "ColorA", "ColorB"),
            ("normal", "NormalA", "NormalB"),
            ("roughness", "RoughnessA", "RoughnessB"),
            ("metallic", "MetallicA", "MetallicB")
        ]
        
        if features.get('use_nanite') and "HeightA" in samples and "HeightB" in samples:
            lerp_configs.append(("height", "HeightA", "HeightB"))
        
        for i, (name, input_a, input_b) in enumerate(lerp_configs):
            if input_a in samples and input_b in samples:
                lerp_coords = self.spacer.get_processing_coords("environment", i + 1)
                lerp = self.lib.create_material_expression(material, unreal.MaterialExpressionLinearInterpolate, *lerp_coords)
                self._connect_sample(samples[input_a], lerp, "A")
                self._connect_sample(samples[input_b], lerp, "B")
                self.lib.connect_material_expressions(blend_mask, "", lerp, "Alpha")
                lerps[name] = lerp
        
        # Color controls
        brightness_param = self.param_manager.create_parameter(material, self.lib, "brightness", "Color")
        brightness_coords = self.spacer.get_processing_coords("environment", len(lerp_configs) + 1)
        brightness_multiply = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, *brightness_coords)
        self.lib.connect_material_expressions(lerps["color"], "", brightness_multiply, "A")
        self.lib.connect_material_expressions(brightness_param, "", brightness_multiply, "B")
        
        # Displacement
        displacement_final = None
        if features.get('use_nanite') and "height" in lerps:
            displacement_intensity = self.param_manager.create_parameter(material, self.lib, "displacement_intensity", "Displacement")
            displacement_coords = self.spacer.get_processing_coords("environment", len(lerp_configs) + 2)
            displacement_multiply = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, *displacement_coords)
            self.lib.connect_material_expressions(lerps["height"], "", displacement_multiply, "A")
            self.lib.connect_material_expressions(displacement_intensity, "", displacement_multiply, "B")
            displacement_final = displacement_multiply
        
        # Create substrate slab
        slab_coords = self.spacer.get_processing_coords("environment", len(lerp_configs) + 3)
        self._create_substrate_slab(material, slab_coords, {
            "diffuse": brightness_multiply,
            "normal": lerps.get("normal"),
            "roughness": lerps.get("roughness"),
            "metallic": lerps.get("metallic"),
            "displacement": displacement_final
        }, features)
    
    def _build_advanced_environment(self, material, samples, features):
        """Build advanced environment with smart spacing"""
        # Create slabs with smart spacing
        slab_a_coords = self.spacer.get_processing_coords("environment", 0)
        slab_b_coords = self.spacer.get_processing_coords("environment", 1)
        
        slab_a = self.lib.create_material_expression(material, unreal.MaterialExpressionSubstrateSlabBSDF, *slab_a_coords)
        slab_b = self.lib.create_material_expression(material, unreal.MaterialExpressionSubstrateSlabBSDF, *slab_b_coords)
        
        # Connect slabs
        self._connect_sample(samples["ColorA"], slab_a, "Diffuse Albedo")
        self._connect_sample(samples["NormalA"], slab_a, "Normal")
        self._connect_sample(samples["RoughnessA"], slab_a, "Roughness")
        self._connect_sample(samples["MetallicA"], slab_a, "F0")
        
        self._connect_sample(samples["ColorB"], slab_b, "Diffuse Albedo")
        self._connect_sample(samples["NormalB"], slab_b, "Normal")
        self._connect_sample(samples["RoughnessB"], slab_b, "Roughness")
        self._connect_sample(samples["MetallicB"], slab_b, "F0")
        
        # World-space mixing
        mixing_pattern = self._create_world_space_mixing(material)
        
        # Displacement
        displacement_final = None
        if features.get('use_nanite') and "HeightA" in samples and "HeightB" in samples:
            height_lerp_coords = self.spacer.get_processing_coords("environment", 2)
            height_lerp = self.lib.create_material_expression(material, unreal.MaterialExpressionLinearInterpolate, *height_lerp_coords)
            self._connect_sample(samples["HeightA"], height_lerp, "A")
            self._connect_sample(samples["HeightB"], height_lerp, "B")
            self.lib.connect_material_expressions(mixing_pattern, "", height_lerp, "Alpha")
            
            displacement_intensity = self.param_manager.create_parameter(material, self.lib, "displacement_intensity", "Displacement")
            displacement_coords = self.spacer.get_processing_coords("environment", 3)
            displacement_multiply = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, *displacement_coords)
            self.lib.connect_material_expressions(height_lerp, "", displacement_multiply, "A")
            self.lib.connect_material_expressions(displacement_intensity, "", displacement_multiply, "B")
            displacement_final = displacement_multiply
        
        # Substrate horizontal mixing
        substrate_mix_coords = self.spacer.get_processing_coords("environment", 4)
        substrate_mix = self.lib.create_material_expression(material, unreal.MaterialExpressionSubstrateHorizontalMixing, *substrate_mix_coords)
        self.lib.connect_material_expressions(slab_a, "", substrate_mix, "Background")
        self.lib.connect_material_expressions(slab_b, "", substrate_mix, "Foreground")
        self.lib.connect_material_expressions(mixing_pattern, "", substrate_mix, "Mix")
        
        # Connect to output
        self.lib.connect_material_property(substrate_mix, "", unreal.MaterialProperty.MP_FRONT_MATERIAL)
        
        # Connect displacement
        if displacement_final:
            self._connect_displacement(material, displacement_final)
    
    def _create_world_space_mixing(self, material):
        """Create world-space mixing pattern with smart spacing"""
        world_pos_coords = self.spacer.get_processing_coords("environment", 5)
        world_pos = self.lib.create_material_expression(material, unreal.MaterialExpressionWorldPosition, *world_pos_coords)
        
        # Extract Z component
        component_coords = self.spacer.get_processing_coords("environment", 6)
        component_mask = self.lib.create_material_expression(material, unreal.MaterialExpressionComponentMask, *component_coords)
        component_mask.set_editor_property("r", False)
        component_mask.set_editor_property("g", False)
        component_mask.set_editor_property("b", True)
        component_mask.set_editor_property("a", False)
        self.lib.connect_material_expressions(world_pos, "", component_mask, "")
        
        # Scale
        scale_param = self.param_manager.create_parameter(material, self.lib, "mix_scale", "Environment")
        scale_coords = self.spacer.get_processing_coords("environment", 7)
        scale_multiply = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, *scale_coords)
        self.lib.connect_material_expressions(component_mask, "", scale_multiply, "A")
        self.lib.connect_material_expressions(scale_param, "", scale_multiply, "B")
        
        # Frac for tiling
        frac_coords = self.spacer.get_processing_coords("environment", 8)
        frac_node = self.lib.create_material_expression(material, unreal.MaterialExpressionFrac, *frac_coords)
        self.lib.connect_material_expressions(scale_multiply, "", frac_node, "")
        
        return frac_node
    
    # ========================================
    # SUBSTRATE SLAB CREATION
    # ========================================
    
    def _create_substrate_slab(self, material, coords, connections, features):
        """Create and connect substrate slab with smart spacing"""
        slab = self.lib.create_material_expression(material, unreal.MaterialExpressionSubstrateSlabBSDF, *coords)
        
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
            second_rough = self.param_manager.create_parameter(material, self.lib, "second_roughness", "Roughness")
            second_weight = self.param_manager.create_parameter(material, self.lib, "second_roughness_weight", "Roughness")
            self.lib.connect_material_expressions(second_rough, "", slab, "Second Roughness")
            self.lib.connect_material_expressions(second_weight, "", slab, "Second Roughness Weight")
        
        # Connect to output
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