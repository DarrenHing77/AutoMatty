"""
AutoMatty Material Instance Editor - FIXED VERSION
Fixes rendering artifacts and adds resizable columns
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

class ModifierAwareSlider(QSlider):
    """Custom slider that respects modifier keys for fine/coarse control"""
    
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.base_step = 1  # Base step size
        self.fine_step = 0.1  # Shift modifier (fine)
        self.coarse_step = 10  # Ctrl modifier (coarse)
        
    def wheelEvent(self, event):
        """Handle mouse wheel with modifier support"""
        modifiers = QApplication.keyboardModifiers()
        
        # Determine step size based on modifiers
        if modifiers & Qt.ShiftModifier:
            step = self.fine_step
        elif modifiers & Qt.ControlModifier:
            step = self.coarse_step
        else:
            step = self.base_step
        
        # Get wheel direction
        delta = event.angleDelta().y()
        if delta > 0:
            new_value = self.value() + step
        else:
            new_value = self.value() - step
        
        # Clamp to range
        new_value = max(self.minimum(), min(self.maximum(), new_value))
        self.setValue(int(new_value))
        
        event.accept()
    
    def mousePressEvent(self, event):
        """Track mouse press for drag detection"""
        if event.button() == Qt.LeftButton:
            self.start_value = self.value()
            self.start_pos = event.pos()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse drag with modifier-aware sensitivity"""
        if event.buttons() & Qt.LeftButton:
            modifiers = QApplication.keyboardModifiers()
            
            # Calculate sensitivity based on modifiers
            if modifiers & Qt.ShiftModifier:
                sensitivity = 0.2  # 5x slower
            elif modifiers & Qt.ControlModifier:
                sensitivity = 5.0   # 5x faster
            else:
                sensitivity = 1.0   # Normal speed
            
            # Calculate movement
            if hasattr(self, 'start_pos'):
                delta_x = event.pos().x() - self.start_pos.x()
                value_range = self.maximum() - self.minimum()
                slider_width = self.width()
                
                if slider_width > 0:
                    # Convert pixel movement to value change
                    value_delta = (delta_x / slider_width) * value_range * sensitivity
                    new_value = self.start_value + value_delta
                    
                    # Clamp to range
                    new_value = max(self.minimum(), min(self.maximum(), new_value))
                    self.setValue(int(new_value))
        
        # Don't call super() to prevent default behavior when using modifiers
        if not (QApplication.keyboardModifiers() & (Qt.ShiftModifier | Qt.ControlModifier)):
            super().mouseMoveEvent(event)

