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

class DesignAgent():
    def __init__(self):
        self.llm_client = None
        self.vector_db = None
        self.load_config()

    def load_config(self):
        self.llm_client = LLMClient(api_key="sk-nnnbfontekeesozhffpmluqdajbwzqvxeskyevmxwfignhgh")
        self.vector_db = FAISSVectorDB("software_design")
        
        if self.vector_db.get_collection_stats()["doc_count"] == 0:
            self._initialize_knowledge_base()

    def _initialize_knowledge_base(self):
        """初始化设计知识库基础数据"""
        design_concepts = [
            {
                "text": "类图(Class Diagram)展示类的结构、属性和方法，以及它们之间的关系。Mermaid 语法:\n```mermaid\nclassDiagram\n    class User {\n        +String name\n        +int age\n        +login()\n    }\n    class System {\n        +User user\n        +authenticate()\n    }\n    User --> System: uses\n```",
                "metadata": {"concept": "类图", "type": "UML", "category": "设计图表"}
            },
            {
                "text": "时序图(Sequence Diagram)展示对象之间按时间顺序的交互。Mermaid 语法:\n```mermaid\nsequenceDiagram\n    participant User\n    participant Server\n    User->>Server: login(username, password)\n    Server-->>User: return token\n```",
                "metadata": {"concept": "时序图", "type": "UML", "category": "设计图表"}
            },
            {
                "text": "组件图(Component Diagram)用于描述系统的组件及其之间的依赖关系。Mermaid 语法:\n```mermaid\ngraph TD\n    componentA[UserService] --> componentB[AuthService]\n    componentA --> componentC[DatabaseService]\n```",
                "metadata": {"concept": "组件图", "type": "UML", "category": "设计图表"}
            },
            {
                "text": "状态图(State Diagram)表示对象在生命周期中的状态转移。Mermaid 语法:\n```mermaid\nstateDiagram-v2\n    [*] --> Idle\n    Idle --> Processing: start\n    Processing --> Completed: finish\n    Completed --> [*]\n```",
                "metadata": {"concept": "状态图", "type": "UML", "category": "设计图表"}
            },
            {
                "text": "用例图(Use Case Diagram)展示用户与系统的交互。Mermaid 语法（使用类图模拟）：\n```mermaid\nclassDiagram\n    class User\n    class System\n    class UseCase1\n    class UseCase2\n    User --> UseCase1: initiate\n    User --> UseCase2\n    UseCase1 --> System\n    UseCase2 --> System\n```",
                "metadata": {"concept": "用例图", "type": "UML", "category": "设计图表"}
            },
            {
                "text": "活动图(Activity Diagram)描述活动流程与决策。Mermaid 语法:\n```mermaid\nflowchart TD\n    Start --> Login\n    Login -->|Success| Dashboard\n    Login -->|Fail| ErrorPage\n```",
                "metadata": {"concept": "活动图", "type": "UML", "category": "设计图表"}
            },
            {
                "text": "部署图(Deployment Diagram)展示系统的部署结构。Mermaid 语法（使用图结构近似）：\n```mermaid\ngraph TD\n    Client --> WebServer\n    WebServer --> AppServer\n    AppServer --> Database\n```",
                "metadata": {"concept": "部署图", "type": "UML", "category": "设计图表"}
            },
            {
                "text": "对象图(Object Diagram)表示某一时刻的对象及其关系（使用类图表示静态关系）。Mermaid 示例:\n```mermaid\nclassDiagram\n    class Order {\n        +id: int\n        +total: float\n    }\n    class Customer {\n        +name: string\n    }\n    Customer --> Order: places\n```",
                "metadata": {"concept": "对象图", "type": "UML", "category": "设计图表"}
            },
            {
                "text": "流程图(Flowchart)用于展示业务流程和控制流。Mermaid 语法:\n```mermaid\nflowchart TD\n    A[开始] --> B{是否登录}\n    B -->|是| C[进入主页]\n    B -->|否| D[跳转登录页]\n    C --> E[完成操作]\n    D --> E\n```",
                "metadata": {"concept": "流程图", "type": "流程建模", "category": "设计图表"}
            },
            {
                "text": "甘特图(Gantt Chart)用于展示项目任务与进度。Mermaid 语法:\n```mermaid\ngantt\n    title 项目开发进度\n    dateFormat  YYYY-MM-DD\n    section 需求分析\n    任务1 :a1, 2025-06-01, 5d\n    section 设计阶段\n    系统设计 :a2, after a1, 3d\n    接口设计 :a3, after a2, 4d\n```",
                "metadata": {"concept": "甘特图", "type": "项目管理", "category": "设计图表"}
            }
        ]


        self.vector_db.batch_insert(design_concepts)

    def chat(self, messages, design_type="总体", diagram_type=None):
        """与LLM对话，专注于软件设计"""
        if len(messages) > 0:
            last_message = messages[-1]['content']
            search_results = self.vector_db.search(last_message, top_k=1)
            
            if search_results:
                context = "\n\n相关设计参考:\n" + "\n".join(
                    f"{i+1}. {res['content']} (来源: {res['metadata'].get('concept', '未知')}"
                    for i, res in enumerate(search_results))
                
                if messages[0]['role'] == 'system':
                    messages[0]['content'] += context
        
        # 添加设计类型和图表类型提示
        if diagram_type:
            prompt = f"请提供{design_type}设计，并生成{diagram_type}图表，使用正确的Mermaid语法。"
            if messages[0]['role'] == 'system':
                messages[0]['content'] += "\n" + prompt
            else:
                messages.insert(0, {"role": "system", "content": prompt})
        
        return self.llm_client.chat_completion(messages)