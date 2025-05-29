import json
import os
import time
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from api import LLMClient
from vector_db import FAISSVectorDB  # 修改导入


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
        self.vector_db = None
        self.load_config()

    def load_config(self):
        self.llm_client = LLMClient(api_key="sk-nnnbfontekeesozhffpmluqdajbwzqvxeskyevmxwfignhgh")
        # 初始化FAISS向量数据库
        self.vector_db = FAISSVectorDB("software_concepts")
        
        # 预加载基础概念知识（首次运行时）
        if self.vector_db.get_collection_stats()["doc_count"] == 0 :
            self._initialize_knowledge_base()

    def _initialize_knowledge_base(self):
        """初始化知识库基础数据"""
        basic_concepts = [
            {
                "text": "多态是面向对象编程的三大特性之一，指同一操作作用于不同对象可以有不同的解释和不同的执行结果",
                "metadata": {"concept": "多态", "type": "OOP", "category": "基础概念"}
            },
            {
                "text": "封装是将数据和操作数据的方法绑定在一起，对外隐藏实现细节，只暴露必要接口的特性",
                "metadata": {"concept": "封装", "type": "OOP", "category": "基础概念"}
            },
            {
                "text": "DABB是Data Address Basic Block",
                "metadata": {"concept": "DABB", "type": "Test", "category": "基础概念"}
            },
        ]
        self.vector_db.batch_insert(basic_concepts)

    def chat(self, messages, use_rag=False):
        """与LLM对话，支持检索增强生成"""
        if use_rag and len(messages) > 0:
            last_message = messages[-1]['content']
            search_results = self.vector_db.search(last_message, top_k=3)
            
            if search_results:
                context = "\n\n相关概念参考:\n" + "\n".join(
                    f"{i+1}. {res['content']} (来源: {res['metadata'].get('concept', '未知')})"
                    for i, res in enumerate(search_results))
                
                # 将上下文添加到系统消息中
                if messages[0]['role'] == 'system':
                    messages[0]['content'] += context
        
        return self.llm_client.chat_completion(messages)