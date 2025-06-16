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
        # ================== 面向对象编程概念 ==================
        {
            "text": "多态(Polymorphism)是面向对象编程的三大特性之一，指同一操作作用于不同对象可以有不同的解释和不同的执行结果。主要包括编译时多态(重载)和运行时多态(重写)。应用场景：接口设计、插件系统、算法策略选择等。",
            "metadata": {"concept": "多态", "type": "OOP", "category": "基础概念"}
        },
        {
            "text": "封装(Encapsulation)是将数据和操作数据的方法绑定在一起，对外隐藏实现细节，只暴露必要接口的特性。通过访问修饰符(public/private/protected)实现。应用场景：模块设计、API设计、数据保护等。",
            "metadata": {"concept": "封装", "type": "OOP", "category": "基础概念"}
        },
        {
            "text": "继承(Inheritance)允许子类继承父类的属性和方法，实现代码复用和层次分类。支持单继承和多继承(视语言而定)。应用场景：GUI组件、游戏实体、业务对象建模等。",
            "metadata": {"concept": "继承", "type": "OOP", "category": "基础概念"}
        },
        {
            "text": "抽象(Abstraction)是通过提取共同特征而忽略非本质细节来简化复杂系统的过程。抽象类和接口是实现抽象的主要方式。应用场景：框架设计、系统架构、协议定义等。",
            "metadata": {"concept": "抽象", "type": "OOP", "category": "基础概念"}
        },
        
        # ================== 设计模式 ==================
        {
            "text": "单例模式(Singleton)确保一个类只有一个实例，并提供一个全局访问点。实现要点：私有构造函数、静态实例变量、静态获取方法。应用场景：配置管理、日志系统、数据库连接池等。",
            "metadata": {"concept": "单例模式", "type": "设计模式", "category": "创建型模式"}
        },
        {
            "text": "工厂模式(Factory)定义一个创建对象的接口，但让子类决定实例化哪个类。将对象创建与使用分离，提高灵活性。变体：简单工厂、工厂方法、抽象工厂。应用场景：跨平台UI组件、数据库访问层、插件系统等。",
            "metadata": {"concept": "工厂模式", "type": "设计模式", "category": "创建型模式"}
        },
        {
            "text": "观察者模式(Observer)定义对象间的一对多依赖关系，当一个对象状态改变时，所有依赖它的对象都会得到通知并自动更新。实现方式：推模型/拉模型。应用场景：事件处理系统、MVC中的模型-视图关系、发布-订阅系统等。",
            "metadata": {"concept": "观察者模式", "type": "设计模式", "category": "行为型模式"}
        },
        {
            "text": "策略模式(Strategy)定义一系列算法，封装每个算法，并使它们可以互相替换。让算法独立于使用它的客户而变化。应用场景：排序算法选择、支付方式选择、压缩算法选择等。",
            "metadata": {"concept": "策略模式", "type": "设计模式", "category": "行为型模式"}
        },
        {
            "text": "装饰器模式(Decorator)动态地给一个对象添加一些额外的职责，就增加功能来说比生成子类更灵活。应用场景：IO流处理、GUI组件增强、中间件实现等。",
            "metadata": {"concept": "装饰器模式", "type": "设计模式", "category": "结构型模式"}
        },
        
        # ================== 软件开发生命周期 ==================
        {
            "text": "敏捷开发(Agile)是一种以人为核心、迭代、循序渐进的开发方法。核心价值观：个体和互动高于流程和工具、可工作的软件高于详尽的文档、客户合作高于合同谈判、响应变化高于遵循计划。常用框架：Scrum、Kanban、XP。",
            "metadata": {"concept": "敏捷开发", "type": "方法论", "category": "开发流程"}
        },
        {
            "text": "Scrum是敏捷开发框架，包含角色(Product Owner, Scrum Master, Dev Team)、工件(Product Backlog, Sprint Backlog)和事件(Sprint, Daily Standup, Sprint Review, Retrospective)。典型迭代周期：2-4周。",
            "metadata": {"concept": "Scrum", "type": "方法论", "category": "开发流程"}
        },
        {
            "text": "持续集成(CI)是指开发人员频繁地(每天多次)将代码集成到共享主干，通过自动化构建和测试快速发现集成错误。关键实践：自动化构建、自动化测试、快速失败、主干开发。工具：Jenkins、GitHub Actions、CircleCI。",
            "metadata": {"concept": "持续集成", "type": "DevOps", "category": "开发流程"}
        },
        {
            "text": "持续交付(CD)是在持续集成基础上，确保代码可以随时安全地部署到生产环境，通常通过自动化部署流水线实现。关键要素：环境一致性、部署自动化、发布策略(蓝绿部署、金丝雀发布)。",
            "metadata": {"concept": "持续交付", "type": "DevOps", "category": "开发流程"}
        },
        
        # ================== 软件架构 ==================
        {
            "text": "MVC(Model-View-Controller)是一种架构模式，将应用分为模型(数据)、视图(UI)和控制器(逻辑)三层，实现关注点分离。变体：MVP、MVVM。应用场景：Web框架(如Spring MVC)、桌面应用、移动应用等。",
            "metadata": {"concept": "MVC", "type": "架构", "category": "设计模式"}
        },
        {
            "text": "微服务架构(Microservices)是将单一应用划分为一组小型服务的风格，每个服务运行在自己的进程中，通过轻量级机制通信。特点：独立部署、技术异构、围绕业务能力组织。挑战：分布式系统复杂性、数据一致性。",
            "metadata": {"concept": "微服务", "type": "架构", "category": "系统设计"}
        },
        {
            "text": "REST(Representational State Transfer)是一种基于HTTP协议的架构风格，使用标准方法(GET/POST/PUT/DELETE)操作资源。核心约束：无状态、统一接口、资源标识、自描述消息。对比：SOAP、GraphQL。",
            "metadata": {"concept": "REST", "type": "架构", "category": "API设计"}
        },
        {
            "text": "事件驱动架构(EDA)是一种以事件的产生、检测、消费和响应为核心的架构模式。组件：事件生产者、事件消费者、事件通道、事件处理器。应用场景：实时系统、IoT、金融交易等。",
            "metadata": {"concept": "事件驱动架构", "type": "架构", "category": "系统设计"}
        },
        
        # ================== 测试相关 ==================
        {
            "text": "单元测试(Unit Test)是针对软件最小可测试单元的测试，通常针对函数或方法。特点：隔离性、快速执行、自动化。工具：JUnit(Java)、pytest(Python)、Jest(JavaScript)。最佳实践：FIRST原则(Fast, Isolated, Repeatable, Self-validating, Timely)。",
            "metadata": {"concept": "单元测试", "type": "测试", "category": "质量保证"}
        },
        {
            "text": "测试驱动开发(TDD)要求在编写功能代码前先写测试代码，然后只编写使测试通过的功能代码，最后重构。循环：红(写失败测试)-绿(写最少代码通过测试)-重构。好处：高测试覆盖率、设计引导、文档作用。",
            "metadata": {"concept": "TDD", "type": "方法论", "category": "开发流程"}
        },
        {
            "text": "集成测试(Integration Test)验证多个组件或系统之间的交互。策略：自顶向下、自底向上、三明治。挑战：测试环境搭建、外部依赖模拟(Mock/Stub)。工具：TestNG、Postman、RestAssured。",
            "metadata": {"concept": "集成测试", "type": "测试", "category": "质量保证"}
        },
        
        # ================== 数据结构与算法 ==================
        {
            "text": "时间复杂度(Time Complexity)表示算法执行时间随输入规模增长的变化趋势，常用大O记号表示。常见复杂度：O(1)常数时间、O(log n)对数时间、O(n)线性时间、O(n²)平方时间。分析方法：最坏情况、平均情况。",
            "metadata": {"concept": "时间复杂度", "type": "算法", "category": "基础概念"}
        },
        {
            "text": "哈希表(Hash Table)通过哈希函数将键映射到存储位置的数据结构，理想情况下提供O(1)的查找、插入和删除操作。冲突解决：开放寻址、链地址法。应用场景：字典、缓存、数据库索引等。",
            "metadata": {"concept": "哈希表", "type": "数据结构", "category": "基础概念"}
        },
        {
            "text": "二叉树(Binary Tree)是每个节点最多有两个子节点的树结构。特殊类型：二叉搜索树(左<根<右)、平衡二叉树(AVL)、完全二叉树。遍历方式：前序、中序、后序、层序。应用场景：文件系统、数据库索引、表达式树等。",
            "metadata": {"concept": "二叉树", "type": "数据结构", "category": "基础概念"}
        },
        
        # ================== 编程原则 ==================
        {
            "text": "SOLID原则包含五个面向对象设计原则：单一职责(SRP)、开闭原则(OCP)、里氏替换(LSP)、接口隔离(ISP)和依赖倒置(DIP)。作用：提高可维护性、可扩展性、可复用性。",
            "metadata": {"concept": "SOLID原则", "type": "OOP", "category": "设计原则"}
        },
        {
            "text": "DRY(Don't Repeat Yourself)原则强调避免代码重复，通过抽象和复用提高可维护性。相关原则：KISS(Keep It Simple, Stupid)、YAGNI(You Aren't Gonna Need It)。",
            "metadata": {"concept": "DRY原则", "type": "编程", "category": "最佳实践"}
        },
        {
            "text": "Law of Demeter(迪米特法则)要求一个对象应该对其他对象有尽可能少的了解，只与直接朋友通信。表现：只调用自身方法、传入参数的方法、创建的对象的方法、自身持有的对象的方法。好处：降低耦合。",
            "metadata": {"concept": "迪米特法则", "type": "OOP", "category": "设计原则"}
        },
        
        # ================== 版本控制 ==================
        {
            "text": "Git是一种分布式版本控制系统，核心概念：仓库(repository)、提交(commit)、分支(branch)、合并(merge)。工作流：集中式、功能分支、Git Flow、GitHub Flow。常用命令：clone、commit、push、pull、merge、rebase。",
            "metadata": {"concept": "Git", "type": "工具", "category": "版本控制"}
        },
        
        # ================== 数据库 ==================
        {
            "text": "关系型数据库(RDBMS)基于关系模型，使用SQL语言操作。特点：ACID事务、结构化数据、表关联。代表产品：MySQL、PostgreSQL、Oracle。对比NoSQL：固定模式vs灵活模式、垂直扩展vs水平扩展。",
            "metadata": {"concept": "关系型数据库", "type": "数据库", "category": "基础概念"}
        },
        {
            "text": "NoSQL数据库适用于非结构化或半结构化数据，类型：键值存储(Redis)、文档存储(MongoDB)、列存储(Cassandra)、图数据库(Neo4j)。特点：高扩展性、灵活模式、最终一致性。",
            "metadata": {"concept": "NoSQL", "type": "数据库", "category": "基础概念"}
        },
        
        # ================== 网络 ==================
        {
            "text": "HTTP协议是无状态的应用层协议，版本：HTTP/1.1(持久连接)、HTTP/2(多路复用)、HTTP/3(基于QUIC)。方法：GET(安全/幂等)、POST(非幂等)、PUT(幂等)、DELETE(幂等)。状态码：2xx成功、3xx重定向、4xx客户端错误、5xx服务端错误。",
            "metadata": {"concept": "HTTP", "type": "网络", "category": "协议"}
        },
        {
            "text": "WebSocket是HTML5提供的全双工通信协议，特点：单一TCP连接、服务端主动推送、低延迟。应用场景：实时聊天、在线游戏、股票行情等。对比HTTP轮询：更高效、更低延迟。",
            "metadata": {"concept": "WebSocket", "type": "网络", "category": "协议"}
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