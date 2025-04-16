import os
import platform
import keyring
import hashlib
import base64
import logging
from cryptography.fernet import Fernet


class Config:
    # 类级别的API配置
    API_ENDPOINT = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    TIMEOUT = 30
    MAX_WORKERS = 4

    # 密钥管理配置
    SERVICE_NAME = "FormulaProSecure"
    _fernet = None
    _instance = None

    # 添加默认保存路径
    @property
    def DEFAULT_SAVE_PATH(self):
        return os.path.expanduser("~/Documents/FormulaReports")

    def __init__(self):
        if Config._instance is not None:
            raise RuntimeError("Config is a singleton class")
        os.makedirs(self.DEFAULT_SAVE_PATH, exist_ok=True)
        self._load_encryption_key()
        self.API_KEY = ""  # 实例属性
        Config._instance = self

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_encryption_key(self):
        """生成/加载加密密钥"""
        try:
            # 使用机器ID和用户名生成唯一的加密密钥
            machine_id = platform.node().encode()
            username = os.getlogin().encode()
            key_base = hashlib.sha256(machine_id + username).digest()[:32]  # 必须是32字节
            self._fernet = Fernet(base64.urlsafe_b64encode(key_base))
            logging.info("Encryption key loaded successfully")
        except Exception as e:
            logging.error(f"Error generating encryption key: {str(e)}")
            raise

    @classmethod
    def get_saved_key(cls):
        """安全获取保存的密钥"""
        try:
            encrypted = keyring.get_password(cls.SERVICE_NAME, "encrypted_api_key")
            if encrypted:
                instance = cls.get_instance()
                decrypted = instance._fernet.decrypt(encrypted.encode()).decode()
                # 同时更新实例中的密钥
                instance.API_KEY = decrypted
                logging.info("Successfully retrieved saved API key")
                return decrypted
            logging.info("No saved API key found")
            return ""
        except Exception as e:
            logging.error(f"Error retrieving key: {str(e)}")
            return ""

    @classmethod
    def save_key(cls, key):
        """安全存储密钥"""
        try:
            instance = cls.get_instance()
            encrypted = instance._fernet.encrypt(key.encode()).decode()
            keyring.set_password(cls.SERVICE_NAME, "encrypted_api_key", encrypted)
            instance.API_KEY = key  # 更新实例中的密钥
            logging.info("API key saved successfully")
        except Exception as e:
            logging.error(f"Error saving key: {str(e)}")
            raise

    @classmethod
    def delete_saved_key(cls):
        """删除保存的密钥"""
        try:
            keyring.delete_password(cls.SERVICE_NAME, "encrypted_api_key")
            if cls._instance:
                cls._instance.API_KEY = ""
            logging.info("API key deleted successfully")
        except keyring.errors.PasswordDeleteError:
            logging.info("No saved key found to delete")
        except Exception as e:
            logging.error(f"Error deleting key: {str(e)}")
            raise

    @classmethod
    def set_api_key(cls, key):
        """设置API密钥"""
        instance = cls.get_instance()
        instance.API_KEY = key 