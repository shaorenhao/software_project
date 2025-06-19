# CaseAgent.py
import json
import os
import random
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from api import LLMClient
from vector_db import FAISSVectorDB

class CaseAgent():
    def __init__(self):
        self.llm_client = None
        self.vector_db = None
        self.current_question = None
        self.load_config()

    def load_config(self):
        self.llm_client = LLMClient(api_key="sk-nnnbfontekeesozhffpmluqdajbwzqvxeskyevmxwfignhgh")
        self.vector_db = FAISSVectorDB("software_engineering_examples")
        
        if self.vector_db.get_collection_stats()["doc_count"] == 0:
            self._initialize_question_bank()

    def _initialize_question_bank(self):
        """Initialize question bank with sample questions"""
        example_questions = [
            {
                "text": "题目：什么是软件生命周期？请简述其主要阶段。\n答案：软件生命周期是指从软件概念提出到最终退役的全过程。主要阶段包括：1) 需求分析 2) 系统设计 3) 编码实现 4) 测试 5) 部署 6) 维护。",
                "metadata": {"concept": "软件生命周期", "type": "基础概念", "difficulty": "简单"}
            },
            {
                "text": "题目：比较瀑布模型和敏捷开发模型的优缺点。\n答案：瀑布模型优点：阶段明确，文档齐全；缺点：灵活性差，难应对需求变化。敏捷开发优点：适应变化快，客户参与度高；缺点：文档较少，对团队要求高。",
                "metadata": {"concept": "开发模型", "type": "开发方法", "difficulty": "中等"}
            },
            {
                "text": "题目：什么是白盒测试和黑盒测试？举例说明。\n答案：白盒测试是基于代码内部结构的测试，如单元测试；黑盒测试只关注输入输出，如功能测试。例如：白盒测试可以检查循环逻辑，黑盒测试验证登录功能。",
                "metadata": {"concept": "软件测试", "type": "测试方法", "difficulty": "中等"}
            },
            {
                "text": "题目：解释软件工程中的'高内聚低耦合'原则。\n答案：高内聚指模块内部元素紧密相关；低耦合指模块间依赖少。好处是提高可维护性和可重用性。例如：将用户认证功能封装成独立模块。",
                "metadata": {"concept": "设计原则", "type": "系统设计", "difficulty": "中等"}
            }
        ]
        self.vector_db.batch_insert(example_questions)

    def generate_question(self):
        """Generate a random question from the knowledge base"""
        search_results = self.vector_db.search("题目", top_k=10)
        if search_results:
            random_question = random.choice(search_results)
            self.current_question = random_question['content'].split('\n')[0]
            return self.current_question
        return "无法获取题目，请稍后再试"

    def analyze_question(self, question=None):
        """Analyze the current or specified question"""
        if not question:
            question = self.current_question
            
        if not question:
            return "请先获取题目或输入要解析的问题"
            
        # Search for similar questions in knowledge base
        search_results = self.vector_db.search(question, top_k=3)
        
        # Build analysis result
        result = f"<b>题目解析：</b><br>{question}<br><br>"
        
        if search_results:
            # Find the exact match if exists
            exact_match = None
            for res in search_results:
                if question in res['content']:
                    exact_match = res['content']
                    break
            
            if exact_match:
                parts = exact_match.split('\n')
                if len(parts) > 1:
                    result += f"<b>参考答案：</b><br>{parts[1].replace('答案：', '')}<br><br>"
            else:
                # If no exact match, show similar questions and their answers
                result += "<b>未找到完全匹配的题目，以下是相关题目解析：</b><br>"
                for i, res in enumerate(search_results):
                    parts = res['content'].split('\n')
                    result += f"{i+1}. {parts[0]}<br>"
                    if len(parts) > 1:
                        result += f"答案：{parts[1].replace('答案：', '')}<br><br>"
                try:
                    llm_response = self.llm_client.chat_completion([
                        {"role": "system", "content": "你是一个软件工程专家，请对以下题目进行专业解析"},
                        {"role": "user", "content": f"请解析以下题目并给出详细答案：{question}"}
                    ])
                    if llm_response and 'choices' in llm_response:
                        llm_answer = llm_response['choices'][0]['message']['content']
                        result += f"<b>AI 解析：</b><br>{llm_answer}<br><br>"
                except Exception as e:
                    result += f"<i>无法获取AI解析：{str(e)}</i><br><br>"
        
        # Add additional related questions
        result += "<br><b>相关题目推荐：</b><br>"
        related_questions = self.vector_db.search("题目", top_k=3)
        for i, q in enumerate(related_questions):
            a_line = q['content'].split('\n')[0] 
            result += f"{i+1}. {a_line}<br>"
            
        return result