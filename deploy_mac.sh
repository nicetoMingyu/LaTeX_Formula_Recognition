#!/bin/bash
set -e

PROJECT="FormulaPro"
VENV="venv"
DIST_DIR="dist"

# 清理环境
rm -rf ${VENV} build ${DIST_DIR} *.spec
find . -name "__pycache__" -exec rm -rf {} \;

# 创建虚拟环境
python -m venv ${VENV}
source ${VENV}/bin/activate

# 安装依赖
pip install -U pip
pip install -r requirements.txt
pip install keyring==24.0.0 cryptography==42.0.5

# 生成spec文件
pyi-makespec \
    --name ${PROJECT} \
    --windowed \
    --add-data "config:config" \
    --add-data "src/core:core" \
    --add-data "src/gui:gui" \
    --add-data "${VENV}/lib/python*/site-packages/matplotlib/mpl-data/*:matplotlib/mpl-data" \
    --add-data "${VENV}/lib/python*/site-packages/cryptography:cryptography" \
    --add-data "${VENV}/lib/python*/site-packages/keyring:keyring" \
    --add-data "${VENV}/lib/python*/site-packages/matplotlib/mpl-data/fonts/ttf/*:matplotlib/mpl-data/fonts/ttf/"\
    --add-data "${VENV}/lib/python*/site-packages/matplotlib/mpl-data/fonts/ttf/*:fonts/"\
    --hidden-import keyring.backends.macOS \
    --hidden-import cryptography.hazmat.backends.openssl \
    --hidden-import cryptography.hazmat.primitives \
    --hidden-import "PyQt6.QtCore" \
    --hidden-import "PyQt6.QtWidgets" \
    --hidden-import "matplotlib.backends.backend_qtagg" \
    --osx-bundle-identifier "com.yourcompany.formulapro" \
    --icon "assets/icon.icns" \
    src/main.py

# 修改spec文件的正确方式
perl -i -pe '
    s/(hiddenimports=\[)/$1\n    "cryptography.hazmat.backends.openssl",\n    "cryptography.hazmat.primitives",/;
    s/(datas=\[)/$1\n    ("venv\/lib\/python*\/site-packages\/cryptography", "cryptography"),\n    ("venv\/lib\/python*\/site-packages\/keyring", "keyring"),/;
' FormulaPro.spec

# 构建应用
pyinstaller ${PROJECT}.spec --clean --noconfirm

# 修复Matplotlib路径
MATPLOTLIB_DATA=$(python -c "import matplotlib; print(matplotlib.get_data_path())")
mkdir -p dist/FormulaPro.app/Contents/Resources/matplotlib/mpl-data
cp -R "${MATPLOTLIB_DATA}"/* dist/FormulaPro.app/Contents/Resources/matplotlib/mpl-data

# 修复权限
find dist/${PROJECT}.app -type f -exec chmod 644 {} \;
find dist/${PROJECT}.app -type d -exec chmod 755 {} \;
chmod +x dist/${PROJECT}.app/Contents/MacOS/${PROJECT}

# 解除安全限制
xattr -cr dist/${PROJECT}.app

echo "Build successful: dist/${PROJECT}.app"

