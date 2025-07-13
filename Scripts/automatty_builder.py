"""
AutoMatty Material Builder - Complete Version with Texture Variation & UV Scale Support
"""
import unreal

 #Setup AutoMatty imports

try:
    from automatty_utils import setup_automatty_imports
    if not setup_automatty_imports():
        raise ImportError("Failed to setup AutoMatty imports")
    from automatty_config import AutoMattyConfig, AutoMattyUtils
except ImportError as e:
    unreal.log_error(f"❌ AutoMatty import failed: {e}")
    raise

class SubstrateMaterialBuilder:
    """Complete Substrate material builder with texture variation and UV scale support"""
    
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
    
    def create_orm_material(self, base_name=None, custom_path=None, use_second_roughness=False, use_nanite=False, use_triplanar=False, use_tex_var=False):
        """Create ORM material with all features including texture variation"""
        if not AutoMattyUtils.is_substrate_enabled():
            unreal.log_error("❌ Substrate is not enabled in project settings!")
            return None
        
        if base_name is None:
            custom_prefix = AutoMattyConfig.get_custom_material_prefix()
            base_name = f"{custom_prefix}_ORM"
        
        folder = custom_path or AutoMattyConfig.get_custom_material_path()
        name = AutoMattyUtils.get_next_asset_name(base_name, folder)
        
        material = self.atools.create_asset(name, folder, unreal.Material, unreal.MaterialFactoryNew())
        
        if use_nanite:
            material.set_editor_property("enable_tessellation", True)
        
        self._build_standard_graph(material, material_type="orm", use_second_roughness=use_second_roughness, use_nanite=use_nanite, use_triplanar=use_triplanar, use_tex_var=use_tex_var)
        
        self.lib.recompile_material(material)
        unreal.EditorAssetLibrary.save_loaded_asset(material)
        
        features = []
        if use_triplanar: features.append("triplanar")
        if use_second_roughness: features.append("dual-roughness")
        if use_nanite: features.append("nanite")
        if use_tex_var: features.append("texture-variation")
        feature_text = f" ({', '.join(features)})" if features else ""
        
        unreal.log(f"✅ ORM material '{name}'{feature_text} created")
        return material
    
    def create_split_material(self, base_name=None, custom_path=None, use_second_roughness=False, use_nanite=False, use_triplanar=False, use_tex_var=False):
        """Create Split material with all features including texture variation"""
        if not AutoMattyUtils.is_substrate_enabled():
            unreal.log_error("❌ Substrate is not enabled in project settings!")
            return None
        
        if base_name is None:
            custom_prefix = AutoMattyConfig.get_custom_material_prefix()
            base_name = f"{custom_prefix}_Split"
        
        folder = custom_path or AutoMattyConfig.get_custom_material_path()
        name = AutoMattyUtils.get_next_asset_name(base_name, folder)
        
        material = self.atools.create_asset(name, folder, unreal.Material, unreal.MaterialFactoryNew())
        
        if use_nanite:
            material.set_editor_property("enable_tessellation", True)
        
        self._build_standard_graph(material, material_type="split", use_second_roughness=use_second_roughness, use_nanite=use_nanite, use_triplanar=use_triplanar, use_tex_var=use_tex_var)
        
        self.lib.recompile_material(material)
        unreal.EditorAssetLibrary.save_loaded_asset(material)
        
        features = []
        if use_triplanar: features.append("triplanar")
        if use_second_roughness: features.append("dual-roughness")
        if use_nanite: features.append("nanite")
        if use_tex_var: features.append("texture-variation")
        feature_text = f" ({', '.join(features)})" if features else ""
        
        unreal.log(f"✅ Split material '{name}'{feature_text} created")
        return material
    

    
    def create_environment_material(self, base_name=None, custom_path=None, use_adv_env=False, use_triplanar=False, use_nanite=False, use_tex_var=False):
        """Create Environment material with UV scale and texture variation support"""
        if not AutoMattyUtils.is_substrate_enabled():
            unreal.log_error("❌ Substrate is not enabled in project settings!")
            return None
        
        if base_name is None:
            custom_prefix = AutoMattyConfig.get_custom_material_prefix()
            env_type = "AdvEnvironment" if use_adv_env else "Environment"
            base_name = f"{custom_prefix}_{env_type}"
        
        folder = custom_path or AutoMattyConfig.get_custom_material_path()
        name = AutoMattyUtils.get_next_asset_name(base_name, folder)
        
        material = self.atools.create_asset(name, folder, unreal.Material, unreal.MaterialFactoryNew())
        
        # Enable tessellation for nanite
        if use_nanite:
            material.set_editor_property("enable_tessellation", True)
            unreal.log(f"🏔️ Enabled tessellation for nanite displacement")
        
        if use_adv_env:
            self._build_environment_graph_advanced(material, use_triplanar=use_triplanar, use_nanite=use_nanite, use_tex_var=use_tex_var)
        else:
            self._build_environment_graph_simple(material, use_triplanar=use_triplanar, use_nanite=use_nanite, use_tex_var=use_tex_var)
        
        self.lib.recompile_material(material)
        unreal.EditorAssetLibrary.save_loaded_asset(material)
        
        features = []
        if use_triplanar: features.append("triplanar")
        if use_adv_env: features.append("advanced-mixing")
        if use_nanite: features.append("nanite")
        if use_tex_var: features.append("texture-variation")
        feature_text = f" ({', '.join(features)})" if features else ""
        
        unreal.log(f"✅ Environment material '{name}'{feature_text} created")
        return material
    
    def _build_standard_graph(self, material, material_type="orm", use_second_roughness=False, use_nanite=False, use_triplanar=False, use_tex_var=False):
        """Build standard material graph with UV scale and texture variation support"""
        default_normal = AutoMattyUtils.find_default_normal()
        
        # Base texture coordinates
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
        
        if use_nanite:
            coords["Height"] = (-1400, -800)
            unreal.log(f"🏔️ Adding Height parameter for nanite displacement")
        
        # UV SCALE SETUP (like environment materials)
        tex_coords = self.lib.create_material_expression(material, unreal.MaterialExpressionTextureCoordinate, -2000, -50)
        
        # UV Scale parameter
        uv_scale_param = self.lib.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -2000, -100)
        uv_scale_param.set_editor_property("parameter_name", "UVScale")
        uv_scale_param.set_editor_property("default_value", 1.0)
        uv_scale_param.set_editor_property("group", "UV Controls")
        
        # Scale the UVs
        uv_multiply = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, -1900, -75)
        self.lib.connect_material_expressions(tex_coords, "", uv_multiply, "A")
        self.lib.connect_material_expressions(uv_scale_param, "", uv_multiply, "B")
        
        # TEXTURE VARIATION SETUP
        variation_uvs = None
        if use_tex_var:
            unreal.log(f"🎲 Setting up texture variation system for {material_type}")
            
            # Create Variation Height Map parameter
            var_height_param = self.lib.create_material_expression(material, unreal.MaterialExpressionTextureSampleParameter2D, -1900, -150)
            var_height_param.set_editor_property("parameter_name", "VariationHeightMap")
            var_height_param.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_GRAYSCALE)
            var_height_param.set_editor_property("group", "Texture Variation")
            
            # Random Rotation and Scale boolean parameter
            random_rot_scale_param = self.lib.create_material_expression(material, unreal.MaterialExpressionStaticSwitchParameter, -1900, -200)
            random_rot_scale_param.set_editor_property("parameter_name", "RandomRotationScale")
            random_rot_scale_param.set_editor_property("default_value", True)
            random_rot_scale_param.set_editor_property("group", "Texture Variation")
            
            # TextureVariation function
            texture_var_func = self.lib.create_material_expression(material, unreal.MaterialExpressionMaterialFunctionCall, -1700, -125)
            texture_variation_function = unreal.EditorAssetLibrary.load_asset("/Engine/Functions/Engine_MaterialFunctions03/Texturing/TextureVariation")
            
            if texture_variation_function:
                texture_var_func.set_editor_property("material_function", texture_variation_function)
                
                # Connect scaled UVs to TextureVariation function
                self.lib.connect_material_expressions(uv_multiply, "", texture_var_func, "UVs")
                self.lib.connect_material_expressions(var_height_param, "", texture_var_func, "Heightmap")
                self.lib.connect_material_expressions(random_rot_scale_param, "", texture_var_func, "Random Rotation and Scale")
                
                # Use the output UVs for texture sampling
                variation_uvs = texture_var_func
                unreal.log(f"✅ Texture variation function connected for {material_type}")
            else:
                unreal.log_error(f"❌ TextureVariation function not found")
                variation_uvs = uv_multiply  # Fallback to scaled UVs
        else:
            variation_uvs = uv_multiply  # Use scaled UVs without variation
        
        # Create texture samples with variation UVs if enabled
        samples = {}
        
        for pname, (x, y) in coords.items():
            if use_triplanar:
                # Triplanar setup
                texture_param = self.lib.create_material_expression(material, unreal.MaterialExpressionTextureObjectParameter, x - 200, y)
                texture_param.set_editor_property("parameter_name", pname)
                
                # Set parameter groups for better organization
                if pname == "Height":
                    texture_param.set_editor_property("group", "Displacement")
                elif pname in ["Color", "ORM"]:
                    texture_param.set_editor_property("group", "Color")
                elif pname in ["Roughness", "Metallic"]:
                    texture_param.set_editor_property("group", pname)
                elif pname == "Normal":
                    texture_param.set_editor_property("group", "Normal")
                elif pname == "Emission":
                    texture_param.set_editor_property("group", "Emission")
                
                if pname == "Normal":
                    # WorldAlignedNormal for normals
                    world_align_func = self.lib.create_material_expression(material, unreal.MaterialExpressionMaterialFunctionCall, x, y)
                    world_aligned_normal = unreal.EditorAssetLibrary.load_asset("/Engine/Functions/Engine_MaterialFunctions01/Texturing/WorldAlignedNormal")
                    
                    if world_aligned_normal:
                        world_align_func.set_editor_property("material_function", world_aligned_normal)
                        self.lib.connect_material_expressions(texture_param, "", world_align_func, "TextureObject")
                        
                        # Connect variation UVs if available
                        if variation_uvs:
                            self.lib.connect_material_expressions(variation_uvs, "", world_align_func, "UVs")
                            unreal.log(f"🎲 Connected variation UVs to triplanar normal {pname}")
                        
                        samples[pname] = (world_align_func, "XYZ Texture")
                        unreal.log(f"🔺 Triplanar Normal setup: {pname}")
                    else:
                        unreal.log_error(f"❌ WorldAlignedNormal function not found, falling back to regular sample")
                        samples[pname] = self._create_regular_texture_sample(material, pname, x, y, default_normal, variation_uvs)
                else:
                    # WorldAlignedTexture for everything else
                    world_align_func = self.lib.create_material_expression(material, unreal.MaterialExpressionMaterialFunctionCall, x, y)
                    world_aligned_texture = unreal.EditorAssetLibrary.load_asset("/Engine/Functions/Engine_MaterialFunctions01/Texturing/WorldAlignedTexture")
                    
                    if world_aligned_texture:
                        world_align_func.set_editor_property("material_function", world_aligned_texture)
                        self.lib.connect_material_expressions(texture_param, "", world_align_func, "TextureObject")
                        
                        # Connect variation UVs if available
                        if variation_uvs:
                            self.lib.connect_material_expressions(variation_uvs, "", world_align_func, "UVs")
                            unreal.log(f"🎲 Connected variation UVs to triplanar {pname}")
                        
                        samples[pname] = (world_align_func, "XYZ Texture")
                        if pname == "Height":
                            unreal.log(f"🏔️ Triplanar Height setup: {pname}")
                        else:
                            unreal.log(f"🔺 Triplanar Texture setup: {pname}")
                    else:
                        unreal.log_error(f"❌ WorldAlignedTexture function not found, falling back to regular sample")
                        samples[pname] = self._create_regular_texture_sample(material, pname, x, y, default_normal, variation_uvs)
            else:
                # Regular texture samples (non-triplanar) with variation UVs
                samples[pname] = self._create_regular_texture_sample(material, pname, x, y, default_normal, variation_uvs)
        
        # Helper function to connect samples (handles both regular and triplanar)
        def connect_sample(sample, target_node, target_input):
            if isinstance(sample, tuple):
                # Triplanar: (node, output_pin)
                source_node, output_pin = sample
                self.lib.connect_material_expressions(source_node, output_pin, target_node, target_input)
            else:
                # Regular texture sample
                self.lib.connect_material_expressions(sample, "", target_node, target_input)
        
        # Color controls
        brightness_param = self.lib.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1100, -100)
        brightness_param.set_editor_property("parameter_name", "Brightness")
        brightness_param.set_editor_property("default_value", 1.0)
        brightness_param.set_editor_property("group", "Color")
        
        brightness_multiply = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, -900, -150)
        connect_sample(samples["Color"], brightness_multiply, "A")
        self.lib.connect_material_expressions(brightness_param, "", brightness_multiply, "B")
        
        color_contrast_param = self.lib.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1100, -150)
        color_contrast_param.set_editor_property("parameter_name", "ColorContrast")
        color_contrast_param.set_editor_property("default_value", 1.0)
        color_contrast_param.set_editor_property("group", "Color")
        
        color_power = self.lib.create_material_expression(material, unreal.MaterialExpressionPower, -750, -150)
        self.lib.connect_material_expressions(brightness_multiply, "", color_power, "Base")
        self.lib.connect_material_expressions(color_contrast_param, "", color_power, "Exp")
        
        hue_shift_param = self.lib.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1100, -200)
        hue_shift_param.set_editor_property("parameter_name", "HueShift")
        hue_shift_param.set_editor_property("default_value", 0.0)
        hue_shift_param.set_editor_property("group", "Color")
        
        hue_shift_function = self.lib.create_material_expression(material, unreal.MaterialExpressionMaterialFunctionCall, -600, -150)
        hueshift_func = unreal.EditorAssetLibrary.load_asset("/Engine/Functions/Engine_MaterialFunctions02/HueShift")
        if hueshift_func:
            hue_shift_function.set_editor_property("material_function", hueshift_func)
            self.lib.connect_material_expressions(color_power, "", hue_shift_function, "Texture")
            self.lib.connect_material_expressions(hue_shift_param, "", hue_shift_function, "Hue Shift Percentage")
        else:
            hue_shift_function = color_power
        
        # Roughness controls
        if material_type == "orm":
            rough_mask = self.lib.create_material_expression(material, unreal.MaterialExpressionComponentMask, -1100, -350)
            rough_mask.set_editor_property("r", False)
            rough_mask.set_editor_property("g", True)
            rough_mask.set_editor_property("b", False)
            rough_mask.set_editor_property("a", False)
            connect_sample(samples["ORM"], rough_mask, "")
            roughness_input = rough_mask
        else:
            roughness_input = samples["Roughness"]
        
        rough_min_param = self.lib.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1100, -450)
        rough_min_param.set_editor_property("parameter_name", "RoughnessMin")
        rough_min_param.set_editor_property("default_value", 0.0)
        rough_min_param.set_editor_property("group", "Roughness")
        
        rough_max_param = self.lib.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1100, -500)
        rough_max_param.set_editor_property("parameter_name", "RoughnessMax")
        rough_max_param.set_editor_property("default_value", 1.0)
        rough_max_param.set_editor_property("group", "Roughness")
        
        remap_roughness = self.lib.create_material_expression(material, unreal.MaterialExpressionMaterialFunctionCall, -700, -400)
        remap_function = unreal.EditorAssetLibrary.load_asset("/Engine/Functions/Engine_MaterialFunctions03/Math/RemapValueRange")
        if remap_function:
            remap_roughness.set_editor_property("material_function", remap_function)
            if isinstance(roughness_input, tuple):
                # Handle triplanar roughness input
                source_node, output_pin = roughness_input
                self.lib.connect_material_expressions(source_node, output_pin, remap_roughness, "Input")
            else:
                # Handle regular roughness input (either component mask or direct sample)
                self.lib.connect_material_expressions(roughness_input, "", remap_roughness, "Input")
            self.lib.connect_material_expressions(rough_min_param, "", remap_roughness, "Target Low")
            self.lib.connect_material_expressions(rough_max_param, "", remap_roughness, "Target High")
        else:
            remap_roughness = roughness_input
        
        # Metallic controls
        if material_type == "orm":
            metal_mask = self.lib.create_material_expression(material, unreal.MaterialExpressionComponentMask, -1100, -550)
            metal_mask.set_editor_property("r", False)
            metal_mask.set_editor_property("g", False)
            metal_mask.set_editor_property("b", True)
            metal_mask.set_editor_property("a", False)
            connect_sample(samples["ORM"], metal_mask, "")
            metallic_input = metal_mask
        else:
            metallic_input = samples["Metallic"]
        
        metal_intensity = self.lib.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1100, -600)
        metal_intensity.set_editor_property("parameter_name", "MetalIntensity")
        metal_intensity.set_editor_property("default_value", 0.0)
        metal_intensity.set_editor_property("group", "Metallic")
        
        metal_final = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, -700, -550)
        if isinstance(metallic_input, tuple):
            # Handle triplanar metallic input
            source_node, output_pin = metallic_input
            self.lib.connect_material_expressions(source_node, output_pin, metal_final, "A")
        else:
            # Handle regular metallic input (either component mask or direct sample)
            self.lib.connect_material_expressions(metallic_input, "", metal_final, "A")
        self.lib.connect_material_expressions(metal_intensity, "", metal_final, "B")
        
        # AO controls (ORM only)
        ao_final = None
        if material_type == "orm":
            ao_mask = self.lib.create_material_expression(material, unreal.MaterialExpressionComponentMask, -1100, -650)
            ao_mask.set_editor_property("r", True)
            ao_mask.set_editor_property("g", False)
            ao_mask.set_editor_property("b", False)
            ao_mask.set_editor_property("a", False)
            connect_sample(samples["ORM"], ao_mask, "")
            ao_final = ao_mask
        
        # Emission controls
        emission_intensity = self.lib.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1100, -700)
        emission_intensity.set_editor_property("parameter_name", "EmissionIntensity")
        emission_intensity.set_editor_property("default_value", 0.0)
        emission_intensity.set_editor_property("group", "Emission")
        
        emission_final = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, -700, -650)
        connect_sample(samples["Emission"], emission_final, "A")
        self.lib.connect_material_expressions(emission_intensity, "", emission_final, "B")
        
        # SSS controls
        mfp_color_param = self.lib.create_material_expression(material, unreal.MaterialExpressionVectorParameter, -1100, -750)
        mfp_color_param.set_editor_property("parameter_name", "MFPColor")
        mfp_color_param.set_editor_property("default_value", unreal.LinearColor(1.0, 0.5, 0.3, 1.0))
        mfp_color_param.set_editor_property("group", "SSS")

        use_diffuse_switch = self.lib.create_material_expression(material, unreal.MaterialExpressionStaticSwitchParameter, -700, -750)
        use_diffuse_switch.set_editor_property("parameter_name", "UseDiffuseAsMFP")
        use_diffuse_switch.set_editor_property("default_value", True)
        use_diffuse_switch.set_editor_property("group", "SSS")

        mfp_scale = self.lib.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1100, -800)
        mfp_scale.set_editor_property("parameter_name", "MFPScale")
        mfp_scale.set_editor_property("default_value", 1.0)
        mfp_scale.set_editor_property("group", "SSS")

        self.lib.connect_material_expressions(hue_shift_function, "", use_diffuse_switch, "True")
        self.lib.connect_material_expressions(mfp_color_param, "", use_diffuse_switch, "False")
        
        # Nanite displacement
        displacement_final = None
        if use_nanite and "Height" in samples:
            displacement_intensity = self.lib.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1100, -850)
            displacement_intensity.set_editor_property("parameter_name", "DisplacementIntensity")
            displacement_intensity.set_editor_property("default_value", 0.1)
            displacement_intensity.set_editor_property("group", "Displacement")
            
            displacement_multiply = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, -700, -800)
            connect_sample(samples["Height"], displacement_multiply, "A")
            self.lib.connect_material_expressions(displacement_intensity, "", displacement_multiply, "B")
            
            displacement_final = displacement_multiply
            unreal.log(f"🏔️ Nanite displacement setup complete")
        
        # Second roughness
        second_roughness_params = {}
        if use_second_roughness:
            second_roughness_param = self.lib.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -500, -450)
            second_roughness_param.set_editor_property("parameter_name", "SecondRoughness")
            second_roughness_param.set_editor_property("default_value", 0.5)
            second_roughness_param.set_editor_property("group", "Roughness")
            second_roughness_params["SecondRoughness"] = second_roughness_param
            
            second_roughness_weight = self.lib.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -500, -500)
            second_roughness_weight.set_editor_property("parameter_name", "SecondRoughnessWeight")
            second_roughness_weight.set_editor_property("default_value", 0.0)
            second_roughness_weight.set_editor_property("group", "Roughness")
            second_roughness_params["SecondRoughnessWeight"] = second_roughness_weight
        
        # Substrate slab
        slab = self.lib.create_material_expression(material, unreal.MaterialExpressionSubstrateSlabBSDF, -200, -400)
        
        # Connect everything to slab
        self.lib.connect_material_expressions(hue_shift_function, "", slab, "Diffuse Albedo")
        self.lib.connect_material_expressions(remap_roughness, "", slab, "Roughness")
        self.lib.connect_material_expressions(metal_final, "", slab, "F0")
        connect_sample(samples["Normal"], slab, "Normal")
        self.lib.connect_material_expressions(use_diffuse_switch, "", slab, "SSS MFP")
        self.lib.connect_material_expressions(mfp_scale, "", slab, "SSS MFP Scale")
        self.lib.connect_material_expressions(emission_final, "", slab, "Emissive Color")
        
        if ao_final:
            self.lib.connect_material_expressions(ao_final, "", slab, "AmbientOcclusion")
        
        if use_second_roughness:
            self.lib.connect_material_expressions(second_roughness_params["SecondRoughness"], "", slab, "Second Roughness")
            self.lib.connect_material_expressions(second_roughness_params["SecondRoughnessWeight"], "", slab, "Second Roughness Weight")
        
        # Connect to outputs
        self.lib.connect_material_property(slab, "", unreal.MaterialProperty.MP_FRONT_MATERIAL)
        
        # Connect displacement for Nanite  
        if use_nanite and displacement_final:
            try:
                self.lib.connect_material_property(displacement_final, "", unreal.MaterialProperty.MP_DISPLACEMENT)
                unreal.log(f"🏔️ Connected displacement to MP_DISPLACEMENT")
            except AttributeError:
                try:
                    self.lib.connect_material_property(displacement_final, "", unreal.MaterialProperty.MP_TESSELLATION_MULTIPLIER)
                    unreal.log(f"🏔️ Connected displacement to MP_TESSELLATION_MULTIPLIER")
                except AttributeError:
                    self.lib.connect_material_property(displacement_final, "", unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
                    unreal.log_warning(f"⚠️ Using MP_WORLD_POSITION_OFFSET as fallback")
    
    def _create_regular_texture_sample(self, material, param_name, x, y, default_normal=None, variation_uvs=None):
        """Create regular texture sample with optional variation UVs"""
        node = self.lib.create_material_expression(material, unreal.MaterialExpressionTextureSampleParameter2D, x, y)
        node.set_editor_property("parameter_name", param_name)
        
        # Connect variation UVs if provided
        if variation_uvs:
            self.lib.connect_material_expressions(variation_uvs, "", node, "UVs")
            unreal.log(f"🎲 Connected variation UVs to {param_name}")
        
        # Set parameter groups for better organization
        if param_name == "Height":
            node.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_GRAYSCALE)
            node.set_editor_property("group", "Displacement")
            unreal.log(f"🏔️ Regular Height texture sample created with Displacement group")
        elif param_name == "Normal":
            node.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
            node.set_editor_property("group", "Normal")
            if default_normal:
                node.set_editor_property("texture", default_normal)
        elif param_name in ["Color", "ORM"]:
            node.set_editor_property("group", "Color")
        elif param_name in ["Roughness", "Metallic"]:
            node.set_editor_property("group", param_name)
        elif param_name == "Emission":
            node.set_editor_property("group", "Emission")
        elif param_name == "VariationHeightMap":
            node.set_editor_property("group", "Texture Variation")
        
        return node
    
    def _build_environment_graph_simple(self, material, use_triplanar=False, use_nanite=False, use_tex_var=False):
        """Build simple environment material with UV scale and texture variation"""
        default_normal = AutoMattyUtils.find_default_normal()
        
        # UV SCALE SETUP FOR ENVIRONMENT
        tex_coords = self.lib.create_material_expression(material, unreal.MaterialExpressionTextureCoordinate, -2000, -50)
        
        # UV Scale parameter
        uv_scale_param = self.lib.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -2000, -100)
        uv_scale_param.set_editor_property("parameter_name", "UVScale")
        uv_scale_param.set_editor_property("default_value", 1.0)
        uv_scale_param.set_editor_property("group", "Environment")
        
        # Scale the UVs
        uv_multiply = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, -1900, -75)
        self.lib.connect_material_expressions(tex_coords, "", uv_multiply, "A")
        self.lib.connect_material_expressions(uv_scale_param, "", uv_multiply, "B")
        
        # TEXTURE VARIATION SETUP
        variation_uvs = None
        if use_tex_var:
            unreal.log(f"🎲 Setting up environment texture variation system")
            
            # Create Variation Height Map parameter
            var_height_param = self.lib.create_material_expression(material, unreal.MaterialExpressionTextureSampleParameter2D, -1900, -150)
            var_height_param.set_editor_property("parameter_name", "VariationHeightMap")
            var_height_param.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_GRAYSCALE)
            var_height_param.set_editor_property("group", "Texture Variation")
            
            # Random Rotation and Scale boolean parameter
            random_rot_scale_param = self.lib.create_material_expression(material, unreal.MaterialExpressionStaticSwitchParameter, -1900, -200)
            random_rot_scale_param.set_editor_property("parameter_name", "RandomRotationScale")
            random_rot_scale_param.set_editor_property("default_value", True)
            random_rot_scale_param.set_editor_property("group", "Texture Variation")
            
            # TextureVariation function
            texture_var_func = self.lib.create_material_expression(material, unreal.MaterialExpressionMaterialFunctionCall, -1700, -125)
            texture_variation_function = unreal.EditorAssetLibrary.load_asset("/Engine/Functions/Engine_MaterialFunctions03/Texturing/TextureVariation")
            
            if texture_variation_function:
                texture_var_func.set_editor_property("material_function", texture_variation_function)
                
                # Connect scaled UVs and other inputs
                self.lib.connect_material_expressions(uv_multiply, "", texture_var_func, "UVs")
                self.lib.connect_material_expressions(var_height_param, "", texture_var_func, "Heightmap")
                self.lib.connect_material_expressions(random_rot_scale_param, "", texture_var_func, "Random Rotation and Scale")
                
                variation_uvs = texture_var_func
                unreal.log(f"✅ Environment texture variation function connected")
            else:
                unreal.log_error(f"❌ TextureVariation function not found")
                variation_uvs = uv_multiply  # Fallback to scaled UVs
        else:
            variation_uvs = uv_multiply  # Use scaled UVs without variation
        
        # Helper function to connect samples (handles both regular and triplanar)
        def connect_sample(sample, target_node, target_input):
            if isinstance(sample, tuple):
                source_node, output_pin = sample
                self.lib.connect_material_expressions(source_node, output_pin, target_node, target_input)
            else:
                self.lib.connect_material_expressions(sample, "", target_node, target_input)
        
        texture_coords = {
            "ColorA": (-1600, -200),
            "ColorB": (-1600, -300),
            "NormalA": (-1600, -400),
            "NormalB": (-1600, -500),
            "RoughnessA": (-1600, -600),
            "RoughnessB": (-1600, -700),
            "MetallicA": (-1600, -800),
            "MetallicB": (-1600, -900),
        }
        
        # Add height maps for nanite displacement
        if use_nanite:
            texture_coords["HeightA"] = (-1600, -1000)
            texture_coords["HeightB"] = (-1600, -1100)
            unreal.log(f"🏔️ Adding Height parameters for environment nanite displacement")
        
        samples = {}
        for param_name, (x, y) in texture_coords.items():
            if use_triplanar:
                unreal.log(f"🔺 Creating triplanar environment texture: {param_name}")
                # Create texture object parameter with proper grouping
                texture_param = self.lib.create_material_expression(material, unreal.MaterialExpressionTextureObjectParameter, x - 200, y)
                texture_param.set_editor_property("parameter_name", param_name)
                
                # Set parameter groups
                if "Color" in param_name:
                    texture_param.set_editor_property("group", "Color")
                elif "Normal" in param_name:
                    texture_param.set_editor_property("group", "Normal")
                elif "Roughness" in param_name:
                    texture_param.set_editor_property("group", "Roughness")
                elif "Metallic" in param_name:
                    texture_param.set_editor_property("group", "Metallic")
                elif "Height" in param_name:
                    texture_param.set_editor_property("group", "Displacement")
                
                if "Normal" in param_name:
                    # WorldAlignedNormal for normals
                    world_align_func = self.lib.create_material_expression(material, unreal.MaterialExpressionMaterialFunctionCall, x, y)
                    world_aligned_normal = unreal.EditorAssetLibrary.load_asset("/Engine/Functions/Engine_MaterialFunctions01/Texturing/WorldAlignedNormal")
                    
                    if world_aligned_normal:
                        world_align_func.set_editor_property("material_function", world_aligned_normal)
                        self.lib.connect_material_expressions(texture_param, "", world_align_func, "TextureObject")
                        
                        # Connect variation UVs if available
                        if variation_uvs:
                            self.lib.connect_material_expressions(variation_uvs, "", world_align_func, "UVs")
                        
                        samples[param_name] = (world_align_func, "XYZ Texture")
                        unreal.log(f"✅ Triplanar Normal: {param_name}")
                    else:
                        unreal.log_error(f"❌ WorldAlignedNormal not found for {param_name}")
                        samples[param_name] = self._create_regular_texture_sample_env(material, param_name, x, y, default_normal, variation_uvs)
                else:
                    # WorldAlignedTexture for everything else
                    world_align_func = self.lib.create_material_expression(material, unreal.MaterialExpressionMaterialFunctionCall, x, y)
                    world_aligned_texture = unreal.EditorAssetLibrary.load_asset("/Engine/Functions/Engine_MaterialFunctions01/Texturing/WorldAlignedTexture")
                    
                    if world_aligned_texture:
                        world_align_func.set_editor_property("material_function", world_aligned_texture)
                        self.lib.connect_material_expressions(texture_param, "", world_align_func, "TextureObject")
                        
                        # Connect variation UVs if available
                        if variation_uvs:
                            self.lib.connect_material_expressions(variation_uvs, "", world_align_func, "UVs")
                        
                        samples[param_name] = (world_align_func, "XYZ Texture")
                        unreal.log(f"✅ Triplanar Texture: {param_name}")
                    else:
                        unreal.log_error(f"❌ WorldAlignedTexture not found for {param_name}")
                        samples[param_name] = self._create_regular_texture_sample_env(material, param_name, x, y, default_normal, variation_uvs)
            else:
                # Regular texture samples
                samples[param_name] = self._create_regular_texture_sample_env(material, param_name, x, y, default_normal, variation_uvs)
        
        # Blend mask
        blend_mask = self.lib.create_material_expression(material, unreal.MaterialExpressionTextureSampleParameter2D, -1600, -100)
        blend_mask.set_editor_property("parameter_name", "BlendMask")
        blend_mask.set_editor_property("group", "Environment")
        
        # Connect variation UVs to blend mask if available
        if variation_uvs:
            self.lib.connect_material_expressions(variation_uvs, "", blend_mask, "UVs")
        
        # Simple lerps
        color_lerp = self.lib.create_material_expression(material, unreal.MaterialExpressionLinearInterpolate, -1200, -250)
        connect_sample(samples["ColorA"], color_lerp, "A")
        connect_sample(samples["ColorB"], color_lerp, "B")
        self.lib.connect_material_expressions(blend_mask, "", color_lerp, "Alpha")
        
        normal_lerp = self.lib.create_material_expression(material, unreal.MaterialExpressionLinearInterpolate, -1200, -450)
        connect_sample(samples["NormalA"], normal_lerp, "A")
        connect_sample(samples["NormalB"], normal_lerp, "B")
        self.lib.connect_material_expressions(blend_mask, "", normal_lerp, "Alpha")
        
        roughness_lerp = self.lib.create_material_expression(material, unreal.MaterialExpressionLinearInterpolate, -1200, -650)
        connect_sample(samples["RoughnessA"], roughness_lerp, "A")
        connect_sample(samples["RoughnessB"], roughness_lerp, "B")
        self.lib.connect_material_expressions(blend_mask, "", roughness_lerp, "Alpha")
        
        metallic_lerp = self.lib.create_material_expression(material, unreal.MaterialExpressionLinearInterpolate, -1200, -850)
        connect_sample(samples["MetallicA"], metallic_lerp, "A")
        connect_sample(samples["MetallicB"], metallic_lerp, "B")
        self.lib.connect_material_expressions(blend_mask, "", metallic_lerp, "Alpha")
        
        # Height lerp for displacement (if nanite enabled)
        height_lerp = None
        if use_nanite and "HeightA" in samples and "HeightB" in samples:
            height_lerp = self.lib.create_material_expression(material, unreal.MaterialExpressionLinearInterpolate, -1200, -1050)
            connect_sample(samples["HeightA"], height_lerp, "A")
            connect_sample(samples["HeightB"], height_lerp, "B")
            self.lib.connect_material_expressions(blend_mask, "", height_lerp, "Alpha")
            unreal.log(f"🏔️ Environment height lerp created")
        
        # Color controls for simple environment
        brightness_param = self.lib.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -900, -200)
        brightness_param.set_editor_property("parameter_name", "Brightness")
        brightness_param.set_editor_property("default_value", 1.0)
        brightness_param.set_editor_property("group", "Color")
        
        brightness_multiply = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, -750, -250)
        self.lib.connect_material_expressions(color_lerp, "", brightness_multiply, "A")
        self.lib.connect_material_expressions(brightness_param, "", brightness_multiply, "B")
        
        # Displacement setup for nanite
        displacement_final = None
        if use_nanite and height_lerp:
            displacement_intensity = self.lib.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -900, -1000)
            displacement_intensity.set_editor_property("parameter_name", "DisplacementIntensity")
            displacement_intensity.set_editor_property("default_value", 0.1)
            displacement_intensity.set_editor_property("group", "Displacement")
            
            displacement_multiply = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, -750, -1050)
            self.lib.connect_material_expressions(height_lerp, "", displacement_multiply, "A")
            self.lib.connect_material_expressions(displacement_intensity, "", displacement_multiply, "B")
            
            displacement_final = displacement_multiply
            unreal.log(f"🏔️ Environment displacement setup complete")
        
        # Final single slab for simple environment
        slab = self.lib.create_material_expression(material, unreal.MaterialExpressionSubstrateSlabBSDF, -600, -500)
        self.lib.connect_material_expressions(brightness_multiply, "", slab, "Diffuse Albedo")
        self.lib.connect_material_expressions(normal_lerp, "", slab, "Normal")
        self.lib.connect_material_expressions(roughness_lerp, "", slab, "Roughness")
        self.lib.connect_material_expressions(metallic_lerp, "", slab, "F0")
        
        # Connect to material output
        self.lib.connect_material_property(slab, "", unreal.MaterialProperty.MP_FRONT_MATERIAL)
        
        # Connect displacement if nanite enabled
        if use_nanite and displacement_final:
            try:
                self.lib.connect_material_property(displacement_final, "", unreal.MaterialProperty.MP_DISPLACEMENT)
                unreal.log(f"🏔️ Environment displacement connected to MP_DISPLACEMENT")
            except AttributeError:
                try:
                    self.lib.connect_material_property(displacement_final, "", unreal.MaterialProperty.MP_TESSELLATION_MULTIPLIER)
                    unreal.log(f"🏔️ Environment displacement connected to MP_TESSELLATION_MULTIPLIER")
                except AttributeError:
                    self.lib.connect_material_property(displacement_final, "", unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
                    unreal.log_warning(f"⚠️ Environment displacement using MP_WORLD_POSITION_OFFSET as fallback")
        
        unreal.log("✅ Simple environment material with UV scale and texture variation created!")
    
    def _build_environment_graph_advanced(self, material, use_triplanar=False, use_nanite=False, use_tex_var=False):
        """Build advanced environment material with UV scale and texture variation"""
        default_normal = AutoMattyUtils.find_default_normal()
        
        unreal.log("🎛️ Building advanced dual-slab environment material...")
        
        # UV SCALE SETUP FOR ADVANCED ENVIRONMENT
        tex_coords = self.lib.create_material_expression(material, unreal.MaterialExpressionTextureCoordinate, -2000, -50)
        
        # UV Scale parameter
        uv_scale_param = self.lib.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -2000, -100)
        uv_scale_param.set_editor_property("parameter_name", "UVScale")
        uv_scale_param.set_editor_property("default_value", 1.0)
        uv_scale_param.set_editor_property("group", "Environment")
        
        # Scale the UVs
        uv_multiply = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, -1900, -75)
        self.lib.connect_material_expressions(tex_coords, "", uv_multiply, "A")
        self.lib.connect_material_expressions(uv_scale_param, "", uv_multiply, "B")
        
        # TEXTURE VARIATION SETUP FOR ADVANCED
        variation_uvs = None
        if use_tex_var:
            unreal.log(f"🎲 Setting up advanced environment texture variation system")
            
            # Create Variation Height Map parameter
            var_height_param = self.lib.create_material_expression(material, unreal.MaterialExpressionTextureSampleParameter2D, -1900, -150)
            var_height_param.set_editor_property("parameter_name", "VariationHeightMap")
            var_height_param.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_GRAYSCALE)
            var_height_param.set_editor_property("group", "Texture Variation")
            
            # Random Rotation and Scale boolean parameter
            random_rot_scale_param = self.lib.create_material_expression(material, unreal.MaterialExpressionStaticSwitchParameter, -1900, -200)
            random_rot_scale_param.set_editor_property("parameter_name", "RandomRotationScale")
            random_rot_scale_param.set_editor_property("default_value", True)
            random_rot_scale_param.set_editor_property("group", "Texture Variation")
            
            # TextureVariation function
            texture_var_func = self.lib.create_material_expression(material, unreal.MaterialExpressionMaterialFunctionCall, -1700, -125)
            texture_variation_function = unreal.EditorAssetLibrary.load_asset("/Engine/Functions/Engine_MaterialFunctions03/Texturing/TextureVariation")
            
            if texture_variation_function:
                texture_var_func.set_editor_property("material_function", texture_variation_function)
                
                # Connect scaled UVs and other inputs
                self.lib.connect_material_expressions(uv_multiply, "", texture_var_func, "UVs")
                self.lib.connect_material_expressions(var_height_param, "", texture_var_func, "Heightmap")
                self.lib.connect_material_expressions(random_rot_scale_param, "", texture_var_func, "Random Rotation and Scale")
                
                variation_uvs = texture_var_func
                unreal.log(f"✅ Advanced environment texture variation function connected")
            else:
                unreal.log_error(f"❌ TextureVariation function not found")
                variation_uvs = uv_multiply  # Fallback to scaled UVs
        else:
            variation_uvs = uv_multiply  # Use scaled UVs without variation
        
        # Helper function to connect samples (handles both regular and triplanar)
        def connect_sample(sample, target_node, target_input):
            if isinstance(sample, tuple):
                source_node, output_pin = sample
                self.lib.connect_material_expressions(source_node, output_pin, target_node, target_input)
            else:
                self.lib.connect_material_expressions(sample, "", target_node, target_input)
        
        # Material A textures
        texture_coords_a = {
            "ColorA": (-1800, -200),
            "NormalA": (-1800, -300),
            "RoughnessA": (-1800, -400),
            "MetallicA": (-1800, -500),
        }
        
        # Material B textures
        texture_coords_b = {
            "ColorB": (-1800, -700),
            "NormalB": (-1800, -800),
            "RoughnessB": (-1800, -900),
            "MetallicB": (-1800, -1000),
        }
        
        # Add height maps for nanite displacement
        if use_nanite:
            texture_coords_a["HeightA"] = (-1800, -600)
            texture_coords_b["HeightB"] = (-1800, -1100)
            unreal.log(f"🏔️ Adding Height parameters for advanced environment nanite displacement")
        
        samples_a = {}
        samples_b = {}
        
        # Create Material A textures with variation UVs
        for param_name, (x, y) in texture_coords_a.items():
            if use_triplanar:
                texture_param = self.lib.create_material_expression(material, unreal.MaterialExpressionTextureObjectParameter, x - 200, y)
                texture_param.set_editor_property("parameter_name", param_name)
                texture_param.set_editor_property("group", "Material A")
                
                if "Normal" in param_name:
                    world_align_func = self.lib.create_material_expression(material, unreal.MaterialExpressionMaterialFunctionCall, x, y)
                    world_aligned_normal = unreal.EditorAssetLibrary.load_asset("/Engine/Functions/Engine_MaterialFunctions01/Texturing/WorldAlignedNormal")
                    if world_aligned_normal:
                        world_align_func.set_editor_property("material_function", world_aligned_normal)
                        self.lib.connect_material_expressions(texture_param, "", world_align_func, "TextureObject")
                        if variation_uvs:
                            self.lib.connect_material_expressions(variation_uvs, "", world_align_func, "UVs")
                        samples_a[param_name] = (world_align_func, "XYZ Texture")
                    else:
                        samples_a[param_name] = self._create_regular_texture_sample_env(material, param_name, x, y, default_normal, variation_uvs)
                else:
                    world_align_func = self.lib.create_material_expression(material, unreal.MaterialExpressionMaterialFunctionCall, x, y)
                    world_aligned_texture = unreal.EditorAssetLibrary.load_asset("/Engine/Functions/Engine_MaterialFunctions01/Texturing/WorldAlignedTexture")
                    if world_aligned_texture:
                        world_align_func.set_editor_property("material_function", world_aligned_texture)
                        self.lib.connect_material_expressions(texture_param, "", world_align_func, "TextureObject")
                        if variation_uvs:
                            self.lib.connect_material_expressions(variation_uvs, "", world_align_func, "UVs")
                        samples_a[param_name] = (world_align_func, "XYZ Texture")
                    else:
                        samples_a[param_name] = self._create_regular_texture_sample_env(material, param_name, x, y, default_normal, variation_uvs)
            else:
                samples_a[param_name] = self._create_regular_texture_sample_env(material, param_name, x, y, default_normal, variation_uvs)
        
        # Create Material B textures with variation UVs
        for param_name, (x, y) in texture_coords_b.items():
            if use_triplanar:
                texture_param = self.lib.create_material_expression(material, unreal.MaterialExpressionTextureObjectParameter, x - 200, y)
                texture_param.set_editor_property("parameter_name", param_name)
                texture_param.set_editor_property("group", "Material B")
                
                if "Normal" in param_name:
                    world_align_func = self.lib.create_material_expression(material, unreal.MaterialExpressionMaterialFunctionCall, x, y)
                    world_aligned_normal = unreal.EditorAssetLibrary.load_asset("/Engine/Functions/Engine_MaterialFunctions01/Texturing/WorldAlignedNormal")
                    if world_aligned_normal:
                        world_align_func.set_editor_property("material_function", world_aligned_normal)
                        self.lib.connect_material_expressions(texture_param, "", world_align_func, "TextureObject")
                        if variation_uvs:
                            self.lib.connect_material_expressions(variation_uvs, "", world_align_func, "UVs")
                        samples_b[param_name] = (world_align_func, "XYZ Texture")
                    else:
                        samples_b[param_name] = self._create_regular_texture_sample_env(material, param_name, x, y, default_normal, variation_uvs)
                else:
                    world_align_func = self.lib.create_material_expression(material, unreal.MaterialExpressionMaterialFunctionCall, x, y)
                    world_aligned_texture = unreal.EditorAssetLibrary.load_asset("/Engine/Functions/Engine_MaterialFunctions01/Texturing/WorldAlignedTexture")
                    if world_aligned_texture:
                        world_align_func.set_editor_property("material_function", world_aligned_texture)
                        self.lib.connect_material_expressions(texture_param, "", world_align_func, "TextureObject")
                        if variation_uvs:
                            self.lib.connect_material_expressions(variation_uvs, "", world_align_func, "UVs")
                        samples_b[param_name] = (world_align_func, "XYZ Texture")
                    else:
                        samples_b[param_name] = self._create_regular_texture_sample_env(material, param_name, x, y, default_normal, variation_uvs)
            else:
                samples_b[param_name] = self._create_regular_texture_sample_env(material, param_name, x, y, default_normal, variation_uvs)
        
        # Create SLAB A
        slab_a = self.lib.create_material_expression(material, unreal.MaterialExpressionSubstrateSlabBSDF, -1400, -350)
        connect_sample(samples_a["ColorA"], slab_a, "Diffuse Albedo")
        connect_sample(samples_a["NormalA"], slab_a, "Normal")
        connect_sample(samples_a["RoughnessA"], slab_a, "Roughness")
        connect_sample(samples_a["MetallicA"], slab_a, "F0")
        
        # Create SLAB B
        slab_b = self.lib.create_material_expression(material, unreal.MaterialExpressionSubstrateSlabBSDF, -1400, -750)
        connect_sample(samples_b["ColorB"], slab_b, "Diffuse Albedo")
        connect_sample(samples_b["NormalB"], slab_b, "Normal")
        connect_sample(samples_b["RoughnessB"], slab_b, "Roughness")
        connect_sample(samples_b["MetallicB"], slab_b, "F0")
        
        # Simple world-space mixing using scaled UVs
        world_pos = self.lib.create_material_expression(material, unreal.MaterialExpressionWorldPosition, -1600, -100)
        
        # Break out just the Z component for height-based mixing
        component_mask = self.lib.create_material_expression(material, unreal.MaterialExpressionComponentMask, -1500, -100)
        component_mask.set_editor_property("r", False)
        component_mask.set_editor_property("g", False)
        component_mask.set_editor_property("b", True)  # Z component
        component_mask.set_editor_property("a", False)
        self.lib.connect_material_expressions(world_pos, "", component_mask, "")
        
        # Scale the world position
        scale_param = self.lib.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1600, -150)
        scale_param.set_editor_property("parameter_name", "MixScale")
        scale_param.set_editor_property("default_value", 0.001)
        scale_param.set_editor_property("group", "Advanced Mixing")
        
        scale_multiply = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, -1400, -125)
        self.lib.connect_material_expressions(component_mask, "", scale_multiply, "A")
        self.lib.connect_material_expressions(scale_param, "", scale_multiply, "B")
        
        # Frac to create tiling pattern
        frac_node = self.lib.create_material_expression(material, unreal.MaterialExpressionFrac, -1300, -125)
        self.lib.connect_material_expressions(scale_multiply, "", frac_node, "")
        
        # Displacement setup for advanced environment
        displacement_final = None
        if use_nanite and "HeightA" in samples_a and "HeightB" in samples_b:
            # Lerp between height A and B using the world-space mixing pattern
            height_lerp = self.lib.create_material_expression(material, unreal.MaterialExpressionLinearInterpolate, -1200, -1150)
            connect_sample(samples_a["HeightA"], height_lerp, "A")
            connect_sample(samples_b["HeightB"], height_lerp, "B")
            self.lib.connect_material_expressions(frac_node, "", height_lerp, "Alpha")
            
            displacement_intensity = self.lib.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1400, -1200)
            displacement_intensity.set_editor_property("parameter_name", "DisplacementIntensity")
            displacement_intensity.set_editor_property("default_value", 0.1)
            displacement_intensity.set_editor_property("group", "Displacement")
            
            displacement_multiply = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, -1000, -1150)
            self.lib.connect_material_expressions(height_lerp, "", displacement_multiply, "A")
            self.lib.connect_material_expressions(displacement_intensity, "", displacement_multiply, "B")
            
            displacement_final = displacement_multiply
            unreal.log(f"🏔️ Advanced environment displacement setup complete")
        
        # SUBSTRATE HORIZONTAL MIXING NODE
        substrate_mix = self.lib.create_material_expression(material, unreal.MaterialExpressionSubstrateHorizontalMixing, -1000, -550)
        self.lib.connect_material_expressions(slab_a, "", substrate_mix, "Background")
        self.lib.connect_material_expressions(slab_b, "", substrate_mix, "Foreground")
        self.lib.connect_material_expressions(frac_node, "", substrate_mix, "Mix")
        
        # Connect to material output
        self.lib.connect_material_property(substrate_mix, "", unreal.MaterialProperty.MP_FRONT_MATERIAL)
        
        # Connect displacement if nanite enabled
        if use_nanite and displacement_final:
            try:
                self.lib.connect_material_property(displacement_final, "", unreal.MaterialProperty.MP_DISPLACEMENT)
                unreal.log(f"🏔️ Advanced environment displacement connected to MP_DISPLACEMENT")
            except AttributeError:
                try:
                    self.lib.connect_material_property(displacement_final, "", unreal.MaterialProperty.MP_TESSELLATION_MULTIPLIER)
                    unreal.log(f"🏔️ Advanced environment displacement connected to MP_TESSELLATION_MULTIPLIER")
                except AttributeError:
                    self.lib.connect_material_property(displacement_final, "", unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
                    unreal.log_warning(f"⚠️ Advanced environment displacement using MP_WORLD_POSITION_OFFSET as fallback")
        
        unreal.log("✅ Advanced dual-slab environment with UV scale and texture variation created!")
    
    def _create_regular_texture_sample_env(self, material, param_name, x, y, default_normal=None, variation_uvs=None):
        """Create regular texture sample for environment materials with variation UVs"""
        tex_node = self.lib.create_material_expression(material, unreal.MaterialExpressionTextureSampleParameter2D, x, y)
        tex_node.set_editor_property("parameter_name", param_name)
        
        # Connect variation UVs if provided
        if variation_uvs:
            self.lib.connect_material_expressions(variation_uvs, "", tex_node, "UVs")
            unreal.log(f"🎲 Connected variation UVs to environment {param_name}")
        
        # Set parameter groups
        if "Color" in param_name:
            tex_node.set_editor_property("group", "Color")
        elif "Normal" in param_name:
            tex_node.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
            tex_node.set_editor_property("group", "Normal")
            if default_normal:
                tex_node.set_editor_property("texture", default_normal)
        elif "Roughness" in param_name:
            tex_node.set_editor_property("group", "Roughness")
        elif "Metallic" in param_name:
            tex_node.set_editor_property("group", "Metallic")
        elif "Height" in param_name:
            tex_node.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_GRAYSCALE)
            tex_node.set_editor_property("group", "Displacement")
            unreal.log(f"🏔️ Environment Height texture sample: {param_name}")
        
        return tex_node

# Convenience functions
def create_orm_material():
    """Create basic ORM material"""
    builder = SubstrateMaterialBuilder()
    return builder.create_orm_material()

def create_split_material():
    """Create basic Split material"""
    builder = SubstrateMaterialBuilder()
    return builder.create_split_material()

def create_environment_material():
    """Create basic Environment material"""
    builder = SubstrateMaterialBuilder()
    return builder.create_environment_material()

# Config button functions with all new parameters
def create_environment_material_with_options(use_adv_env=False, use_triplanar=False, use_nanite=False, use_tex_var=False):
    """Create Environment material with all options including texture variation"""
    builder = SubstrateMaterialBuilder()
    return builder.create_environment_material(use_adv_env=use_adv_env, use_triplanar=use_triplanar, use_nanite=use_nanite, use_tex_var=use_tex_var)

if __name__ == "__main__":
    create_orm_material()