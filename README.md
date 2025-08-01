**AutoMatty v0.1.0 🎨**
A comprehensive material automation toolkit for Unreal Engine 5.6
AutoMatty streamlines subtrate material creation and management workflows with intelligent texture matching, smart naming, and flexible path configuration.

✨ Features

Material Builders

ORM Materials: Packed Occlusion/Roughness/Metallic workflow
Split Materials: Individual texture channels (Color, Normal, Roughness, Metallic, Occlusion)
Advanced Materials: Enhanced workflow with contrast controls, remapping, and subsurface scattering

Smart Material Instances

Intelligent texture matching using regex patterns
Automatic naming based on texture file analysis (e.g., ChrHead_color_1001_sRGB.jpg → M_ChrHead_Inst)
Workflow detection (ORM vs Split vs Basic)
Custom path support with UI configuration

Texture Repather

Batch texture replacement in material instances
Smart matching with version-agnostic detection
File dialog integration for easy folder selection
Multiple matching strategies (exact, version, type-based)

UI & Configuration

Editor Utility Widget with clean interface
Persistent path settings via JSON configuration
Real-time path validation and folder creation
Modular architecture for easy extension

🔧 Requirements

Unreal Engine 5.6+
Substrate Material System enabled
Python Plugin enabled
Editor Utility Widgets plugin enabled

📦 Installation

Copy the AutoMatty folder to your project's Plugins directory
Enable the plugin in Project Settings
Restart the editor
Access via Windows → AutoMatty or run the Editor Utility Widget

🚀 Quick Start

Set your material path: Enter desired path in the UI (e.g., Materials/MyProject)
Create base materials: Use ORM, Split, or Advanced builders
Generate instances: Select a material + import textures for automatic instance creation
Repath textures: Select material instances + use repather to swap texture sets

🏗️ Architecture

Modular Python scripts in /Scripts folder
Centralized configuration via automatty_config.py
Extensible builder pattern for new material types
Smart utility functions for texture analysis and naming

🐛 Known Issues

Substrate must be enabled in project settings
Some material parameter APIs changed in UE 5.6 (handled automatically)

🤝 Contributing

Built for internal use but designed with extensibility in mind. The modular architecture makes it easy to add new material types and workflows.

Note: This plugin uses UE 5.6's Python API and may require updates for future engine versions.

Feel free to customize the version number, add screenshots, or adjust the tone to match your style!
