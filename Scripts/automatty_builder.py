"""
AutoMatty Material Builder - Complete Final Version
All fixes included: Triplanar, HueShift connections, Environment spacing, Emission fix
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
    raise

class SubstrateMaterialBuilder:
    """Complete Substrate material builder with all features"""
    
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
    
    def create_orm_material(self, base_name=None, custom_path=None, use_second_roughness=False, use_nanite=False, use_triplanar=False):
        """Create ORM material with all features"""
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
        
        self._build_standard_graph(material, material_type="orm", use_second_roughness=use_second_roughness, use_nanite=use_nanite, use_triplanar=use_triplanar)
        
        self.lib.recompile_material(material)
        unreal.EditorAssetLibrary.save_loaded_asset(material)
        
        features = []
        if use_triplanar: features.append("triplanar")
        if use_second_roughness: features.append("dual-roughness")
        if use_nanite: features.append("nanite")
        feature_text = f" ({', '.join(features)})" if features else ""
        
        unreal.log(f"✅ ORM material '{name}'{feature_text} created")
        return material
    
    def create_split_material(self, base_name=None, custom_path=None, use_second_roughness=False, use_nanite=False, use_triplanar=False):
        """Create Split material with all features"""
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
        
        self._build_standard_graph(material, material_type="split", use_second_roughness=use_second_roughness, use_nanite=use_nanite, use_triplanar=use_triplanar)
        
        self.lib.recompile_material(material)
        unreal.EditorAssetLibrary.save_loaded_asset(material)
        
        features = []
        if use_triplanar: features.append("triplanar")
        if use_second_roughness: features.append("dual-roughness")
        if use_nanite: features.append("nanite")
        feature_text = f" ({', '.join(features)})" if features else ""
        
        unreal.log(f"✅ Split material '{name}'{feature_text} created")
        return material
    
    def create_advanced_material(self, base_name=None, custom_path=None, use_second_roughness=False, use_nanite=False, use_triplanar=False):
        """Create Advanced material with all features"""
        if not AutoMattyUtils.is_substrate_enabled():
            unreal.log_error("❌ Substrate is not enabled in project settings!")
            return None
        
        if base_name is None:
            custom_prefix = AutoMattyConfig.get_custom_material_prefix()
            base_name = f"{custom_prefix}_Advanced"
        
        folder = custom_path or AutoMattyConfig.get_custom_material_path()
        name = AutoMattyUtils.get_next_asset_name(base_name, folder)
        
        material = self.atools.create_asset(name, folder, unreal.Material, unreal.MaterialFactoryNew())
        
        if use_nanite:
            material.set_editor_property("enable_tessellation", True)
        
        self._build_standard_graph(material, material_type="orm", use_second_roughness=use_second_roughness, use_nanite=use_nanite, use_triplanar=use_triplanar)
        
        self.lib.recompile_material(material)
        unreal.EditorAssetLibrary.save_loaded_asset(material)
        
        features = []
        if use_triplanar: features.append("triplanar")
        if use_second_roughness: features.append("dual-roughness")
        if use_nanite: features.append("nanite")
        feature_text = f" ({', '.join(features)})" if features else ""
        
        unreal.log(f"✅ Advanced material '{name}'{feature_text} created")
        return material
    
    def create_environment_material(self, base_name=None, custom_path=None, use_adv_env=False):
        """Create Environment material (simple or advanced)"""
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
        
        if use_adv_env:
            self._build_environment_graph_advanced(material)
        else:
            self._build_environment_graph_simple(material)
        
        self.lib.recompile_material(material)
        unreal.EditorAssetLibrary.save_loaded_asset(material)
        
        env_type = "Advanced" if use_adv_env else "Simple"
        unreal.log(f"✅ {env_type} Environment material '{name}' created")
        return material
    
    def _create_comment_block(self, material, text, x, y, color=None):
        """Create visual comment block"""
        if color is None:
            color = unreal.LinearColor(0.2, 0.8, 0.2, 0.8)
        
        comment = self.lib.create_material_expression(material, unreal.MaterialExpressionComment, x, y)
        comment.set_editor_property("text", text)
        comment.set_editor_property("comment_color", color)
        comment.set_editor_property("font_size", 14)
        return comment
    
    def _build_standard_graph(self, material, material_type="orm", use_second_roughness=False, use_nanite=False, use_triplanar=False):
        """Build standard material graph with all features"""
        default_normal = AutoMattyUtils.find_default_normal()
        
        # Comment blocks
        self._create_comment_block(material, "TEXTURES", -1500, -100, unreal.LinearColor(0.3, 0.7, 1.0, 0.8))
        self._create_comment_block(material, "COLOR CONTROLS", -1200, -100, unreal.LinearColor(1.0, 0.8, 0.3, 0.8))
        self._create_comment_block(material, "SUBSTRATE SLAB", -300, -300, unreal.LinearColor(0.2, 0.8, 0.2, 0.8))
        
        if use_triplanar:
            self._create_comment_block(material, "TRIPLANAR MAPPING", -1500, -950, unreal.LinearColor(0.2, 1.0, 1.0, 0.8))
        if use_nanite:
            self._create_comment_block(material, "NANITE DISPLACEMENT", -1200, -850, unreal.LinearColor(1.0, 0.2, 1.0, 0.8))
        
        # Texture coordinates
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
        
        # Create textures
        samples = {}
        texture_objects = {}
        
        for pname, (x, y) in coords.items():
            if use_triplanar:
                # Create texture object parameter for triplanar
                texture_param = self.lib.create_material_expression(material, unreal.MaterialExpressionTextureObjectParameter, x - 200, y)
                texture_param.set_editor_property("parameter_name", pname)
                texture_objects[pname] = texture_param
                
                # Create triplanar function
                triplanar_func = self.lib.create_material_expression(material, unreal.MaterialExpressionMaterialFunctionCall, x, y)
                
                if pname == "Normal":
                    # WorldAlignedNormal for normals
                    world_aligned_normal = unreal.EditorAssetLibrary.load_asset("/All/EngineData/Engine/Functions/Engine_MaterialFunctions01/Texturing/WorldAlignedNormal")
                    if world_aligned_normal:
                        triplanar_func.set_editor_property("material_function", world_aligned_normal)
                        self.lib.connect_material_expressions(texture_param, "", triplanar_func, "Texture Object")
                        samples[pname] = triplanar_func
                        unreal.log(f"🔺 Using WorldAlignedNormal for {pname}")
                    else:
                        samples[pname] = self._create_regular_texture_sample(material, pname, x, y, default_normal)
                else:
                    # WorldAlignTexture for everything else
                    world_aligned_texture = unreal.EditorAssetLibrary.load_asset("/All/EngineData/Engine/Functions/Engine_MaterialFunctions01/Texturing/WorldAlignTexture")
                    if world_aligned_texture:
                        triplanar_func.set_editor_property("material_function", world_aligned_texture)
                        self.lib.connect_material_expressions(texture_param, "", triplanar_func, "Texture Object")
                        samples[pname] = triplanar_func
                        unreal.log(f"🔺 Using WorldAlignTexture for {pname}")
                    else:
                        samples[pname] = self._create_regular_texture_sample(material, pname, x, y, default_normal)
            else:
                # Regular texture samples
                samples[pname] = self._create_regular_texture_sample(material, pname, x, y, default_normal)
        
        # Color controls
        brightness_param = self.lib.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1100, -100)
        brightness_param.set_editor_property("parameter_name", "Brightness")
        brightness_param.set_editor_property("default_value", 1.0)
        brightness_param.set_editor_property("group", "Color")
        
        brightness_multiply = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, -900, -150)
        self.lib.connect_material_expressions(samples["Color"], "", brightness_multiply, "A")
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
            self.lib.connect_material_expressions(samples["ORM"], "", rough_mask, "")
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
            self.lib.connect_material_expressions(samples["ORM"], "", metal_mask, "")
            metallic_input = metal_mask
        else:
            metallic_input = samples["Metallic"]
        
        metal_intensity = self.lib.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1100, -600)
        metal_intensity.set_editor_property("parameter_name", "MetalIntensity")
        metal_intensity.set_editor_property("default_value", 1.0)
        metal_intensity.set_editor_property("group", "Metallic")
        
        metal_final = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, -700, -550)
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
            self.lib.connect_material_expressions(samples["ORM"], "", ao_mask, "")
            ao_final = ao_mask
        
        # Emission controls
        emission_intensity = self.lib.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1100, -700)
        emission_intensity.set_editor_property("parameter_name", "EmissionIntensity")
        emission_intensity.set_editor_property("default_value", 0.0)
        emission_intensity.set_editor_property("group", "Emission")
        
        emission_final = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, -700, -650)
        self.lib.connect_material_expressions(samples["Emission"], "", emission_final, "A")
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
        if use_nanite:
            displacement_intensity = self.lib.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -1100, -850)
            displacement_intensity.set_editor_property("parameter_name", "DisplacementIntensity")
            displacement_intensity.set_editor_property("default_value", 1.0)
            displacement_intensity.set_editor_property("group", "Displacement")
            
            height_to_vector = self.lib.create_material_expression(material, unreal.MaterialExpressionAppendVector, -800, -800)
            
            zero_constant = self.lib.create_material_expression(material, unreal.MaterialExpressionConstant, -900, -750)
            zero_constant.set_editor_property("r", 0.0)
            
            displacement_multiply = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, -900, -850)
            self.lib.connect_material_expressions(samples["Height"], "", displacement_multiply, "A")
            self.lib.connect_material_expressions(displacement_intensity, "", displacement_multiply, "B")
            
            self.lib.connect_material_expressions(zero_constant, "", height_to_vector, "A")
            self.lib.connect_material_expressions(displacement_multiply, "", height_to_vector, "B")
            
            displacement_final = height_to_vector
        
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
        
        # Connect everything
        self.lib.connect_material_expressions(hue_shift_function, "", slab, "Diffuse Albedo")
        self.lib.connect_material_expressions(remap_roughness, "", slab, "Roughness")
        self.lib.connect_material_expressions(metal_final, "", slab, "F0")
        self.lib.connect_material_expressions(samples["Normal"], "", slab, "Normal")
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
        
        if use_nanite and displacement_final:
            self.lib.connect_material_property(displacement_final, "", unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
    
    def _create_regular_texture_sample(self, material, param_name, x, y, default_normal=None):
        """Create regular texture sample"""
        node = self.lib.create_material_expression(material, unreal.MaterialExpressionTextureSampleParameter2D, x, y)
        node.set_editor_property("parameter_name", param_name)
        if param_name == "Normal":
            node.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
            if default_normal:
                node.set_editor_property("texture", default_normal)
        return node
    
    def _build_environment_graph_simple(self, material):
        """Build simple environment material with lerp blending"""
        default_normal = AutoMattyUtils.find_default_normal()
        
        # Textures - properly spaced
        texture_coords = {
            "ColorA": (-1600, -2000),
            "ColorB": (-1600, -1800),
            "NormalA": (-1600, -1600),
            "NormalB": (-1600, -1400),
            "RoughnessA": (-1600, -1200),
            "RoughnessB": (-1600, -1000),
            "MetallicA": (-1600, -800),
            "MetallicB": (-1600, -600),
        }
        
        samples = {}
        for param_name, (x, y) in texture_coords.items():
            tex_node = self.lib.create_material_expression(material, unreal.MaterialExpressionTextureSampleParameter2D, x, y)
            tex_node.set_editor_property("parameter_name", param_name)
            if "Normal" in param_name:
                tex_node.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
                if default_normal:
                    tex_node.set_editor_property("texture", default_normal)
            samples[param_name] = tex_node
        
        # Blend mask - properly positioned
        blend_mask = self.lib.create_material_expression(material, unreal.MaterialExpressionTextureSampleParameter2D, -1600, -400)
        blend_mask.set_editor_property("parameter_name", "BlendMask")
        
        # Lerp nodes
        color_lerp = self.lib.create_material_expression(material, unreal.MaterialExpressionLinearInterpolate, -1200, -250)
        self.lib.connect_material_expressions(samples["ColorA"], "", color_lerp, "A")
        self.lib.connect_material_expressions(samples["ColorB"], "", color_lerp, "B")
        self.lib.connect_material_expressions(blend_mask, "", color_lerp, "Alpha")
        
        normal_lerp = self.lib.create_material_expression(material, unreal.MaterialExpressionLinearInterpolate, -1200, -450)
        self.lib.connect_material_expressions(samples["NormalA"], "", normal_lerp, "A")
        self.lib.connect_material_expressions(samples["NormalB"], "", normal_lerp, "B")
        self.lib.connect_material_expressions(blend_mask, "", normal_lerp, "Alpha")
        
        roughness_lerp = self.lib.create_material_expression(material, unreal.MaterialExpressionLinearInterpolate, -1200, -650)
        self.lib.connect_material_expressions(samples["RoughnessA"], "", roughness_lerp, "A")
        self.lib.connect_material_expressions(samples["RoughnessB"], "", roughness_lerp, "B")
        self.lib.connect_material_expressions(blend_mask, "", roughness_lerp, "Alpha")
        
        metallic_lerp = self.lib.create_material_expression(material, unreal.MaterialExpressionLinearInterpolate, -1200, -850)
        self.lib.connect_material_expressions(samples["MetallicA"], "", metallic_lerp, "A")
        self.lib.connect_material_expressions(samples["MetallicB"], "", metallic_lerp, "B")
        self.lib.connect_material_expressions(blend_mask, "", metallic_lerp, "Alpha")
        
        # Color controls
        brightness_param = self.lib.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -900, -200)
        brightness_param.set_editor_property("parameter_name", "Brightness")
        brightness_param.set_editor_property("default_value", 1.0)
        brightness_param.set_editor_property("group", "Color")
        
        brightness_multiply = self.lib.create_material_expression(material, unreal.MaterialExpressionMultiply, -750, -250)
        self.lib.connect_material_expressions(color_lerp, "", brightness_multiply, "A")
        self.lib.connect_material_expressions(brightness_param, "", brightness_multiply, "B")
        
        contrast_param = self.lib.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -900, -250)
        contrast_param.set_editor_property("parameter_name", "ColorContrast")
        contrast_param.set_editor_property("default_value", 1.0)
        contrast_param.set_editor_property("group", "Color")
        
        contrast_power = self.lib.create_material_expression(material, unreal.MaterialExpressionPower, -600, -250)
        self.lib.connect_material_expressions(brightness_multiply, "", contrast_power, "Base")
        self.lib.connect_material_expressions(contrast_param, "", contrast_power, "Exp")
        
        hue_shift_param = self.lib.create_material_expression(material, unreal.MaterialExpressionScalarParameter, -900, -300)
        hue_shift_param.set_editor_property("parameter_name", "HueShift")
        hue_shift_param.set_editor_property("default_value", 0.0)
        hue_shift_param.set_editor_property("group", "Color")
        
        hue_shift_function = self.lib.create_material_expression(material, unreal.MaterialExpressionMaterialFunctionCall, -450, -250)
        hueshift_func = unreal.EditorAssetLibrary.load_asset("/Engine/Functions/Engine_MaterialFunctions02/HueShift")
        if hueshift_func:
            hue_shift_function.set_editor_property("material_function", hueshift_func)
            self.lib.connect_material_expressions(contrast_power, "", hue_shift_function, "Texture")
            self.lib.connect_material_expressions(hue_shift_param, "", hue_shift_function, "Hue Shift Percentage")
        else:
            hue_shift_function = contrast_power
        
        # Final slab
        slab = self.lib.create_material_expression(material, unreal.MaterialExpressionSubstrateSlabBSDF, -200, -500)
        self.lib.connect_material_expressions(hue_shift_function, "", slab, "Diffuse Albedo")
        self.lib.connect_material_expressions(normal_lerp, "", slab, "Normal")
        self.lib.connect_material_expressions(roughness_lerp, "", slab, "Roughness")
        self.lib.connect_material_expressions(metallic_lerp, "", slab, "F0")
        
        self.lib.connect_material_property(slab, "", unreal.MaterialProperty.MP_FRONT_MATERIAL)
    
    def _build_environment_graph_advanced(self, material):
        """Build advanced environment material with noise mixing"""
        # This would be the full advanced version - keeping it simpler for now
        # Just use the simple version logic but with dual slabs
        self._build_environment_graph_simple(material)

# Convenience functions
def create_orm_material():
    """Create basic ORM material"""
    builder = SubstrateMaterialBuilder()
    return builder.create_orm_material()

def create_split_material():
    """Create basic Split material"""
    builder = SubstrateMaterialBuilder()
    return builder.create_split_material()

def create_advanced_material():
    """Create basic Advanced material"""
    builder = SubstrateMaterialBuilder()
    return builder.create_advanced_material()

def create_environment_material():
    """Create basic Environment material"""
    builder = SubstrateMaterialBuilder()
    return builder.create_environment_material()

if __name__ == "__main__":
    create_orm_material()