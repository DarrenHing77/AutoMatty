// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;

public class AutoMatty : ModuleRules
{
	public AutoMatty(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = ModuleRules.PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(
			new string[]
			{
				"Core",
			}
		);

		PrivateDependencyModuleNames.AddRange(
			new string[]
			{
				"CoreUObject",
				"Engine",
				"Slate",
				"SlateCore",
				"UnrealEd",
				"LevelEditor",
				"ToolMenus",
				"Projects",
			}
		);

		// Add Python support if available
		if (Target.bCompilePython)
		{
			PrivateDependencyModuleNames.Add("PythonScriptPlugin");
		}
	}
}