import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QSizePolicy, QButtonGroup,
    QProgressBar
)
from PyQt6.QtCore import Qt, QPoint, QThread, pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from DesignAgent import DesignAgent

class Worker(QThread):
    finished = pyqtSignal(dict, str, str)  # 返回响应、设计类型、图表类型
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
            self.finished.emit(response, self.design_type, self.diagram_type)
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
        self.diagram_type = "class"    # "class", "sequence", "component", "state", "dataflow"
        
        self.message_history = [{
            'role': 'system', 
            'content': '你是专业的软件工程设计智能体，可生成总体/详细设计图表。\
                       ```mermaid\
                        [mermaid代码]\
                        ```\
                        [mermaid代码]必须完全符合mermaid语法规范，特别注意:\
                        1. 数据流图使用flowchart TB或flowchart LR\
                        2. 类图使用classDiagram\
                        3. 时序图使用sequenceDiagram\
                        4. 确保所有节点和连接符正确\
                        5. 不要包含任何非mermaid语法的内容\
                        生成图表后，请简要解释图表内容。\
                        如果无法生成正确的mermaid代码，请直接说明而不生成错误图表。\
                        拒绝与软件设计无关的问题。'
        }]
        
        self.setup_ui()
        self.current_html = ""

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 顶部标题栏
        self.title_bar = QWidget(self)
        self.title_bar.setStyleSheet("background-color: #007acc;")
        self.title_bar.setFixedHeight(40)
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(10, 0, 10, 0)
        title_layout.addWidget(QLabel("软件工程设计图表生成器", alignment=Qt.AlignmentFlag.AlignCenter))
        
        self.close_button = QPushButton("✕")
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("""
            QPushButton {background-color: #e81123; color: white; border: none;}
            QPushButton:hover {background-color: #b50c1a;}
        """)
        self.close_button.clicked.connect(self.hide)
        title_layout.addWidget(self.close_button)
        self.title_bar.setLayout(title_layout)
        main_layout.addWidget(self.title_bar)

        # 设计类型选择
        design_type_layout = QHBoxLayout()
        design_type_layout.setContentsMargins(5, 5, 5, 5)
        
        self.overall_btn = QPushButton("总体设计")
        self.overall_btn.setCheckable(True); self.overall_btn.setChecked(True)
        self.overall_btn.clicked.connect(lambda: self.set_design_type("总体"))
        
        self.detailed_btn = QPushButton("详细设计")
        self.detailed_btn.setCheckable(True)
        self.detailed_btn.clicked.connect(lambda: self.set_design_type("详细"))
        
        # 设置设计类型按钮样式
        self.set_design_type_button_styles()
        
        design_group = QButtonGroup(self); design_group.addButton(self.overall_btn, 1)
        design_group.addButton(self.detailed_btn, 2); design_group.setExclusive(True)
        
        design_type_layout.addWidget(QLabel("设计类型:"))
        design_type_layout.addWidget(self.overall_btn); design_type_layout.addWidget(self.detailed_btn)
        design_type_layout.addStretch()
        main_layout.addLayout(design_type_layout)

        # 图表类型选择
        diagram_type_layout = QHBoxLayout()
        diagram_type_layout.setContentsMargins(5, 0, 5, 5)
        
        self.class_btn = QPushButton("类图(class)"); self.class_btn.setCheckable(True)
        self.class_btn.clicked.connect(lambda: self.set_diagram_type("类图"))
        
        self.sequence_btn = QPushButton("时序图(sequence)"); self.sequence_btn.setCheckable(True)
        self.sequence_btn.clicked.connect(lambda: self.set_diagram_type("时序图"))
        
        self.component_btn = QPushButton("组件图(component)"); self.component_btn.setCheckable(True)
        self.component_btn.clicked.connect(lambda: self.set_diagram_type("组件图"))
        
        self.state_btn = QPushButton("状态图(state)"); self.state_btn.setCheckable(True)
        self.state_btn.clicked.connect(lambda: self.set_diagram_type("状态图"))
        
        self.dataflow_btn = QPushButton("数据流图(DFD)"); self.dataflow_btn.setCheckable(True)
        self.dataflow_btn.clicked.connect(lambda: self.set_diagram_type("数据流图"))
        
        # 设置图表类型按钮样式
        self.set_diagram_type_button_styles()
        
        diagram_group = QButtonGroup(self)
        diagram_group.addButton(self.class_btn, 1); diagram_group.addButton(self.sequence_btn, 2)
        diagram_group.addButton(self.component_btn, 3); diagram_group.addButton(self.state_btn, 4)
        diagram_group.addButton(self.dataflow_btn, 5); diagram_group.setExclusive(True)
        
        diagram_type_layout.addWidget(QLabel("图表类型:"))
        diagram_type_layout.addWidget(self.class_btn); diagram_type_layout.addWidget(self.sequence_btn)
        diagram_type_layout.addWidget(self.component_btn); diagram_type_layout.addWidget(self.state_btn)
        diagram_type_layout.addWidget(self.dataflow_btn); diagram_type_layout.addStretch()
        main_layout.addLayout(diagram_type_layout)

        # 输入区
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(5, 5, 5, 5)
        
        self.input_entry = QLineEdit(placeholderText="输入设计需求(如：设计学生管理系统的用户认证模块)...")
        self.input_entry.setStyleSheet("padding: 8px; font-size: 14px; border: 1px solid #007acc;")
        self.input_entry.setFixedHeight(40)
        
        self.send_button = QPushButton("生成图表"); self.send_button.setFixedSize(100, 40)
        self.send_button.setStyleSheet("background-color: #007acc; color: white; font-weight: bold;")
        self.send_button.clicked.connect(self.on_send)
        self.input_entry.returnPressed.connect(self.on_send)
        
        input_layout.addWidget(self.input_entry); input_layout.addWidget(self.send_button)
        main_layout.addLayout(input_layout)

        # 结果展示区
        result_layout = QHBoxLayout()
        result_layout.setContentsMargins(5, 5, 5, 5)
        result_layout.setSpacing(5)
        
        # 左侧图表展示
        self.diagram_view = QWebEngineView()
        self.init_diagram_html()
        result_layout.addWidget(self.diagram_view, 3)  # 占3份宽度
        
        # 右侧解释说明
        self.explanation_area = QTextEdit()
        self.explanation_area.setReadOnly(True)
        self.explanation_area.setStyleSheet("border: 1px solid #ddd; padding: 10px;")
        result_layout.addWidget(self.explanation_area, 2)  # 占2份宽度
        
        main_layout.addLayout(result_layout)
        self.setLayout(main_layout)

    def set_design_type_button_styles(self):
        """设置设计类型按钮的样式"""
        button_style = """
            QPushButton {
                background-color: #f0f0f0;
                color: #333;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 6px 12px;
                margin-right: 5px;
            }
            QPushButton:checked {
                background-color: #007acc;
                color: white;
                border: 1px solid #007acc;
            }
            QPushButton:hover {
                border: 1px solid #007acc;
            }
        """
        self.overall_btn.setStyleSheet(button_style)
        self.detailed_btn.setStyleSheet(button_style)

    def set_diagram_type_button_styles(self):
        """设置图表类型按钮的样式"""
        button_style = """
            QPushButton {
                background-color: #f0f0f0;
                color: #333;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 6px 12px;
                margin-right: 5px;
            }
            QPushButton:checked {
                background-color: #3498db;
                color: white;
                border: 1px solid #3498db;
            }
            QPushButton:hover {
                border: 1px solid #3498db;
            }
        """
        self.class_btn.setStyleSheet(button_style)
        self.sequence_btn.setStyleSheet(button_style)
        self.component_btn.setStyleSheet(button_style)
        self.state_btn.setStyleSheet(button_style)
        self.dataflow_btn.setStyleSheet(button_style)

    def set_design_type(self, design_type):
        self.design_type = design_type
        self.overall_btn.setChecked(design_type == "总体")
        self.detailed_btn.setChecked(design_type == "详细")

    def set_diagram_type(self, diagram_type):
        self.diagram_type = diagram_type
        {
            "类图": self.class_btn.setChecked,
            "时序图": self.sequence_btn.setChecked,
            "组件图": self.component_btn.setChecked,
            "状态图": self.state_btn.setChecked,
            "数据流图": self.dataflow_btn.setChecked
        }[diagram_type](True)

    def init_diagram_html(self):
        html = """
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
        self.diagram_view.setHtml(html)

    def show_loading(self):
        """显示加载状态"""
        loading_html = f"""
            <div class="loading-message">
                <i class="fa fa-spinner fa-spin"></i> AI正在生成{self.get_diagram_title()}...
            </div>
        """
        self.diagram_view.page().runJavaScript(f"""
            document.getElementById('diagram-container').innerHTML = `{loading_html}`;
        """)
        
        # 更新解释区域
        self.explanation_area.setPlainText(f"AI正在生成{self.get_diagram_title()}，请稍候...")
        self.explanation_area.setStyleSheet("""
            border: 1px solid #007acc;
            padding: 10px;
            background-color: #e6f2ff;
        """)

    def hide_loading(self):
        """隐藏加载状态"""
        self.explanation_area.setStyleSheet("border: 1px solid #ddd; padding: 10px;")

    def get_diagram_title(self):
        """获取当前图表类型的标题"""
        diagram_titles = {
            "类图": "类图", "时序图": "时序图", "组件图": "组件图",
            "状态图": "状态图", "数据流图": "数据流图"
        }
        return f"{self.design_type.capitalize()}设计 - {diagram_titles.get(self.diagram_type, self.diagram_type)}"

    def on_send(self):
        message = self.input_entry.text().strip()
        if not message: 
            self.explanation_area.setPlainText("请输入设计需求后再生成图表")
            return
            
        self.message_history.append({"role": "user", "content": message})
        
        # 显示加载状态
        self.show_loading()
        
        self.worker = Worker(
            self.message_history.copy(),
            self.design_type,
            self.diagram_type
        )
        self.worker.finished.connect(self.handle_response)
        self.worker.error.connect(lambda e: self.explanation_area.setPlainText(f"错误: {e}"))
        self.worker.start()
        self.input_entry.clear()

    def handle_response(self, response, design_type, diagram_type):
        self.hide_loading()
        
        if not response or 'choices' not in response:
            self.explanation_area.setPlainText("错误: 未获取到有效响应")
            return
            
        reply = response['choices'][0]['message']['content']
        diagram_title = {
            "类图": "类图", "时序图": "时序图", "组件图": "组件图",
            "状态图": "状态图", "数据流图": "数据流图"
        }.get(diagram_type, diagram_type)
        
        try:
            if "```mermaid" in reply:
                # 解析Mermaid代码和解释文本
                parts = reply.split("```mermaid")
                mermaid_code = parts[1].split("```")[0].strip()
                explanation = parts[-1].split("```")[-1].strip()
                print(mermaid_code)
                
                # 更新图表
                diagram_html = f"""
                <h3 style="color: #007acc; border-bottom: 1px solid #ddd; padding-bottom: 5px;">
                    {design_type.capitalize()}设计 - {diagram_title}
                </h3>
                <div class="mermaid-container">
                    <pre class="mermaid">{mermaid_code}</pre>
                </div>
                <script>renderMermaid();</script>
                """
                self.diagram_view.page().runJavaScript(f"""
                var div = document.createElement('div');
                div.innerHTML = `{diagram_html}`;
                document.body.appendChild(div);
                window.scrollTo(0, document.body.scrollHeight);
                """)
                
                # 更新解释
                self.explanation_area.setPlainText(explanation or "图表解释说明")
                
                # 保存到历史
                self.message_history.append({"role": "assistant", "content": reply})
                
            else:
                self.explanation_area.setPlainText(f"错误: 未找到Mermaid图表代码\n\n原始响应: {reply}")
                
        except Exception as e:
            self.explanation_area.setPlainText(f"解析响应失败: {str(e)}\n\n原始响应: {reply}")

    def mousePressEvent(self, event):
        if self.title_bar.underMouse():
            self._drag_active = True
            self._drag_position = event.globalPosition().toPoint()
        event.ignore()

    def mouseMoveEvent(self, event):
        if self._drag_active:
            delta = event.globalPosition().toPoint() - self._drag_position
            self.move(self.pos() + delta)
            self._drag_position = event.globalPosition().toPoint()
        event.ignore()

    def mouseReleaseEvent(self, event):
        self._drag_active = False
        event.ignore()