import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QSizePolicy
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
            'role': 'root-system', 
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

        # 支持关键词展示
        self.keywords_label = QLabel("支持关键词：")
        self.keywords_label.setStyleSheet("padding: 0px 5px; font-size: 12px; color: #555555;")
        self.keywords_label.setFixedHeight(25)
        main_layout.addWidget(self.keywords_label)

        # 对话区
        self.dialogue_area = QWebEngineView()
        # self.dialogue_area.setReadOnly(True)
        # self.dialogue_area.setStyleSheet("""
        #     QTextEdit {
        #         background-color: #223355;
        #         border: 1px solid #ccc;
        #         border-radius: 0px;
        #         font-family: Arial;
        #     }
        # """)
        
        # 初始化HTML内容
        self.init_html_content()
        main_layout.addWidget(self.dialogue_area)

        # 输入区
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(5, 5, 5, 5)
        input_layout.setSpacing(5)

        self.input_entry = QLineEdit()
        self.input_entry.setPlaceholderText("请输入您的问题...")
        self.input_entry.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                font-size: 14px;
                border: 1px solid #007acc;
            }
        """)
        self.input_entry.setFixedHeight(50)

        self.send_button = QPushButton("发送")
        self.send_button.setFixedSize(70, 50)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005f99;
            }
        """)

        input_layout.addWidget(self.input_entry)
        input_layout.addWidget(self.send_button)
        main_layout.addLayout(input_layout)

        self.setLayout(main_layout)

        # 绑定发送事件
        self.send_button.clicked.connect(self.on_send)
        self.input_entry.returnPressed.connect(self.on_send)

    def init_html_content(self):
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
            <style>
                .user-message {
                    background-color: #87CEEB;
                    padding: 10px;
                    border-radius: 8px;
                    margin-bottom: 10px;
                    color: white;
                    max-width: 80%;
                    margin-left: auto;
                }
                .ai-message {
                    background-color: #f0f0f0;
                    padding: 10px;
                    border-radius: 8px;
                    margin-bottom: 10px;
                    max-width: 80%;
                }
                .mermaid {
                    background-color: white;
                    margin: 15px 0;
                    padding: 15px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                }
                .mermaid-error {
                    color: red;
                    border: 1px solid red;
                    padding: 10px;
                }
            </style>
        </head>
        <body>
            <div id="content"></div>
            <script>
                function renderMermaid() {
                    try {
                        mermaid.initialize({startOnLoad:false});
                        mermaid.init(undefined, document.querySelectorAll('.mermaid'));
                    } catch(e) {
                        console.error('Mermaid渲染错误:', e);
                        const mermaidDivs = document.querySelectorAll('.mermaid');
                        mermaidDivs.forEach(div => {
                            div.classList.add('mermaid-error');
                            div.innerHTML = '图表渲染错误: ' + e.message;
                        });
                    }
                }

                const observer = new MutationObserver(() => {
                    renderMermaid();
                });
                observer.observe(document.body, { childList: true, subtree: true });
            </script>
        </body>
        </html>
        """
        self.dialogue_area.setHtml(html_content)


    def on_send(self):
        message = self.input_entry.text()
        if message:
            self.display_user_message(message)
            
            self.input_entry.clear()
            # 显示"正在思考..."提示
            self.display_thinking_message()
            
            self.message_history.append({"role": "user", "content": message})
            self.worker = Worker(self.message_history.copy())
            self.worker.finished.connect(self.handle_response)
            self.worker.error.connect(self.display_error_message)
            self.worker.start()

    def display_thinking_message(self):
        """显示正在思考的消息"""
        thinking_html = """
        <div class="ai-message">
            AI: 正在思考...
        </div>
        """
        self.append_html(thinking_html)

    def handle_response(self, response, original_message):
        """处理LLM的响应"""
        if response and 'choices' in response and len(response['choices']) > 0:
            reply = response['choices'][0]['message']['content']
            self.display_model_message(reply)
            self.message_history.append({"role": "assistant", "content": reply})
        else:
            self.display_error_message("错误: 无法获取有效的回复")

    def display_user_message(self, message):
        """显示用户消息"""
        user_html = f"""
        <div class="user-message">
            你: {message}
        </div>
        """
        self.append_html(user_html)

    def display_model_message(self, message):
        """显示AI回复，处理Mermaid图表"""
        if "```mermaid" in message:
            try:
                # 提取Mermaid代码
                parts = message.split("```mermaid")
                mermaid_part = parts[1].split("```")[0].strip()
                
                # 创建图表HTML
                chart_html = f"""
                <div class="ai-message">
                    AI: 以下是系统图表:
                </div>
                <div class="mermaid">
                    {mermaid_part}
                </div>
                <script>
                    renderMermaid();
                </script>
                """
                self.append_html(chart_html)
                
                # 显示剩余文本（如果有）
                remaining_text = parts[-1].split("```")[-1].strip()
                if remaining_text:
                    text_html = f"""
                    <div class="ai-message">
                        AI: {remaining_text}
                    </div>
                    """
                    self.append_html(text_html)
            except Exception as e:
                print(f"处理Mermaid图表时出错: {str(e)}")
                error_html = f"""
                <div class="ai-message">
                    AI: 图表生成失败: {str(e)}
                </div>
                <div class="ai-message">
                    {message}
                </div>
                """
                self.append_html(error_html)
        else:
            # 普通消息
            self.append_html(f"""
            <div class="ai-message">
                AI: {message}
            </div>
            """)

    def display_error_message(self, error_msg):
        """显示错误消息"""
        error_html = f"""
        <div class="ai-message" style="color: red;">
            {error_msg}
        </div>
        """
        self.append_html(error_html)

    def append_html(self, html_content):
        """追加HTML内容到对话区域"""
        # # 获取当前HTML
        # self.dialogue_area.page().toHtml(lambda html: setattr(self, "current_html", html))
        
        # # 在</body>前插入新内容
        # new_html = self.current_html.replace("</body>", html_content + "</body>")
        # print(new_html)
        # print("啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊\n")

        # # 设置新HTML
        # self.dialogue_area.setHtml(new_html)
        
        # # 滚动到底部
        # # self.dialogue_area.page().verticalScrollBar().setValue(
        # #     self.dialogue_area.page().verticalScrollBar().maximum()
        # # )
        # # self.dialogue_area.page().runJavaScript("window.scrollTo(0, document.body.scrollHeight);")
    # 使用JavaScript直接插入新内容
        print(html_content)
        js_code = f"""
        var div = document.createElement('div');
        div.innerHTML = `{html_content}`;
        document.body.appendChild(div);
        window.scrollTo(0, document.body.scrollHeight);
        """
        self.dialogue_area.page().runJavaScript(js_code)

    def mousePressEvent(self, event):
        event.ignore()

    def mouseMoveEvent(self, event):
        event.ignore()

    def mouseReleaseEvent(self, event):
        event.ignore()