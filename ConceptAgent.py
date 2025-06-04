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
        # 面向对象编程概念
        {
            "text": "多态(Polymorphism)是面向对象编程的三大特性之一，指同一操作作用于不同对象可以有不同的解释和不同的执行结果。主要包括编译时多态(重载)和运行时多态(重写)。",
            "metadata": {"concept": "多态", "type": "OOP", "category": "基础概念"}
        },
        {
            "text": "封装(Encapsulation)是将数据和操作数据的方法绑定在一起，对外隐藏实现细节，只暴露必要接口的特性。通过访问修饰符(public/private/protected)实现。",
            "metadata": {"concept": "封装", "type": "OOP", "category": "基础概念"}
        },
        {
            "text": "继承(Inheritance)允许子类继承父类的属性和方法，实现代码复用和层次分类。支持单继承和多继承(视语言而定)。",
            "metadata": {"concept": "继承", "type": "OOP", "category": "基础概念"}
        },
        {
            "text": "抽象(Abstraction)是通过提取共同特征而忽略非本质细节来简化复杂系统的过程。抽象类和接口是实现抽象的主要方式。",
            "metadata": {"concept": "抽象", "type": "OOP", "category": "基础概念"}
        },
        
        # 设计模式
        {
            "text": "单例模式(Singleton)确保一个类只有一个实例，并提供一个全局访问点。常用于配置管理、连接池等场景。",
            "metadata": {"concept": "单例模式", "type": "设计模式", "category": "创建型模式"}
        },
        {
            "text": "工厂模式(Factory)定义一个创建对象的接口，但让子类决定实例化哪个类。将对象创建与使用分离，提高灵活性。",
            "metadata": {"concept": "工厂模式", "type": "设计模式", "category": "创建型模式"}
        },
        {
            "text": "观察者模式(Observer)定义对象间的一对多依赖关系，当一个对象状态改变时，所有依赖它的对象都会得到通知并自动更新。",
            "metadata": {"concept": "观察者模式", "type": "设计模式", "category": "行为型模式"}
        },
        {
            "text": "策略模式(Strategy)定义一系列算法，封装每个算法，并使它们可以互相替换。让算法独立于使用它的客户而变化。",
            "metadata": {"concept": "策略模式", "type": "设计模式", "category": "行为型模式"}
        },
        
        # 软件开发生命周期
        {
            "text": "敏捷开发(Agile)是一种以人为核心、迭代、循序渐进的开发方法。强调快速响应变化、持续交付可工作软件和紧密的团队协作。",
            "metadata": {"concept": "敏捷开发", "type": "方法论", "category": "开发流程"}
        },
        {
            "text": "Scrum是敏捷开发框架，包含角色(Product Owner, Scrum Master, Dev Team)、工件(Product Backlog, Sprint Backlog)和事件(Sprint, Daily Standup)。",
            "metadata": {"concept": "Scrum", "type": "方法论", "category": "开发流程"}
        },
        {
            "text": "持续集成(CI)是指开发人员频繁地(每天多次)将代码集成到共享主干，通过自动化构建和测试快速发现集成错误。",
            "metadata": {"concept": "持续集成", "type": "DevOps", "category": "开发流程"}
        },
        {
            "text": "持续交付(CD)是在持续集成基础上，确保代码可以随时安全地部署到生产环境，通常通过自动化部署流水线实现。",
            "metadata": {"concept": "持续交付", "type": "DevOps", "category": "开发流程"}
        },
        
        # 软件架构
        {
            "text": "MVC(Model-View-Controller)是一种架构模式，将应用分为模型(数据)、视图(UI)和控制器(逻辑)三层，实现关注点分离。",
            "metadata": {"concept": "MVC", "type": "架构", "category": "设计模式"}
        },
        {
            "text": "微服务架构(Microservices)是将单一应用划分为一组小型服务的风格，每个服务运行在自己的进程中，通过轻量级机制通信。",
            "metadata": {"concept": "微服务", "type": "架构", "category": "系统设计"}
        },
        {
            "text": "REST(Representational State Transfer)是一种基于HTTP协议的架构风格，使用标准方法(GET/POST/PUT/DELETE)操作资源。",
            "metadata": {"concept": "REST", "type": "架构", "category": "API设计"}
        },
        
        # 测试相关
        {
            "text": "单元测试(Unit Test)是针对软件最小可测试单元的测试，通常针对函数或方法。目标是隔离每个部分并验证其正确性。",
            "metadata": {"concept": "单元测试", "type": "测试", "category": "质量保证"}
        },
        {
            "text": "测试驱动开发(TDD)要求在编写功能代码前先写测试代码，然后只编写使测试通过的功能代码，最后重构。遵循红-绿-重构循环。",
            "metadata": {"concept": "TDD", "type": "方法论", "category": "开发流程"}
        },

        # 数据结构与算法
        {
            "text": "时间复杂度(Time Complexity)表示算法执行时间随输入规模增长的变化趋势，常用大O记号表示，如O(1), O(n), O(n²)等。",
            "metadata": {"concept": "时间复杂度", "type": "算法", "category": "基础概念"}
        },
        {
            "text": "哈希表(Hash Table)通过哈希函数将键映射到存储位置的数据结构，理想情况下提供O(1)的查找、插入和删除操作。",
            "metadata": {"concept": "哈希表", "type": "数据结构", "category": "基础概念"}
        },
        
        # 编程原则
        {
            "text": "SOLID原则包含五个面向对象设计原则：单一职责(SRP)、开闭原则(OCP)、里氏替换(LSP)、接口隔离(ISP)和依赖倒置(DIP)。",
            "metadata": {"concept": "SOLID原则", "type": "OOP", "category": "设计原则"}
        },
        {
            "text": "DRY(Don't Repeat Yourself)原则强调避免代码重复，通过抽象和复用提高可维护性。",
            "metadata": {"concept": "DRY原则", "type": "编程", "category": "最佳实践"}
        },
        {
            "text": "KISS(Keep It Simple, Stupid)原则提倡简单设计，避免不必要的复杂性。",
            "metadata": {"concept": "KISS原则", "type": "编程", "category": "最佳实践"}
        }
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