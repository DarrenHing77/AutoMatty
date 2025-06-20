import unreal, re

# —— VERSIONING HELPER —— #
def get_next_asset_name(base_name, folder, prefix="v", pad=3):
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    assets   = registry.get_assets_by_path(folder, recursive=False)
    pat      = re.compile(rf"^{re.escape(base_name)}_{prefix}(\d{{{pad}}})$")
    max_idx  = 0
    for ad in assets:
        m = pat.match(str(ad.asset_name))
        if m and int(m.group(1)) > max_idx:
            max_idx = int(m.group(1))
    return f"{base_name}_{prefix}{max_idx+1:0{pad}d}"

# —— FIND ENGINE DEFAULT NORMAL —— #
def find_default_normal():
    for path in unreal.EditorAssetLibrary.list_assets("/Engine", recursive=True, include_folder=False):
        if path.lower().endswith("defaultnormal"):
            return unreal.EditorAssetLibrary.load_asset(path)
    unreal.log_warning("⚠️ Couldn't find DefaultNormal in /Engine; Normal sampler may error.")
    return None

# —— CONFIG —— #
BASE_NAME = "M_AutoMattyORM"
FOLDER    = "/Game/Materials/AutoMatty"

# 1) version bump
name           = get_next_asset_name(BASE_NAME, FOLDER)
default_normal = find_default_normal()

# 2) create the Material
tools    = unreal.AssetToolsHelpers.get_asset_tools()
material = tools.create_asset(name, FOLDER, unreal.Material, unreal.MaterialFactoryNew())
lib      = unreal.MaterialEditingLibrary

# 3) spawn TextureSampleParameter2D nodes
samples = {}
for pname, (x, y) in {
    "Color":  (-400,  200),
    "ORM":    (-400,    0),
    "Normal": (-400, -200),
}.items():
    node = lib.create_material_expression(
        material,
        unreal.MaterialExpressionTextureSampleParameter2D,
        x, y
    )
    node.set_editor_property("parameter_name", pname)
    if pname == "Normal":
        node.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
        if default_normal:
            node.set_editor_property("texture", default_normal)
    samples[pname] = node

# 4) create the Substrate Slab BSDF
slab = lib.create_material_expression(
    material,
    unreal.MaterialExpressionSubstrateSlabBSDF,
    0, 0
)

# 5) hook Color → Diffuse Albedo
lib.connect_material_expressions(samples["Color"], "", slab, "Diffuse Albedo")

# 6) split ORM → Roughness & F0
rough_mask = lib.create_material_expression(material, unreal.MaterialExpressionComponentMask, -200, 50)
rough_mask.set_editor_property("g", True)
lib.connect_material_expressions(samples["ORM"], "", rough_mask, "")
lib.connect_material_expressions(rough_mask, "", slab, "Roughness")

metal_mask = lib.create_material_expression(material, unreal.MaterialExpressionComponentMask, -200, -150)
metal_mask.set_editor_property("b", True)
lib.connect_material_expressions(samples["ORM"], "", metal_mask, "")
lib.connect_material_expressions(metal_mask, "", slab, "F0")

# 7) hook Normal → Normal
lib.connect_material_expressions(samples["Normal"], "", slab, "Normal")

# 8) wire slab → Material Output’s FrontMaterial
lib.connect_material_property(slab, "", unreal.MaterialProperty.MP_FRONT_MATERIAL)

# 9) compile & save
lib.recompile_material(material)
unreal.EditorAssetLibrary.save_loaded_asset(material)

unreal.log(f"✅ ORM Substrate master '{name}' created in {FOLDER}")
