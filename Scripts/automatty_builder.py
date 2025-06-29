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

# Usage functions
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
    builder.create_orm_material()
    builder.create_split_material()