# settings.py
import os
import platform
import keyring
import hashlib
import base64
from cryptography.fernet import Fernet


class Config:
    # 类级别的API配置
    API_ENDPOINT = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    TIMEOUT = 30
    MAX_WORKERS = 4

    # 密钥管理配置
    SERVICE_NAME = "FormulaProSecure"
    _fernet = None

    # 添加默认保存路径
    @property
    def DEFAULT_SAVE_PATH(self):
        return os.path.expanduser("~/Documents/FormulaReports")

    def __init__(self):
        os.makedirs(self.DEFAULT_SAVE_PATH, exist_ok=True)
        self._load_encryption_key()
        self.API_KEY = ""  # 实例属性

    def _load_encryption_key(self):
        """生成/加载加密密钥"""
        machine_id = platform.node().encode()
        key_base = hashlib.sha256(machine_id).digest()[:35]
        self._fernet = Fernet(base64.urlsafe_b64encode(key_base))

    @classmethod
    def get_saved_key(cls):
        """安全获取保存的密钥"""
        try:
            encrypted = keyring.get_password(cls.SERVICE_NAME, "encrypted_api_key")
            if encrypted:
                return cls()._fernet.decrypt(encrypted.encode()).decode()
            return ""
        except Exception as e:
            print(f"Error retrieving key: {str(e)}")
            return ""

    @classmethod
    def save_key(cls, key):
        """安全存储密钥"""
        try:
            encrypted = cls()._fernet.encrypt(key.encode()).decode()
            keyring.set_password(cls.SERVICE_NAME, "encrypted_api_key", encrypted)
        except Exception as e:
            print(f"Error saving key: {str(e)}")

    @classmethod
    def delete_saved_key(cls):
        """删除保存的密钥"""
        try:
            keyring.delete_password(cls.SERVICE_NAME, "encrypted_api_key")
        except keyring.errors.PasswordDeleteError:
            pass

    def set_api_key(self, key):
        """设置当前会话密钥"""
        if len(key) != 35 or not key.startswith("sk-"):
            raise ValueError("API key must start with 'sk-' and be 32 characters long")
        self.API_KEY = key


# 单例配置实例（确保全局唯一）
config = Config()