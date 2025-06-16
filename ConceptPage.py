import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, QPoint, QThread, pyqtSignal
from PyQt6.QtGui import QTextCursor
from ConceptAgent import ConceptAgent
import time
import json

class Worker(QThread):
    finished = pyqtSignal(dict, str)  # 返回响应和原始消息
    error = pyqtSignal(str)

    def __init__(self, message, use_rag):
        super().__init__()
        self.agent = ConceptAgent()
        self.message = message
        self.use_rag = use_rag

    def run(self):
        self.message=str(self.message)
        try:
            response = self.agent.chat([
                {"role": "user", "content": self.message}
            ], self.use_rag)
            self.finished.emit(response, self.message)
        except Exception as e:
            self.error.emit(str(e))

class ConceptPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        # 去掉系统边框，自定义标题栏
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("""
            background-color: #f5f5f5;
            border: 1px solid #ddd;
            font-family: 'Arial';
        """)
        self._drag_active = False  # 用于窗口拖动
        self._drag_position = QPoint()
        self.message_history = [{
            'role': 'system', 
            'content': """你是一个专业的软件工程课程助手的概念解析助手智能体，专注于回答与软件工程相关的概念解析问题。
                        请以清晰、结构化的方式回答用户的问题，包括定义、分类、应用场景和相关概念。
                        对于每个概念，尽量提供以下结构化信息：
                        1. 定义：简明扼要的定义
                        2. 分类：属于哪个类别或领域
                        3. 应用：实际应用场景
                        4. 相关：相关术语或概念
                        
                        请避免一直重复同一句话。
                        必须拒绝回答任何与软件工程无关的问题，并礼貌地将对话引导回软件工程主题。"""
        }]
        self.setup_ui()
        self.use_rag = True
        self.worker = Worker(self.message_history.copy(),self.use_rag)
        
        # 初始化时显示欢迎消息
        self.display_model_message("""
        🎉 欢迎使用概念解析助手！
        
        我可以帮助您理解各种软件工程概念，包括：
        - 面向对象编程（OOP）概念
        - 设计模式
        - 软件开发生命周期
        - 软件架构
        - 测试相关概念
        
        例如，您可以问我：
        - "什么是多态？"
        - "解释一下MVC模式"
        - "敏捷开发的特点是什么？"
        
        请在下方的输入框中输入您的问题...
        """)

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 顶部自定义标题栏
        self.title_bar = QWidget(self)
        self.title_bar.setStyleSheet("""
            background-color: #2c3e50;
            color: white;
            font-weight: bold;
            font-size: 16px;
        """)
        self.title_bar.setFixedHeight(40)
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(10, 0, 10, 0)
        title_layout.setSpacing(0)

        # 智能体名称
        self.title_label = QLabel("📚 概念解析助手")
        self.title_label.setStyleSheet("font-size: 16px; color: #ffffff; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(self.title_label)

        # 占位符扩展空间
        title_layout.addStretch()

        # 关闭按钮
        self.close_button = QPushButton("✕")
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                font-weight: bold;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.close_button.clicked.connect(self.hide)
        title_layout.addWidget(self.close_button)

        self.title_bar.setLayout(title_layout)
        main_layout.addWidget(self.title_bar)

        # 支持关键词展示
        self.keywords_label = QLabel("💡 支持查询：类、对象、继承、多态、封装、设计模式、MVC、REST、敏捷开发、单元测试等")
        self.keywords_label.setStyleSheet("""
            padding: 5px 10px;
            font-size: 12px;
            color: #555555;
            background-color: #ecf0f1;
            border-bottom: 1px solid #ddd;
        """)
        self.keywords_label.setFixedHeight(30)
        main_layout.addWidget(self.keywords_label)

        # 对话区 - 占据主要高度
        self.dialogue_area = QTextEdit()
        self.dialogue_area.setReadOnly(True)
        self.dialogue_area.setStyleSheet("""
            background-color: #ffffff;
            border: none;
            padding: 10px;
            font-size: 14px;
        """)
        main_layout.addWidget(self.dialogue_area)

        # 输入区
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(10, 10, 10, 10)
        input_layout.setSpacing(10)

        self.input_entry = QLineEdit()
        self.input_entry.setPlaceholderText("请输入软件工程术语或问题...")
        self.input_entry.setStyleSheet("""
            padding: 10px;
            font-size: 14px;
            border: 2px solid #3498db;
            border-radius: 5px;
        """)
        self.input_entry.setFixedHeight(50)

        self.send_button = QPushButton("发送")
        self.send_button.setFixedSize(80, 50)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

        input_layout.addWidget(self.input_entry)
        input_layout.addWidget(self.send_button)

        self.rag_toggle = QPushButton("🔍 知识库已启用")
        self.rag_toggle.setCheckable(True)
        self.rag_toggle.setChecked(True)
        self.rag_toggle.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                font-size: 14px;
                padding: 0 10px;
            }
            QPushButton:checked {
                background-color: #27ae60;
            }
            QPushButton:!checked {
                background-color: #e74c3c;
            }
        """)
        self.rag_toggle.toggled.connect(self.toggle_rag)
        input_layout.addWidget(self.rag_toggle)
        main_layout.addLayout(input_layout)

        self.setLayout(main_layout)

        # 绑定发送事件
        self.send_button.clicked.connect(self.on_send)
        self.input_entry.returnPressed.connect(self.on_send)

    def toggle_rag(self, checked):
        """切换是否使用检索增强生成"""
        if checked:
            self.rag_toggle.setText("🔍 知识库已启用")
        else:
            self.rag_toggle.setText("🔍 知识库已禁用")
        self.use_rag = checked

    def on_send(self):
        message = self.input_entry.text().strip()
        if not message:
            return
            
        self.display_user_message(message)
        self.input_entry.clear()
        
        # 显示"正在思考..."提示
        self.display_model_message("💭 正在思考...", is_thinking=True)
        
        self.message_history.append({"role": "user", "content": message})
        # 创建并启动工作线程
        self.worker = Worker(message, self.use_rag)
        self.worker.finished.connect(self.handle_response)
        self.worker.error.connect(self.display_error_message)
        self.worker.start()

    def handle_response(self, response, original_message):
        """处理LLM的响应"""
        # 移除"正在思考..."消息
        self.dialogue_area.moveCursor(QTextCursor.MoveOperation.End)
        self.dialogue_area.textCursor().select(QTextCursor.SelectionType.LineUnderCursor)
        self.dialogue_area.textCursor().removeSelectedText()
        self.dialogue_area.textCursor().deletePreviousChar()
        
        if response and 'choices' in response and len(response['choices']) > 0:
            reply = response['choices'][0]['message']['content']
            self.display_model_message(reply)
            self.message_history.append({"role": "assistant", "content": reply})
        else:
            self.display_error_message("错误: 无法获取有效的回复")

    def display_user_message(self, message):
        html = f"""
        <div style="margin: 10px 0; text-align: right;">
            <div style="display: inline-block; max-width: 80%; 
                        background-color: #3498db; color: white; 
                        padding: 10px 15px; border-radius: 15px 15px 0 15px;
                        word-wrap: break-word;">
                {message}
            </div>
        </div>
        """
        self.dialogue_area.append(html)
        self.scroll_to_bottom()

    def display_model_message(self, message, is_thinking=False):
        if is_thinking:
            html = f"""
            <div style="margin: 10px 0; text-align: left;">
                <div style="display: inline-block; max-width: 80%; 
                            background-color: #ecf0f1; color: #333; 
                            padding: 10px 15px; border-radius: 15px 15px 15px 0;
                            word-wrap: break-word;">
                    {message}
                </div>
            </div>
            """
        else:
            # 格式化回复中的结构化内容
            formatted_message = message.replace("\n", "<br>")
            formatted_message = formatted_message.replace("1. 定义：", "<b>📖 定义：</b>")
            formatted_message = formatted_message.replace("2. 分类：", "<br><b>📂 分类：</b>")
            formatted_message = formatted_message.replace("3. 应用：", "<br><b>🛠️ 应用：</b>")
            formatted_message = formatted_message.replace("4. 相关：", "<br><b>🔗 相关：</b>")
            
            html = f"""
            <div style="margin: 10px 0; text-align: left;">
                <div style="display: inline-block; max-width: 80%; 
                            background-color: #f8f9fa; color: #333; 
                            padding: 10px 15px; border-radius: 15px 15px 15px 0;
                            border: 1px solid #ddd; word-wrap: break-word;">
                    {formatted_message}
                </div>
            </div>
            """
        self.dialogue_area.append(html)
        self.scroll_to_bottom()

    def display_error_message(self, message):
        html = f"""
        <div style="margin: 10px 0; text-align: left;">
            <div style="display: inline-block; max-width: 80%; 
                        background-color: #ffebee; color: #c62828; 
                        padding: 10px 15px; border-radius: 15px 15px 15px 0;
                        border: 1px solid #ef9a9a; word-wrap: break-word;">
                ⚠️ {message}
            </div>
        </div>
        """
        self.dialogue_area.append(html)
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        cursor = self.dialogue_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.dialogue_area.setTextCursor(cursor)
        self.dialogue_area.ensureCursorVisible()

    # ===========================
    # 窗口拖动逻辑
    # ===========================
    def mousePressEvent(self, event):
        event.ignore()

    def mouseMoveEvent(self, event):
        event.ignore()

    def mouseReleaseEvent(self, event):
        event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 测试窗口
    window = ConceptPage(None)
    window.resize(700, 800)
    window.show()

    sys.exit(app.exec())