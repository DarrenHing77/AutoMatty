"""
AutoMatty Menu Registration - PROPER IMPLEMENTATION
This file should be placed at: AutoMatty/Content/Python/init_unreal.py
Runs ONCE on editor startup, avoiding class registration conflicts
"""
import unreal

@unreal.uclass()
class AutoMattyMaterialEditor(unreal.ToolMenuEntryScript):
    """Menu script for AutoMatty Material Editor"""
    
    @unreal.ufunction(override=True)
    def execute(self, context):
        """Execute when menu item is clicked"""
        try:
            # Simple import - no path discovery needed!
            import automatty_material_instance_editor
            import importlib
            importlib.reload(automatty_material_instance_editor)
            automatty_material_instance_editor.show_editor_for_selection()
            unreal.log("🎯 AutoMatty Material Editor opened!")
        except Exception as e:
            unreal.log_error(f"❌ Failed to open AutoMatty editor: {e}")

@unreal.uclass()
class AutoMattyMainWidget(unreal.ToolMenuEntryScript):
    """Menu script for main AutoMatty widget"""
    
    @unreal.ufunction(override=True)
    def execute(self, context):
        """Execute when menu item is clicked"""
        try:
            # Open the main AutoMatty widget
            subsystem = unreal.get_editor_subsystem(unreal.EditorUtilitySubsystem)
            blueprint = unreal.EditorAssetLibrary.load_asset("/AutoMatty/EUW_AutoMatty")
            
            if blueprint:
                widget = subsystem.spawn_and_register_tab(blueprint)
                if widget:
                    unreal.log("🎯 AutoMatty main widget opened!")
                else:
                    unreal.log_error("❌ Failed to spawn AutoMatty widget")
            else:
                unreal.log_error("❌ Could not load EUW_AutoMatty blueprint")
                
        except Exception as e:
            unreal.log_error(f"❌ Failed to open AutoMatty widget: {e}")

def register_automatty_menus():
    """Register AutoMatty menu entries"""
    try:
        # Get the Tools menu
        menus = unreal.ToolMenus.get()
        tools_menu = menus.find_menu("LevelEditor.MainMenu.Tools")
        
        if not tools_menu:
            unreal.log_error("❌ Could not find Tools menu")
            return False
        
        # 1. MAIN WIDGET ENTRY
        widget_script = AutoMattyMainWidget()
        widget_script.init_entry(
            owner_name="AutoMatty",
            menu="LevelEditor.MainMenu.Tools", 
            section="LevelEditorModules",
            name="AutoMattyWidget",
            label="AutoMatty",
            tool_tip="Open AutoMatty main widget"
        )
        widget_script.register_menu_entry()
        
        # 2. MATERIAL EDITOR ENTRY  
        editor_script = AutoMattyMaterialEditor()
        editor_script.init_entry(
            owner_name="AutoMatty",
            menu="LevelEditor.MainMenu.Tools", 
            section="LevelEditorModules", 
            name="AutoMattyMaterialEditor",
            label="AutoMatty Material Editor",
            tool_tip="Open AutoMatty Material Instance Editor"
        )
        editor_script.register_menu_entry()
        
        # Refresh menus
        menus.refresh_all_widgets()
        
        unreal.log("✅ AutoMatty menu entries registered!")
        unreal.log("📋 Available in Tools menu:")
        unreal.log("   • AutoMatty (main widget)")
        unreal.log("   • AutoMatty Material Editor")
        unreal.log("💡 Set hotkeys: Edit → Editor Preferences → Keyboard Shortcuts → Search 'AutoMatty'")
        
        return True
        
    except Exception as e:
        unreal.log_error(f"❌ Menu registration failed: {e}")
        return False

def main():
    """Main function called on startup"""
    unreal.log("🚀 AutoMatty startup script running...")
    register_automatty_menus()

# Run the registration
if __name__ == '__main__':
    main()