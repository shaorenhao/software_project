import requests
import json
from typing import Dict, Optional

class LLMClient:
    def __init__(self, api_key: str, base_url: str = "https://api.siliconflow.cn/v1"):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.timeout = 30  # 设置30秒超时
    
    def chat_completion(self, messages: list, model: str = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B", **kwargs) -> Optional[Dict]:
        """与LLM进行交互"""
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "max_tokens": 8192,
            "temperature": 0.7,
            **kwargs
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API请求出错: {e}")
            raise  # 重新抛出异常以便在worker线程中捕获

# 示例用法
if __name__ == "__main__":
    client = LLMClient(api_key="sk-nnnbfontekeesozhffpmluqdajbwzqvxeskyevmxwfignhgh")
    response = client.chat_completion([
        {"role": "user", "content": "你好，你是谁？"}
    ])
    print(response)