"""
AutoMatty Button Utilities - Clean unified approach with Triplanar support
"""
import unreal, sys, os

def setup_automatty_and_get_checkboxes():
    """One function to rule them all - setup imports and get checkbox states"""
    
    # Bootstrap AutoMatty imports
    engine_scripts_path = os.path.join(unreal.Paths.engine_dir(), "Plugins", "AutoMatty", "Scripts")
    if engine_scripts_path not in sys.path:
        sys.path.insert(0, engine_scripts_path)
    
    # Setup AutoMatty
    try:
        from automatty_utils import setup_automatty_imports
        if not setup_automatty_imports():
            unreal.log_error("❌ Failed to setup AutoMatty imports")
            return None, {}
    except Exception as e:
        unreal.log_error(f"❌ AutoMatty import failed: {e}")
        return None, {}
    
    # Get checkbox values from EUW - FIXED: Added use_triplanar
    checkboxes = {
        'use_nanite': False,
        'use_second_roughness': False,
        'use_adv_env': False,
        'use_triplanar': False  # ADDED THIS
    }
    
    try:
        subsystem = unreal.get_editor_subsystem(unreal.EditorUtilitySubsystem)
        euw_path = "/AutoMatty/EUW_AutoMatty"
        
        euw_blueprint = unreal.EditorAssetLibrary.load_asset(euw_path)
        if euw_blueprint:
            widget = subsystem.find_utility_widget_from_blueprint(euw_blueprint)
            if widget:
                # Get all checkbox states - FIXED: Added triplanar reading
                nanite_checkbox = widget.get_editor_property("UseNanite")
                roughness_checkbox = widget.get_editor_property("UseSecondRoughness")
                adv_env_checkbox = widget.get_editor_property("UseAdvEnv")
                triplanar_checkbox = widget.get_editor_property("UseTriplanar")  # ADDED THIS
                
                checkboxes['use_nanite'] = nanite_checkbox.is_checked() if nanite_checkbox else False
                checkboxes['use_second_roughness'] = roughness_checkbox.is_checked() if roughness_checkbox else False
                checkboxes['use_adv_env'] = adv_env_checkbox.is_checked() if adv_env_checkbox else False
                checkboxes['use_triplanar'] = triplanar_checkbox.is_checked() if triplanar_checkbox else False  # ADDED THIS
                
                # FIXED: Added triplanar to log
                unreal.log(f"✅ Checkboxes: Nanite={checkboxes['use_nanite']}, SecondRough={checkboxes['use_second_roughness']}, AdvEnv={checkboxes['use_adv_env']}, Triplanar={checkboxes['use_triplanar']}")
                
    except Exception as e:
        unreal.log_error(f"⚠️ Checkbox access failed: {e}")
        # Ensure all keys exist even if reading fails
        checkboxes = {
            'use_nanite': False,
            'use_second_roughness': False,
            'use_adv_env': False,
            'use_triplanar': False
        }
    
    # Import and reload builder
    try:
        import importlib
        import automatty_builder_final  # Use the final builder
        importlib.reload(automatty_builder_final)
        from automatty_builder_final import SubstrateMaterialBuilder
        
        return SubstrateMaterialBuilder(), checkboxes
        
    except Exception as e:
        unreal.log_error(f"❌ Builder import failed: {e}")
        return None, {}

def create_orm_material():
    """Clean ORM material button"""
    unreal.log("🔧 Creating ORM Material...")
    
    builder, checkboxes = setup_automatty_and_get_checkboxes()
    if not builder:
        return
    
    try:
        material = builder.create_orm_material(
            use_second_roughness=checkboxes['use_second_roughness'],
            use_nanite=checkboxes['use_nanite'],
            use_triplanar=checkboxes['use_triplanar']  # This will work now
        )
        
        if material:
            features = []
            if checkboxes['use_second_roughness']: features.append("dual-roughness")
            if checkboxes['use_nanite']: features.append("nanite displacement")
            if checkboxes['use_triplanar']: features.append("triplanar mapping")
            feature_text = f" with {', '.join(features)}" if features else ""
            unreal.log(f"🎉 SUCCESS! Created ORM material{feature_text}: {material.get_name()}")
        else:
            unreal.log_error("❌ Failed to create ORM material")
            
    except Exception as e:
        unreal.log_error(f"❌ Error creating ORM material: {e}")

