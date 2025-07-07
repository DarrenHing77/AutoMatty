# ========================================
# ORM MATERIAL BUTTON - Complete Working Version
# ========================================

import unreal, sys, os
unreal.log("🔧 ORM Material Button (with widget access)")

def get_checkbox_values():
    try:
        subsystem = unreal.get_editor_subsystem(unreal.EditorUtilitySubsystem)
        euw_path = "/AutoMatty/EUW_AutoMatty"
        
        euw_blueprint = unreal.EditorAssetLibrary.load_asset(euw_path)
        if euw_blueprint:
            widget = subsystem.find_utility_widget_from_blueprint(euw_blueprint)
            if widget:
                # Get the checkbox widgets and their checked state
                nanite_checkbox = widget.get_editor_property("UseNanite")
                roughness_checkbox = widget.get_editor_property("UseSecondRoughness")
                
                use_nanite = nanite_checkbox.is_checked() if nanite_checkbox else False
                use_second_roughness = roughness_checkbox.is_checked() if roughness_checkbox else False
                
                unreal.log(f"✅ Checkbox values: UseNanite={use_nanite}, UseSecondRoughness={use_second_roughness}")
                return use_nanite, use_second_roughness
                
    except Exception as e:
        unreal.log_warning(f"⚠️ Checkbox access failed: {e}")
    
    return False, False

# GET CHECKBOX VALUES
use_nanite, use_second_roughness = get_checkbox_values()

# Bootstrap AutoMatty imports
engine_scripts_path = os.path.join(unreal.Paths.engine_dir(), "Plugins", "AutoMatty", "Scripts")
if engine_scripts_path not in sys.path:
    sys.path.insert(0, engine_scripts_path)

try:
    from automatty_utils import setup_automatty_imports
    
    if setup_automatty_imports():
        unreal.log("✅ AutoMatty imports setup successful")
        
        import importlib
        import automatty_builder
        importlib.reload(automatty_builder)
        from automatty_builder import SubstrateMaterialBuilder
        
        # CREATE MATERIAL WITH FLAGS
        builder = SubstrateMaterialBuilder()
        material = builder.create_orm_material(
            use_second_roughness=use_second_roughness,
            use_nanite=use_nanite
        )
        
        if material:
            features = []
            if use_second_roughness: features.append("dual-roughness")
            if use_nanite: features.append("nanite displacement")
            feature_text = f" with {', '.join(features)}" if features else ""
            unreal.log(f"🎉 SUCCESS! Created ORM material{feature_text}: {material.get_name()}")
        else:
            unreal.log_error("❌ Failed to create ORM material")
    else:
        unreal.log_error("❌ Failed to setup AutoMatty imports")
        
except Exception as e:
    unreal.log_error(f"❌ Error in ORM button: {e}")
    import traceback
    unreal.log_error(traceback.format_exc())

# ========================================
# SPLIT MATERIAL BUTTON - Complete Working Version
# ========================================

import unreal, sys, os
unreal.log("🔧 Split Material Button (with widget access)")

def get_checkbox_values():
    try:
        subsystem = unreal.get_editor_subsystem(unreal.EditorUtilitySubsystem)
        euw_path = "/AutoMatty/EUW_AutoMatty"
        
        euw_blueprint = unreal.EditorAssetLibrary.load_asset(euw_path)
        if euw_blueprint:
            widget = subsystem.find_utility_widget_from_blueprint(euw_blueprint)
            if widget:
                # Get the checkbox widgets and their checked state
                nanite_checkbox = widget.get_editor_property("UseNanite")
                roughness_checkbox = widget.get_editor_property("UseSecondRoughness")
                
                use_nanite = nanite_checkbox.is_checked() if nanite_checkbox else False
                use_second_roughness = roughness_checkbox.is_checked() if roughness_checkbox else False
                
                unreal.log(f"✅ Checkbox values: UseNanite={use_nanite}, UseSecondRoughness={use_second_roughness}")
                return use_nanite, use_second_roughness
                
    except Exception as e:
        unreal.log_warning(f"⚠️ Checkbox access failed: {e}")
    
    return False, False

# GET CHECKBOX VALUES
use_nanite, use_second_roughness = get_checkbox_values()

# Bootstrap AutoMatty imports
engine_scripts_path = os.path.join(unreal.Paths.engine_dir(), "Plugins", "AutoMatty", "Scripts")
if engine_scripts_path not in sys.path:
    sys.path.insert(0, engine_scripts_path)

