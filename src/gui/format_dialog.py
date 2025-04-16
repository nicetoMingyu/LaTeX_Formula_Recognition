# format_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QCheckBox,
    QDialogButtonBox, QLabel, QPushButton, QHBoxLayout
)


class FormatSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Output Formats")
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout()
        
        # 添加全选按钮
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self.toggle_all)
        layout.addWidget(self.select_all_btn)
        
        # 添加复选框
        self.checkboxes = {}
        formats = [
            ("Word Document (*.docx)", "docx"),
            ("PDF Document (*.pdf)", "pdf"),
            ("LaTeX Document (*.tex)", "tex"),
            ("Markdown Document (*.md)", "md"),
            ("SVG Images (*.svg)", "svg"),
            ("PNG Images (*.png)", "png")
        ]
        
        for label, fmt in formats:
            checkbox = QCheckBox(label)
            self.checkboxes[fmt] = checkbox
            layout.addWidget(checkbox)
            
        # 添加按钮
        buttons = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        layout.addLayout(buttons)
        
        self.setLayout(layout)
        
    def toggle_all(self):
        """Toggle all checkboxes"""
        # 检查是否所有的复选框都被选中
        all_checked = all(cb.isChecked() for cb in self.checkboxes.values())
        # 如果全部选中，则取消全选；否则全选
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(not all_checked)
        # 更新按钮文本
        self.select_all_btn.setText("Deselect All" if not all_checked else "Select All")
        
    def selected_formats(self):
        """Get selected formats"""
        return [fmt for fmt, cb in self.checkboxes.items() if cb.isChecked()]