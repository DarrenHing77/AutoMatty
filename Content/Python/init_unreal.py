"""
AutoMatty Menu Registration - FIXED NO DUPLICATES
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
            blueprint = unreal.EditorAssetLibrary.load_asset("/AutoMatty/Blueprints/EUW_AutoMatty")
            
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
    """Register AutoMatty Tools menu entries - NO DUPLICATES"""
    try:
        # Tools menu gets ONLY the main widget and material editor
        # Toolbar gets everything else
        menus = unreal.ToolMenus.get()
        tools_menu = menus.find_menu("LevelEditor.MainMenu.Tools")
        
        if not tools_menu:
            unreal.log_error("❌ Could not find Tools menu")
            return False
        
        # 1. MAIN WIDGET ENTRY (Tools menu version)
        widget_script = AutoMattyMainWidget()
        widget_script.init_entry(
            owner_name="AutoMattyTools",  # Different owner to avoid conflicts
            menu="LevelEditor.MainMenu.Tools", 
            section="LevelEditorModules",
            name="AutoMattyWidgetTools",  # Different name
            label="AutoMatty",
            tool_tip="Open AutoMatty main widget"
        )
        widget_script.register_menu_entry()
        
        # 2. MATERIAL EDITOR ENTRY (Tools menu version)
        editor_script = AutoMattyMaterialEditor()
        editor_script.init_entry(
            owner_name="AutoMattyTools",  # Different owner
            menu="LevelEditor.MainMenu.Tools", 
            section="LevelEditorModules", 
            name="AutoMattyMaterialEditorTools",  # Different name
            label="AutoMatty Material Editor",
            tool_tip="Open AutoMatty Material Instance Editor"
        )
        editor_script.register_menu_entry()
        
        # Refresh menus
        menus.refresh_all_widgets()
        
        unreal.log("✅ AutoMatty Tools menu entries registered!")
        return True
        
    except Exception as e:
        unreal.log_error(f"❌ Tools menu registration failed: {e}")
        return False

def main():
    """Main function called on startup"""
    unreal.log("🚀 AutoMatty startup script running...")
    register_automatty_menus()  # Tools menu items
    # NOTE: Toolbar button is now registered by C++ module, not Python
    # from automatty_config import AutoMattyMenuManager
    # AutoMattyMenuManager.register_main_menu()  # Toolbar dropdown

# Run the registration
if __name__ == '__main__':
    main()