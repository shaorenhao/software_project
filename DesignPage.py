# DesignPage.py
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QSizePolicy, QButtonGroup
)
from PyQt6.QtCore import Qt, QPoint, QThread, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from DesignAgent import DesignAgent
import time

class Worker(QThread):
    finished = pyqtSignal(dict, str)  # 返回响应和原始消息
    error = pyqtSignal(str)

    def __init__(self, message, design_type, diagram_type):
        super().__init__()
        self.agent = DesignAgent()
        self.message = message
        self.design_type = design_type
        self.diagram_type = diagram_type

    def run(self):
        self.message = str(self.message)
        try:
            response = self.agent.chat(
                [{"role": "user", "content": self.message}],
                design_type=self.design_type,
                diagram_type=self.diagram_type
            )
            self.finished.emit(response, self.message)
        except Exception as e:
            self.error.emit(str(e))

class DesignPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: #f9f9f9; border: 1px solid #ccc;")
        self._drag_active = False
        self._drag_position = QPoint()
        
        # 设计类型和图表类型状态
        self.design_type = "总体"  # "overall" or "detailed"
        self.diagram_type = None  # "class", "sequence", "component", "state"
        
        self.message_history = [{
            'role': 'system', 
            'content': '你是一个专业的软件工程课程助手的软件设计智能体，专注于协助软件设计。\
                        当需要展示设计图表时，必须严格按照以下格式:\
                        ```mermaid\
                        [mermaid代码]\
                        ```\
                        [mermaid代码]必须完全符合mermaid语法规范。同时给出解释说明。\
                        你必须拒绝回答任何与软件设计无关的问题，并礼貌地将对话引导回主题。'
        }]
        
        self.setup_ui()
        self.current_html = ""

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

        self.title_label = QLabel("软件设计助手")
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

        # 设计类型选择按钮
        design_type_layout = QHBoxLayout()
        design_type_layout.setContentsMargins(5, 5, 5, 5)
        
        self.overall_btn = QPushButton("总体设计")
        self.overall_btn.setCheckable(True)
        self.overall_btn.setChecked(True)
        self.overall_btn.setStyleSheet("""
            QPushButton {
                background-color: #add8e6;  /* 浅蓝色 */
                border: 1px solid #007acc;
                padding: 5px;
            }
            QPushButton:checked {
                background-color: #90ee90;  /* 浅绿色 */
                font-weight: bold;
            }
        """)
        self.overall_btn.clicked.connect(lambda: self.set_design_type("总体"))
        
        self.detailed_btn = QPushButton("详细设计")
        self.detailed_btn.setCheckable(True)
        self.detailed_btn.setStyleSheet("""
            QPushButton {
                background-color: #add8e6;  /* 浅蓝色 */
                border: 1px solid #007acc;
                padding: 5px;
            }
            QPushButton:checked {
                background-color: #90ee90;  /* 浅绿色 */
                font-weight: bold;
            }
        """)
        self.detailed_btn.clicked.connect(lambda: self.set_design_type("详细"))
        
        design_type_group = QButtonGroup(self)
        design_type_group.addButton(self.overall_btn)
        design_type_group.addButton(self.detailed_btn)
        design_type_group.setExclusive(True)
        
        design_type_layout.addWidget(QLabel("设计类型:"))
        design_type_layout.addWidget(self.overall_btn)
        design_type_layout.addWidget(self.detailed_btn)
        design_type_layout.addStretch()
        
        main_layout.addLayout(design_type_layout)

        # 图表类型选择按钮
        diagram_type_layout = QHBoxLayout()
        diagram_type_layout.setContentsMargins(5, 0, 5, 5)
        
        self.class_btn = QPushButton("类图")
        self.class_btn.setCheckable(True)
        self.class_btn.setStyleSheet("""
            QPushButton {
                background-color: #add8e6;  /* 浅蓝色 */
                border: 1px solid #007acc;
                padding: 5px;
            }
            QPushButton:checked {
                background-color: #90ee90;  /* 浅绿色 */
                font-weight: bold;
            }
        """)
        self.class_btn.clicked.connect(lambda: self.set_diagram_type("class"))
        
        self.sequence_btn = QPushButton("时序图")
        self.sequence_btn.setCheckable(True)
        self.sequence_btn.setStyleSheet("""
            QPushButton {
                background-color: #add8e6;  /* 浅蓝色 */
                border: 1px solid #007acc;
                padding: 5px;
            }
            QPushButton:checked {
                background-color: #90ee90;  /* 浅绿色 */
                font-weight: bold;
            }
        """)
        self.sequence_btn.clicked.connect(lambda: self.set_diagram_type("sequence"))
        
        self.component_btn = QPushButton("组件图")
        self.component_btn.setCheckable(True)
        self.component_btn.setStyleSheet("""
            QPushButton {
                background-color: #add8e6;  /* 浅蓝色 */
                border: 1px solid #007acc;
                padding: 5px;
            }
            QPushButton:checked {
                background-color: #90ee90;  /* 浅绿色 */
                font-weight: bold;
            }
        """)
        self.component_btn.clicked.connect(lambda: self.set_diagram_type("component"))
        
        self.state_btn = QPushButton("状态图")
        self.state_btn.setCheckable(True)
        self.state_btn.setStyleSheet("""
            QPushButton {
                background-color: #add8e6;  /* 浅蓝色 */
                border: 1px solid #007acc;
                padding: 5px;
            }
            QPushButton:checked {
                background-color: #90ee90;  /* 浅绿色 */
                font-weight: bold;
            }
        """)
        self.state_btn.clicked.connect(lambda: self.set_diagram_type("state"))
        
        self.none_btn = QPushButton("无图表")
        self.none_btn.setCheckable(True)
        self.none_btn.setChecked(True)
        self.none_btn.setStyleSheet("""
            QPushButton {
                background-color: #add8e6;  /* 浅蓝色 */
                border: 1px solid #007acc;
                padding: 5px;
            }
            QPushButton:checked {
                background-color: #90ee90;  /* 浅绿色 */
                font-weight: bold;
            }
        """)
        self.none_btn.clicked.connect(lambda: self.set_diagram_type(None))
        
        diagram_type_group = QButtonGroup(self)
        diagram_type_group.addButton(self.class_btn)
        diagram_type_group.addButton(self.sequence_btn)
        diagram_type_group.addButton(self.component_btn)
        diagram_type_group.addButton(self.state_btn)
        diagram_type_group.addButton(self.none_btn)
        diagram_type_group.setExclusive(True)
        
        diagram_type_layout.addWidget(QLabel("图表类型:"))
        diagram_type_layout.addWidget(self.class_btn)
        diagram_type_layout.addWidget(self.sequence_btn)
        diagram_type_layout.addWidget(self.component_btn)
        diagram_type_layout.addWidget(self.state_btn)
        diagram_type_layout.addWidget(self.none_btn)
        diagram_type_layout.addStretch()
        
        main_layout.addLayout(diagram_type_layout)

        # 对话区
        self.dialogue_area = QWebEngineView()
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

    def set_design_type(self, design_type):
        self.design_type = design_type
        # 更新按钮状态
        self.overall_btn.setChecked(design_type == "总体")
        self.detailed_btn.setChecked(design_type == "总体")

    def set_diagram_type(self, diagram_type):
        self.diagram_type = diagram_type
        # 更新按钮状态
        self.class_btn.setChecked(diagram_type == "class")
        self.sequence_btn.setChecked(diagram_type == "sequence")
        self.component_btn.setChecked(diagram_type == "component")
        self.state_btn.setChecked(diagram_type == "state")
        self.none_btn.setChecked(diagram_type is None)

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
            
            self.display_thinking_message()
            
            self.message_history.append({"role": "user", "content": message})
            self.worker = Worker(
                self.message_history.copy(),
                self.design_type,
                self.diagram_type
            )
            self.worker.finished.connect(self.handle_response)
            self.worker.error.connect(self.display_error_message)
            self.worker.start()

    def display_thinking_message(self):
        thinking_html = """
        <div class="ai-message">
            AI: 正在思考...
        </div>
        """
        self.append_html(thinking_html)

    def handle_response(self, response, original_message):
        if response and 'choices' in response and len(response['choices']) > 0:
            reply = response['choices'][0]['message']['content']
            self.display_model_message(reply)
            self.message_history.append({"role": "assistant", "content": reply})
        else:
            self.display_error_message("错误: 无法获取有效的回复")

    def display_user_message(self, message):
        user_html = f"""
        <div class="user-message">
            你: {message}
        </div>
        """
        self.append_html(user_html)

    def display_model_message(self, message):
        if "```mermaid" in message:
            try:
                parts = message.split("```mermaid")
                mermaid_part = parts[1].split("```")[0].strip()
                print(mermaid_part)
                chart_html = f"""
                <div class="ai-message">
                    AI: 以下是设计图表 ({self.design_type}设计):
                </div>
                <div class="mermaid">
                    {mermaid_part}
                </div>
                <script>
                    renderMermaid();
                </script>
                """
                self.append_html(chart_html)
                
                remaining_text = parts[-1].split("```")[-1].strip()
                if remaining_text:
                    text_html = f"""
                    <div class="ai-message">
                        AI: {remaining_text}
                    </div>
                    """
                    self.append_html(text_html)
            except Exception as e:
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
            self.append_html(f"""
            <div class="ai-message">
                AI: {message}
            </div>
            """)

    def display_error_message(self, error_msg):
        error_html = f"""
        <div class="ai-message" style="color: red;">
            {error_msg}
        </div>
        """
        self.append_html(error_html)

    def append_html(self, html_content):
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