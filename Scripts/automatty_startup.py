"""
AutoMatty Startup - Menu registration and plugin initialization
"""
import unreal

def register_menu_entry():
    """Register AutoMatty in the Tools menu"""
    try:
        menu_owner = unreal.ToolMenus.get().extend_menu("LevelEditor.MainMenu.Tools")
        section = menu_owner.add_section("AutoMatty", label="AutoMatty")
        
        entry = unreal.ToolMenuEntry(
            name="AutoMatty",
            type=unreal.MultiBlockType.MENU_ENTRY,
            insert_position=unreal.ToolMenuInsert("", unreal.ToolMenuInsertType.DEFAULT)
        )
        entry.set_label("AutoMatty")
        entry.set_tool_tip("Open AutoMatty Material Utilities")
        
        # Command to open the AutoMatty UI widget
        # Adjust the path to match your widget location
        entry.set_string_command(
            unreal.ToolMenuStringCommandType.PYTHON,
            custom_type="",
            string="import unreal; unreal.EditorUtilityLibrary.spawn_and_register_tab_and_get_id(unreal.EditorAssetLibrary.load_asset('/AutoMatty/EUW_AutoMatty'))"
        )
        
        section.add_entry("AutoMatty", entry)
        unreal.log("✅ AutoMatty menu entry registered in Tools menu")
        
    except Exception as e:
        unreal.log_error(f"❌ Failed to register AutoMatty menu: {e}")

def register_python_commands():
    """Register Python commands for AutoMatty functions"""
    try:
        # This is optional advanced functionality
        unreal.log("🐍 Python command registration skipped (not essential)")
        
    except Exception as e:
        unreal.log_warning(f"⚠️ Python command registration failed: {e}")

def initialize_automatty():
    """Initialize AutoMatty plugin - called when plugin loads"""
    unreal.log("🚀 Initializing AutoMatty plugin...")
    
    # Check if we can import our modules
    try:
        from automatty_utils import setup_automatty_imports, log_plugin_info
        if setup_automatty_imports():
            log_plugin_info()
            unreal.log("✅ AutoMatty imports configured successfully")
        else:
            unreal.log_error("❌ Failed to setup AutoMatty imports")
            return False
    except ImportError as e:
        unreal.log_error(f"❌ AutoMatty utils not found: {e}")
        return False
    
    # Register menu entries
    register_menu_entry()
    
    # Register Python commands (optional - for advanced users)
    register_python_commands()
    
    unreal.log("🎉 AutoMatty plugin initialized successfully!")
    return True

def shutdown_automatty():
    """Cleanup when plugin is unloaded"""
    try:
        # Remove menu entries
        menu_owner = unreal.ToolMenus.get().find_menu("LevelEditor.MainMenu.Tools")
        if menu_owner:
            menu_owner.remove_section("AutoMatty")
        
        unreal.log("✅ AutoMatty plugin cleaned up")
    except Exception as e:
        unreal.log_warning(f"⚠️ Cleanup warning: {e}")

# Auto-register when plugin loads
if __name__ == "__main__":
    initialize_automatty()