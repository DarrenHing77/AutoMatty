# AutoMatty v1.0 🎨

**Material automation for Unreal Engine 5.6**

AutoMatty streamlines Substrate material creation and management with intelligent texture matching, smart naming, and automated workflows. Built for 3D artists who quick materials on the fly without libraries and tedious asset migration. Not aimed at game use although there are basic to overkill options

https://drive.google.com/file/d/1STtd5BEGBTqlvhe9qh0VeEomb5CUbEKh/view?usp=sharing

**--THIS IS IN BETA - EXPECT ISSUES--** 

(let me know what they are though and I'll try my best to address them in a timely manner)

---

## 🚀 Quick Start

### Requirements
- **Unreal Engine 5.6+**
- **Substrate enabled** (Project Settings → Rendering → Substrate)
- **Python Plugin enabled** (Edit → Plugins → Python)

### Material Editor Setup (Optional but Recommended)
The **Material Editor** is probably 1 of my favorite features as it makes working with instance parameters a little more convenient

**Installation Steps:**
1. **Press Windows Key + R**
2. **Type:** `cmd` 
3. **Press Enter** (opens black command window)
4. **Copy and paste this command** (replace UE_5.6 with your version):
   ```
   "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Python3\Win64\python.exe" -m pip install unreal-qt
   ```
5. **Press Enter** and wait for "Successfully installed"
6. **Restart Unreal Editor**

**Alternative (if above is too long):**
Try these simpler commands first - they might work:
```bash
pip install unreal-qt
python -m pip install unreal-qt
py -m pip install unreal-qt
```

---

## 📦 Installation

1. Copy **AutoMatty** folder to `YourProject/Plugins/`
2. Enable plugin 
3.**Restart Unreal Editor**
4. **AutoMatty** should be on the tools menu at the top and also in a dropdown on the toolbar(next to platforms)

---

## ✨ Core Features

### 🔧 Material Builders

**What they do:** Create complete Substrate materials with proper node networks, parameters, and optimizations.

- **ORM Materials** - Packed Occlusion/Roughness/Metallic workflow
- **Split Materials** - Individual texture channels (Color, Normal, Roughness, Metallic)
- **Environment Materials** - Basically an blend material for mixing 2 looks

**Features available:**
- ✅ **Nanite Displacement** - Real height-based geometry displacement
- ✅ **Triplanar Mapping** - World-space projection (no UV stretching)
- ✅ **Texture Variation** - Automatic texture randomization for natural looks
- ✅ **Advanced Environment** - Separate A/B material layers with world-space blending
- ✅ **Second Roughness** - Dual-roughness coating effects

### 🎯 Smart Material Instancer

**What it does:** Creates material instances and automatically assigns textures based on naming.

**Smart texture matching:**
- `Wood_Color_1001.jpg` → **Color** parameter
- `Wood_Normal_1001.jpg` → **Normal** parameter  
- `Wood_ORM_1001.jpg` → **ORM** parameter
- `Wood_Height_1001.jpg` → **Height** parameter (if Nanite enabled)

Triggers import dialog (select textures to import)

### 🔄 Texture Repather

**What it does:** Batch replaces textures in existing material instances.

**Use cases:**
- Swap texture sets (e.g., 4K → 8K versions)
- Update materials with new texture variations
- Replace placeholder textures with final assets


### 🎛️ Material Editor

**What it does:** A parameter editor similar to the built-in UE version but selection based. (requires unreal-qt)

**Features:**
- **Dropdown Slots Menu** - lists all materials assigned to the current selection allowing you to easily switch and adjust multi-material assets 
- **Drag-value boxes** - Click and drag to adjust values
- **Visual sliders** with progress bar fills
- **Parameter grouping** - Organized by Color, Roughness, UV Controls, etc.
- **Override toggles** - Enable/disable parameter overrides


**Controls:**
- **Drag** - Change values
- **Shift + Drag** - Fine control (5x slower)
- **Ctrl + Drag** - Coarse control (5x faster)
- **Double-click** - Manual input
- **Mouse wheel** - Adjust values
- **Reset button** - Return to original value

---

## 🎮 How to Use

### Creating Materials

(skip step 1 and 2 if you're not using substrate and the builders included and just want to use your own material)

1.**Choose features** - Check boxes for Nanite, Triplanar, etc.
2. **Set Paths** - Where tos store materials, textures and material name prefix
3.**Create master material** → Choose material type(ORM or split)
4. **Select master and click create instance** - triggers import dialog where you can select textures
5. **Select textures** - new instance is created in same location as master material


### Making Instances

1. **Select a Material** in Content Browser
2. **Click AutoMatty** → **Create Material Instance**
3. **Select/import textures** - AutoMatty matches them automatically
4. **Instance created** with all textures properly assigned

### Editing Parameters

1. **Select mesh** in viewport with materials
2. **Click AutoMatty** → **Material Editor**
3. **Adjust parameters** with visual sliders
4. **Changes apply instantly** to your mesh

### Batch Texture Updates

1. **Select material instances** in Content Browser
2. **Click AutoMatty** → **Repath Textures**
3. **Choose new texture folder** in import dialog
4. **All instances updated** with new textures

---

## ⚙️ Configuration

**Material Path:** Where new materials are created (`/Game/Materials/AutoMatty`)
**Texture Path:** Where textures are imported (`/Game/Textures/AutoMatty`)
**Material Prefix:** Naming prefix for materials (`M_AutoMatty`)

*Settings are saved per-project and remembered between sessions.*

---

## 🏗️ Technical Details

### Substrate Materials
- Uses UE 5.6's new Substrate material system
- Proper BSDF node setup for physically accurate rendering
- Optimized for Lumen and Nanite

### Texture Naming Conventions
AutoMatty recognizes these patterns:
- **Color:** `*color*`, `*albedo*`, `*diffuse*`, `*basecolor*`
- **Normal:** `*normal*`, `*norm*`, `*nrm*`
- **Roughness:** `*roughness*`, `*rough*`
- **Metallic:** `*metallic*`, `*metal*`
- **ORM:** `*orm*`, `*occlusion*roughness*metallic*`
- **Height:** `*height*`, `*displacement*`, `*disp*`
- **Emission:** `*emission*`, `*emissive*`, `*glow*`

(I will update this in future so you can set your own custom patterns)

### Environment Materials
- **Simple:** A/B texture blending with blend mask
- **Advanced:** Separate material BSDF layers with world-space mixing
- Supports height blending for better transitions

### Texture Variation
- Uses Unreal's TextureVariation material function
- Requires variation height map for randomization
- Automatically breaks up tiling patterns when using UVs


---

## 🎯 Workflow Example

### Standard PBR Material
1. AutoMatty → **Create Split Material**
2. AutoMatty → **Create Material Instance** 
4. Result: Complete PBR material with proper parameters

---

## 🔧 Issues/Troubleshooting

- **Check Output Log** (Window → Output Log) for detailed error messages
- **Material Editor issues:** Usually unreal-qt installation problems
- **Texture matching issues:** Check naming conventions above
- **Path issues:** Use `/Game/` prefix for all paths


### "Select exactly one Material asset"
- You need to select a **Material** (not Material Instance) to create instances
- Or select **Material Instance** to edit parameters

### "No textures found"
- Make sure texture names match patterns match the above patterns


### Material Editor won't open

 - ** install unreal_qt**
  ```
  "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Python3\Win64\python.exe" -m pip install unreal-qt
  ```
- **Always restart** Unreal Editor after installing
- Check Output Log for detailed error messages

### Nanite displacement not working
- Enable Nanite on your Static Mesh
- Material needs Height parameter and texture
- Check Project Settings → Rendering → Nanite

### "Substrate not enabled"
- Project Settings → Rendering → Materials → Substrate
- Restart editor after enabling

