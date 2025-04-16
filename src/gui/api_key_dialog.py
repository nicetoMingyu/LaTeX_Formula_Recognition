# api_key_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox,
    QCheckBox, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from config.settings import Config
import logging

class ApiKeyDialog(QDialog):
    key_verified = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("API Configuration")
        self.setFixedSize(450, 200)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self._init_ui()
        self._load_saved_key()

    def _init_ui(self):
        layout = QVBoxLayout()

        # API Key输入
        self.lbl_key = QLabel("Please enter your Qwen API Key:")
        self.input_key = QLineEdit()
        self.input_key.setPlaceholderText("sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        self.input_key.setEchoMode(QLineEdit.EchoMode.Password)
        
        # 回车键处理
        self.input_key.returnPressed.connect(self._validate_api_key)

        # 高级选项
        self.chk_save = QCheckBox("Save key securely")
        self.chk_show = QCheckBox("Show key")
        self.chk_test = QCheckBox("Validate with test API call")
        self.chk_show.stateChanged.connect(self._toggle_visibility)
        self.chk_test.setChecked(True)

        # 按钮
        self.btn_confirm = QPushButton("Verify & Save")
        self.btn_clear = QPushButton("Clear Saved Key")

        # 布局
        options_layout = QHBoxLayout()
        options_layout.addWidget(self.chk_save)
        options_layout.addWidget(self.chk_show)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_clear)
        button_layout.addWidget(self.btn_confirm)

        layout.addWidget(self.lbl_key)
        layout.addWidget(self.input_key)
        layout.addLayout(options_layout)
        layout.addWidget(self.chk_test)
        layout.addLayout(button_layout)

        # 事件绑定
        self.btn_confirm.clicked.connect(self._validate_api_key)
        self.btn_clear.clicked.connect(self._clear_saved_key)

        self.setLayout(layout)

    def _toggle_visibility(self, state):
        self.input_key.setEchoMode(
            QLineEdit.EchoMode.Normal
            if state
            else QLineEdit.EchoMode.Password
        )

    def _load_saved_key(self):
        try:
            saved_key = Config.get_saved_key()
            if saved_key:
                self.input_key.setText(saved_key)
                self.chk_save.setChecked(True)
                # 自动验证已保存的密钥
                self._validate_api_key()
        except Exception as e:
            logging.error(f"Error loading saved key: {str(e)}")
            QMessageBox.warning(self, "Warning",
                "Failed to load saved API key. Please enter your key again.")

    def _validate_api_key(self):
        key = self.input_key.text().strip()

        try:
            # 验证密钥格式
            if not key.startswith("sk-") or len(key) != 35:
                raise ValueError("Invalid API key format. Key must start with 'sk-' and be exactly 35 characters long.")

            # 可选API测试验证
            if self.chk_test.isChecked():
                from openai import OpenAI
                client = OpenAI(
                    api_key=key,
                    base_url=Config.API_ENDPOINT,
                    timeout=5
                )
                response = client.chat.completions.create(
                    model="qwen-vl-max",
                    messages=[{
                        "role": "user",
                        "content": [{
                            "type": "text",
                            "text": "Test connection"
                        }]
                    }],
                    max_tokens=5
                )
                if not response.choices[0].message.content:
                    raise ConnectionError("API test failed")

            # 保存配置
            if self.chk_save.isChecked():
                Config.save_key(key)
            else:
                Config.delete_saved_key()

            # 设置当前实例的API密钥
            Config.set_api_key(key)

            self.key_verified.emit(key)
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Validation Failed",
                f"API Key verification failed:\n{str(e)}\n\n"
                "Please check:\n"
                "1. Key format (starts with sk-, exactly 35 chars)\n"
                "2. Network connection\n"
                "3. API endpoint accessibility")
            self.input_key.selectAll()

    def _clear_saved_key(self):
        try:
            Config.delete_saved_key()
            self.input_key.clear()
            QMessageBox.information(self, "Success",
                "Saved API key has been removed from system keychain.")
        except Exception as e:
            logging.error(f"Error clearing saved key: {str(e)}")
            QMessageBox.warning(self, "Warning",
                "Failed to clear saved API key. Please try again.")