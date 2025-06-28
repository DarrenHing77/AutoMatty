import unreal
from automatty_config import AutoMattyConfig, AutoMattyUtils

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
    
    def create_orm_material(self, base_name="M_AutoMattyORM", custom_path=None):
        """Create ORM packed Substrate material"""
        if not AutoMattyUtils.is_substrate_enabled():
            unreal.log_error("❌ Substrate is not enabled in project settings!")
            return None
        
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
    
    def create_split_material(self, base_name="M_AutoMattySplit", custom_path=None):
        """Create split texture Substrate material"""
        if not AutoMattyUtils.is_substrate_enabled():
            unreal.log_error("❌ Substrate is not enabled in project settings!")
            return None
        
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
    
    def create_advanced_material(self, base_name="M_AdvancedSubstrate", custom_path=None):
        """Create advanced Substrate material with built-in UE functions"""
        if not AutoMattyUtils.is_substrate_enabled():
            unreal.log_error("❌ Substrate is not enabled in project settings!")
            return None
        
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
        """Build ORM material node graph"""
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
        
        # Split ORM channels
        rough_mask = self.lib.create_material_expression(
            material, unreal.MaterialExpressionComponentMask, -200, 50
        )
        rough_mask.set_editor_property("g", True)
        self.lib.connect_material_expressions(samples["ORM"], "", rough_mask, "")
        self.lib.connect_material_expressions(rough_mask, "", slab, "Roughness")
        
        metal_mask = self.lib.create_material_expression(
            material, unreal.MaterialExpressionComponentMask, -200, -150
        )
        metal_mask.set_editor_property("b", True)
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
        """Build advanced material using built-in UE material expression nodes"""
        default_normal = AutoMattyUtils.find_default_normal()
        
        # === COLOR CHANNEL GROUP ===
        color_tex = self.lib.create_material_expression(
            material, unreal.MaterialExpressionTextureSampleParameter2D, -800, 400
        )
        color_tex.set_editor_property("parameter_name", "Color")

        # Color Contrast using Power node (cheap contrast approximation)
        color_contrast_param = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -600, 450
        )
        color_contrast_param.set_editor_property("parameter_name", "ColorContrast")
        color_contrast_param.set_editor_property("default_value", 1.0)
        
        color_power = self.lib.create_material_expression(
            material, unreal.MaterialExpressionPower, -600, 400
        )
        self.lib.connect_material_expressions(color_tex, "", color_power, "Base")
        self.lib.connect_material_expressions(color_contrast_param, "", color_power, "Exp")

        # Color Remap using Lerp
        color_min_param = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -400, 350
        )
        color_min_param.set_editor_property("parameter_name", "ColorMin")
        color_min_param.set_editor_property("default_value", 0.0)
        
        color_max_param = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -400, 450
        )
        color_max_param.set_editor_property("parameter_name", "ColorMax")
        color_max_param.set_editor_property("default_value", 1.0)
        
        color_lerp = self.lib.create_material_expression(
            material, unreal.MaterialExpressionLinearInterpolate, -400, 400
        )
        self.lib.connect_material_expressions(color_min_param, "", color_lerp, "A")
        self.lib.connect_material_expressions(color_max_param, "", color_lerp, "B")
        self.lib.connect_material_expressions(color_power, "", color_lerp, "Alpha")

        # === ORM CHANNEL GROUP ===
        orm_tex = self.lib.create_material_expression(
            material, unreal.MaterialExpressionTextureSampleParameter2D, -800, 0
        )
        orm_tex.set_editor_property("parameter_name", "ORM")

        # Roughness mask (G channel)
        rough_mask = self.lib.create_material_expression(
            material, unreal.MaterialExpressionComponentMask, -600, 0
        )
        rough_mask.set_editor_property("g", True)
        self.lib.connect_material_expressions(orm_tex, "", rough_mask, "")

        # Roughness Contrast
        rough_contrast_param = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -400, 50
        )
        rough_contrast_param.set_editor_property("parameter_name", "RoughnessContrast")
        rough_contrast_param.set_editor_property("default_value", 1.0)
        
        rough_power = self.lib.create_material_expression(
            material, unreal.MaterialExpressionPower, -400, 0
        )
        self.lib.connect_material_expressions(rough_mask, "", rough_power, "Base")
        self.lib.connect_material_expressions(rough_contrast_param, "", rough_power, "Exp")

        # Roughness Remap
        rough_min_param = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -200, -50
        )
        rough_min_param.set_editor_property("parameter_name", "RoughnessMin")
        rough_min_param.set_editor_property("default_value", 0.0)
        
        rough_max_param = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -200, 50
        )
        rough_max_param.set_editor_property("parameter_name", "RoughnessMax")
        rough_max_param.set_editor_property("default_value", 1.0)
        
        rough_lerp = self.lib.create_material_expression(
            material, unreal.MaterialExpressionLinearInterpolate, -200, 0
        )
        self.lib.connect_material_expressions(rough_min_param, "", rough_lerp, "A")
        self.lib.connect_material_expressions(rough_max_param, "", rough_lerp, "B")
        self.lib.connect_material_expressions(rough_power, "", rough_lerp, "Alpha")

        # Metallic mask (B channel)
        metal_mask = self.lib.create_material_expression(
            material, unreal.MaterialExpressionComponentMask, -600, -150
        )
        metal_mask.set_editor_property("b", True)
        self.lib.connect_material_expressions(orm_tex, "", metal_mask, "")

        # === NORMAL CHANNEL GROUP ===
        normal_tex = self.lib.create_material_expression(
            material, unreal.MaterialExpressionTextureSampleParameter2D, -800, -300
        )
        normal_tex.set_editor_property("parameter_name", "Normal")
        normal_tex.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
        if default_normal:
            normal_tex.set_editor_property("texture", default_normal)

        # === MFP/SSS CHANNEL GROUP ===
        # UseDiffuseAsMFP switch
        switch = self.lib.create_material_expression(
            material, unreal.MaterialExpressionStaticSwitchParameter, -800, -500
        )
        switch.set_editor_property("parameter_name", "UseDiffuseAsMFP")
        switch.set_editor_property("default_value", True)

        # MFP Color Multiplier
        mfp_col_mult = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -600, -500
        )
        mfp_col_mult.set_editor_property("parameter_name", "MFPColorMultiplier")
        mfp_col_mult.set_editor_property("default_value", 1.0)

        # MFP Scale
        mfp_scale = self.lib.create_material_expression(
            material, unreal.MaterialExpressionScalarParameter, -400, -500
        )
        mfp_scale.set_editor_property("parameter_name", "MFPScale")
        mfp_scale.set_editor_property("default_value", 1.0)

        # Multiply Color * MFPColorMultiplier
        mfp_mul = self.lib.create_material_expression(
            material, unreal.MaterialExpressionMultiply, -200, -450
        )
        self.lib.connect_material_expressions(color_tex, "", mfp_mul, "A")
        self.lib.connect_material_expressions(mfp_col_mult, "", mfp_mul, "B")

        # Switch: True = mul result, False = raw color
        self.lib.connect_material_expressions(mfp_mul, "", switch, "True")
        self.lib.connect_material_expressions(color_tex, "", switch, "False")

        # === SUBSTRATE SLAB BSDF & HOOKUP ===
        slab = self.lib.create_material_expression(
            material, unreal.MaterialExpressionSubstrateSlabBSDF, 200, 0
        )

        # Connect processed outputs
        self.lib.connect_material_expressions(color_lerp, "", slab, "Diffuse Albedo")
        self.lib.connect_material_expressions(rough_lerp, "", slab, "Roughness")
        self.lib.connect_material_expressions(metal_mask, "", slab, "F0")
        
        # Use R channel for AO
        ao_mask = self.lib.create_material_expression(
            material, unreal.MaterialExpressionComponentMask, -600, -100
        )
        ao_mask.set_editor_property("r", True)
        self.lib.connect_material_expressions(orm_tex, "", ao_mask, "")
        self.lib.connect_material_expressions(ao_mask, "", slab, "AmbientOcclusion")
        
        self.lib.connect_material_expressions(normal_tex, "", slab, "Normal")
        self.lib.connect_material_expressions(switch, "", slab, "SSS MFP")
        self.lib.connect_material_expressions(mfp_scale, "", slab, "SSS MFP Scale")

        # Wire to output
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