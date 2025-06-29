import unreal

def register_menu_entry():
    """Register AutoMatty in the Tools menu"""
    menu_owner = unreal.ToolMenus.get().extend_menu("LevelEditor.MainMenu.Tools")
    section = menu_owner.add_section("AutoMatty", label="AutoMatty")
    
    entry = unreal.ToolMenuEntry(
        name="AutoMatty",
        type=unreal.MultiBlockType.MENU_ENTRY,
        insert_position=unreal.ToolMenuInsert("", unreal.ToolMenuInsertType.DEFAULT)
    )
    entry.set_label("AutoMatty")
    entry.set_tool_tip("Open AutoMatty Material Utilities")
    entry.set_string_command(
        unreal.ToolMenuStringCommandType.PYTHON,
        custom_type="",
        string="import unreal; unreal.EditorUtilityLibrary.spawn_and_register_tab_and_get_id(unreal.EditorAssetLibrary.load_asset('/AutoMatty/UI/WBP_AutoMatty'))"
    )
    
    section.add_entry("AutoMatty", entry)

# Auto-register when plugin loads
if __name__ == "__main__":
    register_menu_entry()