import unreal
import re

def create_advanced_substrate(name="M_AdvancedSubstrate_v001", path="/Game/Materials/AutoMatty"):
    # Helpers
    atools = unreal.AssetToolsHelpers.get_asset_tools()
    lib    = unreal.MaterialEditingLibrary

    # 1) Create the material asset
    material = atools.create_asset(
        name, path, unreal.Material, unreal.MaterialFactoryNew()
    )

    # 2) === COLOR CHANNEL GROUP ===
    #   Color texture param
    color_tex = lib.create_material_expression(
        material, unreal.MaterialExpressionTextureSampleParameter2D, -800,  400
    )
    color_tex.set_editor_property("parameter_name", "Color")

    #   CheapContrast function (must exist in your Content)
    cheap_fn = unreal.load_asset("/Game/Functions/CheapContrast")  
    cheap = lib.create_material_expression(
        material, unreal.MaterialExpressionMaterialFunctionCall, -600, 400
    )
    cheap.set_editor_property("function", cheap_fn)
    lib.connect_material_expressions(color_tex, "", cheap, "In")

    #   RemapValueRange function (must exist in your Content)
    remap_fn = unreal.load_asset("/Game/Functions/RemapValueRange")
    remap = lib.create_material_expression(
        material, unreal.MaterialExpressionMaterialFunctionCall, -400, 400
    )
    remap.set_editor_property("function", remap_fn)
    # connect Contrast→Remap
    lib.connect_material_expressions(cheap,   "Result", remap, "Input S")

    # 3) === ORM CHANNEL GROUP ===
    orm_tex = lib.create_material_expression(
        material, unreal.MaterialExpressionTextureSampleParameter2D, -800,    0
    )
    orm_tex.set_editor_property("parameter_name", "ORM")

    # Roughness mask (G)
    rough_mask = lib.create_material_expression(
        material, unreal.MaterialExpressionComponentMask, -600,  0
    )
    rough_mask.set_editor_property("g", True)
    lib.connect_material_expressions(orm_tex, "", rough_mask, "")

    # Roughness Contrast param
    rough_con = lib.create_material_expression(
        material, unreal.MaterialExpressionScalarParameter, -400,  50
    )
    rough_con.set_editor_property("parameter_name", "RoughnessContrast")
    # Contrast node
    rough_cheap = lib.create_material_expression(
        material, unreal.MaterialExpressionMaterialFunctionCall, -200, 50
    )
    rough_cheap.set_editor_property("function", cheap_fn)
    lib.connect_material_expressions(rough_mask, "", rough_cheap, "In")
    lib.connect_material_expressions(rough_con,  "", rough_cheap, "Contrast")

    # Remap Roughness range
    rough_remap = lib.create_material_expression(
        material, unreal.MaterialExpressionMaterialFunctionCall,    0,   50
    )
    rough_remap.set_editor_property("function", remap_fn)
    lib.connect_material_expressions(rough_cheap, "Result", rough_remap, "Input S")

    # Metallic mask (B)
    metal_mask = lib.create_material_expression(
        material, unreal.MaterialExpressionComponentMask, -600, -150
    )
    metal_mask.set_editor_property("b", True)
    lib.connect_material_expressions(orm_tex, "", metal_mask, "")

    # 4) === NORMAL CHANNEL GROUP ===
    normal_tex = lib.create_material_expression(
        material, unreal.MaterialExpressionTextureSampleParameter2D, -800, -300
    )
    normal_tex.set_editor_property("parameter_name", "Normal")
    normal_tex.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)

    # 5) === MFP CHANNEL GROUP ===
    # UseDiffuseAsMFP switch
    switch = lib.create_material_expression(
        material, unreal.MaterialExpressionStaticSwitchParameter, -800, -500
    )
    switch.set_editor_property("parameter_name", "UseDiffuseAsMFP")
    switch.set_editor_property("default_value", True)

    # MFP Color Multiplier
    mfp_col_mult = lib.create_material_expression(
        material, unreal.MaterialExpressionScalarParameter, -600, -500
    )
    mfp_col_mult.set_editor_property("parameter_name", "MFPColorMultiplier")
    mfp_col_mult.set_editor_property("default_value", 1.0)

    # MFP Scale
    mfp_scale = lib.create_material_expression(
        material, unreal.MaterialExpressionScalarParameter, -400, -500
    )
    mfp_scale.set_editor_property("parameter_name", "MFPScale")
    mfp_scale.set_editor_property("default_value", 1.0)

    # Multiply Color * MFPColorMultiplier
    mfp_mul = lib.create_material_expression(
        material, unreal.MaterialExpressionMultiply, -200, -450
    )
    lib.connect_material_expressions(color_tex,  "", mfp_mul, "A")
    lib.connect_material_expressions(mfp_col_mult, "", mfp_mul, "B")

    # Switch: True = mul result, False = raw color
    lib.connect_material_expressions(mfp_mul,   "", switch, "True")
    lib.connect_material_expressions(color_tex, "", switch, "False")

    # 6) === SUBSTRATE SLAB BSDF & HOOKUP ===
    slab = lib.create_material_expression(
        material, unreal.MaterialExpressionSubstrateSlabBSDF, 200, 0
    )

    # connect remapped Color into Diffuse Albedo
    lib.connect_material_expressions(remap,    "Result", slab, "Diffuse Albedo")
    # connect remapped Roughness into Roughness
    lib.connect_material_expressions(rough_remap, "Result", slab, "Roughness")
    # connect metallic mask
    lib.connect_material_expressions(metal_mask, "", slab, "F0")
    # connect AO (use raw or remapped, whatever you prefer)
    lib.connect_material_expressions(orm_tex,   "", slab, "AmbientOcclusion")
    # connect normal
    lib.connect_material_expressions(normal_tex,"", slab, "Normal")
    # connect MFP switch into SSS MFP
    lib.connect_material_expressions(switch,   "", slab, "SSS MFP")
    # connect MFP scale param
    lib.connect_material_expressions(mfp_scale,"", slab, "SSS MFP Scale")

    # wire into Material Output
    lib.connect_material_property(slab, "", unreal.MaterialProperty.MP_FRONT_MATERIAL)

    # 7) Compile & save
    lib.recompile_material(material)
    unreal.EditorAssetLibrary.save_loaded_asset(material)
    unreal.log(f"✅ Advanced Substrate material '{name}' created at {path}")

# Execute
create_advanced_substrate()
