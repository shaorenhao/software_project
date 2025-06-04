import json
import os
import time
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from api import LLMClient
from vector_db import FAISSVectorDB


class Worker(QThread):
    finished = pyqtSignal(dict, str)  # 返回响应和原始消息
    error = pyqtSignal(str)

    def __init__(self, client, message):
        super().__init__()
        self.client = client
        self.message = message

    def run(self):
        self.message = str(self.message)
        try:
            response = self.client.chat_completion([
                {"role": "user", "content": self.message}
            ])
            self.finished.emit(response, self.message)
        except Exception as e:
            self.error.emit(str(e))


class RequirementAgent():
    def __init__(self):
        self.llm_client = None
        self.vector_db = None
        self.load_config()

    def load_config(self):
        self.llm_client = LLMClient(api_key="sk-nnnbfontekeesozhffpmluqdajbwzqvxeskyevmxwfignhgh")
        # 初始化FAISS向量数据库
        self.vector_db = FAISSVectorDB("software_requirements")
        
        # 预加载需求分析知识（首次运行时）
        if self.vector_db.get_collection_stats()["doc_count"] == 0:
            self._initialize_knowledge_base()

    def _initialize_knowledge_base(self):
        """初始化需求分析知识库基础数据"""
        basic_concepts = [
            # 需求工程基础概念
            {
                "text": "功能需求(Functional Requirements)描述系统应该做什么，包括系统功能、输入输出、数据处理等。通常以'系统应该...'的形式表述。",
                "metadata": {"concept": "功能需求", "type": "需求类型", "category": "基础概念"}
            },
            {
                "text": "非功能需求(Non-functional Requirements)描述系统运行时的特性，如性能、安全性、可靠性等。通常以'系统应该能够...'的形式表述。",
                "metadata": {"concept": "非功能需求", "type": "需求类型", "category": "基础概念"}
            },
            {
                "text": "用户故事(User Story)是从用户角度描述需求的轻量级方法，格式为'作为[角色]，我想要[功能]，以便[价值]'。",
                "metadata": {"concept": "用户故事", "type": "需求方法", "category": "敏捷开发"}
            },
            
            # 需求分析方法
            {
                "text": "用例图(Use Case Diagram)展示系统与外部参与者的交互，包含参与者(Actors)、用例(Use Cases)和它们之间的关系。",
                "metadata": {"concept": "用例图", "type": "UML", "category": "建模技术"}
            },
            {
                "text": "用户故事地图(User Story Mapping)是将用户故事按用户活动和优先级组织的可视化技术，帮助理解整体功能和发布计划。",
                "metadata": {"concept": "用户故事地图", "type": "需求方法", "category": "敏捷开发"}
            },
            {
                "text": "MoSCoW优先级排序法将需求分为必须有(Must have)、应该有(Should have)、可以有(Could have)和不需要有(Won't have)四类。",
                "metadata": {"concept": "MoSCoW方法", "type": "需求方法", "category": "优先级排序"}
            },
            
            # 需求文档
            {
                "text": "软件需求规格说明书(SRS)是正式文档，详细描述系统功能、接口、性能等需求。通常包含引言、总体描述、具体需求等章节。",
                "metadata": {"concept": "SRS", "type": "需求文档", "category": "文档规范"}
            },
            {
                "text": "需求可追溯性矩阵(Requirements Traceability Matrix)跟踪需求从源头到实现的整个过程，确保所有需求都被满足。",
                "metadata": {"concept": "需求追溯", "type": "需求管理", "category": "质量保证"}
            },
            
            # 需求验证
            {
                "text": "需求评审(Requirements Review)是系统化检查需求文档的过程，目的是发现错误、不一致和遗漏。参与者包括开发、测试和业务代表。",
                "metadata": {"concept": "需求评审", "type": "需求验证", "category": "质量保证"}
            },
            {
                "text": "原型法(Prototyping)通过快速构建系统原型帮助用户理解需求，特别适用于用户需求不明确的情况。",
                "metadata": {"concept": "原型法", "type": "需求方法", "category": "用户参与"}
            },

            # Mermaid语法知识
            {
                "text": "Mermaid类图语法示例:\n```mermaid\nclassDiagram\n    class User {\n        +String name\n        +String email\n        +login()\n    }\n    class Admin {\n        +String privileges\n        +manageUsers()\n    }\n    User <|-- Admin\n```",
                "metadata": {"concept": "类图", "type": "Mermaid", "category": "图表语法"}
            },
            {
                "text": "Mermaid时序图语法示例:\n```mermaid\nsequenceDiagram\n    participant User\n    participant System\n    User->>System: 登录请求\n    System-->>User: 验证请求\n    User->>System: 提交凭证\n    System-->>User: 登录成功\n```",
                "metadata": {"concept": "时序图", "type": "Mermaid", "category": "图表语法"}
            },
            {
                "text": "Mermaid状态图语法示例:\n```mermaid\nstateDiagram-v2\n    [*] --> Idle\n    Idle --> Processing: 开始处理\n    Processing --> Success: 操作成功\n    Processing --> Error: 操作失败\n    Error --> Processing: 重试\n    Success --> [*]\n```",
                "metadata": {"concept": "状态图", "type": "Mermaid", "category": "图表语法"}
            },
            {
                "text": "Mermaid甘特图语法示例:\n```mermaid\ngantt\n    title 项目计划\n    dateFormat  YYYY-MM-DD\n    section 需求阶段\n    需求收集     :a1, 2023-01-01, 15d\n    需求分析     :after a1, 10d\n    section 开发阶段\n    系统设计     :2023-01-20, 20d\n    编码实现     :2023-02-10, 30d\n```",
                "metadata": {"concept": "甘特图", "type": "Mermaid", "category": "图表语法"}
            }
            
        ]
        self.vector_db.batch_insert(basic_concepts)

    def chat(self, messages):
        """与LLM对话，专注于需求分析"""
        if len(messages) > 0:
            last_message = messages[-1]['content']
            search_results = self.vector_db.search(last_message, top_k=3)
            
            if search_results:
                context = "\n\n相关需求分析参考:\n" + "\n".join(
                    f"{i+1}. {res['content']} (来源: {res['metadata'].get('concept', '未知')}"
                    for i, res in enumerate(search_results))
                
                # 将上下文添加到系统消息中
                if messages[0]['role'] == 'system':
                    messages[0]['content'] += context
        
        return self.llm_client.chat_completion(messages)