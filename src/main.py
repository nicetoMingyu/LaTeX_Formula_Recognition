import sys
import os
import logging
import platform
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
import keyring

def init_keyring():
    """初始化系统密钥环"""
    system = platform.system().lower()
    try:
        # 尝试使用系统密钥环
        if system == 'darwin':  # macOS
            from keyring.backends import macOS
            keyring.set_keyring(macos.Keyring())
        elif system == 'windows':
            from keyring.backends import Windows
            keyring.set_keyring(Windows.WinVaultKeyring())
        else:  # Linux 和其他系统
            from keyring.backends import SecretService
            keyring.set_keyring(SecretService.Keyring())
        logging.info(f"Successfully initialized keyring for {system}")
    except Exception as e:
        logging.error(f"Failed to initialize system keyring: {str(e)}")
        try:
            # 尝试使用文件系统作为后备方案
            from keyring.backends import plaintext
            keyring.set_keyring(plaintext.PlaintextKeyring())
            logging.info("Using plaintext keyring as fallback")
        except Exception as e:
            logging.error(f"Failed to initialize fallback keyring: {str(e)}")
            # 如果所有尝试都失败，使用默认密钥环
            logging.info("Using default keyring")

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def configure_app():
    # Configure logging
    logging.basicConfig(
        filename=resource_path('app.log'),
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # 初始化密钥环
    init_keyring()

    # Configure matplotlib
    import matplotlib
    from matplotlib import font_manager

    if getattr(sys, 'frozen', False):
        matplotlib.rcParams['backend'] = 'Agg'
        mpl_data_dir = resource_path('matplotlib/mpl-data')
        os.environ['MATPLOTLIBDATA'] = mpl_data_dir
        font_manager._load_fontmanager(try_read_cache=False)

    app = QApplication(sys.argv)

    # Load stylesheet
    style_path = resource_path('config/style.qss')
    if os.path.exists(style_path):
        with open(style_path, "r") as f:
            app.setStyleSheet(f.read())

    return app


if __name__ == "__main__":
    sys.excepthook = lambda exc_type, exc_value, exc_tb: logging.critical(
        "Unhandled exception", exc_info=(exc_type, exc_value, exc_tb)
    )

    app = configure_app()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())