"""
AutoMatty Material Builder - Substrate material creation with universal plugin support and custom prefix
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
    """Modular builder for Substrate materials"""
    
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
    
    def create_orm_material(self, base_name=None, custom_path=None):
        """Create ORM packed Substrate material"""
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
        
        # Build the material graph
        self._build_orm_graph(material)
        
        # Compile and save
        self.lib.recompile_material(material)
        unreal.EditorAssetLibrary.save_loaded_asset(material)
        
        unreal.log(f"✅ ORM Substrate material '{name}' created in {folder}")
        return material
    
    def create_split_material(self, base_name=None, custom_path=None):
        """Create split texture Substrate material"""
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
        
        # Build the material graph
        self._build_split_graph(material)
        
        # Compile and save
        self.lib.recompile_material(material)
        unreal.EditorAssetLibrary.save_loaded_asset(material)
        
        unreal.log(f"✅ Split Substrate material '{name}' created in {folder}")
        return material
    
    def create_advanced_material(self, base_name=None, custom_path=None):
        """Create advanced Substrate material with built-in UE functions"""
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
        
        # Build the material graph using built-in nodes
        self._build_advanced_graph_builtin(material)
        
        # Compile and save
        self.lib.recompile_material(material)
        unreal.EditorAssetLibrary.save_loaded_asset(material)
        
        unreal.log(f"✅ Advanced Substrate material '{name}' created in {folder}")
        return material
    
    def create_environment_material(self, base_name=None, custom_path=None):
        """Create advanced environment material with dual slabs and noise mixing"""
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
        
        # Build the complex environment graph
        self._build_environment_graph(material)
        
        # Compile and save
        self.lib.recompile_material(material)
        unreal.EditorAssetLibrary.save_loaded_asset(material)
        
        unreal.log(f"✅ Environment Substrate material '{name}' created in {folder}")
        return material
    
    def _build_orm_graph(self, material):
        """Build ORM material node graph - FIXED CHANNEL MASKS"""
        default_normal = AutoMattyUtils.find_default_normal()
        
        # Create texture sample nodes
        samples = {}
        coords = {
            "Color": (-400, 200),
            "ORM": (-400, 0),
            "Normal": (-400, -200),
        }
        
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
        
        # Create Substrate Slab BSDF
        slab = self.lib.create_material_expression(
            material, unreal.MaterialExpressionSubstrateSlabBSDF, 0, 0
        )
        
        # Connect Color → Diffuse Albedo
        self.lib.connect_material_expressions(samples["Color"], "", slab, "Diffuse Albedo")
        
        # Split ORM channels - FIXED VERSION
        rough_mask = self.lib.create_material_expression(
            material, unreal.MaterialExpressionComponentMask, -200, 50
        )
        # Explicitly set all channels - only G should be True
        rough_mask.set_editor_property("r", False)
        rough_mask.set_editor_property("g", True)   # Roughness = Green channel
        rough_mask.set_editor_property("b", False)
        rough_mask.set_editor_property("a", False)
        self.lib.connect_material_expressions(samples["ORM"], "", rough_mask, "")
        self.lib.connect_material_expressions(rough_mask, "", slab, "Roughness")
        
        metal_mask = self.lib.create_material_expression(
            material, unreal.MaterialExpressionComponentMask, -200, -150
        )
        # Explicitly set all channels - only B should be True
        metal_mask.set_editor_property("r", False)
        metal_mask.set_editor_property("g", False)
        metal_mask.set_editor_property("b", True)   # Metallic = Blue channel
        metal_mask.set_editor_property("a", False)
        self.lib.connect_material_expressions(samples["ORM"], "", metal_mask, "")
        self.lib.connect_material_expressions(metal_mask, "", slab, "F0")
        
        # Connect Normal
        self.lib.connect_material_expressions(samples["Normal"], "", slab, "Normal")
        
        # Connect to output
        self.lib.connect_material_property(slab, "", unreal.MaterialProperty.MP_FRONT_MATERIAL)
    
    def _build_split_graph(self, material):
        """Build split texture material node graph"""
        default_normal = AutoMattyUtils.find_default_normal()
        
        # Create texture sample nodes
        samples = {}
        coords = {
            "Color": (-400, 200),
            "Roughness": (-400, 0),
            "Metallic": (-400, -100),
            "Occlusion": (-400, -200),
            "Normal": (-400, -300),
        }
        
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
        
        # Create Substrate Slab BSDF
        slab = self.lib.create_material_expression(
            material, unreal.MaterialExpressionSubstrateSlabBSDF, 0, 0
        )
        
        # Direct connections
        self.lib.connect_material_expressions(samples["Color"], "", slab, "Diffuse Albedo")
        self.lib.connect_material_expressions(samples["Normal"], "", slab, "Normal")
        self.lib.connect_material_expressions(samples["Roughness"], "", slab, "Roughness")
        self.lib.connect_material_expressions(samples["Metallic"], "", slab, "F0")
        self.lib.connect_material_expressions(samples["Occlusion"], "", slab, "AmbientOcclusion")
        
        # Connect to output
        self.lib.connect_material_property(slab, "", unreal.MaterialProperty.MP_FRONT_MATERIAL)
    
    def _build_advanced_graph_builtin(self, material):
        """Build advanced material using built-in UE material expression nodes - CLEANED UP VERSION"""
        default_normal = AutoMattyUtils.find_default_normal()
        
        # === TEXTURE SAMPLERS (Left Column) ===
        color_tex = self.lib.create_material_expression(
            material, unreal.MaterialExpressionTextureSampleParameter2D, -1200, 200
        )
        color_tex.set_editor_property("parameter_name", "Color")

        orm_tex = self.lib.create_material_expression(
            material, unreal.MaterialExpressionTextureSampleParameter2D, -1200, -100
        )
        orm_tex.set_editor_property("parameter_name", "ORM")

        normal_tex = self.lib.create_material_expression(
            material, unreal.MaterialExpressionTextureSampleParameter2D, -1200, -400
        )
        normal_tex.set_editor_property("parameter_name", "Normal")
        normal_tex.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
        if default_normal:
            normal_tex.set_editor_property("texture", default_normal)

        # === COLOR PROCESSING ===
        # Color Contrast using Power node only
        color_contrast_param = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -900, 250
        )
        color_contrast_param.set_editor_property("parameter_name", "ColorContrast")
        color_contrast_param.set_editor_property("default_value", 1.0)
        
        color_power = self.lib.create_material_expression(
            material, unreal.MaterialExpressionPower, -600, 200
        )
        self.lib.connect_material_expressions(color_tex, "", color_power, "Base")
        self.lib.connect_material_expressions(color_contrast_param, "", color_power, "Exp")

        # === ORM BREAKDOWN (Middle-Left) ===
        # Roughness mask (G channel) - FIXED
        rough_mask = self.lib.create_material_expression(
            material, unreal.MaterialExpressionComponentMask, -900, -50
        )
        rough_mask.set_editor_property("r", False)
        rough_mask.set_editor_property("g", True)   # Roughness = Green channel
        rough_mask.set_editor_property("b", False)
        rough_mask.set_editor_property("a", False)
        self.lib.connect_material_expressions(orm_tex, "", rough_mask, "")

        # Metallic mask (B channel) - FIXED
        metal_mask = self.lib.create_material_expression(
            material, unreal.MaterialExpressionComponentMask, -900, -200
        )
        metal_mask.set_editor_property("r", False)
        metal_mask.set_editor_property("g", False)
        metal_mask.set_editor_property("b", True)   # Metallic = Blue channel
        metal_mask.set_editor_property("a", False)
        self.lib.connect_material_expressions(orm_tex, "", metal_mask, "")

        # AO mask (R channel) - FIXED
        ao_mask = self.lib.create_material_expression(
            material, unreal.MaterialExpressionComponentMask, -900, -350
        )
        ao_mask.set_editor_property("r", True)   # AO = Red channel
        ao_mask.set_editor_property("g", False)
        ao_mask.set_editor_property("b", False)
        ao_mask.set_editor_property("a", False)
        self.lib.connect_material_expressions(orm_tex, "", ao_mask, "")

        # === ROUGHNESS PROCESSING ===
        # Roughness parameters
        rough_min_param = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -600, -50
        )
        rough_min_param.set_editor_property("parameter_name", "RoughnessMin")
        rough_min_param.set_editor_property("default_value", 0.0)
        
        rough_max_param = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -600, -100
        )
        rough_max_param.set_editor_property("parameter_name", "RoughnessMax")
        rough_max_param.set_editor_property("default_value", 1.0)
        
        # MaterialFunctionCall for RemapValueRange (FIXED!)
        remap_roughness = self.lib.create_material_expression(
            material, unreal.MaterialExpressionMaterialFunctionCall, -300, -100
        )
        
        # Load the built-in RemapValueRange function
        remap_function = unreal.EditorAssetLibrary.load_asset("/Engine/Functions/Engine_MaterialFunctions03/Math/RemapValueRange")
        if remap_function:
            remap_roughness.set_editor_property("material_function", remap_function)
            
            # Connect inputs: Value, Output Min, Output Max
            self.lib.connect_material_expressions(rough_mask, "", remap_roughness, "Input")
            self.lib.connect_material_expressions(rough_min_param, "", remap_roughness, "Target Low")
            self.lib.connect_material_expressions(rough_max_param, "", remap_roughness, "Target High")
        else:
            unreal.log_error("❌ RemapValueRange function not found!")
            # Fallback to direct roughness connection
            remap_roughness = rough_mask

        # === MFP/SSS PROCESSING ===
        # MFP Color parameter (NEW!)
        mfp_color_param = self.lib.create_material_expression(
            material, unreal.MaterialExpressionVectorParameter, -1200, -700
        )
        mfp_color_param.set_editor_property("parameter_name", "MFPColor")
        mfp_color_param.set_editor_property("default_value", unreal.LinearColor(1.0, 0.5, 0.3, 1.0))  # Nice skin tone default

        # UseDiffuseAsMFP switch
        use_diffuse_switch = self.lib.create_material_expression(
            material, unreal.MaterialExpressionStaticSwitchParameter, -600, -400
        )
        use_diffuse_switch.set_editor_property("parameter_name", "UseDiffuseAsMFP")
        use_diffuse_switch.set_editor_property("default_value", True)

        # MFP Scale
        mfp_scale = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -600, -500
        )
        mfp_scale.set_editor_property("parameter_name", "MFPScale")
        mfp_scale.set_editor_property("default_value", 1.0)

        # Switch connections: True = diffuse color, False = MFP color parameter
        self.lib.connect_material_expressions(color_power, "", use_diffuse_switch, "True")
        self.lib.connect_material_expressions(mfp_color_param, "", use_diffuse_switch, "False")

        # === SUBSTRATE SLAB BSDF ===
        slab = self.lib.create_material_expression(
            material, unreal.MaterialExpressionSubstrateSlabBSDF, 100, -100
        )

        # Connect everything to Substrate Slab
        self.lib.connect_material_expressions(color_power, "", slab, "Diffuse Albedo")
        self.lib.connect_material_expressions(remap_roughness, "", slab, "Roughness")
        self.lib.connect_material_expressions(metal_mask, "", slab, "F0")
        self.lib.connect_material_expressions(ao_mask, "", slab, "AmbientOcclusion")
        self.lib.connect_material_expressions(normal_tex, "", slab, "Normal")
        self.lib.connect_material_expressions(use_diffuse_switch, "", slab, "SSS MFP")
        self.lib.connect_material_expressions(mfp_scale, "", slab, "SSS MFP Scale")

        # Connect to material output
        self.lib.connect_material_property(slab, "", unreal.MaterialProperty.MP_FRONT_MATERIAL)
    
    def _build_environment_graph(self, material):
        """Build dual-slab environment material with advanced controls - This is gonna be chunky"""
        default_normal = AutoMattyUtils.find_default_normal()
        
        # === TEXTURE COORDINATES & VARIATION ===
        # Base UV
        base_uv = self.lib.create_material_expression(
            material, unreal.MaterialExpressionTextureCoordinate, -2000, 0
        )
        
        # TextureVariation function call - you'll need to fix the path/connections
        texture_variation = self.lib.create_material_expression(
            material, unreal.MaterialExpressionMaterialFunctionCall, -1800, 0
        )
        # texture_variation.set_editor_property("material_function", your_texture_variation_function)
        # Connect base_uv to texture_variation input when you get the function
        
        # === NOISE FOR MIXING (GOING ABSOLUTELY BATSHIT) ===
        # Primary noise layer
        noise_scale_1 = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1600, 400
        )
        noise_scale_1.set_editor_property("parameter_name", "NoiseScale1")
        noise_scale_1.set_editor_property("default_value", 5.0)
        
        noise_multiply_1 = self.lib.create_material_expression(
            material, unreal.MaterialExpressionMultiply, -1400, 300
        )
        self.lib.connect_material_expressions(base_uv, "", noise_multiply_1, "A")
        self.lib.connect_material_expressions(noise_scale_1, "", noise_multiply_1, "B")
        
        noise_1 = self.lib.create_material_expression(
            material, unreal.MaterialExpressionNoise, -1200, 300
        )
        noise_1.set_editor_property("quality", 4)
        noise_1.set_editor_property("noise_function", unreal.NoiseFunction.NOISEFUNCTION_SIMPLEX_TEX)
        self.lib.connect_material_expressions(noise_multiply_1, "", noise_1, "Position")
        
        # Secondary noise layer for detail
        noise_scale_2 = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1600, 600
        )
        noise_scale_2.set_editor_property("parameter_name", "NoiseScale2")
        noise_scale_2.set_editor_property("default_value", 15.0)
        
        noise_multiply_2 = self.lib.create_material_expression(
            material, unreal.MaterialExpressionMultiply, -1400, 500
        )
        self.lib.connect_material_expressions(base_uv, "", noise_multiply_2, "A")
        self.lib.connect_material_expressions(noise_scale_2, "", noise_multiply_2, "B")
        
        noise_2 = self.lib.create_material_expression(
            material, unreal.MaterialExpressionNoise, -1200, 500
        )
        noise_2.set_editor_property("quality", 4)
        noise_2.set_editor_property("noise_function", unreal.NoiseFunction.NOISEFUNCTION_GRADIENT_TEX)
        self.lib.connect_material_expressions(noise_multiply_2, "", noise_2, "Position")
        
        # Detail noise intensity
        detail_intensity = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1000, 550
        )
        detail_intensity.set_editor_property("parameter_name", "DetailNoiseIntensity")
        detail_intensity.set_editor_property("default_value", 0.3)
        
        detail_scaled = self.lib.create_material_expression(
            material, unreal.MaterialExpressionMultiply, -800, 500
        )
        self.lib.connect_material_expressions(noise_2, "", detail_scaled, "A")
        self.lib.connect_material_expressions(detail_intensity, "", detail_scaled, "B")
        
        # Combine noises
        noise_combined = self.lib.create_material_expression(
            material, unreal.MaterialExpressionAdd, -600, 400
        )
        self.lib.connect_material_expressions(noise_1, "", noise_combined, "A")
        self.lib.connect_material_expressions(detail_scaled, "", noise_combined, "B")
        
        # Noise contrast control
        noise_contrast = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1000, 400
        )
        noise_contrast.set_editor_property("parameter_name", "NoiseContrast")
        noise_contrast.set_editor_property("default_value", 3.0)
        
        # Noise bias (shift the center point)
        noise_bias = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1000, 450
        )
        noise_bias.set_editor_property("parameter_name", "NoiseBias")
        noise_bias.set_editor_property("default_value", 0.0)
        
        noise_biased = self.lib.create_material_expression(
            material, unreal.MaterialExpressionAdd, -400, 400
        )
        self.lib.connect_material_expressions(noise_combined, "", noise_biased, "A")
        self.lib.connect_material_expressions(noise_bias, "", noise_biased, "B")
        
        noise_power = self.lib.create_material_expression(
            material, unreal.MaterialExpressionPower, -200, 400
        )
        self.lib.connect_material_expressions(noise_biased, "", noise_power, "Base")
        self.lib.connect_material_expressions(noise_contrast, "", noise_power, "Exp")
        
        # Clamp that bad boy
        noise_final = self.lib.create_material_expression(
            material, unreal.MaterialExpressionClamp, 0, 400
        )
        noise_final.set_editor_property("min_default", 0.0)
        noise_final.set_editor_property("max_default", 1.0)
        self.lib.connect_material_expressions(noise_power, "", noise_final, "")
        
        # === THIRD NOISE LAYER FOR EDGE DETAILS (Because why the fuck not?) ===
        edge_noise_scale = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1600, 800
        )
        edge_noise_scale.set_editor_property("parameter_name", "EdgeNoiseScale")
        edge_noise_scale.set_editor_property("default_value", 50.0)
        
        edge_noise_multiply = self.lib.create_material_expression(
            material, unreal.MaterialExpressionMultiply, -1400, 700
        )
        self.lib.connect_material_expressions(base_uv, "", edge_noise_multiply, "A")
        self.lib.connect_material_expressions(edge_noise_scale, "", edge_noise_multiply, "B")
        
        edge_noise = self.lib.create_material_expression(
            material, unreal.MaterialExpressionNoise, -1200, 700
        )
        edge_noise.set_editor_property("quality", 3)
        edge_noise.set_editor_property("noise_function", unreal.NoiseFunction.NOISEFUNCTION_VORONOI_ALU)
        self.lib.connect_material_expressions(edge_noise_multiply, "", edge_noise, "Position")
        
        # === SLAB A TEXTURES (LEFT SIDE) - NOW WITH DISPLACEMENT ===
        slab_a_textures = {}
        slab_a_coords = {
            "ColorA": (-1600, -400),
            "NormalA": (-1600, -600),
            "RoughnessA": (-1600, -800),
            "MetallicA": (-1600, -1000),
            "OcclusionA": (-1600, -1200),
            "DisplacementA": (-1600, -1400),  # Fuck it, displacement too
            "EmissionA": (-1600, -1500),      # And emission because why not
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
            # Connect UV variation here when you get the function working
            slab_a_textures[param_name] = tex_node
        
        # === SLAB B TEXTURES (RIGHT SIDE) - SAME INSANITY ===
        slab_b_textures = {}
        slab_b_coords = {
            "ColorB": (-1600, -1600),
            "NormalB": (-1600, -1800),
            "RoughnessB": (-1600, -2000),
            "MetallicB": (-1600, -2200),
            "OcclusionB": (-1600, -2400),
            "DisplacementB": (-1600, -2600),
            "EmissionB": (-1600, -2700),
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
        
        # === ADVANCED COLOR CONTROLS FOR SLAB A (GOING MENTAL) ===
        # Basic contrast
        color_a_contrast = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1200, -350
        )
        color_a_contrast.set_editor_property("parameter_name", "ColorAContrast")
        color_a_contrast.set_editor_property("default_value", 1.0)
        
        color_a_power = self.lib.create_material_expression(
            material, unreal.MaterialExpressionPower, -1000, -400
        )
        self.lib.connect_material_expressions(slab_a_textures["ColorA"], "", color_a_power, "Base")
        self.lib.connect_material_expressions(color_a_contrast, "", color_a_power, "Exp")
        
        # Color tinting
        color_a_tint = self.lib.create_material_expression(
            material, unreal.MaterialExpressionVectorParameter, -1200, -450
        )
        color_a_tint.set_editor_property("parameter_name", "ColorATint")
        color_a_tint.set_editor_property("default_value", unreal.LinearColor(1.0, 1.0, 1.0, 1.0))
        
        color_a_tinted = self.lib.create_material_expression(
            material, unreal.MaterialExpressionMultiply, -800, -400
        )
        self.lib.connect_material_expressions(color_a_power, "", color_a_tinted, "A")
        self.lib.connect_material_expressions(color_a_tint, "", color_a_tinted, "B")
        
        # Brightness/Desaturation controls
        color_a_brightness = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1200, -500
        )
        color_a_brightness.set_editor_property("parameter_name", "ColorABrightness")
        color_a_brightness.set_editor_property("default_value", 0.0)
        
        color_a_bright = self.lib.create_material_expression(
            material, unreal.MaterialExpressionAdd, -600, -400
        )
        self.lib.connect_material_expressions(color_a_tinted, "", color_a_bright, "A")
        self.lib.connect_material_expressions(color_a_brightness, "", color_a_bright, "B")
        
        # Desaturation
        color_a_desat = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1200, -550
        )
        color_a_desat.set_editor_property("parameter_name", "ColorADesaturation")
        color_a_desat.set_editor_property("default_value", 0.0)
        
        color_a_final = self.lib.create_material_expression(
            material, unreal.MaterialExpressionDesaturation, -400, -400
        )
        self.lib.connect_material_expressions(color_a_bright, "", color_a_final, "Input")
        self.lib.connect_material_expressions(color_a_desat, "", color_a_final, "Fraction")
        
        # === SAME INSANITY FOR SLAB B ===
        color_b_contrast = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1200, -1550
        )
        color_b_contrast.set_editor_property("parameter_name", "ColorBContrast")
        color_b_contrast.set_editor_property("default_value", 1.0)
        
        color_b_power = self.lib.create_material_expression(
            material, unreal.MaterialExpressionPower, -1000, -1600
        )
        self.lib.connect_material_expressions(slab_b_textures["ColorB"], "", color_b_power, "Base")
        self.lib.connect_material_expressions(color_b_contrast, "", color_b_power, "Exp")
        
        color_b_tint = self.lib.create_material_expression(
            material, unreal.MaterialExpressionVectorParameter, -1200, -1650
        )
        color_b_tint.set_editor_property("parameter_name", "ColorBTint")
        color_b_tint.set_editor_property("default_value", unreal.LinearColor(1.0, 1.0, 1.0, 1.0))
        
        color_b_tinted = self.lib.create_material_expression(
            material, unreal.MaterialExpressionMultiply, -800, -1600
        )
        self.lib.connect_material_expressions(color_b_power, "", color_b_tinted, "A")
        self.lib.connect_material_expressions(color_b_tint, "", color_b_tinted, "B")
        
        color_b_brightness = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1200, -1700
        )
        color_b_brightness.set_editor_property("parameter_name", "ColorBBrightness")
        color_b_brightness.set_editor_property("default_value", 0.0)
        
        color_b_bright = self.lib.create_material_expression(
            material, unreal.MaterialExpressionAdd, -600, -1600
        )
        self.lib.connect_material_expressions(color_b_tinted, "", color_b_bright, "A")
        self.lib.connect_material_expressions(color_b_brightness, "", color_b_bright, "B")
        
        color_b_desat = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1200, -1750
        )
        color_b_desat.set_editor_property("parameter_name", "ColorBDesaturation")
        color_b_desat.set_editor_property("default_value", 0.0)
        
        color_b_final = self.lib.create_material_expression(
            material, unreal.MaterialExpressionDesaturation, -400, -1600
        )
        self.lib.connect_material_expressions(color_b_bright, "", color_b_final, "Input")
        self.lib.connect_material_expressions(color_b_desat, "", color_b_final, "Fraction")
        
        # === ROUGHNESS REMAPPING FOR SLAB A ===
        rough_a_min = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1000, -750
        )
        rough_a_min.set_editor_property("parameter_name", "RoughnessAMin")
        rough_a_min.set_editor_property("default_value", 0.0)
        
        rough_a_max = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1000, -800
        )
        rough_a_max.set_editor_property("parameter_name", "RoughnessAMax")
        rough_a_max.set_editor_property("default_value", 1.0)
        
        remap_rough_a = self.lib.create_material_expression(
            material, unreal.MaterialExpressionMaterialFunctionCall, -600, -800
        )
        # Load RemapValueRange function if available
        remap_function = unreal.EditorAssetLibrary.load_asset("/Engine/Functions/Engine_MaterialFunctions03/Math/RemapValueRange")
        if remap_function:
            remap_rough_a.set_editor_property("material_function", remap_function)
            self.lib.connect_material_expressions(slab_a_textures["RoughnessA"], "", remap_rough_a, "Input")
            self.lib.connect_material_expressions(rough_a_min, "", remap_rough_a, "Target Low")
            self.lib.connect_material_expressions(rough_a_max, "", remap_rough_a, "Target High")
        else:
            remap_rough_a = slab_a_textures["RoughnessA"]
        
        # === ROUGHNESS REMAPPING FOR SLAB B ===
        rough_b_min = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1000, -1750
        )
        rough_b_min.set_editor_property("parameter_name", "RoughnessBMin")
        rough_b_min.set_editor_property("default_value", 0.0)
        
        rough_b_max = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -1000, -1800
        )
        rough_b_max.set_editor_property("parameter_name", "RoughnessBMax")
        rough_b_max.set_editor_property("default_value", 1.0)
        
        remap_rough_b = self.lib.create_material_expression(
            material, unreal.MaterialExpressionMaterialFunctionCall, -600, -1800
        )
        if remap_function:
            remap_rough_b.set_editor_property("material_function", remap_function)
            self.lib.connect_material_expressions(slab_b_textures["RoughnessB"], "", remap_rough_b, "Input")
            self.lib.connect_material_expressions(rough_b_min, "", remap_rough_b, "Target Low")
            self.lib.connect_material_expressions(rough_b_max, "", remap_rough_b, "Target High")
        else:
            remap_rough_b = slab_b_textures["RoughnessB"]
        
        # === CREATE SUBSTRATE SLABS ===
        slab_a = self.lib.create_material_expression(
            material, unreal.MaterialExpressionSubstrateSlabBSDF, -200, -800
        )
        slab_b = self.lib.create_material_expression(
            material, unreal.MaterialExpressionSubstrateSlabBSDF, -200, -1600
        )
        
        # === CONNECT SLAB A (WITH ALL THE MADNESS) ===
        self.lib.connect_material_expressions(color_a_final, "", slab_a, "Diffuse Albedo")
        self.lib.connect_material_expressions(slab_a_textures["NormalA"], "", slab_a, "Normal")
        self.lib.connect_material_expressions(remap_rough_a, "", slab_a, "Roughness")
        self.lib.connect_material_expressions(slab_a_textures["MetallicA"], "", slab_a, "F0")
        self.lib.connect_material_expressions(slab_a_textures["OcclusionA"], "", slab_a, "AmbientOcclusion")
        
        # === CONNECT SLAB B (SAME ENERGY) ===
        self.lib.connect_material_expressions(color_b_final, "", slab_b, "Diffuse Albedo")
        self.lib.connect_material_expressions(slab_b_textures["NormalB"], "", slab_b, "Normal")
        self.lib.connect_material_expressions(remap_rough_b, "", slab_b, "Roughness")
        self.lib.connect_material_expressions(slab_b_textures["MetallicB"], "", slab_b, "F0")
        self.lib.connect_material_expressions(slab_b_textures["OcclusionB"], "", slab_b, "AmbientOcclusion")
        
        # === MIX THE SLABS (WITH EDGE DETAIL) ===
        # Use edge noise to modify the main mixing
        edge_influence = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -600, 600
        )
        edge_influence.set_editor_property("parameter_name", "EdgeInfluence")
        edge_influence.set_editor_property("default_value", 0.1)
        
        edge_scaled = self.lib.create_material_expression(
            material, unreal.MaterialExpressionMultiply, -400, 650
        )
        self.lib.connect_material_expressions(edge_noise, "", edge_scaled, "A")
        self.lib.connect_material_expressions(edge_influence, "", edge_scaled, "B")
        
        # Combine main noise with edge detail
        final_mix_mask = self.lib.create_material_expression(
            material, unreal.MaterialExpressionAdd, -200, 500
        )
        self.lib.connect_material_expressions(noise_final, "", final_mix_mask, "A")
        self.lib.connect_material_expressions(edge_scaled, "", final_mix_mask, "B")
        
        # Clamp the final mix
        final_mix_clamped = self.lib.create_material_expression(
            material, unreal.MaterialExpressionClamp, 0, 500
        )
        final_mix_clamped.set_editor_property("min_default", 0.0)
        final_mix_clamped.set_editor_property("max_default", 1.0)
        self.lib.connect_material_expressions(final_mix_mask, "", final_mix_clamped, "")
        
        slab_mix = self.lib.create_material_expression(
            material, unreal.MaterialExpressionSubstrateHorizontalMixing, 200, -1200
        )
        self.lib.connect_material_expressions(slab_a, "", slab_mix, "Foreground")
        self.lib.connect_material_expressions(slab_b, "", slab_mix, "Background")
        self.lib.connect_material_expressions(final_mix_clamped, "", slab_mix, "Mix")
        
        # === DISPLACEMENT OUTPUT (Because fuck vertex limits) ===
        # Mix the two displacement maps
        displacement_mix = self.lib.create_material_expression(
            material, unreal.MaterialExpressionLinearInterpolate, 400, -400
        )
        self.lib.connect_material_expressions(slab_a_textures["DisplacementA"], "", displacement_mix, "A")
        self.lib.connect_material_expressions(slab_b_textures["DisplacementB"], "", displacement_mix, "B")
        self.lib.connect_material_expressions(final_mix_clamped, "", displacement_mix, "Alpha")
        
        # Displacement intensity control
        displacement_intensity = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, 600, -350
        )
        displacement_intensity.set_editor_property("parameter_name", "DisplacementIntensity")
        displacement_intensity.set_editor_property("default_value", 1.0)
        
        displacement_final = self.lib.create_material_expression(
            material, unreal.MaterialExpressionMultiply, 800, -400
        )
        self.lib.connect_material_expressions(displacement_mix, "", displacement_final, "A")
        self.lib.connect_material_expressions(displacement_intensity, "", displacement_final, "B")
        
        # === EMISSION OUTPUT (Because we're going FULL SEND) ===
        # Mix emission maps
        emission_mix = self.lib.create_material_expression(
            material, unreal.MaterialExpressionLinearInterpolate, 400, -600
        )
        self.lib.connect_material_expressions(slab_a_textures["EmissionA"], "", emission_mix, "A")
        self.lib.connect_material_expressions(slab_b_textures["EmissionB"], "", emission_mix, "B")
        self.lib.connect_material_expressions(final_mix_clamped, "", emission_mix, "Alpha")
        
        # Emission intensity
        emission_intensity = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, 600, -550
        )
        emission_intensity.set_editor_property("parameter_name", "EmissionIntensity")
        emission_intensity.set_editor_property("default_value", 0.0)  # Off by default
        
        emission_final = self.lib.create_material_expression(
            material, unreal.MaterialExpressionMultiply, 800, -600
        )
        self.lib.connect_material_expressions(emission_mix, "", emission_final, "A")
        self.lib.connect_material_expressions(emission_intensity, "", emission_final, "B")
        
        # === CONNECT TO ALL THE OUTPUTS (BECAUSE WE'RE MENTAL) ===
        # Main substrate output
        self.lib.connect_material_property(slab_mix, "", unreal.MaterialProperty.MP_FRONT_MATERIAL)
        
        # Displacement output
        self.lib.connect_material_property(displacement_final, "", unreal.MaterialProperty.MP_WORLD_DISPLACEMENT)
        
        # Emission output
        self.lib.connect_material_property(emission_final, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        
        unreal.log("🔥 ENVIRONMENT MATERIAL CREATED WITH MAXIMUM CHAOS:")
        unreal.log("   - Dual substrate slabs with split textures")
        unreal.log("   - Triple-layer noise mixing (Simplex + Gradient + Voronoi)")
        unreal.log("   - Full color grading per slab (tint, brightness, desaturation)")
        unreal.log("   - Roughness remapping for both slabs")
        unreal.log("   - Displacement and emission mixing")
        unreal.log("   - Edge detail noise influence")
        unreal.log("   - 14 texture inputs total")
        unreal.log("   - 20+ parameters for insane control")
        unreal.log("💀 Your GPU is going to hate you but it'll look AMAZING")

# Usage functions
def create_environment_material_with_path():
    """Create environment material with optional custom path"""
    custom_path = AutoMattyUtils.get_user_path(
        "Material destination:", 
        AutoMattyConfig.DEFAULT_MATERIAL_PATH
    )
    
    builder = SubstrateMaterialBuilder()
    return builder.create_environment_material(custom_path=custom_path)

def create_orm_material_with_path():
    """Create ORM material with optional custom path"""
    custom_path = AutoMattyUtils.get_user_path(
        "Material destination:", 
        AutoMattyConfig.DEFAULT_MATERIAL_PATH
    )
    
    builder = SubstrateMaterialBuilder()
    return builder.create_orm_material(custom_path=custom_path)

def create_split_material_with_path():
    """Create split material with optional custom path"""
    custom_path = AutoMattyUtils.get_user_path(
        "Material destination:", 
        AutoMattyConfig.DEFAULT_MATERIAL_PATH
    )
    
    builder = SubstrateMaterialBuilder()
    return builder.create_split_material(custom_path=custom_path)

# Execute based on what you want
if __name__ == "__main__":
    # Example usage
    builder = SubstrateMaterialBuilder()
    builder.create_environment_material()