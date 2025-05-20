import json
import os
import time
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from api import LLMClient

class Worker(QThread):
    finished = pyqtSignal(dict, str)  # 返回响应和原始消息
    error = pyqtSignal(str)

    def __init__(self, client, message):
        super().__init__()
        self.client = client
        self.message = message

    def run(self):
        self.message=str(self.message)
        try:
            response = self.client.chat_completion([
                {"role": "user", "content": self.message}
            ])
            self.finished.emit(response, self.message)
        except Exception as e:
            self.error.emit(str(e))

class ConceptAgent():
    def __init__(self):

        self.llm_client = None
        self.load_config()

    def load_config(self):
        self.llm_client = LLMClient(api_key="sk-nnnbfontekeesozhffpmluqdajbwzqvxeskyevmxwfignhgh")

    def chat(self, message):
        return self.llm_client.chat_completion(message)