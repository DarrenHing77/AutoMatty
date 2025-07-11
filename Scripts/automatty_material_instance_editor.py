"""
AutoMatty Material Instance Editor - Complete Integration (FIXED)
Modern Qt-based material parameter editor with real-time UE integration
"""

import unreal_qt
unreal_qt.setup()
import sys
import unreal
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# Global widget reference for hot reloading
material_editor_widget = None

class CollapsibleSection(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("CollapsibleSection")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Header button
        self.header = QPushButton(title)
        self.header.setCheckable(True)
        self.header.setChecked(True)
        self.header.setObjectName("SectionHeader")
        self.header.clicked.connect(self.toggle_content)
        
        # Content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(15, 10, 15, 10)
        self.content_layout.setSpacing(8)
        
        self.layout.addWidget(self.header)
        self.layout.addWidget(self.content_widget)
        
    def toggle_content(self):
        self.content_widget.setVisible(self.header.isChecked())
        
    def add_widget(self, widget):
        self.content_layout.addWidget(widget)
    
    def clear_widgets(self):
        """Remove all widgets from this section"""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

class ParameterSlider(QWidget):
    value_changed = Signal(str, float)
    
    def __init__(self, param_name, min_val=0.0, max_val=1.0, current_val=0.5, parent=None):
        super().__init__(parent)
        self.param_name = param_name
        self.default_val = current_val
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Parameter name label
        self.label = QLabel(param_name)
        self.label.setMinimumWidth(100)
        self.label.setObjectName("ParamLabel")
        
        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(int(min_val * 1000))
        self.slider.setMaximum(int(max_val * 1000))
        self.slider.setValue(int(current_val * 1000))
        self.slider.valueChanged.connect(self.on_slider_changed)
        
        # Value display/input
        self.value_input = QDoubleSpinBox()
        self.value_input.setMinimum(min_val)
        self.value_input.setMaximum(max_val)
        self.value_input.setValue(current_val)
        self.value_input.setDecimals(3)
        self.value_input.setSingleStep(0.01)
        self.value_input.setMaximumWidth(70)
        self.value_input.valueChanged.connect(self.on_input_changed)
        
        # Reset button
        self.reset_btn = QPushButton("↺")
        self.reset_btn.setMaximumWidth(25)
        self.reset_btn.setObjectName("ResetButton")
        self.reset_btn.clicked.connect(lambda: self.set_value(self.default_val))
        
        layout.addWidget(self.label)
        layout.addWidget(self.slider, 1)
        layout.addWidget(self.value_input)
        layout.addWidget(self.reset_btn)
        
    def on_slider_changed(self, value):
        float_val = value / 1000.0
        self.value_input.blockSignals(True)
        self.value_input.setValue(float_val)
        self.value_input.blockSignals(False)
        self.value_changed.emit(self.param_name, float_val)
        
    def on_input_changed(self, value):
        self.slider.blockSignals(True)
        self.slider.setValue(int(value * 1000))
        self.slider.blockSignals(False)
        self.value_changed.emit(self.param_name, value)
        
    def set_value(self, value):
        self.slider.setValue(int(value * 1000))
        self.value_input.setValue(value)

class ColorPicker(QWidget):
    color_changed = Signal(str, QColor)
    
    def __init__(self, param_name, current_color=None, parent=None):
        super().__init__(parent)
        self.param_name = param_name
        
        # Convert UE LinearColor to QColor if provided
        if current_color and hasattr(current_color, 'r'):
            self.current_color = QColor.fromRgbF(current_color.r, current_color.g, current_color.b, current_color.a)
        else:
            self.current_color = current_color or QColor(128, 128, 128)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Parameter name
        self.label = QLabel(param_name)
        self.label.setMinimumWidth(100)
        self.label.setObjectName("ParamLabel")
        
        # Color button
        self.color_btn = QPushButton()
        self.color_btn.setMaximumWidth(40)
        self.color_btn.setMaximumHeight(25)
        self.color_btn.clicked.connect(self.pick_color)
        
        # RGB values
        self.rgb_label = QLabel(f"RGB({self.current_color.red()}, {self.current_color.green()}, {self.current_color.blue()})")
        self.rgb_label.setObjectName("RGBLabel")
        
        # Update color button after rgb_label exists
        self.update_color_button()
        
        layout.addWidget(self.label)
        layout.addWidget(self.color_btn)
        layout.addWidget(self.rgb_label, 1)
        
    def update_color_button(self):
        self.color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgb({self.current_color.red()}, {self.current_color.green()}, {self.current_color.blue()});
                border: 1px solid #555;
                border-radius: 3px;
            }}
        """)
        if hasattr(self, 'rgb_label'):
            self.rgb_label.setText(f"RGB({self.current_color.red()}, {self.current_color.green()}, {self.current_color.blue()})")
        
    def pick_color(self):
        color = QColorDialog.getColor(self.current_color, self)
        if color.isValid():
            self.current_color = color
            self.update_color_button()
            self.color_changed.emit(self.param_name, color)

class MaterialInstanceEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Material Instance Editor")
        self.setFixedSize(380, 650)
        
        # Data
        self.current_materials = []
        self.current_instance = None
        self.parameter_widgets = {}
        self.sections = {}
        
        # Make it frameless and add rounded corners
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.init_ui()
        self.apply_styles()
        
        # Make it draggable
        self.drag_position = None
        
    def init_ui(self):
        # Main container with rounded background
        self.container = QWidget()
        self.container.setObjectName("MainContainer")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addWidget(self.container)
        
        # Container layout
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Material Instance Editor")
        title.setObjectName("Title")
        
        close_btn = QPushButton("×")
        close_btn.setObjectName("CloseButton")
        close_btn.setMaximumWidth(30)
        close_btn.clicked.connect(self.close)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        
        # Material dropdown
        self.material_dropdown = QComboBox()
        self.material_dropdown.setObjectName("MaterialDropdown")
        self.material_dropdown.currentIndexChanged.connect(self.on_material_selected)
        
        # Scroll area for parameters
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setObjectName("ScrollArea")
        
        # Parameters widget
        self.params_widget = QWidget()
        self.params_layout = QVBoxLayout(self.params_widget)
        self.params_layout.setContentsMargins(5, 5, 5, 5)
        self.params_layout.setSpacing(5)
        
        # Add stretch at bottom to push everything up
        self.params_layout.addStretch()
        
        scroll.setWidget(self.params_widget)
        
        # Action buttons
        button_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh Selection")
        refresh_btn.setObjectName("ActionButton")
        refresh_btn.clicked.connect(self.refresh_from_selection)
        
        reset_all_btn = QPushButton("Reset All")
        reset_all_btn.setObjectName("ActionButton")
        reset_all_btn.clicked.connect(self.reset_all_parameters)
        
        button_layout.addWidget(refresh_btn)
        button_layout.addWidget(reset_all_btn)
        
        # Add to main layout
        layout.addLayout(header_layout)
        layout.addWidget(self.material_dropdown)
        layout.addWidget(scroll, 1)
        layout.addLayout(button_layout)
        
    def load_materials(self, material_list):
        """Load materials from selected mesh into dropdown"""
        self.current_materials = material_list
        
        # Update dropdown
        self.material_dropdown.clear()
        for mat_info in material_list:
            display_name = f"{mat_info['actor']} - {mat_info['name']} (Slot {mat_info['slot']})"
            self.material_dropdown.addItem(display_name, mat_info)
        
        # Load first material if available
        if material_list:
            self.load_material_instance(material_list[0]['instance'])
            unreal.log(f"🎯 Loaded {len(material_list)} material instances")
    
    def on_material_selected(self, index):
        """Handle material dropdown selection"""
        if index >= 0 and index < len(self.current_materials):
            material_info = self.current_materials[index]
            self.load_material_instance(material_info['instance'])
    
    def load_material_instance(self, instance):
        """Dynamically create UI for this specific material instance"""
        self.current_instance = instance
        
        unreal.log(f"🔧 Loading parameters for: {instance.get_name()}")
        
        # Clear existing parameter widgets
        self.clear_all_parameters()
        
        # Get all parameter types from the parent material
        parent_material = instance.get_editor_property('parent')
        if not parent_material:
            unreal.log_warning("⚠️ No parent material found")
            return
        
        try:
            # Get parameter names from parent material
            scalar_params = unreal.MaterialEditingLibrary.get_scalar_parameter_names(parent_material)
            vector_params = unreal.MaterialEditingLibrary.get_vector_parameter_names(parent_material)
            texture_params = unreal.MaterialEditingLibrary.get_texture_parameter_names(parent_material)
            
            # Group parameters by category
            param_groups = self.group_parameters(scalar_params, vector_params, texture_params)
            
            # Create sections and parameters
            for group_name, params in param_groups.items():
                if params['scalars'] or params['vectors'] or params['textures']:
                    section = CollapsibleSection(group_name)
                    self.sections[group_name] = section
                    
                    # Add scalar parameters
                    for param_name in params['scalars']:
                        try:
                            current_value = unreal.MaterialEditingLibrary.get_material_instance_scalar_parameter_value(instance, param_name)
                            slider = ParameterSlider(str(param_name), 0.0, 2.0, current_value)
                            slider.value_changed.connect(self.on_scalar_parameter_changed)
                            section.add_widget(slider)
                            self.parameter_widgets[str(param_name)] = slider
                        except Exception as e:
                            unreal.log_warning(f"⚠️ Failed to load scalar parameter {param_name}: {e}")
                    
                    # Add vector parameters
                    for param_name in params['vectors']:
                        try:
                            current_value = unreal.MaterialEditingLibrary.get_material_instance_vector_parameter_value(instance, param_name)
                            color_picker = ColorPicker(str(param_name), current_value)
                            color_picker.color_changed.connect(self.on_vector_parameter_changed)
                            section.add_widget(color_picker)
                            self.parameter_widgets[str(param_name)] = color_picker
                        except Exception as e:
                            unreal.log_warning(f"⚠️ Failed to load vector parameter {param_name}: {e}")
                    
                    # Add texture parameters (just show names for now)
                    for param_name in params['textures']:
                        try:
                            current_texture = unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value(instance, param_name)
                            texture_name = current_texture.get_name() if current_texture else "None"
                            texture_label = QLabel(f"{str(param_name)}: {texture_name}")
                            texture_label.setObjectName("TextureLabel")
                            section.add_widget(texture_label)
                        except Exception as e:
                            unreal.log_warning(f"⚠️ Failed to load texture parameter {param_name}: {e}")
                    
                    # Add section to layout
                    self.params_layout.insertWidget(self.params_layout.count() - 1, section)
            
            unreal.log(f"✅ Loaded {len(scalar_params)} scalar, {len(vector_params)} vector, {len(texture_params)} texture parameters")
            
        except Exception as e:
            unreal.log_error(f"❌ Failed to load material parameters: {e}")
    
    def group_parameters(self, scalar_params, vector_params, texture_params):
        """Group parameters by logical categories"""
        groups = {
            "Color": {"scalars": [], "vectors": [], "textures": []},
            "Roughness": {"scalars": [], "vectors": [], "textures": []},
            "Material Properties": {"scalars": [], "vectors": [], "textures": []},
            "UV Controls": {"scalars": [], "vectors": [], "textures": []},
            "Displacement": {"scalars": [], "vectors": [], "textures": []},
            "Environment": {"scalars": [], "vectors": [], "textures": []},
            "Texture Variation": {"scalars": [], "vectors": [], "textures": []},
            "Other": {"scalars": [], "vectors": [], "textures": []}
        }
        
        # Categorize scalar parameters - FIXED: Convert Name to string
        for param in scalar_params:
            param_lower = str(param).lower()
            if any(word in param_lower for word in ['color', 'brightness', 'contrast', 'hue']):
                groups["Color"]["scalars"].append(param)
            elif any(word in param_lower for word in ['roughness', 'rough']):
                groups["Roughness"]["scalars"].append(param)
            elif any(word in param_lower for word in ['metal', 'emission', 'mfp', 'sss']):
                groups["Material Properties"]["scalars"].append(param)
            elif any(word in param_lower for word in ['uv', 'scale', 'tiling']):
                groups["UV Controls"]["scalars"].append(param)
            elif any(word in param_lower for word in ['displacement', 'height', 'disp']):
                groups["Displacement"]["scalars"].append(param)
            elif any(word in param_lower for word in ['mix', 'blend', 'env']):
                groups["Environment"]["scalars"].append(param)
            elif any(word in param_lower for word in ['variation', 'random', 'var']):
                groups["Texture Variation"]["scalars"].append(param)
            else:
                groups["Other"]["scalars"].append(param)
        
        # Categorize vector parameters - FIXED: Convert Name to string
        for param in vector_params:
            param_lower = str(param).lower()
            if any(word in param_lower for word in ['color', 'tint']):
                groups["Color"]["vectors"].append(param)
            else:
                groups["Other"]["vectors"].append(param)
        
        # Categorize texture parameters - FIXED: Convert Name to string
        for param in texture_params:
            param_lower = str(param).lower()
            if any(word in param_lower for word in ['color', 'albedo', 'diffuse']):
                groups["Color"]["textures"].append(param)
            elif any(word in param_lower for word in ['roughness', 'rough']):
                groups["Roughness"]["textures"].append(param)
            elif any(word in param_lower for word in ['metal', 'emission']):
                groups["Material Properties"]["textures"].append(param)
            elif any(word in param_lower for word in ['height', 'displacement', 'disp']):
                groups["Displacement"]["textures"].append(param)
            elif any(word in param_lower for word in ['blend', 'mask', 'mix']):
                groups["Environment"]["textures"].append(param)
            elif any(word in param_lower for word in ['variation', 'var']):
                groups["Texture Variation"]["textures"].append(param)
            else:
                groups["Other"]["textures"].append(param)
        
        return groups
    
    def clear_all_parameters(self):
        """Remove all parameter widgets and sections"""
        self.parameter_widgets.clear()
        
        # Clear sections
        for section in self.sections.values():
            section.deleteLater()
        self.sections.clear()
        
        # Clear layout (except the stretch at the end)
        while self.params_layout.count() > 1:
            child = self.params_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def on_scalar_parameter_changed(self, param_name, value):
        """Update scalar parameter in material instance"""
        if self.current_instance:
            try:
                unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(
                    self.current_instance, param_name, value
                )
                # Force update
                unreal.MaterialEditingLibrary.update_material_instance(self.current_instance)
            except Exception as e:
                unreal.log_warning(f"⚠️ Failed to set scalar parameter {param_name}: {e}")
    
    def on_vector_parameter_changed(self, param_name, qcolor):
        """Update vector parameter in material instance"""
        if self.current_instance:
            try:
                # Convert QColor to UE LinearColor
                linear_color = unreal.LinearColor(qcolor.redF(), qcolor.greenF(), qcolor.blueF(), qcolor.alphaF())
                unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(
                    self.current_instance, param_name, linear_color
                )
                # Force update
                unreal.MaterialEditingLibrary.update_material_instance(self.current_instance)
            except Exception as e:
                unreal.log_warning(f"⚠️ Failed to set vector parameter {param_name}: {e}")
    
    def refresh_from_selection(self):
        """Refresh materials from current viewport selection"""
        materials = get_selected_mesh_materials()
        if materials:
            self.load_materials(materials)
        else:
            unreal.log_warning("⚠️ No material instances found on selected mesh")
    
    def reset_all_parameters(self):
        """Reset all parameters to their default values"""
        for widget in self.parameter_widgets.values():
            if isinstance(widget, ParameterSlider):
                widget.set_value(widget.default_val)
    
    def apply_styles(self):
        self.setStyleSheet("""
            #MainContainer {
                background-color: #2b2b2b;
                border-radius: 10px;
                border: 1px solid #3c3c3c;
            }
            
            #Title {
                font-size: 14px;
                font-weight: bold;
                color: #ffffff;
                margin-bottom: 5px;
            }
            
            #MaterialDropdown {
                font-size: 11px;
                color: #ffffff;
                background-color: #1e1e1e;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 5px;
                margin-bottom: 10px;
            }
            
            #CloseButton {
                background-color: #ff4444;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            
            #CloseButton:hover {
                background-color: #ff6666;
            }
            
            #ScrollArea {
                border: 1px solid #3c3c3c;
                border-radius: 5px;
                background-color: #1e1e1e;
            }
            
            #CollapsibleSection {
                margin: 2px;
            }
            
            #SectionHeader {
                text-align: left;
                padding: 8px 12px;
                background-color: #404040;
                border: 1px solid #555;
                border-radius: 4px;
                color: #ffffff;
                font-weight: bold;
                font-size: 11px;
            }
            
            #SectionHeader:hover {
                background-color: #4a4a4a;
            }
            
            #SectionHeader:checked {
                background-color: #0078d4;
            }
            
            #ParamLabel {
                color: #cccccc;
                font-size: 10px;
                font-weight: bold;
            }
            
            #RGBLabel {
                color: #999999;
                font-size: 9px;
                font-family: monospace;
            }
            
            #TextureLabel {
                color: #aaaaaa;
                font-size: 9px;
                padding: 2px;
                background-color: #333333;
                border-radius: 2px;
                margin: 1px;
            }
            
            QSlider::groove:horizontal {
                height: 6px;
                background: #3c3c3c;
                border-radius: 3px;
            }
            
            QSlider::handle:horizontal {
                background: #0078d4;
                border: 1px solid #005499;
                width: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
            
            QSlider::handle:horizontal:hover {
                background: #1a8cff;
            }
            
            QDoubleSpinBox {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 2px 4px;
                color: #ffffff;
                font-size: 10px;
            }
            
            QDoubleSpinBox:focus {
                border-color: #0078d4;
            }
            
            #ResetButton {
                background-color: #606060;
                border: 1px solid #777;
                border-radius: 3px;
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
            }
            
            #ResetButton:hover {
                background-color: #707070;
            }
            
            #ActionButton {
                background-color: #0078d4;
                border: 1px solid #005499;
                border-radius: 4px;
                color: white;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 11px;
            }
            
            #ActionButton:hover {
                background-color: #1a8cff;
            }
            
            QScrollBar:vertical {
                background-color: #2b2b2b;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #666666;
            }
        """)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            try:
                # New Qt6 way
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            except AttributeError:
                # Fallback for older Qt
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position:
            try:
                # New Qt6 way
                self.move(event.globalPosition().toPoint() - self.drag_position)
            except AttributeError:
                # Fallback for older Qt
                self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def paintEvent(self, event):
        # Draw rounded background with shadow effect
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Shadow
        shadow_rect = self.rect().adjusted(2, 2, 2, 2)
        painter.fillRect(shadow_rect, QColor(0, 0, 0, 50))
        
        super().paintEvent(event)

# ========================================
# UE INTEGRATION FUNCTIONS - FIXED
# ========================================

def get_selected_mesh_materials():
    """Get all material instances from selected mesh in viewport - FIXED: Use new API"""
    # Use new API instead of deprecated one
    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    selected_actors = editor_actor_subsystem.get_selected_level_actors()
    
    material_instances = []
    
    for actor in selected_actors:
        # Check if it's a static mesh or skeletal mesh
        if isinstance(actor, (unreal.StaticMeshActor, unreal.SkeletalMeshActor)):
            mesh_component = None
            
            if isinstance(actor, unreal.StaticMeshActor):
                mesh_component = actor.get_component_by_class(unreal.StaticMeshComponent)
            else:  # SkeletalMeshActor
                mesh_component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
            
            if mesh_component:
                # Get all materials on this mesh
                num_materials = mesh_component.get_num_materials()
                
                for i in range(num_materials):
                    material = mesh_component.get_material(i)
                    if isinstance(material, unreal.MaterialInstanceConstant):
                        material_instances.append({
                            'name': material.get_name(),
                            'instance': material,
                            'slot': i,
                            'actor': actor.get_name()
                        })
    
    return material_instances

def show_editor_for_selection():
    """Show editor with materials from selected mesh"""
    global material_editor_widget
    
    materials = get_selected_mesh_materials()
    
    if not materials:
        unreal.log_warning("⚠️ No material instances found on selected mesh")
        unreal.log("💡 Select a Static Mesh or Skeletal Mesh actor in the viewport")
        return
    
    # Close existing widget if it exists
    if material_editor_widget:
        try:
            material_editor_widget.close()
            material_editor_widget.deleteLater()
        except:
            pass
    
    # Create new editor
    material_editor_widget = MaterialInstanceEditor()
    material_editor_widget.load_materials(materials)
    material_editor_widget.show()
    
    unreal.log(f"🎉 Material Editor opened with {len(materials)} instances")

def reload_material_editor():
    """Hot-reload the material editor without restarting UE"""
    import importlib
    try:
        import automatty_material_instance_editor
        importlib.reload(automatty_material_instance_editor)
        unreal.log("🔄 Material editor reloaded!")
        return automatty_material_instance_editor
    except Exception as e:
        unreal.log_error(f"❌ Reload failed: {e}")
        return None

def show_material_editor():
    """Show the material editor with current selection (with hot reload)"""
    editor_module = reload_material_editor()
    if editor_module:
        editor_module.show_editor_for_selection()

# Quick test function
def test_editor():
    """Test the editor UI (standalone)"""
    global material_editor_widget
    
    if material_editor_widget:
        try:
            material_editor_widget.close()
        except:
            pass
    
    material_editor_widget = MaterialInstanceEditor()
    material_editor_widget.show()
    unreal.log("🧪 Test editor shown (no materials loaded)")