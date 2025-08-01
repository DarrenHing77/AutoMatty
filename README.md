# AutoMatty v1.0 🎨

**Smart material automation for Unreal Engine 5.6**

AutoMatty streamlines Substrate material creation and management with intelligent texture matching, smart naming, and automated workflows. Built for 3D artists who want powerful materials without the tedium.

---

## 🚀 Quick Start

### Requirements
- **Unreal Engine 5.6+**
- **Substrate enabled** (Project Settings → Rendering → Substrate)
- **Python Plugin enabled** (Edit → Plugins → Python)

### Material Editor Setup (Optional but Recommended)
The **Material Editor** provides visual sliders and real-time parameter editing.

**Installation Steps:**
1. **Press Windows Key + R**
2. **Type:** `cmd` 
3. **Press Enter** (opens black command window)
4. **Type:** `pip install unreal-qt`
5. **Press Enter** and wait for "Successfully installed"
6. **Restart Unreal Editor**

**If that doesn't work, try these commands instead:**
```bash
python -m pip install unreal-qt
py -m pip install unreal-qt  
pip install unreal-qt --user
```

---

## 📦 Installation

1. Copy **AutoMatty** folder to `YourProject/Plugins/`
2. **Restart Unreal Editor**
3. Look for **AutoMatty** button in the main toolbar

---

## ✨ Core Features

### 🔧 Material Builders

**What they do:** Create complete Substrate materials with proper node networks, parameters, and optimizations.

- **ORM Materials** - Packed Occlusion/Roughness/Metallic workflow (most common)
- **Split Materials** - Individual texture channels (Color, Normal, Roughness, Metallic)
- **Environment Materials** - Advanced A/B blending for landscapes and complex surfaces

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

**Works with:**
- Content browser texture selection
- Import dialog (select textures to import)
- Existing texture folders

### 🔄 Texture Repather

**What it does:** Batch replaces textures in existing material instances.

**Use cases:**
- Swap texture sets (e.g., 4K → 8K versions)
- Update materials with new texture variations
- Replace placeholder textures with final assets

**Smart matching:**
- Version-agnostic (`Wood_v001.jpg` matches `Wood_v002.jpg`)
- Type-aware (preserves Normal → Normal, Color → Color mapping)
- Handles texture variations and height maps

### 🎛️ Material Editor (Advanced)

**What it does:** Visual parameter editor with real-time feedback (requires unreal-qt).

**Features:**
- **Drag-value boxes** - Click and drag to adjust values
- **Visual sliders** with progress bar fills
- **Parameter grouping** - Organized by Color, Roughness, UV Controls, etc.
- **Override toggles** - Enable/disable parameter overrides
- **Conflict detection** - Warns about incompatible parameter combinations
- **Master material protection** - Prevents accidental changes to master materials

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

1. **Click AutoMatty toolbar button** → Choose material type
2. **Select textures** (optional) - from Content Browser or import new ones
3. **Enable features** - Check boxes for Nanite, Triplanar, etc.
4. **Click Create** - Material appears in your Materials folder

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

### Environment Materials
- **Simple:** A/B texture blending with blend mask
- **Advanced:** Separate material layers with world-space mixing
- Supports height blending for realistic terrain transitions

### Texture Variation
- Uses Unreal's TextureVariation material function
- Requires variation height map for randomization
- Automatically breaks up tiling patterns

---

## 🔧 Troubleshooting

### "Select exactly one Material asset"
- You need to select a **Material** (not Material Instance) to create instances
- Or select **Material Instance** to edit parameters

### "No textures found"
- Make sure texture names match patterns (Color, Normal, etc.)
- Try importing textures first, then creating instance
- Check texture path in AutoMatty settings

### Material Editor won't open
- Install unreal-qt: `pip install unreal-qt`
- Restart Unreal Editor
- Check Output Log for detailed error messages

### Nanite displacement not working
- Enable Nanite on your Static Mesh
- Material needs Height parameter and texture
- Check Project Settings → Rendering → Nanite

### "Substrate not enabled"
- Project Settings → Rendering → Materials → Substrate
- Restart editor after enabling

---

## 🎯 Workflow Examples

### Standard PBR Material
1. Import textures: `Wood_Color.jpg`, `Wood_Normal.jpg`, `Wood_ORM.jpg`
2. AutoMatty → **Create ORM Material**
3. AutoMatty → **Create Material Instance** 
4. Result: Complete PBR material with proper parameters

### Nanite Landscape Material  
1. Import: `Rock_Color.jpg`, `Rock_Normal.jpg`, `Rock_Height.jpg`
2. AutoMatty → **Create ORM Material**
3. ✅ **Enable Nanite** checkbox
4. Create → Material supports real displacement

### Environment Blending
1. Import: `GrassA_Color.jpg`, `GrassB_Color.jpg`, `Blend_Mask.jpg`, etc.
2. AutoMatty → **Create Environment Material**
3. ✅ **Enable Advanced Environment**
4. Result: World-space blended material perfect for landscapes

---

## 🤝 Support

- **Check Output Log** (Window → Output Log) for detailed error messages
- **Material Editor issues:** Usually unreal-qt installation problems
- **Texture matching issues:** Check naming conventions above
- **Path issues:** Use `/Game/` prefix for all paths

Built for UE 5.6 Substrate system. May require updates for future engine versions.
