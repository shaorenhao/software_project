import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, QPoint, QThread, pyqtSignal
from TestAgent import TestAgent
import time


class Worker(QThread):
    finished = pyqtSignal(dict, str)  # 返回响应和原始消息
    error = pyqtSignal(str)

    def __init__(self, message):
        super().__init__()
        self.agent = TestAgent()
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


class TestPage(QWidget):
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
            'content': '你是一个专业的软件工程课程助手的软件测试智能体，专注于协助软件测试。请按照以下格式生成测试用例：\n'
                       '影响的变量：[变量1, 变量2, ...]\n'
                       '测试用例：\n'
                       '- 变量取值：[取值1, 取值2, ...]，预期结果：[预期结果描述]\n'
                       '- 变量取值：[取值1, 取值2, ...]，预期结果：[预期结果描述]\n'
                       '请避免一直重复同一句话。同时，你必须拒绝回答任何与软件工程或软件测试无关的问题，并礼貌地将对话引导回主题。'
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
        self.title_label = QLabel("测试助手")
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

        # 输入区 - 高度贴近，仅占 60px，高度适中
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(5, 5, 5, 5)
        input_layout.setSpacing(5)

        self.input_entry = QLineEdit()
        self.input_entry.setPlaceholderText("请输入您想要的测试用例的相关信息...")
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

        # 对话区 - 占据主要高度
        self.dialogue_area = QTextEdit()
        self.dialogue_area.setReadOnly(True)
        self.dialogue_area.setStyleSheet(
            "background-color: #ffffff; border: 1px solid #ccc; border-radius: 0px;"
        )
        main_layout.addWidget(self.dialogue_area)

        self.setLayout(main_layout)

        # 绑定发送事件
        self.send_button.clicked.connect(self.on_send)
        self.input_entry.returnPressed.connect(self.on_send)

    def on_send(self):
        message = self.input_entry.text()
        if message:
            self.input_entry.clear()
            self.message_history.append({"role": "user", "content": message})
            # 创建并启动工作线程
            self.worker = Worker(self.message_history.copy())
            self.worker.finished.connect(self.handle_response)
            self.worker.error.connect(self.display_model_message)
            self.worker.start()

    def handle_response(self, response, original_message):
        """处理LLM的响应"""
        if response and 'choices' in response and len(response['choices']) > 0:
            reply = response['choices'][0]['message']['content']
            self.display_model_message(reply)
        else:
            self.display_error_message("错误: 无法获取有效的回复")

    def display_model_message(self, message):
        # 优化样式，增加换行、空行，调整文字大小和字体
        model_message = f"""
        <div style='
            background-color: #D3D3D3; 
            padding: 15px; 
            border-radius: 8px; 
            margin-bottom: 15px; 
            max-width: 70%; 
            align-self: flex-start; 
            text-align: left;
            font-family: Arial, sans-serif;
            font-size: 14px;
        '>
            AI: <pre style='white-space: pre-wrap; word-wrap: break-word;'>{message}</pre>
        </div>
        """
        self.dialogue_area.append(model_message)

    def display_error_message(self, message):
        error_message = f"<div style='color: red; padding: 10px; text-align: left;'>{message}</div>"
        self.dialogue_area.append(error_message)


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#
#     # 测试窗口
#     window = TestPage(None)
#     window.resize(700, 800)  # 宽度 700，高度 800，与主窗口高度保持一致
#     window.show()
#
#     sys.exit(app.exec())