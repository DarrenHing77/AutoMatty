// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FToolBarBuilder;
class FMenuBuilder;

class FAutoMattyModule : public IModuleInterface
{
public:
	/** IModuleInterface implementation */
	virtual void StartupModule() override;
	virtual void ShutdownModule() override;

private:
	/** Registers the toolbar button */
	void RegisterMenus();

	/** Initialize the plugin's style set (icons, brushes, etc.) */
	void InitializeStyle();

	/** Shutdown the plugin's style set */
	void ShutdownStyle();

	/** Callback when toolbar button is clicked */
	void OnToolbarButtonClicked();

	/** Generate the dropdown menu content */
	TSharedRef<SWidget> GenerateToolbarMenu();

	/** Execute Python command helper */
	void ExecutePythonCommand(const FString& Command);

	/** Adds toolbar extension */
	void AddToolbarExtension(FToolBarBuilder& Builder);

private:
	TSharedPtr<class FUICommandList> PluginCommands;
	TSharedPtr<class FSlateStyleSet> StyleSet;
};