class ModifierAwareSpinBox(QDoubleSpinBox):
    """Custom spinbox with modifier key support"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.base_step = 0.001
        self.fine_step = 0.0001  # 10x finer
        self.coarse_step = 0.01   # 10x coarser
        
    def wheelEvent(self, event):
        """Handle mouse wheel with modifier support"""
        modifiers = QApplication.keyboardModifiers()
        
        # Store original step
        original_step = self.singleStep()
        
        # Set step based on modifiers
        if modifiers & Qt.ShiftModifier:
            self.setSingleStep(self.fine_step)
        elif modifiers & Qt.ControlModifier:
            self.setSingleStep(self.coarse_step)
        else:
            self.setSingleStep(self.base_step)
        
        # Call parent wheel event
        super().wheelEvent(event)
        
        # Restore original step
        self.setSingleStep(original_step)
    
    def keyPressEvent(self, event):
        """Handle arrow keys with modifiers"""
        if event.key() in (Qt.Key_Up, Qt.Key_Down):
            modifiers = QApplication.keyboardModifiers()
            
            # Store original step
            original_step = self.singleStep()
            
            # Set step based on modifiers
            if modifiers & Qt.ShiftModifier:
                self.setSingleStep(self.fine_step)
            elif modifiers & Qt.ControlModifier:
                self.setSingleStep(self.coarse_step)
            else:
                self.setSingleStep(self.base_step)
            
            # Call parent key event
            super().keyPressEvent(event)
            
            # Restore original step
            self.setSingleStep(original_step)
        else:
            super().keyPressEvent(event)

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
        self.original_value = current_val  # Store for conflict resolution
        self.min_val = min_val
        self.max_val = max_val
        self.is_dragging = False
        self.last_mouse_pos = None
        
        # Use a splitter for resizable columns
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Create main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.splitter)
        
        # Parameter name widget (with minimum width and text eliding)
        name_widget = QWidget()
        name_layout = QHBoxLayout(name_widget)
        name_layout.setContentsMargins(5, 0, 5, 0)
        
        self.label = QLabel(param_name)
        self.label.setMinimumWidth(80)
        self.label.setMaximumWidth(200)
        self.label.setObjectName("ParamLabel")
        self.label.setToolTip(param_name)  # Show full name on hover
        # Enable text eliding for long names
        self.label.setWordWrap(False)
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        name_layout.addWidget(self.label)
        name_layout.addStretch()
        
        # Slider widget
        slider_widget = QWidget()
        slider_layout = QHBoxLayout(slider_widget)
        slider_layout.setContentsMargins(5, 0, 5, 0)
        
        self.slider = ModifierAwareSlider(Qt.Horizontal)
        self.slider.setMinimum(int(min_val * 1000))
        self.slider.setMaximum(int(max_val * 1000))
        self.slider.setValue(int(current_val * 1000))
        self.slider.valueChanged.connect(self.on_slider_changed)
        self.slider.setMinimumWidth(100)
        
        slider_layout.addWidget(self.slider)
        
        # Value input widget
        value_widget = QWidget()
        value_layout = QHBoxLayout(value_widget)
        value_layout.setContentsMargins(5, 0, 5, 0)
        
        self.value_input = ModifierAwareSpinBox()
        self.value_input.setMinimum(min_val)
        self.value_input.setMaximum(max_val)
        self.value_input.setValue(current_val)
        self.value_input.setDecimals(3)
        self.value_input.setSingleStep(0.001)
        self.value_input.setFixedWidth(80)
        self.value_input.valueChanged.connect(self.on_input_changed)
        
        value_layout.addWidget(self.value_input)
        
        # Reset button widget
        reset_widget = QWidget()
        reset_layout = QHBoxLayout(reset_widget)
        reset_layout.setContentsMargins(5, 0, 5, 0)
        
        self.reset_btn = QPushButton("↺")
        self.reset_btn.setFixedWidth(30)
        self.reset_btn.setObjectName("ResetButton")
        self.reset_btn.clicked.connect(lambda: self.set_value(self.default_val))
        
        reset_layout.addWidget(self.reset_btn)
        
        # Add widgets to splitter
        self.splitter.addWidget(name_widget)
        self.splitter.addWidget(slider_widget)
        self.splitter.addWidget(value_widget)
        self.splitter.addWidget(reset_widget)
        
        # Set splitter proportions: name gets more space, others fixed-ish
        self.splitter.setStretchFactor(0, 3)  # Name column - expandable
        self.splitter.setStretchFactor(1, 4)  # Slider column - most space
        self.splitter.setStretchFactor(2, 1)  # Value column - fixed-ish
        self.splitter.setStretchFactor(3, 0)  # Reset column - fixed
        
        # Set initial sizes
        self.splitter.setSizes([120, 200, 80, 30])
        
        # Add tooltip with modifier key info
        tooltip_text = (f"{param_name}\n\n"
                       "💡 Modifier Keys:\n"
                       "• Normal: Regular speed\n" 
                       "• Shift: Fine control (5x slower)\n"
                       "• Ctrl: Coarse control (5x faster)\n\n"
                       "Works with: Mouse drag, wheel, arrow keys")
        self.slider.setToolTip(tooltip_text)
        self.value_input.setToolTip(tooltip_text)
        
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
        
    def reset_to_original(self):
        """Reset to the value when parameter was first loaded"""
        self.set_value(self.original_value)
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for fine control"""
        if event.key() in (Qt.Key_Left, Qt.Key_Right):
            modifiers = QApplication.keyboardModifiers()
            
            # Determine step size
            if modifiers & Qt.ShiftModifier:
                step = 0.1  # Fine
            elif modifiers & Qt.ControlModifier:
                step = 10.0  # Coarse
            else:
                step = 1.0   # Normal
            
            # Apply step
            current = self.slider.value()
            if event.key() == Qt.Key_Right:
                new_value = current + step
            else:
                new_value = current - step
            
            # Clamp and set
            new_value = max(self.slider.minimum(), min(self.slider.maximum(), new_value))
            self.slider.setValue(int(new_value))
            
            event.accept()
        else:
            super().keyPressEvent(event)