try:
    from automatty_utils import setup_automatty_imports
    
    if setup_automatty_imports():
        unreal.log("✅ AutoMatty imports setup successful")
        
        import importlib
        import automatty_builder
        importlib.reload(automatty_builder)
        from automatty_builder import SubstrateMaterialBuilder
        
        # CREATE MATERIAL WITH FLAGS
        builder = SubstrateMaterialBuilder()
        material = builder.create_split_material(
            use_second_roughness=use_second_roughness,
            use_nanite=use_nanite
        )
        
        if material:
            features = []
            if use_second_roughness: features.append("dual-roughness")
            if use_nanite: features.append("nanite displacement")
            feature_text = f" with {', '.join(features)}" if features else ""
            unreal.log(f"🎉 SUCCESS! Created Split material{feature_text}: {material.get_name()}")
        else:
            unreal.log_error("❌ Failed to create Split material")
    else:
        unreal.log_error("❌ Failed to setup AutoMatty imports")
        
except Exception as e:
    unreal.log_error(f"❌ Error in Split button: {e}")
    import traceback
    unreal.log_error(traceback.format_exc())

# ========================================
# ADVANCED MATERIAL BUTTON - Complete Working Version
# ========================================

import unreal, sys, os
unreal.log("🔧 Advanced Material Button (with widget access)")

def get_checkbox_values():
    try:
        subsystem = unreal.get_editor_subsystem(unreal.EditorUtilitySubsystem)
        euw_path = "/AutoMatty/EUW_AutoMatty"
        
        euw_blueprint = unreal.EditorAssetLibrary.load_asset(euw_path)
        if euw_blueprint:
            widget = subsystem.find_utility_widget_from_blueprint(euw_blueprint)
            if widget:
                # Get the checkbox widgets and their checked state
                nanite_checkbox = widget.get_editor_property("UseNanite")
                roughness_checkbox = widget.get_editor_property("UseSecondRoughness")
                
                use_nanite = nanite_checkbox.is_checked() if nanite_checkbox else False
                use_second_roughness = roughness_checkbox.is_checked() if roughness_checkbox else False
                
                unreal.log(f"✅ Checkbox values: UseNanite={use_nanite}, UseSecondRoughness={use_second_roughness}")
                return use_nanite, use_second_roughness
                
    except Exception as e:
        unreal.log_warning(f"⚠️ Checkbox access failed: {e}")
    
    return False, False

# GET CHECKBOX VALUES
use_nanite, use_second_roughness = get_checkbox_values()

# Bootstrap AutoMatty imports
engine_scripts_path = os.path.join(unreal.Paths.engine_dir(), "Plugins", "AutoMatty", "Scripts")
if engine_scripts_path not in sys.path:
    sys.path.insert(0, engine_scripts_path)

try:
    from automatty_utils import setup_automatty_imports
    
    if setup_automatty_imports():
        unreal.log("✅ AutoMatty imports setup successful")
        
        import importlib
        import automatty_builder
        importlib.reload(automatty_builder)
        from automatty_builder import SubstrateMaterialBuilder
        
        # CREATE MATERIAL WITH FLAGS
        builder = SubstrateMaterialBuilder()
        material = builder.create_advanced_material(
            use_second_roughness=use_second_roughness,
            use_nanite=use_nanite
        )
        
        if material:
            features = []
            if use_second_roughness: features.append("dual-roughness")
            if use_nanite: features.append("nanite displacement")
            feature_text = f" with {', '.join(features)}" if features else ""
            unreal.log(f"🎉 SUCCESS! Created Advanced material{feature_text}: {material.get_name()}")
        else:
            unreal.log_error("❌ Failed to create Advanced material")
    else:
        unreal.log_error("❌ Failed to setup AutoMatty imports")
        
except Exception as e:
    unreal.log_error(f"❌ Error in Advanced button: {e}")
    import traceback
    unreal.log_error(traceback.format_exc())

# ========================================
# ENVIRONMENT MATERIAL BUTTON - No Changes (Specialized Workflow)
# ========================================

import unreal, sys, os
unreal.log("🔧 Environment Material Button (using automatty_utils)")

# Bootstrap AutoMatty imports
engine_scripts_path = os.path.join(unreal.Paths.engine_dir(), "Plugins", "AutoMatty", "Scripts")
if engine_scripts_path not in sys.path:
    sys.path.insert(0, engine_scripts_path)

try:
    from automatty_utils import setup_automatty_imports
    
    if setup_automatty_imports():
        unreal.log("✅ AutoMatty imports setup successful")
        
        # Force reload to make sure we get the latest code
        import importlib
        import automatty_builder
        importlib.reload(automatty_builder)
        
        # Now import the builder
        from automatty_builder import SubstrateMaterialBuilder
        
        builder = SubstrateMaterialBuilder()
        material = builder.create_environment_material()
        
        if material:
            unreal.log(f"🎉 SUCCESS! Created Environment material: {material.get_name()}")
            unreal.log("💀 Dual-slab mixing with world-space noise - your GPU will cry")
        else:
            unreal.log_error("❌ Failed to create Environment material")
    else:
        unreal.log_error("❌ Failed to setup AutoMatty imports")
        
except Exception as e:
    unreal.log_error(f"❌ Error in Environment Material button: {e}")
    import traceback
    unreal.log_error(traceback.format_exc())