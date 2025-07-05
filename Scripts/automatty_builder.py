"""
AutoMatty Material Builder - Substrate material creation with universal plugin support and custom prefix
FINAL VERSION: Proper organization, parameter grouping, comment blocks, world position noise
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

class SubstrateMaterialBuilder:
    """Modular builder for Substrate materials with parameter grouping and visual organization"""
    
    def __init__(self, custom_paths=None):
        self.config = AutoMattyConfig()
        if custom_paths:
            self._override_paths(custom_paths)
        
        self.lib = unreal.MaterialEditingLibrary
        self.atools = unreal.AssetToolsHelpers.get_asset_tools()
    
    def _override_paths(self, custom_paths):
        """Override default paths with user-provided ones"""
        for key, value in custom_paths.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
    
    def create_orm_material(self, base_name=None, custom_path=None, use_second_roughness=False, use_nanite=False):
        """Create ORM packed Substrate material with optional 2nd roughness and nanite support"""
        if not AutoMattyUtils.is_substrate_enabled():
            unreal.log_error("❌ Substrate is not enabled in project settings!")
            return None
        
        # Use custom prefix if no base_name provided
        if base_name is None:
            custom_prefix = AutoMattyConfig.get_custom_material_prefix()
            base_name = f"{custom_prefix}_ORM"
            unreal.log(f"🏷️ Using custom prefix: {base_name}")
        
        folder = custom_path or AutoMattyConfig.get_custom_material_path()
        name = AutoMattyUtils.get_next_asset_name(base_name, folder)
        
        # Create material
        material = self.atools.create_asset(
            name, folder, unreal.Material, unreal.MaterialFactoryNew()
        )
        
        # Enable tessellation for nanite if requested
        if use_nanite:
            # UE 5.6 uses boolean tessellation instead of enum mode
            material.set_editor_property("enable_tessellation", True)
            unreal.log(f"🔧 Enabled tessellation for Nanite support")
        
        # Build the material graph - ORM variant
        self._build_standard_graph(material, material_type="orm", use_second_roughness=use_second_roughness, use_nanite=use_nanite)
        
        # Compile and save
        self.lib.recompile_material(material)
        unreal.EditorAssetLibrary.save_loaded_asset(material)
        
        unreal.log(f"✅ ORM Substrate material '{name}' created in {folder}")
        return material
    
    def create_split_material(self, base_name=None, custom_path=None, use_second_roughness=False, use_nanite=False):
        """Create split texture Substrate material with optional 2nd roughness and nanite support"""
        if not AutoMattyUtils.is_substrate_enabled():
            unreal.log_error("❌ Substrate is not enabled in project settings!")
            return None
        
        # Use custom prefix if no base_name provided
        if base_name is None:
            custom_prefix = AutoMattyConfig.get_custom_material_prefix()
            base_name = f"{custom_prefix}_Split"
            unreal.log(f"🏷️ Using custom prefix: {base_name}")
        
        folder = custom_path or AutoMattyConfig.get_custom_material_path()
        name = AutoMattyUtils.get_next_asset_name(base_name, folder)
        
        # Create material
        material = self.atools.create_asset(
            name, folder, unreal.Material, unreal.MaterialFactoryNew()
        )
        
        # Enable tessellation for nanite if requested
        if use_nanite:
            # UE 5.6 uses boolean tessellation instead of enum mode
            material.set_editor_property("enable_tessellation", True)
            unreal.log(f"🔧 Enabled tessellation for Nanite support")
        
        # Build the material graph - Split variant
        self._build_standard_graph(material, material_type="split", use_second_roughness=use_second_roughness, use_nanite=use_nanite)
        
        # Compile and save
        self.lib.recompile_material(material)
        unreal.EditorAssetLibrary.save_loaded_asset(material)
        
        unreal.log(f"✅ Split Substrate material '{name}' created in {folder}")
        return material
    
    def create_advanced_material(self, base_name=None, custom_path=None, use_second_roughness=False, use_nanite=False):
        """Create advanced Substrate material with built-in UE functions and nanite support"""
        if not AutoMattyUtils.is_substrate_enabled():
            unreal.log_error("❌ Substrate is not enabled in project settings!")
            return None
        
        # Use custom prefix if no base_name provided
        if base_name is None:
            custom_prefix = AutoMattyConfig.get_custom_material_prefix()
            base_name = f"{custom_prefix}_Advanced"
            unreal.log(f"🏷️ Using custom prefix: {base_name}")
        
        folder = custom_path or AutoMattyConfig.get_custom_material_path()
        name = AutoMattyUtils.get_next_asset_name(base_name, folder)
        
        # Create material
        material = self.atools.create_asset(
            name, folder, unreal.Material, unreal.MaterialFactoryNew()
        )
        
        # Enable tessellation for nanite if requested
        if use_nanite:
            # UE 5.6 uses boolean tessellation instead of enum mode
            material.set_editor_property("enable_tessellation", True)
            unreal.log(f"🔧 Enabled tessellation for Nanite support")
        
        # Build the material graph - Advanced variant (same as ORM)
        self._build_standard_graph(material, material_type="orm", use_second_roughness=use_second_roughness, use_nanite=use_nanite)
        
        # Compile and save
        self.lib.recompile_material(material)
        unreal.EditorAssetLibrary.save_loaded_asset(material)
        
        unreal.log(f"✅ Advanced Substrate material '{name}' created in {folder}")
        return material
    
    def create_environment_material(self, base_name=None, custom_path=None):
        """Create environment material with proper world-space noise and clean organization"""
        if not AutoMattyUtils.is_substrate_enabled():
            unreal.log_error("❌ Substrate is not enabled in project settings!")
            return None
        
        # Use custom prefix if no base_name provided
        if base_name is None:
            custom_prefix = AutoMattyConfig.get_custom_material_prefix()
            base_name = f"{custom_prefix}_Environment"
            unreal.log(f"🏷️ Using custom prefix: {base_name}")
        
        folder = custom_path or AutoMattyConfig.get_custom_material_path()
        name = AutoMattyUtils.get_next_asset_name(base_name, folder)
        
        # Create material
        material = self.atools.create_asset(
            name, folder, unreal.Material, unreal.MaterialFactoryNew()
        )
        
        # Build the properly organized environment graph
        self._build_environment_graph_fixed(material)
        
        # Compile and save
        self.lib.recompile_material(material)
        unreal.EditorAssetLibrary.save_loaded_asset(material)
        
        unreal.log(f"✅ Environment Substrate material '{name}' created in {folder}")
        return material
    
    def _create_comment_block(self, material, text, x, y, width=None, height=None, color=None):
        """Create a visual comment block for material graph organization"""
        if color is None:
            color = unreal.LinearColor(0.2, 0.8, 0.2, 0.8)  # Default green
        
        comment = self.lib.create_material_expression(
            material, unreal.MaterialExpressionComment, x, y
        )
        comment.set_editor_property("text", text)
        comment.set_editor_property("comment_color", color)
        comment.set_editor_property("font_size", 14)
        comment.set_editor_property("comment_bubble_visible_in_details_panel", True)
        
        return comment
    
    def _build_standard_graph(self, material, material_type="orm", use_second_roughness=False, use_nanite=False):
        """Build standardized material graph - unified for ORM, Split, and Advanced"""
        default_normal = AutoMattyUtils.find_default_normal()
        
        # ========================================
        # COMMENT BLOCKS FOR VISUAL ORGANIZATION
        # ========================================
        self._create_comment_block(material, "TEXTURES", -1500, -100, 
                                 color=unreal.LinearColor(0.3, 0.7, 1.0, 0.8))  # Blue
        self._create_comment_block(material, "COLOR CONTROLS", -1200, -100,
                                 color=unreal.LinearColor(1.0, 0.8, 0.3, 0.8))  # Orange
        self._create_comment_block(material, "ROUGHNESS CONTROLS", -1200, -300,
                                 color=unreal.LinearColor(0.8, 0.3, 1.0, 0.8))  # Purple
        self._create_comment_block(material, "METALLIC & AO", -1200, -550,
                                 color=unreal.LinearColor(0.7, 0.7, 0.7, 0.8))  # Gray
        self._create_comment_block(material, "EMISSION & SSS", -1200, -700,
                                 color=unreal.LinearColor(1.0, 0.3, 0.3, 0.8))  # Red
        self._create_comment_block(material, "SUBSTRATE SLAB", -300, -300,
                                 color=unreal.LinearColor(0.2, 0.8, 0.2, 0.8))  # Green
        
        if use_nanite:
            self._create_comment_block(material, "NANITE DISPLACEMENT", -1200, -850,
                                     color=unreal.LinearColor(1.0, 0.2, 1.0, 0.8))  # Magenta
        
        # ========================================
        # TEXTURES
        # ========================================
        samples = {}
        
        if material_type == "orm":
            coords = {
                "Color": (-1400, -200),
                "ORM": (-1400, -400),
                "Normal": (-1400, -600),
                "Emission": (-1400, -700),
            }
        else:  # split
            coords = {
                "Color": (-1400, -200),
                "Roughness": (-1400, -400),
                "Metallic": (-1400, -500),
                "Normal": (-1400, -600),
                "Emission": (-1400, -700),
            }
        
        # Add height texture for nanite displacement
        if use_nanite:
            coords["Height"] = (-1400, -800)
        
        for pname, (x, y) in coords.items():
            node = self.lib.create_material_expression(
                material, unreal.MaterialExpressionTextureSampleParameter2D, x, y
            )
            node.set_editor_property("parameter_name", pname)
            if pname == "Normal":
                node.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
                if default_normal:
                    node.set_editor_property("texture", default_normal)
            samples[pname] = node
        
        # ========================================
        # COLOR CONTROLS
        # ========================================
        color_contrast_param = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1100, -150
        )
        color_contrast_param.set_editor_property("parameter_name", "ColorContrast")
        color_contrast_param.set_editor_property("default_value", 1.0)
        color_contrast_param.set_editor_property("group", "Color")
        
        color_power = self.lib.create_material_expression(
            material, unreal.MaterialExpressionPower, -800, -200
        )
        self.lib.connect_material_expressions(samples["Color"], "", color_power, "Base")
        self.lib.connect_material_expressions(color_contrast_param, "", color_power, "Exp")
        
        # ========================================
        # ROUGHNESS CONTROLS
        # ========================================
        if material_type == "orm":
            # Extract roughness from ORM (G channel)
            rough_mask = self.lib.create_material_expression(
                material, unreal.MaterialExpressionComponentMask, -1100, -350
            )
            rough_mask.set_editor_property("r", False)
            rough_mask.set_editor_property("g", True)
            rough_mask.set_editor_property("b", False)
            rough_mask.set_editor_property("a", False)
            self.lib.connect_material_expressions(samples["ORM"], "", rough_mask, "")
            roughness_input = rough_mask
        else:  # split
            roughness_input = samples["Roughness"]
        
        # Roughness min/max remapping
        rough_min_param = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1100, -450
        )
        rough_min_param.set_editor_property("parameter_name", "RoughnessMin")
        rough_min_param.set_editor_property("default_value", 0.0)
        rough_min_param.set_editor_property("group", "Roughness")
        
        rough_max_param = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1100, -500
        )
        rough_max_param.set_editor_property("parameter_name", "RoughnessMax")
        rough_max_param.set_editor_property("default_value", 1.0)
        rough_max_param.set_editor_property("group", "Roughness")
        
        # RemapValueRange function for roughness
        remap_roughness = self.lib.create_material_expression(
            material, unreal.MaterialExpressionMaterialFunctionCall, -700, -400
        )
        remap_function = unreal.EditorAssetLibrary.load_asset("/Engine/Functions/Engine_MaterialFunctions03/Math/RemapValueRange")
        if remap_function:
            remap_roughness.set_editor_property("material_function", remap_function)
            self.lib.connect_material_expressions(roughness_input, "", remap_roughness, "Input")
            self.lib.connect_material_expressions(rough_min_param, "", remap_roughness, "Target Low")
            self.lib.connect_material_expressions(rough_max_param, "", remap_roughness, "Target High")
        else:
            remap_roughness = roughness_input
        
        # ========================================
        # METALLIC CONTROLS
        # ========================================
        if material_type == "orm":
            # Extract metallic from ORM (B channel)
            metal_mask = self.lib.create_material_expression(
                material, unreal.MaterialExpressionComponentMask, -1100, -550
            )
            metal_mask.set_editor_property("r", False)
            metal_mask.set_editor_property("g", False)
            metal_mask.set_editor_property("b", True)
            metal_mask.set_editor_property("a", False)
            self.lib.connect_material_expressions(samples["ORM"], "", metal_mask, "")
            metallic_input = metal_mask
        else:  # split
            metallic_input = samples["Metallic"]
        
        # Metal intensity control
        metal_intensity = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1100, -600
        )
        metal_intensity.set_editor_property("parameter_name", "MetalIntensity")
        metal_intensity.set_editor_property("default_value", 1.0)
        metal_intensity.set_editor_property("group", "Metallic")
        
        metal_final = self.lib.create_material_expression(
            material, unreal.MaterialExpressionMultiply, -700, -550
        )
        self.lib.connect_material_expressions(metallic_input, "", metal_final, "A")
        self.lib.connect_material_expressions(metal_intensity, "", metal_final, "B")
        
        # ========================================
        # AO CONTROLS (ORM only)
        # ========================================
        ao_final = None
        if material_type == "orm":
            # AO mask (R channel)
            ao_mask = self.lib.create_material_expression(
                material, unreal.MaterialExpressionComponentMask, -1100, -650
            )
            ao_mask.set_editor_property("r", True)
            ao_mask.set_editor_property("g", False)
            ao_mask.set_editor_property("b", False)
            ao_mask.set_editor_property("a", False)
            self.lib.connect_material_expressions(samples["ORM"], "", ao_mask, "")
            ao_final = ao_mask
        
        # ========================================
        # EMISSION CONTROLS
        # ========================================
        emission_intensity = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1100, -700
        )
        emission_intensity.set_editor_property("parameter_name", "EmissionIntensity")
        emission_intensity.set_editor_property("default_value", 0.0)
        emission_intensity.set_editor_property("group", "Emission")
        
        emission_final = self.lib.create_material_expression(
            material, unreal.MaterialExpressionMultiply, -700, -650
        )
        self.lib.connect_material_expressions(samples["Emission"], "", emission_final, "A")
        self.lib.connect_material_expressions(emission_intensity, "", emission_final, "B")
        
        # ========================================
        # MFP/SSS CONTROLS
        # ========================================
        mfp_color_param = self.lib.create_material_expression(
            material, unreal.MaterialExpressionVectorParameter, -1100, -750
        )
        mfp_color_param.set_editor_property("parameter_name", "MFPColor")
        mfp_color_param.set_editor_property("default_value", unreal.LinearColor(1.0, 0.5, 0.3, 1.0))
        mfp_color_param.set_editor_property("group", "SSS")

        use_diffuse_switch = self.lib.create_material_expression(
            material, unreal.MaterialExpressionStaticSwitchParameter, -700, -750
        )
        use_diffuse_switch.set_editor_property("parameter_name", "UseDiffuseAsMFP")
        use_diffuse_switch.set_editor_property("default_value", True)
        use_diffuse_switch.set_editor_property("group", "SSS")

        mfp_scale = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1100, -800
        )
        mfp_scale.set_editor_property("parameter_name", "MFPScale")
        mfp_scale.set_editor_property("default_value", 1.0)
        mfp_scale.set_editor_property("group", "SSS")

        self.lib.connect_material_expressions(color_power, "", use_diffuse_switch, "True")
        self.lib.connect_material_expressions(mfp_color_param, "", use_diffuse_switch, "False")
        
        # ========================================
        # NANITE DISPLACEMENT CONTROLS
        # ========================================
        displacement_final = None
        if use_nanite:
            displacement_intensity = self.lib.create_material_expression(
                material, unreal.MaterialExpressionScalarParameter, -1100, -850
            )
            displacement_intensity.set_editor_property("parameter_name", "DisplacementIntensity")
            displacement_intensity.set_editor_property("default_value", 1.0)
            displacement_intensity.set_editor_property("group", "Displacement")
            
            # Convert height to vector for world position offset
            height_to_vector = self.lib.create_material_expression(
                material, unreal.MaterialExpressionAppendVector, -800, -800
            )
            
            # Zero values for X and Y (no horizontal displacement)
            zero_constant = self.lib.create_material_expression(
                material, unreal.MaterialExpressionConstant, -900, -750
            )
            zero_constant.set_editor_property("r", 0.0)
            
            # Height × intensity for Z displacement
            displacement_multiply = self.lib.create_material_expression(
                material, unreal.MaterialExpressionMultiply, -900, -850
            )
            self.lib.connect_material_expressions(samples["Height"], "", displacement_multiply, "A")
            self.lib.connect_material_expressions(displacement_intensity, "", displacement_multiply, "B")
            
            # Create vector (0, 0, height×intensity)
            self.lib.connect_material_expressions(zero_constant, "", height_to_vector, "A")
            self.lib.connect_material_expressions(displacement_multiply, "", height_to_vector, "B")
            
            displacement_final = height_to_vector
        
        # ========================================
        # SECOND ROUGHNESS CONTROLS
        # ========================================
        second_roughness_params = {}
        if use_second_roughness:
            second_roughness_param = self.lib.create_material_expression(
                material, unreal.MaterialExpressionScalarParameter, -500, -450
            )
            second_roughness_param.set_editor_property("parameter_name", "SecondRoughness")
            second_roughness_param.set_editor_property("default_value", 0.5)
            second_roughness_param.set_editor_property("group", "Roughness")
            second_roughness_params["SecondRoughness"] = second_roughness_param
            
            second_roughness_weight = self.lib.create_material_expression(
                material, unreal.MaterialExpressionScalarParameter, -500, -500
            )
            second_roughness_weight.set_editor_property("parameter_name", "SecondRoughnessWeight")
            second_roughness_weight.set_editor_property("default_value", 0.0)
            second_roughness_weight.set_editor_property("group", "Roughness")
            second_roughness_params["SecondRoughnessWeight"] = second_roughness_weight
        
        # ========================================
        # SUBSTRATE SLAB
        # ========================================
        slab = self.lib.create_material_expression(
            material, unreal.MaterialExpressionSubstrateSlabBSDF, -200, -400
        )
        
        # Connect everything
        self.lib.connect_material_expressions(color_power, "", slab, "Diffuse Albedo")
        self.lib.connect_material_expressions(remap_roughness, "", slab, "Roughness")
        self.lib.connect_material_expressions(metal_final, "", slab, "F0")
        self.lib.connect_material_expressions(samples["Normal"], "", slab, "Normal")
        self.lib.connect_material_expressions(use_diffuse_switch, "", slab, "SSS MFP")
        self.lib.connect_material_expressions(mfp_scale, "", slab, "SSS MFP Scale")
        self.lib.connect_material_expressions(emission_final, "", slab, "Emission Color")
        
        # Connect AO if available (ORM only)
        if ao_final:
            self.lib.connect_material_expressions(ao_final, "", slab, "AmbientOcclusion")
        
        # Connect second roughness parameters if enabled
        if use_second_roughness:
            self.lib.connect_material_expressions(second_roughness_params["SecondRoughness"], "", slab, "Second Roughness")
            self.lib.connect_material_expressions(second_roughness_params["SecondRoughnessWeight"], "", slab, "Second Roughness Weight")
        
        # Connect to outputs
        self.lib.connect_material_property(slab, "", unreal.MaterialProperty.MP_FRONT_MATERIAL)
        
        # Connect displacement for nanite if enabled
        if use_nanite and displacement_final:
            self.lib.connect_material_property(displacement_final, "", unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
    
    def _build_environment_graph_fixed(self, material):
        """Build environment material with proper organization and world-space noise"""
        default_normal = AutoMattyUtils.find_default_normal()
        
        # ========================================
        # COMMENT BLOCKS FOR VISUAL ORGANIZATION
        # ========================================
        self._create_comment_block(material, "UV/TEXTURE VARIATION", -2100, -100,
                                 color=unreal.LinearColor(0.3, 0.7, 1.0, 0.8))  # Blue
        self._create_comment_block(material, "NOISE GENERATION", -1800, 300,
                                 color=unreal.LinearColor(1.0, 1.0, 0.3, 0.8))  # Yellow
        self._create_comment_block(material, "SLAB A TEXTURES", -1700, -500,
                                 color=unreal.LinearColor(0.3, 1.0, 0.3, 0.8))  # Green
        self._create_comment_block(material, "SLAB B TEXTURES", -1700, -1300,
                                 color=unreal.LinearColor(0.3, 1.0, 0.8, 0.8))  # Cyan
        self._create_comment_block(material, "COLOR A CONTROLS", -1300, -400,
                                 color=unreal.LinearColor(1.0, 0.8, 0.3, 0.8))  # Orange
        self._create_comment_block(material, "COLOR B CONTROLS", -1300, -1200,
                                 color=unreal.LinearColor(1.0, 0.6, 0.1, 0.8))  # Dark Orange
        self._create_comment_block(material, "ROUGHNESS A CONTROLS", -1100, -700,
                                 color=unreal.LinearColor(0.8, 0.3, 1.0, 0.8))  # Purple
        self._create_comment_block(material, "ROUGHNESS B CONTROLS", -1100, -1500,
                                 color=unreal.LinearColor(0.6, 0.1, 0.8, 0.8))  # Dark Purple
        self._create_comment_block(material, "SUBSTRATE SLABS", -300, -800,
                                 color=unreal.LinearColor(0.2, 0.8, 0.2, 0.8))  # Green
        self._create_comment_block(material, "SLAB MIXING", 100, -1300,
                                 color=unreal.LinearColor(1.0, 0.3, 0.3, 0.8))  # Red
        
        # ========================================
        # UV/TEXTURE VARIATION
        # ========================================
        base_uv = self.lib.create_material_expression(
            material, unreal.MaterialExpressionTextureCoordinate, -2000, 0
        )
        
        # World position for noise (FIXED!)
        world_pos = self.lib.create_material_expression(
            material, unreal.MaterialExpressionWorldPosition, -2000, 400
        )
        
        # ========================================
        # NOISE
        # ========================================
        # Primary noise layer
        noise_scale_1 = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1600, 400
        )
        noise_scale_1.set_editor_property("parameter_name", "NoiseScale1")
        noise_scale_1.set_editor_property("default_value", 500.0)  # World scale
        noise_scale_1.set_editor_property("group", "Noise")
        
        noise_multiply_1 = self.lib.create_material_expression(
            material, unreal.MaterialExpressionDivide, -1400, 400
        )
        self.lib.connect_material_expressions(world_pos, "", noise_multiply_1, "A")
        self.lib.connect_material_expressions(noise_scale_1, "", noise_multiply_1, "B")
        
        noise_1 = self.lib.create_material_expression(
            material, unreal.MaterialExpressionNoise, -1200, 400
        )
        noise_1.set_editor_property("quality", 4)
        noise_1.set_editor_property("noise_function", unreal.NoiseFunction.NOISEFUNCTION_SIMPLEX_TEX)
        self.lib.connect_material_expressions(noise_multiply_1, "", noise_1, "Position")
        
        # Secondary detail noise
        noise_scale_2 = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1600, 600
        )
        noise_scale_2.set_editor_property("parameter_name", "NoiseScale2")
        noise_scale_2.set_editor_property("default_value", 150.0)  # World scale
        noise_scale_2.set_editor_property("group", "Noise")
        
        noise_multiply_2 = self.lib.create_material_expression(
            material, unreal.MaterialExpressionDivide, -1400, 600
        )
        self.lib.connect_material_expressions(world_pos, "", noise_multiply_2, "A")
        self.lib.connect_material_expressions(noise_scale_2, "", noise_multiply_2, "B")
        
        noise_2 = self.lib.create_material_expression(
            material, unreal.MaterialExpressionNoise, -1200, 600
        )
        noise_2.set_editor_property("quality", 4)
        noise_2.set_editor_property("noise_function", unreal.NoiseFunction.NOISEFUNCTION_GRADIENT_TEX)
        self.lib.connect_material_expressions(noise_multiply_2, "", noise_2, "Position")
        
        # Detail noise intensity
        detail_intensity = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1000, 650
        )
        detail_intensity.set_editor_property("parameter_name", "DetailNoiseIntensity")
        detail_intensity.set_editor_property("default_value", 0.3)
        detail_intensity.set_editor_property("group", "Noise")
        
        detail_scaled = self.lib.create_material_expression(
            material, unreal.MaterialExpressionMultiply, -800, 600
        )
        self.lib.connect_material_expressions(noise_2, "", detail_scaled, "A")
        self.lib.connect_material_expressions(detail_intensity, "", detail_scaled, "B")
        
        # Combine noises
        noise_combined = self.lib.create_material_expression(
            material, unreal.MaterialExpressionAdd, -600, 500
        )
        self.lib.connect_material_expressions(noise_1, "", noise_combined, "A")
        self.lib.connect_material_expressions(detail_scaled, "", noise_combined, "B")
        
        # Noise contrast
        noise_contrast = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1000, 500
        )
        noise_contrast.set_editor_property("parameter_name", "NoiseContrast")
        noise_contrast.set_editor_property("default_value", 3.0)
        noise_contrast.set_editor_property("group", "Noise")
        
        noise_power = self.lib.create_material_expression(
            material, unreal.MaterialExpressionPower, -400, 500
        )
        self.lib.connect_material_expressions(noise_combined, "", noise_power, "Base")
        self.lib.connect_material_expressions(noise_contrast, "", noise_power, "Exp")
        
        # Clamp final noise
        noise_final = self.lib.create_material_expression(
            material, unreal.MaterialExpressionClamp, -200, 500
        )
        noise_final.set_editor_property("min_default", 0.0)
        noise_final.set_editor_property("max_default", 1.0)
        self.lib.connect_material_expressions(noise_power, "", noise_final, "")
        
        # ========================================
        # TEXTURES - SLAB A
        # ========================================
        slab_a_textures = {}
        slab_a_coords = {
            "ColorA": (-1600, -400),
            "NormalA": (-1600, -600),
            "RoughnessA": (-1600, -800),
            "MetallicA": (-1600, -1000),
        }
        
        for param_name, (x, y) in slab_a_coords.items():
            tex_node = self.lib.create_material_expression(
                material, unreal.MaterialExpressionTextureSampleParameter2D, x, y
            )
            tex_node.set_editor_property("parameter_name", param_name)
            if "Normal" in param_name:
                tex_node.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
                if default_normal:
                    tex_node.set_editor_property("texture", default_normal)
            slab_a_textures[param_name] = tex_node
        
        # ========================================
        # TEXTURES - SLAB B
        # ========================================
        slab_b_textures = {}
        slab_b_coords = {
            "ColorB": (-1600, -1200),
            "NormalB": (-1600, -1400),
            "RoughnessB": (-1600, -1600),
            "MetallicB": (-1600, -1800),
        }
        
        for param_name, (x, y) in slab_b_coords.items():
            tex_node = self.lib.create_material_expression(
                material, unreal.MaterialExpressionTextureSampleParameter2D, x, y
            )
            tex_node.set_editor_property("parameter_name", param_name)
            if "Normal" in param_name:
                tex_node.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
                if default_normal:
                    tex_node.set_editor_property("texture", default_normal)
            slab_b_textures[param_name] = tex_node
        
        # ========================================
        # COLOR A CONTROLS
        # ========================================
        color_a_contrast = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1200, -350
        )
        color_a_contrast.set_editor_property("parameter_name", "ColorAContrast")
        color_a_contrast.set_editor_property("default_value", 1.0)
        color_a_contrast.set_editor_property("group", "ColorA")
        
        color_a_power = self.lib.create_material_expression(
            material, unreal.MaterialExpressionPower, -1000, -400
        )
        self.lib.connect_material_expressions(slab_a_textures["ColorA"], "", color_a_power, "Base")
        self.lib.connect_material_expressions(color_a_contrast, "", color_a_power, "Exp")
        
        color_a_tint = self.lib.create_material_expression(
            material, unreal.MaterialExpressionVectorParameter, -1200, -450
        )
        color_a_tint.set_editor_property("parameter_name", "ColorATint")
        color_a_tint.set_editor_property("default_value", unreal.LinearColor(1.0, 1.0, 1.0, 1.0))
        color_a_tint.set_editor_property("group", "ColorA")
        
        color_a_final = self.lib.create_material_expression(
            material, unreal.MaterialExpressionMultiply, -800, -400
        )
        self.lib.connect_material_expressions(color_a_power, "", color_a_final, "A")
        self.lib.connect_material_expressions(color_a_tint, "", color_a_final, "B")
        
        # ========================================
        # COLOR B CONTROLS
        # ========================================
        color_b_contrast = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1200, -1150
        )
        color_b_contrast.set_editor_property("parameter_name", "ColorBContrast")
        color_b_contrast.set_editor_property("default_value", 1.0)
        color_b_contrast.set_editor_property("group", "ColorB")
        
        color_b_power = self.lib.create_material_expression(
            material, unreal.MaterialExpressionPower, -1000, -1200
        )
        self.lib.connect_material_expressions(slab_b_textures["ColorB"], "", color_b_power, "Base")
        self.lib.connect_material_expressions(color_b_contrast, "", color_b_power, "Exp")
        
        color_b_tint = self.lib.create_material_expression(
            material, unreal.MaterialExpressionVectorParameter, -1200, -1250
        )
        color_b_tint.set_editor_property("parameter_name", "ColorBTint")
        color_b_tint.set_editor_property("default_value", unreal.LinearColor(1.0, 1.0, 1.0, 1.0))
        color_b_tint.set_editor_property("group", "ColorB")
        
        color_b_final = self.lib.create_material_expression(
            material, unreal.MaterialExpressionMultiply, -800, -1200
        )
        self.lib.connect_material_expressions(color_b_power, "", color_b_final, "A")
        self.lib.connect_material_expressions(color_b_tint, "", color_b_final, "B")
        
        # ========================================
        # ROUGHNESS A CONTROLS
        # ========================================
        rough_a_min = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1000, -750
        )
        rough_a_min.set_editor_property("parameter_name", "RoughnessAMin")
        rough_a_min.set_editor_property("default_value", 0.0)
        rough_a_min.set_editor_property("group", "RoughnessA")
        
        rough_a_max = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1000, -800
        )
        rough_a_max.set_editor_property("parameter_name", "RoughnessAMax")
        rough_a_max.set_editor_property("default_value", 1.0)
        rough_a_max.set_editor_property("group", "RoughnessA")
        
        remap_rough_a = self.lib.create_material_expression(
            material, unreal.MaterialExpressionMaterialFunctionCall, -600, -800
        )
        remap_function = unreal.EditorAssetLibrary.load_asset("/Engine/Functions/Engine_MaterialFunctions03/Math/RemapValueRange")
        if remap_function:
            remap_rough_a.set_editor_property("material_function", remap_function)
            self.lib.connect_material_expressions(slab_a_textures["RoughnessA"], "", remap_rough_a, "Input")
            self.lib.connect_material_expressions(rough_a_min, "", remap_rough_a, "Target Low")
            self.lib.connect_material_expressions(rough_a_max, "", remap_rough_a, "Target High")
        else:
            remap_rough_a = slab_a_textures["RoughnessA"]
        
        # ========================================
        # ROUGHNESS B CONTROLS
        # ========================================
        rough_b_min = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1000, -1550
        )
        rough_b_min.set_editor_property("parameter_name", "RoughnessBMin")
        rough_b_min.set_editor_property("default_value", 0.0)
        rough_b_min.set_editor_property("group", "RoughnessB")
        
        rough_b_max = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1000, -1600
        )
        rough_b_max.set_editor_property("parameter_name", "RoughnessBMax")
        rough_b_max.set_editor_property("default_value", 1.0)
        rough_b_max.set_editor_property("group", "RoughnessB")
        
        remap_rough_b = self.lib.create_material_expression(
            material, unreal.MaterialExpressionMaterialFunctionCall, -600, -1600
        )
        if remap_function:
            remap_rough_b.set_editor_property("material_function", remap_function)
            self.lib.connect_material_expressions(slab_b_textures["RoughnessB"], "", remap_rough_b, "Input")
            self.lib.connect_material_expressions(rough_b_min, "", remap_rough_b, "Target Low")
            self.lib.connect_material_expressions(rough_b_max, "", remap_rough_b, "Target High")
        else:
            remap_rough_b = slab_b_textures["RoughnessB"]
        
        # ========================================
        # SUBSTRATE SLABS
        # ========================================
        slab_a = self.lib.create_material_expression(
            material, unreal.MaterialExpressionSubstrateSlabBSDF, -200, -800
        )
        slab_b = self.lib.create_material_expression(
            material, unreal.MaterialExpressionSubstrateSlabBSDF, -200, -1400
        )
        
        # Connect Slab A
        self.lib.connect_material_expressions(color_a_final, "", slab_a, "Diffuse Albedo")
        self.lib.connect_material_expressions(slab_a_textures["NormalA"], "", slab_a, "Normal")
        self.lib.connect_material_expressions(remap_rough_a, "", slab_a, "Roughness")
        self.lib.connect_material_expressions(slab_a_textures["MetallicA"], "", slab_a, "F0")
        
        # Connect Slab B
        self.lib.connect_material_expressions(color_b_final, "", slab_b, "Diffuse Albedo")
        self.lib.connect_material_expressions(slab_b_textures["NormalB"], "", slab_b, "Normal")
        self.lib.connect_material_expressions(remap_rough_b, "", slab_b, "Roughness")
        self.lib.connect_material_expressions(slab_b_textures["MetallicB"], "", slab_b, "F0")
        
        # Mix the slabs
        slab_mix = self.lib.create_material_expression(
            material, unreal.MaterialExpressionSubstrateHorizontalMixing, 200, -1200
        )
        self.lib.connect_material_expressions(slab_a, "", slab_mix, "Foreground")
        self.lib.connect_material_expressions(slab_b, "", slab_mix, "Background")
        self.lib.connect_material_expressions(noise_final, "", slab_mix, "Mix")
        
        # Connect to output
        self.lib.connect_material_property(slab_mix, "", unreal.MaterialProperty.MP_FRONT_MATERIAL)
        
        unreal.log("✅ Environment material created with proper world-space noise and organized parameters")

# Usage functions with new parameters
def create_orm_material_with_second_roughness():
    """Create ORM material with 2nd roughness option"""
    builder = SubstrateMaterialBuilder()
    return builder.create_orm_material(use_second_roughness=True)

def create_split_material_with_second_roughness():
    """Create split material with 2nd roughness option"""
    builder = SubstrateMaterialBuilder()
    return builder.create_split_material(use_second_roughness=True)

def create_advanced_material_with_second_roughness():
    """Create advanced material with 2nd roughness option"""
    builder = SubstrateMaterialBuilder()
    return builder.create_advanced_material(use_second_roughness=True)

def create_orm_material_with_nanite():
    """Create ORM material with nanite displacement support"""
    builder = SubstrateMaterialBuilder()
    return builder.create_orm_material(use_nanite=True)

def create_split_material_with_nanite():
    """Create split material with nanite displacement support"""
    builder = SubstrateMaterialBuilder()
    return builder.create_split_material(use_nanite=True)

def create_advanced_material_with_nanite():
    """Create advanced material with nanite displacement support"""
    builder = SubstrateMaterialBuilder()
    return builder.create_advanced_material(use_nanite=True)

def create_orm_material_full_featured():
    """Create ORM material with both 2nd roughness and nanite support"""
    builder = SubstrateMaterialBuilder()
    return builder.create_orm_material(use_second_roughness=True, use_nanite=True)

def create_split_material_full_featured():
    """Create split material with both 2nd roughness and nanite support"""
    builder = SubstrateMaterialBuilder()
    return builder.create_split_material(use_second_roughness=True, use_nanite=True)

def create_advanced_material_full_featured():
    """Create advanced material with both 2nd roughness and nanite support"""
    builder = SubstrateMaterialBuilder()
    return builder.create_advanced_material(use_second_roughness=True, use_nanite=True)

def create_environment_material_fixed():
    """Create the fixed environment material"""
    builder = SubstrateMaterialBuilder()
    return builder.create_environment_material()

# Execute based on what you want
if __name__ == "__main__":
    builder = SubstrateMaterialBuilder()
    builder.create_environment_material()