import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QSizePolicy, QSplitter
)
from PyQt6.QtCore import Qt, QPoint, QThread, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from RequirementAgent import RequirementAgent
import time

class Worker(QThread):
    finished = pyqtSignal(dict, str)  # 返回响应和原始消息
    error = pyqtSignal(str)

    def __init__(self, message):
        super().__init__()
        self.agent = RequirementAgent()
        self.message = message

    def run(self):
        self.message=str(self.message)
        try:
            response = self.agent.chat([
                {"role": "user", "content": self.message}
            ])
            self.finished.emit(response, self.message)
        except Exception as e:
            self.error.emit(str(e))

class RequirementPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: #f9f9f9; border: 1px solid #ccc;")
        self._drag_active = False
        self._drag_position = QPoint()
        self.message_history = [{
            'role': 'system', 
            'content': '你是一个专业的软件工程课程助手的需求分析智能体，专注于协助需求分析，主动分析user提出的系统，进行需求分析。\
                        当需要展示系统架构、流程图、类图或时序图时，必须严格按照以下格式:\
                        ```mermaid\
                        [mermaid代码]\
                        ```\
                        [mermaid代码]必须完全符合mermaid语法规范，特别注意:\
                        1. 流程图使用flowchart TB或flowchart LR\
                        2. 类图使用classDiagram\
                        3. 时序图使用sequenceDiagram\
                        4. 确保所有节点和连接符正确\
                        5. 不要包含任何非mermaid语法的内容\
                        生成图表后，请简要解释图表内容。\
                        如果无法生成正确的mermaid代码，请直接说明而不生成错误图表。\
                        你必须拒绝回答任何与软件工程或需求分析无关的问题，并礼貌地将对话引导回主题。'
        }]
        self.setup_ui()
        self.worker = Worker(self.message_history.copy())
        self.current_html=""

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 顶部自定义标题栏
        self.title_bar = QWidget(self)
        self.title_bar.setStyleSheet("background-color: #007acc;")
        self.title_bar.setFixedHeight(40)
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(10, 0, 10, 0)
        title_layout.setSpacing(0)

        self.title_label = QLabel("需求分析助手")
        self.title_label.setStyleSheet("font-size: 16px; color: #ffffff; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(self.title_label)

        title_layout.addStretch()

        self.close_button = QPushButton("✕")
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #e81123;
                color: white;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b50c1a;
            }
        """)
        self.close_button.clicked.connect(self.hide)
        title_layout.addWidget(self.close_button)

        self.title_bar.setLayout(title_layout)
        main_layout.addWidget(self.title_bar)

        # 输入区
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(10, 10, 10, 10)
        input_layout.setSpacing(10)

        self.input_entry = QLineEdit()
        self.input_entry.setPlaceholderText("请输入系统功能描述...")
        self.input_entry.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #007acc;
                border-radius: 4px;
            }
        """)
        self.input_entry.setFixedHeight(40)

        self.send_button = QPushButton("生成分析")
        self.send_button.setFixedSize(100, 40)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005f99;
            }
        """)
        self.send_button.clicked.connect(self.on_send)
        self.input_entry.returnPressed.connect(self.on_send)

        input_layout.addWidget(self.input_entry)
        input_layout.addWidget(self.send_button)
        main_layout.addLayout(input_layout)

        # 拆分区
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧图表区
        self.diagram_view = QWebEngineView()
        self.init_mermaid_template()
        splitter.addWidget(self.diagram_view)

        # 右侧解释区
        self.explanation_text = QTextEdit()
        self.explanation_text.setReadOnly(True)
        self.explanation_text.setStyleSheet("""
            QTextEdit {
                padding: 10px;
                font-size: 14px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        splitter.addWidget(self.explanation_text)
        splitter.setSizes([600, 400])

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

    def init_mermaid_template(self):
        base_html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
            <style>
                .mermaid {
                    background-color: white;
                    padding: 15px;
                }
                .mermaid-error {
                    color: red;
                    border: 1px solid red;
                    padding: 10px;
                }
            </style>
        </head>
        <body>
            <div class="mermaid" id="diagram">
                graph TD
                A[等待输入] --> B[将生成图表]
            </div>
            <script>
                mermaid.initialize({startOnLoad:true});
            </script>
        </body>
        </html>
        '''
        self.diagram_view.setHtml(base_html)

    def on_send(self):
        message = self.input_entry.text()
        if message:
            self.input_entry.clear()
            
            # 显示"正在分析..."提示
            self.explanation_text.setPlainText("正在分析需求，请稍候...")
            
            self.message_history.append({"role": "user", "content": message})
            self.worker = Worker(self.message_history.copy())
            self.worker.finished.connect(self.handle_response)
            self.worker.error.connect(self.display_error_message)
            self.worker.start()

    def handle_response(self, response, original_message):
        """处理LLM的响应"""
        if response and 'choices' in response and len(response['choices']) > 0:
            reply = response['choices'][0]['message']['content']
            self.process_model_reply(reply)
            self.message_history.append({"role": "assistant", "content": reply})
        else:
            self.display_error_message("错误: 无法获取有效的回复")

    def process_model_reply(self, reply):
        """处理模型回复，分离图表和解释文本"""
        if "```mermaid" in reply:
            try:
                # 提取Mermaid代码
                mermaid_code = reply.split("```mermaid")[1].split("```")[0].strip()
                # 提取解释文本（在最后一个```之后的内容）
                explanation = reply.split("```")[-1].strip()
                
                # 更新图表
                html = f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
                    <style>
                        .mermaid {{
                            background-color: white;
                            padding: 15px;
                        }}
                        .mermaid-error {{
                            color: red;
                            border: 1px solid red;
                            padding: 10px;
                        }}
                    </style>
                </head>
                <body>
                    <div class="mermaid">
                    {mermaid_code}
                    </div>
                    <script>
                        mermaid.initialize({{startOnLoad:true}});
                    </script>
                </body>
                </html>
                '''
                self.diagram_view.setHtml(html)
                
                # 更新解释文本
                self.explanation_text.setPlainText(explanation if explanation else "图表已生成，请查看左侧。")
            except Exception as e:
                self.display_error_message(f"处理图表时出错: {str(e)}")
                self.explanation_text.setPlainText(reply)
        else:
            # 如果没有图表，全部显示在解释区域
            self.explanation_text.setPlainText(reply)

    def display_error_message(self, error_msg):
        """显示错误消息"""
        self.explanation_text.setPlainText(f"错误: {error_msg}")

    def mousePressEvent(self, event):
        event.ignore()

    def mouseMoveEvent(self, event):
        event.ignore()

    def mouseReleaseEvent(self, event):
        event.ignore()