// Copyright Epic Games, Inc. All Rights Reserved.

#include "AutoMatty.h"
#include "Styling/SlateStyleRegistry.h"
#include "Styling/SlateStyle.h"
#include "Styling/SlateStyleMacros.h"
#include "Interfaces/IPluginManager.h"
#include "ToolMenus.h"
#include "LevelEditor.h"
#include "Modules/ModuleManager.h"
#include "Framework/MultiBox/MultiBoxBuilder.h"
#include "Widgets/SWidget.h"

#define LOCTEXT_NAMESPACE "FAutoMattyModule"

void FAutoMattyModule::StartupModule()
{
	// This code will execute after your module is loaded into memory; the exact timing is specified in the .uplugin file per-module

	// Initialize custom style (icons)
	InitializeStyle();

	// Register menus after the engine has fully loaded
	UToolMenus::RegisterStartupCallback(FSimpleMulticastDelegate::FDelegate::CreateRaw(this, &FAutoMattyModule::RegisterMenus));
}

void FAutoMattyModule::ShutdownModule()
{
	// Unregister all menus
	UToolMenus::UnRegisterStartupCallback(this);
	UToolMenus::UnregisterOwner(this);

	// Cleanup style
	ShutdownStyle();
}

void FAutoMattyModule::InitializeStyle()
{
	// Only initialize once
	if (StyleSet.IsValid())
	{
		return;
	}

	// Create the style set
	StyleSet = MakeShareable(new FSlateStyleSet("AutoMattyStyle"));

	// Get the plugin's content directory for resources
	TSharedPtr<IPlugin> Plugin = IPluginManager::Get().FindPlugin(TEXT("AutoMatty"));
	if (Plugin.IsValid())
	{
		FString ResourcesDir = Plugin->GetBaseDir() / TEXT("Resources");
		StyleSet->SetContentRoot(ResourcesDir);

		// Build full path to icon
		FString IconPath = ResourcesDir / TEXT("Icon_AutoMatty_40x.png");

		// Check if icon exists and log it
		if (FPaths::FileExists(IconPath))
		{
			UE_LOG(LogTemp, Log, TEXT("AutoMatty: Found icon at %s"), *IconPath);

			// Register icon - 40x40 is the standard toolbar icon size
			StyleSet->Set("AutoMatty.ToolbarIcon", new FSlateImageBrush(
				IconPath,
				FVector2D(40.0f, 40.0f)
			));
		}
		else
		{
			UE_LOG(LogTemp, Warning, TEXT("AutoMatty: Icon not found at %s - using default"), *IconPath);

			// Fallback to engine icon
			StyleSet->Set("AutoMatty.ToolbarIcon", new FSlateImageBrush(
				FPaths::EngineContentDir() / TEXT("Editor/Slate/Icons/icon_tab_Tools_40x.png"),
				FVector2D(40.0f, 40.0f)
			));
		}
	}

	// Register the style set
	FSlateStyleRegistry::RegisterSlateStyle(*StyleSet);
}

void FAutoMattyModule::ShutdownStyle()
{
	if (StyleSet.IsValid())
	{
		FSlateStyleRegistry::UnRegisterSlateStyle(*StyleSet);
		StyleSet.Reset();
	}
}

void FAutoMattyModule::RegisterMenus()
{
	// Owner will be used for cleanup in call to UToolMenus::UnregisterOwner
	FToolMenuOwnerScoped OwnerScoped(this);

	// Get the level editor toolbar menu
	UToolMenu* ToolbarMenu = UToolMenus::Get()->ExtendMenu("LevelEditor.LevelEditorToolBar.PlayToolBar");

	if (ToolbarMenu)
	{
		FToolMenuSection& Section = ToolbarMenu->FindOrAddSection("PluginTools");

		// Add a toolbar button with dropdown menu - using InitComboButton with HasDownArrow style
		FToolMenuEntry& Entry = Section.AddEntry(FToolMenuEntry::InitComboButton(
			"AutoMatty",
			FUIAction(),  // No direct click action - only dropdown
			FOnGetContent::CreateRaw(this, &FAutoMattyModule::GenerateToolbarMenu),
			LOCTEXT("AutoMattyLabel", "AutoMatty"),
			LOCTEXT("AutoMattyTooltip", "AutoMatty Material Tools"),
			FSlateIcon("AutoMattyStyle", "AutoMatty.ToolbarIcon"),
			false  // bInSimpleComboBox = false (shows dropdown arrow)
		));

		Entry.SetCommandList(PluginCommands);
	}
}

void FAutoMattyModule::ExecutePythonCommand(const FString& Command)
{
	// Check if Python module is loaded
	if (FModuleManager::Get().IsModuleLoaded("PythonScriptPlugin"))
	{
		FModuleManager::LoadModuleChecked<IModuleInterface>("PythonScriptPlugin");

		// Get the Python library class
		UClass* PythonLibClass = FindObject<UClass>(nullptr, TEXT("/Script/PythonScriptPlugin.PythonScriptLibrary"));
		if (PythonLibClass)
		{
			UFunction* ExecuteFunc = PythonLibClass->FindFunctionByName(TEXT("ExecutePythonCommand"));
			if (ExecuteFunc)
			{
				struct FPythonCommandParams
				{
					FString PythonCommand;
				};

				FPythonCommandParams Params;
				Params.PythonCommand = Command;

				PythonLibClass->GetDefaultObject()->ProcessEvent(ExecuteFunc, &Params);
				return;
			}
		}
	}

	UE_LOG(LogTemp, Warning, TEXT("AutoMatty: Python plugin not available"));
}

