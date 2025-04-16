import fitz  # PyMuPDF
import cv2
import numpy as np
import logging
import re
from typing import List, Tuple, Union, Optional
from PIL import Image, ImageDraw, ImageFont

class PDFParser:
    def __init__(self):
        self.formulas = []
        self.logger = logging.getLogger(__name__)
        # 定义数学公式的特征模式
        self.formula_patterns = [
            # 行内公式
            r'\$[^$]+\$',
            r'\\\([^)]+\\\)',
            r'\\\[[^\]]+\\\]',
            
            # 数学环境
            r'\\begin\{equation\}.*?\\end\{equation\}',
            r'\\begin\{align\}.*?\\end\{align\}',
            r'\\begin\{gather\}.*?\\end\{gather\}',
            r'\\begin\{math\}.*?\\end\{math\}',
            r'\\begin\{displaymath\}.*?\\end\{displaymath\}',
            r'\\begin\{array\}.*?\\end\{array\}',
            r'\\begin\{matrix\}.*?\\end\{matrix\}',
            r'\\begin\{bmatrix\}.*?\\end\{bmatrix\}',
            r'\\begin\{pmatrix\}.*?\\end\{pmatrix\}',
            r'\\begin\{vmatrix\}.*?\\end\{vmatrix\}',
            r'\\begin\{cases\}.*?\\end\{cases\}',
            r'\\begin\{split\}.*?\\end\{split\}',
            r'\\begin\{multline\}.*?\\end\{multline\}',
            
            # 数学函数和符号
            r'\\frac\{.*?\}\{.*?\}',
            r'\\sum_\{.*?\}\^\{.*?\}',
            r'\\int_\{.*?\}\^\{.*?\}',
            r'\\lim_\{.*?\}',
            r'\\sqrt\{.*?\}',
            r'\\left.*?\\right',
            r'\\bigl.*?\\bigr',
            r'\\Bigl.*?\\Bigr',
            r'\\biggl.*?\\biggr',
            r'\\Biggl.*?\\Biggr',
            r'\\langle.*?\\rangle',
            r'\\lceil.*?\\rceil',
            r'\\lfloor.*?\\rfloor',
            r'\\|.*?\\|',
            r'\\|.*?\\|',
            r'\\vert.*?\\vert',
            r'\\Vert.*?\\Vert',
            r'\\lbrace.*?\\rbrace',
            r'\\lgroup.*?\\rgroup',
            r'\\lmoustache.*?\\rmoustache',
            r'\\ulcorner.*?\\urcorner',
            r'\\llcorner.*?\\lrcorner',
            
            # 数学运算符
            r'\\pm',
            r'\\mp',
            r'\\times',
            r'\\div',
            r'\\cdot',
            r'\\ast',
            r'\\star',
            r'\\dagger',
            r'\\ddagger',
            r'\\amalg',
            r'\\cap',
            r'\\cup',
            r'\\uplus',
            r'\\sqcap',
            r'\\sqcup',
            r'\\vee',
            r'\\wedge',
            r'\\setminus',
            r'\\wr',
            r'\\diamond',
            r'\\bigtriangleup',
            r'\\bigtriangledown',
            r'\\triangleleft',
            r'\\triangleright',
            r'\\lhd',
            r'\\rhd',
            r'\\unlhd',
            r'\\unrhd',
            r'\\oplus',
            r'\\ominus',
            r'\\otimes',
            r'\\oslash',
            r'\\odot',
            r'\\bigcirc',
            r'\\dagger',
            r'\\ddagger',
            r'\\amalg',
            
            # 数学关系符
            r'\\leq',
            r'\\geq',
            r'\\equiv',
            r'\\models',
            r'\\prec',
            r'\\succ',
            r'\\sim',
            r'\\perp',
            r'\\preceq',
            r'\\succeq',
            r'\\simeq',
            r'\\mid',
            r'\\ll',
            r'\\gg',
            r'\\asymp',
            r'\\parallel',
            r'\\subset',
            r'\\supset',
            r'\\approx',
            r'\\bowtie',
            r'\\subseteq',
            r'\\supseteq',
            r'\\cong',
            r'\\sqsubset',
            r'\\sqsupset',
            r'\\Join',
            r'\\sqsubseteq',
            r'\\sqsupseteq',
            r'\\doteq',
            r'\\in',
            r'\\ni',
            r'\\propto',
            r'\\vdash',
            r'\\dashv',
            
            # 箭头
            r'\\leftarrow',
            r'\\rightarrow',
            r'\\leftrightarrow',
            r'\\Leftarrow',
            r'\\Rightarrow',
            r'\\Leftrightarrow',
            r'\\mapsto',
            r'\\hookleftarrow',
            r'\\hookrightarrow',
            r'\\leftharpoonup',
            r'\\rightharpoonup',
            r'\\leftharpoondown',
            r'\\rightharpoondown',
            r'\\rightleftharpoons',
            r'\\curvearrowleft',
            r'\\curvearrowright',
            r'\\circlearrowleft',
            r'\\circlearrowright',
            r'\\multimap',
            r'\\boxtimes',
            r'\\boxplus',
            r'\\triangleq',
            r'\\circeq',
            r'\\doteqdot',
            r'\\risingdotseq',
            r'\\fallingdotseq',
            r'\\eqcirc',
            r'\\cirsim',
            r'\\backsimeq',
            r'\\thicksim',
            r'\\thickapprox',
            r'\\approxeq',
            r'\\bumpeq',
            r'\\Bumpeq',
            r'\\eqsim',
            r'\\simeq',
            r'\\backepsilon',
            r'\\models',
            r'\\vDash',
            r'\\Vdash',
            r'\\Vvdash',
            r'\\VDash',
            r'\\nvdash',
            r'\\nvDash',
            r'\\nVdash',
            r'\\nVDash',
            r'\\ulcorner',
            r'\\urcorner',
            r'\\llcorner',
            r'\\lrcorner',
        ]

    def extract_formulas(self, pdf_path: str) -> List[Tuple[np.ndarray, Tuple[float, float, float, float], float]]:
        """Extract formulas from PDF file"""
        try:
            doc = fitz.open(pdf_path)
            formulas = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # 1. 提取文本形式的数学公式
                text_blocks = page.get_text("blocks")
                for block in text_blocks:
                    if block[6] == 0:  # 文本块
                        text = block[4]
                        # 检查是否包含数学公式
                        if self._is_text_formula(text):
                            # 获取文本块的位置
                            x0, y0, x1, y1 = block[:4]
                            # 将文本转换为图片
                            img = self._text_to_image(text, page, (x0, y0, x1, y1))
                            if img is not None:
                                # 计算文本公式的置信度
                                confidence = self._calculate_text_formula_confidence(text)
                                formulas.append((img, (x0, y0, x1, y1), confidence))
                
                # 2. 提取图片形式的数学公式
                image_list = page.get_images()
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    # 将图片转换为numpy数组
                    nparray = np.frombuffer(image_bytes, np.uint8)
                    img_array = cv2.imdecode(nparray, cv2.IMREAD_COLOR)
                    
                    # 检查是否为彩色图片
                    if self._is_color_image(img_array):
                        continue
                        
                    # 检查是否为数学公式
                    is_formula, confidence = self._is_formula(img_array)
                    if is_formula:
                        # 获取图片位置
                        rect = page.get_image_bbox(img)
                        if rect:
                            x0, y0, x1, y1 = rect
                            formulas.append((img_array, (x0, y0, x1, y1), confidence))
            
            doc.close()
            return formulas
            
        except Exception as e:
            self.logger.error(f"Error extracting formulas from PDF: {str(e)}")
            return []
            
    def _is_color_image(self, img: np.ndarray) -> bool:
        """Check if image is color image"""
        try:
            # 转换为灰度图
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 计算颜色通道的差异
            b, g, r = cv2.split(img)
            diff_bg = cv2.absdiff(b, g)
            diff_br = cv2.absdiff(b, r)
            diff_gr = cv2.absdiff(g, r)
            
            # 如果颜色通道差异大于阈值，认为是彩色图片
            threshold = 10
            if np.mean(diff_bg) > threshold or np.mean(diff_br) > threshold or np.mean(diff_gr) > threshold:
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking color image: {str(e)}")
            return True  # 如果出错，保守处理，认为是彩色图片
            
    def _text_to_image(self, text: str, page: fitz.Page, rect: Tuple[float, float, float, float]) -> Optional[np.ndarray]:
        """Convert text to image"""
        try:
            # 创建一个白色背景的图片
            width = int(rect[2] - rect[0])
            height = int(rect[3] - rect[1])
            img = np.ones((height, width, 3), dtype=np.uint8) * 255
            
            # 使用PIL绘制文本
            pil_img = Image.fromarray(img)
            draw = ImageDraw.Draw(pil_img)
            
            # 设置字体和大小
            font_size = int(height * 0.8)  # 使用80%的高度作为字体大小
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # 绘制文本
            draw.text((0, 0), text, font=font, fill=(0, 0, 0))
            
            # 转换回numpy数组
            return np.array(pil_img)
            
        except Exception as e:
            self.logger.error(f"Error converting text to image: {str(e)}")
            return None
            
    def _is_text_formula(self, text: str) -> bool:
        """Check if text is a mathematical formula"""
        try:
            # 1. 检查是否包含数学符号
            math_symbols = r'[α-ωΑ-Ω∑∫∏√∞±×÷≠≤≥∈∉⊂⊃∪∩]'
            if re.search(math_symbols, text):
                return True
                
            # 2. 检查是否包含LaTeX命令
            latex_commands = r'\\[a-zA-Z]+'
            if re.search(latex_commands, text):
                return True
                
            # 3. 检查是否包含数学运算符
            operators = r'[+\-*/=<>]'
            if re.search(operators, text):
                return True
                
            # 4. 检查是否包含数学函数
            math_functions = r'\\sin|\\cos|\\tan|\\log|\\ln|\\exp|\\lim|\\sum|\\int|\\prod|\\oint|\\iint|\\iiint|\\iiiint|\\idotsint'
            if re.search(math_functions, text):
                return True
                
            # 5. 检查是否包含上下标
            subscripts = r'_[^}]+'
            superscripts = r'\^[^}]+'
            if re.search(subscripts, text) or re.search(superscripts, text):
                return True
                
            # 6. 检查是否包含数学括号
            brackets = r'\\left|\\right|\\bigl|\\bigr|\\Bigl|\\Bigr|\\biggl|\\biggr|\\Biggl|\\Biggr'
            if re.search(brackets, text):
                return True
                
            # 7. 检查是否包含数学箭头
            arrows = r'\\rightarrow|\\leftarrow|\\leftrightarrow|\\Rightarrow|\\Leftarrow|\\Leftrightarrow'
            if re.search(arrows, text):
                return True
                
            # 8. 检查是否包含数学环境
            environments = r'\\begin\{.*?\}.*?\\end\{.*?\}'
            if re.search(environments, text):
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking text formula: {str(e)}")
            return False

    def _is_formula(self, image: np.ndarray) -> Tuple[bool, float]:
        """Check if image is a mathematical formula"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate feature scores
            scores = []
            
            # 1. White pixel ratio score (formulas usually have black text on white background)
            white_ratio = np.sum(gray > 240) / gray.size
            white_score = min(white_ratio * 1.0, 1.0)  # 进一步降低白色像素比例要求
            scores.append(white_score)
            self.logger.debug(f"White pixel ratio score: {white_score:.2f} (ratio: {white_ratio:.2f})")
            
            # 2. Aspect ratio score (formulas usually have reasonable height/width ratio)
            height, width = gray.shape
            aspect_ratio = height / width
            aspect_score = 1.0 - min(abs(aspect_ratio - 1.0), 1.0)  # 进一步调整比例范围
            scores.append(aspect_score)
            self.logger.debug(f"Aspect ratio score: {aspect_score:.2f} (ratio: {aspect_ratio:.2f})")
            
            # 3. Connected components score (formulas usually have multiple small characters)
            _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contour_count = len(contours)
            contour_score = min(contour_count / 6, 1.0)  # 进一步降低连通区域要求
            scores.append(contour_score)
            self.logger.debug(f"Connected components score: {contour_score:.2f} (found {contour_count} components)")
            
            # 4. Edge detection score (formulas usually have many vertical and horizontal edges)
            edges = cv2.Canny(gray, 100, 200)
            edge_ratio = np.sum(edges > 0) / edges.size
            edge_score = min(edge_ratio * 4, 1.0)  # 进一步降低边缘检测要求
            scores.append(edge_score)
            self.logger.debug(f"Edge detection score: {edge_score:.2f} (ratio: {edge_ratio:.2f})")
            
            # Calculate confidence score
            confidence = np.mean(scores)
            self.logger.debug(f"Final image confidence score: {confidence:.2f}")
            
            # Return whether it's a formula and the confidence
            return confidence > 0.3, confidence  # 进一步降低图片公式的置信度阈值
            
        except Exception as e:
            self.logger.error(f"Error in formula detection: {str(e)}")
            return False, 0.0

    def _calculate_text_formula_confidence(self, text: str) -> float:
        """Calculate confidence score for text formula"""
        try:
            scores = []
            
            # 1. 检查是否包含数学符号
            math_symbols = r'[α-ωΑ-Ω∑∫∏√∞±×÷≠≤≥∈∉⊂⊃∪∩]'
            symbol_count = len(re.findall(math_symbols, text))
            symbol_score = min(symbol_count / 1.2, 1.0)
            scores.append(symbol_score)
            
            # 2. 检查是否包含LaTeX命令
            latex_commands = r'\\[a-zA-Z]+'
            command_count = len(re.findall(latex_commands, text))
            command_score = min(command_count / 1.0, 1.0)
            scores.append(command_score)
            
            # 3. 检查是否包含数学运算符
            operators = r'[+\-*/=<>]'
            operator_count = len(re.findall(operators, text))
            operator_score = min(operator_count / 1.0, 1.0)
            scores.append(operator_score)
            
            # 4. 检查是否包含数学函数
            math_functions = r'\\sin|\\cos|\\tan|\\log|\\ln|\\exp|\\lim|\\sum|\\int|\\prod|\\oint|\\iint|\\iiint|\\iiiint|\\idotsint'
            func_count = len(re.findall(math_functions, text))
            func_score = min(func_count / 1.2, 1.0)
            scores.append(func_score)
            
            # 5. 检查是否包含上下标
            subscripts = r'_[^}]+'
            superscripts = r'\^[^}]+'
            sub_count = len(re.findall(subscripts, text))
            sup_count = len(re.findall(superscripts, text))
            sub_sup_score = min((sub_count + sup_count) / 1.5, 1.0)
            scores.append(sub_sup_score)
            
            # 6. 检查是否包含数学括号
            brackets = r'\\left|\\right|\\bigl|\\bigr|\\Bigl|\\Bigr|\\biggl|\\biggr|\\Biggl|\\Biggr'
            bracket_count = len(re.findall(brackets, text))
            bracket_score = min(bracket_count / 1.5, 1.0)
            scores.append(bracket_score)
            
            # 7. 检查是否包含数学箭头
            arrows = r'\\rightarrow|\\leftarrow|\\leftrightarrow|\\Rightarrow|\\Leftarrow|\\Leftrightarrow'
            arrow_count = len(re.findall(arrows, text))
            arrow_score = min(arrow_count / 1.5, 1.0)
            scores.append(arrow_score)
            
            # 8. 检查是否包含数学环境
            environments = r'\\begin\{.*?\}.*?\\end\{.*?\}'
            env_score = 1.0 if re.search(environments, text) else 0.0
            scores.append(env_score)
            
            # 计算最终得分
            return np.mean(scores)
            
        except Exception as e:
            self.logger.error(f"Error calculating text formula confidence: {str(e)}")
            return 0.0 