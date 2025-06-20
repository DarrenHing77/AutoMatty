import unreal, re, os

def auto_instance_with_dialog():
    # 1) Grab selected Material
    assets = unreal.EditorUtilityLibrary.get_selected_assets()
    if len(assets) != 1 or not isinstance(assets[0], unreal.Material):
        unreal.log_error("❌ Select exactly one Material asset.")
        return
    base_mat = assets[0]
    unreal.log(f"🔧 Base material: {base_mat.get_name()}")

    # 2) Pop up import dialog & import into your Textures folder
    atools = unreal.AssetToolsHelpers.get_asset_tools()
    dest   = "/Game/Textures/AutoMatty"
    imported = atools.import_assets_with_dialog(dest)
    if not imported:
        unreal.log("⚠️ No assets imported. Aborting.")
        return

    # 3) Build name→Texture2D map
    textures = {
        obj.get_name().lower(): obj
        for obj in imported
        if isinstance(obj, unreal.Texture2D)
    }

    # 4) Regex‐patterns for every slot
    patterns = {
        "Color":     re.compile(r"(colou?r|albedo|base[-_]?color)", re.IGNORECASE),
        "Normal":    re.compile(r"normal",                          re.IGNORECASE),
        "Occlusion": re.compile(r"(?:^|[_\W])(?:ao|occlusion)(?:$|[_\W])", re.IGNORECASE),
        "Roughness": re.compile(r"roughness",                       re.IGNORECASE),
        "Metallic":  re.compile(r"metal(?:lic|ness)",               re.IGNORECASE),
        "ORM":       re.compile(r"(?:^|[_\W])orm(?:$|[_\W])|occlusion[-_]?roughness[-_]?metalness",
                                    re.IGNORECASE),
    }

    # 5) Find matches (each param only once)
    found = {}
    for name, tex in textures.items():
        for param, pat in patterns.items():
            if param not in found and pat.search(name):
                found[param] = tex
                unreal.log(f"🔗 Matched '{name}' → {param}")

    if not found:
        unreal.log_warning("⚠️ No matching textures found. Aborting.")
        return

    # 6) Decide mode
    split_keys = {"Occlusion","Roughness","Metallic"}
    has_split  = any(k in found for k in split_keys)
    has_orm    = "ORM" in found

    if has_split:
        to_set = ["Color","Normal","Occlusion","Roughness","Metallic"]
    elif has_orm:
        to_set = ["Color","Normal","ORM"]
    else:
        to_set = list(found.keys())

    # 7) Create the Material Instance
    mic_fact = unreal.MaterialInstanceConstantFactoryNew()
    inst_name= f"{base_mat.get_name()}_Inst"
    inst_path= "/Game/Materials/AutoMatty"
    instance = atools.create_asset(inst_name, inst_path,
                                   unreal.MaterialInstanceConstant, mic_fact)
    unreal.MaterialEditingLibrary.set_material_instance_parent(instance, base_mat)
    unreal.log(f"🎉 Created instance: {instance.get_name()}")

    # 8) Hook up each matched texture
    for param in to_set:
        tex = found.get(param)
        if tex:
            unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
                instance, param, tex
            )
            unreal.log(f"✅ Set '{param}' → {tex.get_name()}")

    # 9) Save it
    unreal.EditorAssetLibrary.save_asset(instance.get_path_name())
    unreal.log(f"💾 Saved instance at {instance.get_path_name()}")

# run it!
auto_instance_with_dialog()