void FAutoMattyModule::OnToolbarButtonClicked()
{
	// Open the AutoMatty main widget via Python - call the simple wrapper function
	const FString PythonCommand = TEXT("import automatty_config; automatty_config.open_main_widget()");

	ExecutePythonCommand(PythonCommand);
	UE_LOG(LogTemp, Log, TEXT("AutoMatty toolbar button clicked - opening widget"));
}

TSharedRef<SWidget> FAutoMattyModule::GenerateToolbarMenu()
{
	// Create menu builder for the dropdown
	FMenuBuilder MenuBuilder(true, nullptr);

	// Main Tools Section
	MenuBuilder.BeginSection("MainTools", LOCTEXT("MainToolsSection", "Main Tools"));
	{
		MenuBuilder.AddMenuEntry(
			LOCTEXT("OpenWidget", "Main Widget"),
			LOCTEXT("OpenWidgetTooltip", "Open AutoMatty main interface"),
			FSlateIcon(),
			FUIAction(FExecuteAction::CreateLambda([this]()
			{
				OnToolbarButtonClicked();
			}))
		);

		MenuBuilder.AddMenuEntry(
			LOCTEXT("MaterialEditor", "Material Instance Editor"),
			LOCTEXT("MaterialEditorTooltip", "Advanced material instance editor (Qt-based)"),
			FSlateIcon(),
			FUIAction(FExecuteAction::CreateLambda([this]()
			{
				// Use the show_material_editor function which handles unreal_qt installation
				const FString Command = TEXT(
					"import automatty_config; "
					"automatty_config.show_material_editor()"
				);
				ExecutePythonCommand(Command);
				UE_LOG(LogTemp, Log, TEXT("AutoMatty: Launched Material Instance Editor"));
			}))
		);
	}
	MenuBuilder.EndSection();

	// Quick Create Section
	MenuBuilder.BeginSection("QuickCreate", LOCTEXT("QuickCreateSection", "Quick Create"));
	{
		MenuBuilder.AddMenuEntry(
			LOCTEXT("CreateORM", "Create ORM Material"),
			LOCTEXT("CreateORMTooltip", "Quick create ORM material with substrate"),
			FSlateIcon(),
			FUIAction(FExecuteAction::CreateLambda([this]()
			{
				ExecutePythonCommand(TEXT("import automatty_config; automatty_config.create_orm_material()"));
			}))
		);

		MenuBuilder.AddMenuEntry(
			LOCTEXT("CreateSplit", "Create Split Material"),
			LOCTEXT("CreateSplitTooltip", "Quick create Split material"),
			FSlateIcon(),
			FUIAction(FExecuteAction::CreateLambda([this]()
			{
				ExecutePythonCommand(TEXT("import automatty_config; automatty_config.create_split_material()"));
			}))
		);

		MenuBuilder.AddMenuEntry(
			LOCTEXT("CreateEnvironment", "Create Environment Material"),
			LOCTEXT("CreateEnvironmentTooltip", "Advanced environment material with A/B blending"),
			FSlateIcon(),
			FUIAction(FExecuteAction::CreateLambda([this]()
			{
				ExecutePythonCommand(TEXT("import automatty_config; automatty_config.create_environment_material()"));
			}))
		);

		MenuBuilder.AddMenuEntry(
			LOCTEXT("CreateInstance", "Create Material Instance"),
			LOCTEXT("CreateInstanceTooltip", "Smart material instance with auto texture matching"),
			FSlateIcon(),
			FUIAction(FExecuteAction::CreateLambda([this]()
			{
				ExecutePythonCommand(TEXT("import automatty_config; automatty_config.create_material_instance()"));
			}))
		);
	}
	MenuBuilder.EndSection();

	// Utilities Section
	MenuBuilder.BeginSection("Utilities", LOCTEXT("UtilitiesSection", "Utilities"));
	{
		MenuBuilder.AddMenuEntry(
			LOCTEXT("RepathTextures", "Repath Textures"),
			LOCTEXT("RepathTexturesTooltip", "Batch repath material instance textures"),
			FSlateIcon(),
			FUIAction(FExecuteAction::CreateLambda([this]()
			{
				ExecutePythonCommand(TEXT("import automatty_config; automatty_config.repath_material_instances()"));
			}))
		);
	}
	MenuBuilder.EndSection();

	return MenuBuilder.MakeWidget();
}

void FAutoMattyModule::AddToolbarExtension(FToolBarBuilder& Builder)
{
	Builder.AddToolBarButton(
		FUIAction(FExecuteAction::CreateRaw(this, &FAutoMattyModule::OnToolbarButtonClicked)),
		NAME_None,
		LOCTEXT("AutoMattyLabel", "AutoMatty"),
		LOCTEXT("AutoMattyTooltip", "Open AutoMatty Material Tools"),
		FSlateIcon(FAppStyle::GetAppStyleSetName(), "LevelEditor.Tabs.Viewports")
	);
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FAutoMattyModule, AutoMatty)