def create_split_material():
    """Clean Split material button"""
    unreal.log("🔧 Creating Split Material...")
    
    builder, checkboxes = setup_automatty_and_get_checkboxes()
    if not builder:
        return
    
    try:
        material = builder.create_split_material(
            use_second_roughness=checkboxes['use_second_roughness'],
            use_nanite=checkboxes['use_nanite'],
            use_triplanar=checkboxes['use_triplanar']
        )
        
        if material:
            features = []
            if checkboxes['use_second_roughness']: features.append("dual-roughness")
            if checkboxes['use_nanite']: features.append("nanite displacement")
            if checkboxes['use_triplanar']: features.append("triplanar mapping")
            feature_text = f" with {', '.join(features)}" if features else ""
            unreal.log(f"🎉 SUCCESS! Created Split material{feature_text}: {material.get_name()}")
        else:
            unreal.log_error("❌ Failed to create Split material")
            
    except Exception as e:
        unreal.log_error(f"❌ Error creating Split material: {e}")

def create_advanced_material():
    """Clean Advanced material button"""
    unreal.log("🔧 Creating Advanced Material...")
    
    builder, checkboxes = setup_automatty_and_get_checkboxes()
    if not builder:
        return
    
    try:
        material = builder.create_advanced_material(
            use_second_roughness=checkboxes['use_second_roughness'],
            use_nanite=checkboxes['use_nanite'],
            use_triplanar=checkboxes['use_triplanar']
        )
        
        if material:
            features = []
            if checkboxes['use_second_roughness']: features.append("dual-roughness")
            if checkboxes['use_nanite']: features.append("nanite displacement")
            if checkboxes['use_triplanar']: features.append("triplanar mapping")
            feature_text = f" with {', '.join(features)}" if features else ""
            unreal.log(f"🎉 SUCCESS! Created Advanced material{feature_text}: {material.get_name()}")
        else:
            unreal.log_error("❌ Failed to create Advanced material")
            
    except Exception as e:
        unreal.log_error(f"❌ Error creating Advanced material: {e}")

def create_environment_material():
    """Clean Environment material button with UseAdvEnv support"""
    unreal.log("🔧 Creating Environment Material...")
    
    builder, checkboxes = setup_automatty_and_get_checkboxes()
    if not builder:
        return
    
    try:
        material = builder.create_environment_material(
            use_adv_env=checkboxes['use_adv_env']
        )
        
        if material:
            env_type = "Advanced (dual-slab noise mixing)" if checkboxes['use_adv_env'] else "Simple (lerp blending)"
            unreal.log(f"🎉 SUCCESS! Created {env_type} Environment material: {material.get_name()}")
            if checkboxes['use_adv_env']:
                unreal.log("💀 Your GPU will hate this advanced version")
        else:
            unreal.log_error("❌ Failed to create Environment material")
            
    except Exception as e:
        unreal.log_error(f"❌ Error creating Environment material: {e}")

def create_material_instance():
    """Clean Material Instance button"""
    unreal.log("🔧 Creating Smart Material Instance...")
    
    # Just need AutoMatty setup, no checkboxes for instancer
    engine_scripts_path = os.path.join(unreal.Paths.engine_dir(), "Plugins", "AutoMatty", "Scripts")
    if engine_scripts_path not in sys.path:
        sys.path.insert(0, engine_scripts_path)
    
    try:
        from automatty_utils import setup_automatty_imports
        if not setup_automatty_imports():
            unreal.log_error("❌ Failed to setup AutoMatty imports")
            return
        
        import importlib
        import automatty_instancer_updated
        importlib.reload(automatty_instancer_updated)
        from automatty_instancer_updated import create_material_instance_smart
        
        instance = create_material_instance_smart()
        
        if instance:
            unreal.log(f"🎉 SUCCESS! Created material instance: {instance.get_name()}")
        else:
            unreal.log("⚠️ No instance created - check selection and textures")
            
    except Exception as e:
        unreal.log_error(f"❌ Error creating material instance: {e}")

def repath_material_instances():
    """Clean Repath button"""
    unreal.log("🔧 Repathing Material Instances...")
    
    # Just need AutoMatty setup, no checkboxes for repather
    engine_scripts_path = os.path.join(unreal.Paths.engine_dir(), "Plugins", "AutoMatty", "Scripts")
    if engine_scripts_path not in sys.path:
        sys.path.insert(0, engine_scripts_path)
    
    try:
        from automatty_utils import setup_automatty_imports
        if not setup_automatty_imports():
            unreal.log_error("❌ Failed to setup AutoMatty imports")
            return
        
        import importlib
        import automatty_repather
        importlib.reload(automatty_repather)
        from automatty_repather import repath_material_instances as repath_func
        
        repath_func()
        unreal.log("🏆 Texture repathing completed")
        
    except Exception as e:
        unreal.log_error(f"❌ Error repathing materials: {e}")

# For backwards compatibility with your existing buttons
def get_checkbox_values():
    """Legacy function - use the new unified approach instead"""
    unreal.log_warning("⚠️ Using legacy checkbox function - consider switching to unified approach")
    _, checkboxes = setup_automatty_and_get_checkboxes()
    return checkboxes.get('use_nanite', False), checkboxes.get('use_second_roughness', False), checkboxes.get('use_triplanar', False)