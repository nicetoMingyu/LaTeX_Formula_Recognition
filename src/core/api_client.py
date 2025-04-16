# api_client.py
import base64
import logging
from openai import OpenAI
from config.settings import Config
import time
from typing import List, Dict, Any

class APIClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=Config.get_instance().API_KEY,
            base_url=Config.API_ENDPOINT,
            timeout=Config.TIMEOUT
        )
        self.logger = logging.getLogger("api_client")
        self.retry_count = 3
        self.model = "qwen-vl-max"

    def recognize_formula(self, image_path):
        for attempt in range(self.retry_count):
            try:
                with open(image_path, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode()

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Convert math formula to LaTeX"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_data}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }],
                    timeout=Config.TIMEOUT  # 使用实例属性
                )
                return self._parse_response(response.choices[0].message.content)
            except Exception as e:
                self.logger.error(f"API Error (attempt {attempt+1}): {str(e)}")
                if attempt == self.retry_count - 1:
                    raise
                time.sleep(1)
        return ""

    @staticmethod
    def _parse_response(response_text):
        try:
            if "```latex" in response_text:
                start = response_text.index("```latex") + len("```latex\n")
                end = response_text.index("\n```", start)
                return response_text[start:end].strip()
            return response_text.strip('$')
        except ValueError:
            return response_text.strip('$')