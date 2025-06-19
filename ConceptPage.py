import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QSizePolicy, QMessageBox,
    QScrollArea, QFrame, QMenu, QFileDialog
)
from PyQt6.QtCore import Qt, QPoint, QThread, pyqtSignal, QTimer, QEventLoop
from PyQt6.QtGui import (
    QTextCursor, QTextCharFormat, QColor, QAction, 
    QFont, QTextDocument, QPixmap, QIcon
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from dotenv import load_dotenv
from KnowledgeGraph import KnowledgeGraph
from ConceptAgent import ConceptAgent
import logging, time, json, pydot

load_dotenv()
# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Worker(QThread):
    finished = pyqtSignal(dict, str)  # response and original message
    error = pyqtSignal(str)
    thinking = pyqtSignal(bool)  # signal for thinking state

    def __init__(self, message, use_rag, use_kg):
        super().__init__()
        self.agent = ConceptAgent()
        self.message = message
        self.use_rag = use_rag
        self.use_kg = use_kg

    def run(self):
        self.thinking.emit(True)
        try:
            response = self.agent.chat(
                [{"role": "user", "content": self.message}],
                use_rag=self.use_rag,
                use_kg=self.use_kg
            )
            self.finished.emit(response, self.message)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.thinking.emit(False)

class ConceptPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
        self.setup_connections()
        self.initialize_state()
        self.total_html=""
        try:
            self.agent = ConceptAgent()
            
        except Exception as e:
            self.display_error_message(f"初始化失败: {str(e)}")

    def get_html(self):
        """同步方式获取 HTML 内容"""
        loop = QEventLoop()
        html_container = {}

        def handle_html(html):
            html_container["html"] = html
            loop.quit()

        self.dialogue_area.page().toHtml(handle_html)
        loop.exec()  # 阻塞，直到 handle_html 调用 loop.quit()

        return html_container["html"]

    def setup_ui(self):
        """Initialize all UI components with enhanced styling"""
        self.setWindowTitle("概念解析助手")
        self.setMinimumSize(500, 700)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Title bar
        self.title_bar = QWidget()
        self.title_bar.setStyleSheet("""
            background-color: #2c3e50;
            padding: 5px;
        """)
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(10, 5, 10, 5)
        
        # Title label
        title_label = QLabel("概念解析助手")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # Knowledge graph toggle
        self.kg_toggle = QPushButton("🌐 知识图谱: ON")
        self.kg_toggle.setCheckable(True)
        self.kg_toggle.setChecked(True)
        self.kg_toggle.setStyleSheet(self.get_toggle_style(True))
        title_layout.addWidget(self.kg_toggle)
        
        # RAG toggle
        self.rag_toggle = QPushButton("🔍 知识库: ON")
        self.rag_toggle.setCheckable(True)
        self.rag_toggle.setChecked(True)
        self.rag_toggle.setStyleSheet(self.get_toggle_style(True))
        title_layout.addWidget(self.rag_toggle)
        
        # History button
        self.history_button = QPushButton("📜 历史")
        self.history_button.setStyleSheet(self.get_button_style())
        title_layout.addWidget(self.history_button)
        
        # Export button
        self.export_button = QPushButton("💾 导出")
        self.export_button.setStyleSheet(self.get_button_style())
        title_layout.addWidget(self.export_button)
        
        # Close button
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
        title_layout.addWidget(self.close_button)
        
        self.title_bar.setLayout(title_layout)
        main_layout.addWidget(self.title_bar)
        
        # Content area
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f7fa;
                border: none;
            }
        """)
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(15)
        
        # Dialogue area - now using QWebEngineView
        self.dialogue_area = QWebEngineView()
        self.init_html_content()
        content_layout.addWidget(self.dialogue_area)
        
        # Input area
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        
        self.input_entry = QLineEdit()
        self.input_entry.setPlaceholderText("输入软件工程概念或问题...")
        self.input_entry.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #3498db;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
        """)
        input_layout.addWidget(self.input_entry, stretch=1)
        
        self.viz_button = QPushButton("可视化图谱")
        self.viz_button.setFixedSize(120, 50)
        self.viz_button.setStyleSheet(self.get_action_button_style("#9b59b6"))
        input_layout.addWidget(self.viz_button)
        
        self.send_button = QPushButton("发送")
        self.send_button.setFixedSize(100, 50)
        self.send_button.setStyleSheet(self.get_action_button_style("#3498db"))
        input_layout.addWidget(self.send_button)
        
        content_layout.addLayout(input_layout)
        content_frame.setLayout(content_layout)
        main_layout.addWidget(content_frame, stretch=1)
        
        # Status bar
        self.status_bar = QLabel("就绪")
        self.status_bar.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                color: #7f8c8d;
                padding: 5px 10px;
                font-size: 12px;
                border-top: 1px solid #ddd;
            }
        """)
        main_layout.addWidget(self.status_bar)
        
        self.setLayout(main_layout)
        
        # History dialog
        self.setup_history_dialog()

        self.display_welcome_message()

    def init_html_content(self):
        """Initialize the HTML content for the WebEngineView"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            
            <style>
                .user-message {
                    background-color: #3498db;
                    color: white;
                    padding: 12px;
                    border-radius: 12px;
                    margin: 10px 0;
                    max-width: 80%;
                    margin-left: auto;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .ai-message {
                    background-color: #f8f9fa;
                    color: #333;
                    padding: 12px;
                    border-radius: 12px;
                    margin: 10px 0;
                    max-width: 80%;
                    border: 1px solid #ddd;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .error-message {
                    background-color: #ffebee;
                    color: #c62828;
                    padding: 12px;
                    border-radius: 12px;
                    margin: 10px 0;
                    max-width: 80%;
                    border: 1px solid #ffcdd2;
                }
                .thinking-message {
                    background-color: #ecf0f1;
                    color: #333;
                    padding: 12px;
                    border-radius: 12px;
                    margin: 10px 0;
                    max-width: 80%;
                    font-style: italic;
                }
                .welcome-message {
                    background-color: white;
                    padding: 15px;
                    border-radius: 8px;
                    margin-bottom: 15px;
                    border: 1px solid #ddd;
                }
                .graph-container {
                    width: 100%;
                    height: 400px;
                    border: 1px solid #ddd;
                    margin: 10px 0;
                    background: white;
                    border-radius: 5px;
                    overflow: auto;
                }
                .graph-controls {
                    margin-top: 10px;
                }
                .graph-button {
                    padding: 5px 10px;
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    margin-right: 10px;
                }
                .download-button {
                    background-color: #2ecc71;
                }
            </style>
        </head>
        <body>
            <div id="content">
            <div class="welcome-message">
            <h2 style="color: #2c3e50;">欢迎使用知识图谱概念助手</h2>
            <p>我可以帮助您探索软件工程概念及其相互关系：</p>
            <ul>
                <li>使用<b>知识图谱</b>查看概念间关系</li>
                <li>使用<b>知识库</b>获取详细解释</li>
                <li>点击<b>可视化图谱</b>查看概念网络</li>
                <li>使用<b>历史</b>功能查看对话记录</li>
            </ul>
            <p>示例问题：</p>
            <ul>
                <li>"什么是多态？它与设计模式有什么关系？"</li>
                <li>"解释MVC架构模式"</li>
                <li>"比较继承和组合的优缺点"</li>
                <li>"敏捷开发和传统瀑布模型有什么区别？"</li>
            </ul> 
            </div>
            </div>
        </body>
        </html>
        """
        self.dialogue_area.setHtml(html_content)

    def setup_history_dialog(self):
        """Setup history dialog"""
        self.history_dialog = QWidget()
        self.history_dialog.setWindowTitle("对话历史")
        self.history_dialog.setWindowModality(Qt.WindowModality.NonModal)
        self.history_dialog.resize(600, 500)
        
        layout = QVBoxLayout()
        
        self.history_list = QWebEngineView()
        self.history_list.setHtml("<body style='background-color:white; padding:10px;'></body>")
        
        layout.addWidget(self.history_list)
        
        button_layout = QHBoxLayout()
        self.clear_history_button = QPushButton("清空历史")
        self.clear_history_button.setStyleSheet(self.get_button_style())
        self.clear_history_button.clicked.connect(self.clear_history)
        button_layout.addWidget(self.clear_history_button)
        
        self.close_history_button = QPushButton("关闭")
        self.close_history_button.setStyleSheet(self.get_button_style())
        self.close_history_button.clicked.connect(self.history_dialog.close)
        button_layout.addWidget(self.close_history_button)
        
        layout.addLayout(button_layout)
        self.history_dialog.setLayout(layout)

    def setup_connections(self):
        """Setup signal-slot connections"""
        self.send_button.clicked.connect(self.on_send)
        self.input_entry.returnPressed.connect(self.on_send)
        self.close_button.clicked.connect(self.close)
        self.kg_toggle.toggled.connect(self.toggle_knowledge_graph)
        self.rag_toggle.toggled.connect(self.toggle_rag)
        self.viz_button.clicked.connect(self.generate_visualization)
        self.history_button.clicked.connect(self.show_history)
        self.export_button.clicked.connect(self.export_conversation)

    def initialize_state(self):
        """Initialize application state"""
        self.use_kg = True
        self.use_rag = True
        self.is_thinking = False
        self.message_history = [{
            'role': 'system',
            'content': """你是专业的软件工程概念助手，请以清晰、结构化的方式回答问题，包括：
                        1. 定义：简明定义
                        2. 分类：所属类别
                        3. 应用：实际应用场景
                        4. 相关：相关概念"""
        }]

    def get_toggle_style(self, active):
        """Get stylesheet for toggle buttons"""
        color = "#27ae60" if active else "#e74c3c"
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                font-weight: bold;
                border-radius: 5px;
                font-size: 14px;
                padding: 5px 10px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {'#2ecc71' if active else '#c0392b'};
            }}
        """

    def get_button_style(self):
        """Get default button style"""
        return """
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                font-size: 14px;
                padding: 5px 10px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """

    def get_action_button_style(self, color):
        """Get style for action buttons"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                font-weight: bold;
                border-radius: 8px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {'#8e44ad' if color == '#9b59b6' else '#2980b9'};
            }}
            QPushButton:disabled {{
                background-color: #95a5a6;
            }}
        """

    def toggle_knowledge_graph(self, checked):
        """Toggle knowledge graph usage"""
        self.use_kg = checked
        self.kg_toggle.setText("🌐 知识图谱: ON" if checked else "🌐 知识图谱: OFF")
        self.kg_toggle.setStyleSheet(self.get_toggle_style(checked))
        self.status_bar.setText(f"知识图谱功能已{'启用' if checked else '禁用'}")

    def toggle_rag(self, checked):
        """Toggle RAG usage"""
        self.use_rag = checked
        self.rag_toggle.setText("🔍 知识库: ON" if checked else "🔍 知识库: OFF")
        self.rag_toggle.setStyleSheet(self.get_toggle_style(checked))
        self.status_bar.setText(f"知识库检索功能已{'启用' if checked else '禁用'}")

    def on_send(self):
        """Handle send button click"""
        message = self.input_entry.text().strip()
        if not message or self.is_thinking:
            return
            
        self.display_user_message(message)
        self.input_entry.clear()
        self.status_bar.setText("正在处理请求...")
        
        # Create and start worker thread
        self.worker = Worker(message, self.use_rag, self.use_kg)
        self.worker.finished.connect(self.handle_response)
        self.worker.error.connect(self.display_error_message)
        self.worker.thinking.connect(self.set_thinking_state)
        self.worker.start()

    def set_thinking_state(self, thinking):
        """Update UI during thinking state"""
        self.is_thinking = thinking
        self.send_button.setDisabled(thinking)
        self.viz_button.setDisabled(thinking)
        
        if thinking:
            self.display_thinking_message()
        else:
            self.remove_thinking_message()
            self.status_bar.setText("就绪")

    def display_thinking_message(self):
        """Show thinking indicator"""
        thinking_html = """
        <div class="thinking-message">
            💭 正在思考...
        </div>
        """
        self.append_html(thinking_html)

    def remove_thinking_message(self):
        """Remove thinking indicator"""
        js_code = """
        var content = document.getElementById('content');
        var lastChild = content.lastChild;
        if (lastChild && lastChild.classList.contains('thinking-message')) {
            content.removeChild(lastChild);
        }
        """
        self.dialogue_area.page().runJavaScript(js_code)

    def handle_response(self, response, original_message):
        """Handle LLM response"""
        if response and 'choices' in response and len(response['choices']) > 0:
            reply = response['choices'][0]['message']['content']
            self.display_model_message(reply)
            self.message_history.append({"role": "assistant", "content": reply})
        else:
            self.display_error_message("无法获取有效回复")

    def dot_to_cytoscape_json(self,dot_str):
        """将 DOT 字符串转为 cytoscape.js 需要的 JSON 格式"""
        graphs = pydot.graph_from_dot_data(dot_str)
        graph = graphs[0]

        elements = []
        node_ids = set()

        for node in graph.get_nodes():
            name = node.get_name().strip('"')
            if name == 'node':  # 跳过默认定义节点
                continue
            node_ids.add(name)
            elements.append({"data": {"id": name, "label": name}})

        for edge in graph.get_edges():
            src = edge.get_source().strip('"')
            dst = edge.get_destination().strip('"')
            label = edge.get_label().strip('"') if edge.get_label() else ""
            if src not in node_ids:
                elements.append({"data": {"id": src, "label": src}})
                node_ids.add(src)
            if dst not in node_ids:
                elements.append({"data": {"id": dst, "label": dst}})
                node_ids.add(dst)
            elements.append({
                "data": {
                    "source": src,
                    "target": dst,
                    "label": label
                }
            })

        return elements

    def generate_visualization(self):
        """生成知识图谱可视化（使用 cytoscape.js）"""
        if not self.message_history or len(self.message_history) < 2:
            self.status_bar.setText("无足够对话历史生成可视化")
            return
        
        last_user_message = None
        for msg in reversed(self.message_history[-5:]):
            if msg['role'] == 'user':
                last_user_message = msg['content'].strip()
                break
        
        if not last_user_message:
            self.status_bar.setText("未找到有效的概念查询")
            return
        try:
            self.status_bar.setText(f"正在生成 {last_user_message} 的知识图谱...")
            QApplication.processEvents()
            
            start_time = time.time()
            dot = self.agent.knowledge_graph.visualize_subgraph(
                last_user_message, 
                depth=2
            )
            

            dot_str = dot  # 清理字符串格式

            elements = self.dot_to_cytoscape_json(dot_str)
            elements_json = json.dumps(elements)

            visualization_html = f"""
            <div class="ai-message">
                <h3>知识图谱可视化</h3>
                <p><b>中心概念</b>: {last_user_message}</p>
                <p><b>生成时间</b>: {(time.time() - start_time):.2f}秒</p>
                <div id="cy" style="width: 100%; height: 500px; background: white; border: 1px solid #ccc;"></div>
            </div>

            <!-- cytoscape.js CDN -->
            <script src="https://unpkg.com/cytoscape@3.24.0/dist/cytoscape.min.js"></script>
            <script>
            document.addEventListener("DOMContentLoaded", function() {{
                var cy = cytoscape({{
                    container: document.getElementById('cy'),
                    elements: {elements_json},
                    style: [
                        {{
                            selector: 'node',
                            style: {{
                                'background-color': '#0074D9',
                                'label': 'data(label)',
                                'color': '#fff',
                                'text-valign': 'center',
                                'text-halign': 'center',
                                'text-outline-color': '#0074D9',
                                'text-outline-width': 2
                            }}
                        }},
                        {{
                            selector: 'edge',
                            style: {{
                                'width': 2,
                                'line-color': '#aaa',
                                'target-arrow-color': '#aaa',
                                'target-arrow-shape': 'triangle',
                                'curve-style': 'bezier',
                                'label': 'data(label)',
                                'font-size': 10,
                                'text-background-color': '#fff',
                                'text-background-opacity': 1,
                                'text-background-padding': 2
                            }}
                        }}
                    ],
                    layout: {{
                        name: 'breadthfirst',
                        directed: true,
                        padding: 20
                    }}
                }});
            }});
            </script>
            """
            
            total_html=self.get_html()[0:-14]+visualization_html+'''
</body></html>
'''         
            self.dialogue_area.setHtml(total_html)
            
            self.dialogue_area.page().runJavaScript("""
            window.scrollTo(0, document.body.scrollHeight);
            """)
            self.status_bar.setText(f"成功生成 {last_user_message} 的知识图谱")
            

        except Exception as e:
            error_msg = f"生成可视化失败: {str(e)}"
            logger.error(error_msg)
            self.display_error_message(error_msg)
            self.status_bar.setText("可视化生成失败")
            

    def show_history(self):
        """Show conversation history"""
        history_html = "<div style='padding:10px;'>"
        for msg in self.message_history:
            if msg['role'] == 'system':
                continue
                
            role = "用户" if msg['role'] == 'user' else "助手"
            message_class = "user-message" if msg['role'] == 'user' else "ai-message"
            history_html += f"""
            <div class="{message_class}">
                <b>{role}:</b> {msg['content']}
            </div>
            """
        history_html += "</div>"
        
        self.history_list.setHtml(f"""
        <html>
        <head>
            <style>
                .user-message {{
                    background-color: #3498db;
                    color: white;
                    padding: 10px;
                    border-radius: 8px;
                    margin: 10px 0;
                }}
                .ai-message {{
                    background-color: #f8f9fa;
                    padding: 10px;
                    border-radius: 8px;
                    margin: 10px 0;
                    border: 1px solid #ddd;
                }}
            </style>
        </head>
        <body>
            {history_html}
        </body>
        </html>
        """)
        self.history_dialog.show()

    def clear_history(self):
        """Clear conversation history"""
        self.message_history = [{
            'role': 'system',
            'content': """你是专业的软件工程概念助手，请以清晰、结构化的方式回答问题"""
        }]
        self.history_list.setHtml("<body style='background-color:white; padding:10px;'></body>")
        self.init_html_content()

    def export_conversation(self):
        """Export conversation to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存对话", "", "HTML Files (*.html);;Text Files (*.txt)"
        )
        if file_path:
            if file_path.endswith('.html'):
                # Get the current HTML content
                def save_html(html):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(html)
                
                self.dialogue_area.page().toHtml(save_html)
            else:
                # Get plain text
                def save_text(text):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(text)
                
                self.dialogue_area.page().toPlainText(save_text)
            
            self.status_bar.setText(f"对话已保存到: {file_path}")

    def display_welcome_message(self):
        """Display enhanced welcome message"""
        welcome_msg = """
        
        
        """
        self.display_model_message(welcome_msg)

    def append_html(self, html_content):
        """Append HTML content to dialogue area"""
        js_code = f"""
        var div = document.createElement('div');
        div.innerHTML = `{html_content}`;
        document.getElementById('content').appendChild(div);
        window.scrollTo(0, document.body.scrollHeight);
        """
        self.dialogue_area.page().runJavaScript(js_code)

    def display_user_message(self, message):
        """Display user message in dialogue area"""
        user_html = f"""
        <div class="user-message">
            {message}
        </div>
        """
        self.append_html(user_html)
        self.message_history.append({"role": "user", "content": message})

    def display_model_message(self, message):
        """Display model response in dialogue area"""
        ai_html = f"""
        <div class="ai-message">
            {message}
        </div>
        """
        self.append_html(ai_html)

    def display_error_message(self, message):
        """Display error message in dialogue area"""
        error_html = f"""
        <div class="error-message">
            ⚠️ {message}
        </div>
        """
        self.append_html(error_html)
        self.status_bar.setText(f"错误: {message}")

    def closeEvent(self, event):
        """Handle window close event"""
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.terminate()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style and font
    app.setStyle("Fusion")
    app.setFont(QFont("Arial", 12))
    
    window = ConceptPage(None)
    window.resize(1000, 800)
    window.show()
    
    sys.exit(app.exec())