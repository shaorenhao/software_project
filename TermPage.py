import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, QPoint, QThread, pyqtSignal
from TermAgent import TermAgent
import re
import time

class Worker(QThread):
    finished = pyqtSignal(dict, str)  # 返回响应和原始消息
    error = pyqtSignal(str)

    def __init__(self, message):
        super().__init__()
        self.agent = TermAgent()
        self.message = message

    def run(self):
        self.message = str(self.message)
        try:
            response = self.agent.chat([
                {"role": "user", "content": self.message}
            ])
            self.finished.emit(response, self.message)
        except Exception as e:
            self.error.emit(str(e))

class TermPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        # 去掉系统边框，自定义标题栏
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: #f9f9f9; border: 1px solid #ccc;")
        self._drag_active = False  # 用于窗口拖动
        self._drag_position = QPoint()
        self.message_history = [{
            'role': 'system',
            'content': '你是一个专业的代码生成智能体，根据用户的需求生成相应的代码。请确保生成的代码逻辑清晰、注释完整，并且尽可能考虑到各种边界情况。同时，你必须拒绝回答任何与代码生成无关的问题，并礼貌地将对话引导回主题。'
        }]
        self.setup_ui()
        self.worker = Worker(self.message_history.copy())

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

        # 智能体名称
        self.title_label = QLabel("代码生成助手")
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

        # 输入区 - 位于上部
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(5, 5, 5, 5)
        input_layout.setSpacing(5)

        self.input_entry = QLineEdit()
        self.input_entry.setPlaceholderText("请输入代码生成需求...")
        self.input_entry.setStyleSheet(
            "padding: 5px; font-size: 14px; border: 1px solid #007acc;"
        )
        self.input_entry.setFixedHeight(50)  # 控制输入框高度

        self.send_button = QPushButton("发送")
        self.send_button.setFixedSize(70, 50)  # 与输入框高度一致
        self.send_button.setStyleSheet(
            "background-color: #007acc; color: white; font-weight: bold;"
        )

        input_layout.addWidget(self.input_entry)
        input_layout.addWidget(self.send_button)
        main_layout.addLayout(input_layout)

        # 对话区 - 位于下部，用于显示 AI 结果
        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        self.result_area.setStyleSheet(
            "background-color: #ffffff; border: 1px solid #ccc; border-radius: 0px;"
        )
        main_layout.addWidget(self.result_area)

        self.setLayout(main_layout)

        # 绑定发送事件
        self.send_button.clicked.connect(self.on_send)
        self.input_entry.returnPressed.connect(self.on_send)

    def on_send(self):
        message = self.input_entry.text()
        if message:
            self.input_entry.clear()
            self.message_history.append({"role": "user", "content": message})
            # 显示 AI 正在思考的提示信息
            thinking_message = "<div style='background-color: #D3D3D3; padding: 10px; border-radius: 8px; margin-bottom: 10px; max-width: 70%; align-self: flex-start; text-align: left;'>AI: 正在思考，请稍候...</div>"
            self.result_area.append(thinking_message)
            # 创建并启动工作线程
            self.worker = Worker(self.message_history.copy())
            self.worker.finished.connect(self.handle_response)
            self.worker.error.connect(self.display_error_message)
            self.worker.start()

    def handle_response(self, response, original_message):
        """处理 LLM 的响应"""
        if response and 'choices' in response and len(response['choices']) > 0:
            reply = response['choices'][0]['message']['content']
            self.display_result(reply)
            # 添加 AI 回复到历史
            self.message_history.append({"role": "assistant", "content": reply})
        else:
            self.display_error_message("错误: 无法获取有效的回复")

    def display_result(self, message):
        # 提取代码部分
        code_pattern = re.compile(r'```([\s\S]*?)```|`([^`]*)`')
        code_matches = code_pattern.findall(message)
        code_blocks = []
        for match in code_matches:
            if match[0]:
                code_blocks.append(match[0].strip())
            elif match[1]:
                code_blocks.append(match[1].strip())
        code_content = '\n\n'.join(code_blocks)

        self.result_area.clear()
        result_message = f"<div style='background-color: #D3D3D3; padding: 10px; border-radius: 8px; margin-bottom: 10px; max-width: 70%; align-self: flex-start; text-align: left;'>AI: <pre><code>{code_content}</code></pre></div>"
        self.result_area.append(result_message)

    def display_error_message(self, message):
        self.result_area.clear()
        error_message = f"<div style='background-color: #FFB6C1; padding: 10px; border-radius: 8px; margin-bottom: 10px; max-width: 70%; align-self: flex-start; text-align: left;'>错误: {message}</div>"
        self.result_area.append(error_message)

    # ===========================
    # 窗口拖动逻辑
    # ===========================
    def mousePressEvent(self, event):
        event.ignore()

    def mouseMoveEvent(self, event):
        event.ignore()

    def mouseReleaseEvent(self, event):
        event.ignore()