class ColorPicker(QWidget):
    color_changed = Signal(str, QColor)
    
    def __init__(self, param_name, current_color=None, parent=None):
        super().__init__(parent)
        self.param_name = param_name
        
        # Convert UE LinearColor to QColor if provided
        if current_color and hasattr(current_color, 'r'):
            self.current_color = QColor.fromRgbF(current_color.r, current_color.g, current_color.b, current_color.a)
            self.original_color = QColor.fromRgbF(current_color.r, current_color.g, current_color.b, current_color.a)
        else:
            self.current_color = current_color or QColor(128, 128, 128)
            self.original_color = QColor(self.current_color)
        
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
            
    def reset_to_original(self):
        """Reset to original color"""
        self.current_color = QColor(self.original_color)
        self.update_color_button()
        self.color_changed.emit(self.param_name, self.current_color)

class MaterialInstanceEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Material Instance Editor")
        self.setMinimumSize(420, 500)  # Set minimum size instead of fixed
        self.resize(500, 700)  # Default size, but resizable
        
        # Data
        self.current_materials = []
        self.current_instance = None
        self.parameter_widgets = {}
        self.sections = {}
        self.is_master_material = False
        self.master_warnings_disabled = set()
        
        # Remove transparency and frameless flags to fix rendering issues
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        
        self.init_ui()
        self.apply_styles()
        
    def init_ui(self):
        # Main layout - no need for container widget now
        layout = QVBoxLayout(self)
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
        
    def get_smart_parameter_range(self, param_name):
        """Get appropriate min/max values based on parameter type"""
        param_lower = param_name.lower()
        
        # UV Scale and tiling parameters - much higher range
        if any(word in param_lower for word in ['scale', 'tiling', 'uvscale', 'tile']):
            return 0.01, 100.0
            
        # Displacement intensity - moderate range
        elif any(word in param_lower for word in ['displacement', 'height', 'disp']):
            return 0.0, 10.0
            
        # Brightness and contrast - moderate range
        elif any(word in param_lower for word in ['brightness', 'contrast']):
            return 0.0, 5.0
            
        # Roughness, metallic, intensity - standard 0-1 range
        elif any(word in param_lower for word in ['roughness', 'metallic', 'intensity', 'weight']):
            return 0.0, 1.0
            
        # Mix, blend parameters - standard 0-1 range
        elif any(word in param_lower for word in ['mix', 'blend', 'alpha']):
            return 0.0, 1.0
            
        # Hue shift - -1 to 1 range
        elif 'hue' in param_lower:
            return -1.0, 1.0
            
        # Default range for unknown parameters
        else:
            return 0.0, 2.0
    
    def show_master_material_confirmation(self, param_name, new_value):
        """Show confirmation before changing master material"""
        msg = QMessageBox()
        msg.setWindowTitle("AutoMatty - Master Material Warning")
        msg.setIcon(QMessageBox.Warning)
        msg.setText(f"Change '{param_name}' in Master Material?")
        msg.setInformativeText(
            f"This will change '{param_name}' to {new_value} in the MASTER material.\n\n"
            "⚠️ This affects ALL objects using this material in your project!\n\n"
            "Consider creating a Material Instance instead for safer editing."
        )
        
        # Add "Don't ask again" checkbox
        dont_ask_checkbox = QCheckBox("Don't warn me again for this material")
        msg.setCheckBox(dont_ask_checkbox)
        
        # Custom buttons
        create_instance_btn = msg.addButton("Create Instance Instead", QMessageBox.AcceptRole)
        proceed_btn = msg.addButton("Proceed (Master)", QMessageBox.DestructiveRole)
        cancel_btn = msg.addButton("Cancel", QMessageBox.RejectRole)
        
        msg.exec_()
        
        result = {
            'action': 'cancel',
            'dont_ask': dont_ask_checkbox.isChecked()
        }
        
        if msg.clickedButton() == create_instance_btn:
            result['action'] = 'create_instance'
        elif msg.clickedButton() == proceed_btn:
            result['action'] = 'proceed'
        
        return result
    
    def show_conflict_warning(self, param_name, conflict_type):
        """Show conflict warnings for incompatible parameter changes"""
        msg = QMessageBox()
        msg.setWindowTitle("AutoMatty - Parameter Conflict")
        msg.setIcon(QMessageBox.Warning)
        
        if conflict_type == "triplanar_uv":
            msg.setText("Triplanar vs UV Conflict")
            msg.setInformativeText(
                f"'{param_name}' conflicts with triplanar mapping!\n\n"
                "Triplanar materials use world-space coordinates and ignore UV scaling.\n"
                "This parameter won't have any visible effect.\n\n"
                "💡 Use either triplanar OR UV controls, not both."
            )
        elif conflict_type == "texture_variation_manual":
            msg.setText("Texture Variation Conflict") 
            msg.setInformativeText(
                f"'{param_name}' may conflict with texture variation!\n\n"
                "Texture variation automatically modifies UVs for randomness.\n"
                "Manual UV adjustments might interfere with the variation effect.\n\n"
                "💡 Disable texture variation if you need precise UV control."
            )
        
        proceed_btn = msg.addButton("Proceed Anyway", QMessageBox.AcceptRole)
        cancel_btn = msg.addButton("Cancel Change", QMessageBox.RejectRole)
        
        msg.exec_()
        
        return msg.clickedButton() == proceed_btn
    
    def detect_parameter_conflicts(self, param_name):
        """Detect potential conflicts with current parameter"""
        if not self.current_instance:
            return None
            
        param_lower = param_name.lower()
        
        # Get parent material to check for triplanar/variation setup
        parent_material = None
        if self.is_master_material:
            parent_material = self.current_instance
        else:
            parent_material = self.current_instance.get_editor_property('parent')
        
        if not parent_material:
            return None
            
        # Check material for triplanar indicators (world-aligned functions)
        # This is a simplified check - in practice you'd analyze the material graph
        material_name = parent_material.get_name().lower()
        
        # UV scale conflicts with triplanar
        if any(word in param_lower for word in ['scale', 'tiling', 'uvscale']):
            if 'triplanar' in material_name or 'worldaligned' in material_name:
                return "triplanar_uv"
                
        # UV adjustments might conflict with texture variation
        if any(word in param_lower for word in ['scale', 'tiling', 'uvscale', 'offset']):
            # Check if material has variation parameters
            try:
                texture_params = unreal.MaterialEditingLibrary.get_texture_parameter_names(parent_material)
                if "VariationHeightMap" in texture_params:
                    return "texture_variation_manual"
            except:
                pass
                
        return None
    
    def show_master_material_warning(self):
        """Show persistent warning for master materials"""
        if not hasattr(self, 'master_warning_label'):
            self.master_warning_label = QLabel("⚠️ EDITING MASTER MATERIAL - AFFECTS ALL INSTANCES")
            self.master_warning_label.setObjectName("MasterWarning")
            # Insert after dropdown in main layout
            self.layout().insertWidget(2, self.master_warning_label)

    def hide_master_material_warning(self):
        """Hide master material warning"""
        if hasattr(self, 'master_warning_label'):
            self.master_warning_label.hide()
    
    def load_materials(self, material_list):
        """Load materials from selected mesh into dropdown"""
        self.current_materials = material_list
        
        # Update dropdown
        self.material_dropdown.clear()
        for mat_info in material_list:
            mat_type = mat_info.get('type', 'Unknown')
            display_name = f"{mat_info['actor']} - {mat_info['name']} ({mat_type}) (Slot {mat_info['slot']})"
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
        """Load material with master/instance detection"""
        self.current_instance = instance
        
        # Check if this is a master material
        self.is_master_material = isinstance(instance, unreal.Material)
        
        if self.is_master_material:
            self.show_master_material_warning()
            unreal.log(f"⚠️ Loading MASTER material: {instance.get_name()}")
        else:
            self.hide_master_material_warning()
            unreal.log(f"🔧 Loading material instance: {instance.get_name()}")
        
        # Clear existing parameter widgets
        self.clear_all_parameters()
        
        # Get all parameter types from the parent material
        parent_material = instance
        if not self.is_master_material:
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
                    
                    # Add scalar parameters with smart ranges
                    for param_name in params['scalars']:
                        try:
                            if self.is_master_material:
                                current_value = unreal.MaterialEditingLibrary.get_material_scalar_parameter_value(instance, param_name)
                            else:
                                current_value = unreal.MaterialEditingLibrary.get_material_instance_scalar_parameter_value(instance, param_name)
                            
                            # Get smart range for this parameter
                            min_val, max_val = self.get_smart_parameter_range(str(param_name))
                            
                            slider = ParameterSlider(str(param_name), min_val, max_val, current_value)
                            slider.value_changed.connect(self.on_scalar_parameter_changed)
                            section.add_widget(slider)
                            self.parameter_widgets[str(param_name)] = slider
                        except Exception as e:
                            unreal.log_warning(f"⚠️ Failed to load scalar parameter {param_name}: {e}")
                    
                    # Add vector parameters
                    for param_name in params['vectors']:
                        try:
                            if self.is_master_material:
                                current_value = unreal.MaterialEditingLibrary.get_material_vector_parameter_value(instance, param_name)
                            else:
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
                            if self.is_master_material:
                                current_texture = unreal.MaterialEditingLibrary.get_material_texture_parameter_value(instance, param_name)
                            else:
                                current_texture = unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value(instance, param_name)
                            
                            texture_name = current_texture.get_name() if current_texture else "None"
                            texture_label = QLabel(f"{str(param_name)}: {texture_name}")
                            texture_label.setObjectName("TextureLabel")
                            section.add_widget(texture_label)
                        except Exception as e:
                            unreal.log_warning(f"⚠️ Failed to load texture parameter {param_name}: {e}")
                    
                    # Add section to layout
                    self.params_layout.insertWidget(self.params_layout.count() - 1, section)
            
            param_count = len(scalar_params) + len(vector_params) + len(texture_params)
            unreal.log(f"✅ Loaded {param_count} parameters ({len(scalar_params)} scalar, {len(vector_params)} vector, {len(texture_params)} texture)")
            
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
        
        # Categorize scalar parameters
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
        
        # Categorize vector parameters
        for param in vector_params:
            param_lower = str(param).lower()
            if any(word in param_lower for word in ['color', 'tint']):
                groups["Color"]["vectors"].append(param)
            else:
                groups["Other"]["vectors"].append(param)
        
        # Categorize texture parameters
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
        """Handle parameter changes with master material protection and conflict detection"""
        if not self.current_instance:
            return
        
        # Check for parameter conflicts first
        conflict_type = self.detect_parameter_conflicts(param_name)
        if conflict_type:
            if not self.show_conflict_warning(param_name, conflict_type):
                # User cancelled - reset parameter
                widget = self.parameter_widgets.get(param_name)
                if widget and isinstance(widget, ParameterSlider):
                    widget.reset_to_original()
                return
        
        # Check if this is a master material and we need confirmation
        if self.is_master_material:
            material_name = self.current_instance.get_name()
            if material_name not in self.master_warnings_disabled:
                
                result = self.show_master_material_confirmation(param_name, value)
                
                if result['action'] == 'cancel':
                    # Reset the slider/input to previous value
                    widget = self.parameter_widgets.get(param_name)
                    if widget and isinstance(widget, ParameterSlider):
                        widget.reset_to_original()
                    return
                
                elif result['action'] == 'create_instance':
                    # Auto-create instance and switch to it
                    self.create_instance_from_master()
                    return
                
                # Remember "don't ask" preference
                if result['dont_ask']:
                    self.master_warnings_disabled.add(material_name)
        
        # Proceed with the change
        self.apply_parameter_change(param_name, value)

    def apply_parameter_change(self, param_name, value):
        """Apply parameter change with proper API"""
        try:
            if self.is_master_material:
                # Use Material API (affects master)
                unreal.MaterialEditingLibrary.set_material_scalar_parameter_value(
                    self.current_instance, param_name, value
                )
                # Force recompilation for master materials
                unreal.MaterialEditingLibrary.recompile_material(self.current_instance)
                unreal.log(f"🔄 Updated master material parameter: {param_name} = {value}")
            else:
                # Use Material Instance API (instance only)
                unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(
                    self.current_instance, param_name, value
                )
                unreal.MaterialEditingLibrary.update_material_instance(self.current_instance)
            
        except Exception as e:
            unreal.log_warning(f"⚠️ Failed to set parameter {param_name}: {e}")

    def create_instance_from_master(self):
        """Auto-create material instance from master material"""
        try:
            base_material = self.current_instance
            
            # Generate unique name
            mi_name = f"MI_{base_material.get_name()}_Auto"
            mi_path = "/Game/Materials/"
            
            # Create the instance
            atools = unreal.AssetToolsHelpers.get_asset_tools()
            mi_factory = unreal.MaterialInstanceConstantFactoryNew()
            
            new_instance = atools.create_asset(
                mi_name, mi_path, unreal.MaterialInstanceConstant, mi_factory
            )
            
            # Set parent
            unreal.MaterialEditingLibrary.set_material_instance_parent(new_instance, base_material)
            
            # Switch editor to the new instance
            self.current_instance = new_instance
            self.is_master_material = False
            self.hide_master_material_warning()
            
            # Reload the interface for the new instance
            self.load_material_instance(new_instance)
            
            unreal.log(f"✅ Created material instance: {mi_name}")
            
            return new_instance
            
        except Exception as e:
            unreal.log_error(f"❌ Failed to create instance: {e}")
            return None
    
    def on_vector_parameter_changed(self, param_name, qcolor):
        """Update vector parameter in material instance"""
        if self.current_instance:
            try:
                # Convert QColor to UE LinearColor
                linear_color = unreal.LinearColor(qcolor.redF(), qcolor.greenF(), qcolor.blueF(), qcolor.alphaF())
                
                if self.is_master_material:
                    unreal.MaterialEditingLibrary.set_material_vector_parameter_value(
                        self.current_instance, param_name, linear_color
                    )
                    unreal.MaterialEditingLibrary.recompile_material(self.current_instance)
                else:
                    unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(
                        self.current_instance, param_name, linear_color
                    )
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
        """Reset all parameters to their original values"""
        for widget in self.parameter_widgets.values():
            if isinstance(widget, ParameterSlider):
                widget.reset_to_original()
            elif isinstance(widget, ColorPicker):
                widget.reset_to_original()
    
    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            
            QMainWindow, QDialog {
                background-color: #2b2b2b;
                border: 1px solid #3c3c3c;
            }
            
            #Title {
                font-size: 14px;
                font-weight: bold;
                color: #ffffff;
                margin-bottom: 5px;
            }
            
            #MasterWarning {
                background-color: #ff4444;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
                text-align: center;
                margin: 5px 0;
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
                padding: 2px;
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
            
            QSplitter::handle {
                background-color: #555555;
                width: 2px;
                margin: 2px;
            }
            
            QSplitter::handle:hover {
                background-color: #0078d4;
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

# ========================================
# UE INTEGRATION FUNCTIONS
# ========================================

def get_selected_mesh_materials():
    """Get ALL materials (both instances and masters) from selected mesh"""
    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    selected_actors = editor_actor_subsystem.get_selected_level_actors()
    
    material_instances = []
    
    for actor in selected_actors:
        if isinstance(actor, (unreal.StaticMeshActor, unreal.SkeletalMeshActor)):
            mesh_component = None
            
            if isinstance(actor, unreal.StaticMeshActor):
                mesh_component = actor.get_component_by_class(unreal.StaticMeshComponent)
            else:
                mesh_component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
            
            if mesh_component:
                num_materials = mesh_component.get_num_materials()
                
                for i in range(num_materials):
                    material = mesh_component.get_material(i)
                    
                    # Accept both Materials and Material Instances
                    if isinstance(material, (unreal.MaterialInstanceConstant, unreal.Material)):
                        material_type = "Master" if isinstance(material, unreal.Material) else "Instance"
                        
                        material_instances.append({
                            'name': material.get_name(),
                            'instance': material,
                            'slot': i,
                            'actor': actor.get_name(),
                            'type': material_type
                        })
    
    return material_instances

def show_editor_for_selection():
    """Show editor with enhanced error handling"""
    global material_editor_widget
    
    materials = get_selected_mesh_materials()
    
    if not materials:
        # Enhanced error handling with helpful messages
        editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        selected_actors = editor_actor_subsystem.get_selected_level_actors()
        
        if not selected_actors:
            unreal.log_error("❌ No actors selected. Select a mesh in the viewport first.")
            return
        
        unreal.log_warning("⚠️ Selected actors don't have any materials.")
        unreal.log("💡 Make sure your mesh has materials assigned before using the editor.")
        return
    
    # Close existing widget
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
    
    unreal.log(f"🎉 Material Editor opened with {len(materials)} materials")

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

