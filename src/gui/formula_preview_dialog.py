from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QScrollArea, QWidget, QGridLayout,
    QPushButton, QLabel, QCheckBox,
    QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
import cv2
import numpy as np

class FormulaItem(QWidget):
    def __init__(self, formula_data, position, confidence, parent=None):
        super().__init__(parent)
        self.formula_data = formula_data
        self.position = position
        self.confidence = confidence
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout()
        
        # Create checkbox and confidence label layout
        checkbox_layout = QHBoxLayout()
        
        # Create checkbox
        self.checkbox = QCheckBox()
        checkbox_layout.addWidget(self.checkbox)
        
        # Add confidence label
        confidence_label = QLabel(f"Confidence: {self.confidence:.2f}")
        checkbox_layout.addWidget(confidence_label)
        
        layout.addLayout(checkbox_layout)
        
        # Display formula based on type
        if isinstance(self.formula_data, np.ndarray):
            # Image formula
            height, width = self.formula_data.shape[:2]
            bytes_per_line = 3 * width
            q_image = QImage(self.formula_data.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            
            # Scale image for preview
            scaled_pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
            label = QLabel()
            label.setPixmap(scaled_pixmap)
            layout.addWidget(label)
        else:
            # Text formula
            text_edit = QTextEdit()
            text_edit.setPlainText(self.formula_data)
            text_edit.setReadOnly(True)
            text_edit.setMinimumHeight(100)
            text_edit.setMaximumHeight(200)
            layout.addWidget(text_edit)
        
        self.setLayout(layout)
        
    def is_selected(self):
        return self.checkbox.isChecked()
        
    def set_selected(self, selected: bool):
        self.checkbox.setChecked(selected)

class FormulaPreviewDialog(QDialog):
    def __init__(self, formulas, parent=None):
        super().__init__(parent)
        self.formulas = formulas
        self.selected_formulas = []
        self.formula_items = []  # 存储所有FormulaItem实例
        self._init_ui()
        
    def _init_ui(self):
        self.setWindowTitle("Formula Preview")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        
        # Create scroll area for formulas
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        grid = QGridLayout()
        
        # Display formula thumbnails
        for i, (formula_data, position, confidence) in enumerate(self.formulas):
            item = FormulaItem(formula_data, position, confidence)
            self.formula_items.append(item)  # 保存引用
            grid.addWidget(item, i//3, i%3)
        
        content.setLayout(grid)
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # Add buttons
        buttons = QHBoxLayout()
        select_all = QPushButton("Select All")
        select_all.clicked.connect(self._select_all)
        deselect_all = QPushButton("Deselect All")
        deselect_all.clicked.connect(self._deselect_all)
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        
        buttons.addWidget(select_all)
        buttons.addWidget(deselect_all)
        buttons.addWidget(ok_button)
        layout.addLayout(buttons)
        
        self.setLayout(layout)
        
    def _select_all(self):
        """Select all formula items"""
        for item in self.formula_items:
            item.set_selected(True)
                
    def _deselect_all(self):
        """Deselect all formula items"""
        for item in self.formula_items:
            item.set_selected(False)
                
    def get_selected_formulas(self):
        """Get selected formulas"""
        selected = []
        for item in self.formula_items:
            if item.is_selected():
                selected.append((item.formula_data, item.position))
        return selected 