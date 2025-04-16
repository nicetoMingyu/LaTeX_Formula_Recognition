# latex_renderer.py
import matplotlib.pyplot as plt
from io import BytesIO
import logging
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import os

# 禁用字体警告
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)


class LatexRenderer:
    def __init__(self):
        plt.style.use('default')
        plt.rcParams['font.sans-serif'] = ['Arial']
        plt.rcParams.update({
            'font.family': 'serif',  # 使用系统自带字体
            'mathtext.fontset': 'cm',  # 使用内置Computer Modern数学字体
            'figure.dpi': 600,  # 提高基础DPI
            'savefig.dpi': 600,
            'figure.autolayout': False,
            'axes.linewidth': 0.8,
            'lines.linewidth': 1.2,
            'mathtext.rm': 'serif',  # 明确配置数学字体
            'mathtext.cal': 'serif',
            'mathtext.it': 'serif:italic',
            'mathtext.bf': 'serif:bold',
        })
        self._precache_fonts()

    def _precache_fonts(self):
        """预加载数学符号字体"""
        test_formulas = [
            r'$\int_{a}^{b} f(x)\,dx$',
            r'$\sum_{n=1}^{\infty} \frac{1}{n^2}$',
            r'$\mathcal{F}(\omega)$'
        ]
        fig = plt.figure()
        for formula in test_formulas:
            fig.text(0.5, 0.5, formula, ha='center', va='center')
        plt.close(fig)

    def render_to_qpixmap(self, code):
        try:
            # 清理代码中的非法命令
            clean_code = self._clean_latex(code)

            # 创建高分辨率画布
            fig = plt.figure(
                figsize=(8, 2),  # 优化画布比例
                dpi=600,  # 最终渲染DPI
                facecolor='none',  # 透明背景
                edgecolor='none'
            )
            ax = fig.add_axes([0, 0, 1, 1])
            ax.axis("off")

            # 处理公式环境
            display_code = self._wrap_environment(code)

            # 渲染文本
            text = ax.text(
                0.5, 0.5,
                display_code,
                fontsize=36,  # 适当增大字号
                ha='center',
                va='center',
            )

            # 保存为高分辨率图像
            buf = BytesIO()
            plt.savefig(
                buf,
                format='png',
                bbox_inches='tight',
                pad_inches=0.1,  # 减少边距
                transparent=True,
                dpi=600,  # 保存DPI与画布一致
            )
            plt.close(fig)

            # 转换为QPixmap并保持高质量缩放
            pixmap = QPixmap()
            pixmap.loadFromData(buf.getvalue())
            return pixmap.scaled(
                1600, 400,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation  # 高质量缩放算法
            )
        except Exception as e:
            logging.error(f"Render Error: {str(e)}", exc_info=True)
            return QPixmap()

    def _wrap_environment(self, code):
        """自动添加合适的数学环境"""
        if any(code.startswith(p) for p in ("\\begin{equation}", "\\[")):
            return code
        return f"\\begin{{equation}}{code}\\end{{equation}}"

    def _clean_for_display(self, code):
        """清理用于显示的LaTeX代码"""
        replacements = {
            "\\begin{equation}": "",
            "\\end{equation}": "",
            "\\displaystyle": "",
            "\\boxed": "",
            "$$": ""
        }
        for k, v in replacements.items():
            code = code.replace(k, v)
        return code.strip()

    @staticmethod
    def _clean_latex(code):
        """移除Mathtext不支持的LaTeX命令"""
        replacements = {
            r'\displaystyle': '',
            r'\begin{equation}': '',
            r'\end{equation}': '',
            r'\boxed': ''
        }
        for key, value in replacements.items():
            code = code.replace(key, value)
        return code.strip()

    @staticmethod
    def _wrap_environment(code):
        env_prefixes = ("\\begin{", "\\[", "$$")
        if any(code.startswith(p) for p in env_prefixes):
            return code
        # 仅添加基本数学环境
        return f'${code}$' if not code.startswith('$') else code