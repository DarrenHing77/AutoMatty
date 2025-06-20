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

# —— CONFIG —— #
BASE_NAME = "M_AutoMattySplit"
FOLDER    = "/Game/Materials/AutoMatty"

# —————————————————— #
# 1) Version bump
name = get_next_asset_name(BASE_NAME, FOLDER)

# 2) Find DefaultNormal dynamically
def find_default_normal():
    for path in unreal.EditorAssetLibrary.list_assets("/Engine", recursive=True, include_folder=False):
        if path.endswith("DefaultNormal"):
            return unreal.EditorAssetLibrary.load_asset(path)
    unreal.log_warning("⚠️ Couldn't find DefaultNormal in /Engine; Normal sampler may error.")
    return None

default_normal = find_default_normal()

# 3) Create the material
tools    = unreal.AssetToolsHelpers.get_asset_tools()
material = tools.create_asset(name, FOLDER, unreal.Material, unreal.MaterialFactoryNew())
lib      = unreal.MaterialEditingLibrary

# 4) Spawn TextureSampleParameter2D nodes
coords = {
    "Color":     (-400,  200),
    "Roughness": (-400,    0),
    "Metallic":  (-400,  -100),
    "Occlusion": (-400,  -200),
    "Normal":    (-400,  -300),
}
samples = {}
for pname,(x,y) in coords.items():
    node = lib.create_material_expression(material, unreal.MaterialExpressionTextureSampleParameter2D, x, y)
    node.set_editor_property("parameter_name", pname)
    if pname == "Normal":
        node.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
        if default_normal:  # Only set if we actually loaded it
            node.set_editor_property("texture", default_normal)
    samples[pname] = node

# 5) Create the Substrate Slab BSDF
slab = lib.create_material_expression(material, unreal.MaterialExpressionSubstrateSlabBSDF, 0, 0)

# 6) Hook channels
lib.connect_material_expressions(samples["Color"],     "", slab, "Diffuse Albedo")
lib.connect_material_expressions(samples["Normal"],    "", slab, "Normal")
lib.connect_material_expressions(samples["Roughness"], "", slab, "Roughness")
lib.connect_material_expressions(samples["Metallic"],  "", slab, "F0")
lib.connect_material_expressions(samples["Occlusion"], "", slab, "AmbientOcclusion")

# 7) Wire Slab → FrontMaterial
lib.connect_material_property(slab, "", unreal.MaterialProperty.MP_FRONT_MATERIAL)

# 8) Compile & Save
lib.recompile_material(material)
unreal.EditorAssetLibrary.save_loaded_asset(material)
unreal.log(f"✅ Split Substrate master '{name}' created in {FOLDER}")