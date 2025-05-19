from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class ChatWindow(QWidget):
    def __init__(self, module_name):
        super().__init__()
        self.setWindowTitle(module_name)
        self.setFixedSize(400, 620)
        self.init_ui(module_name)

    def init_ui(self, module_name):
        font = QFont("微软雅黑", 12)
        self.setFont(font)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # 模块名称显示
        module_label = QTextEdit()
        module_label.setReadOnly(True)
        module_label.setText(f"当前模块：{module_name}")
        module_label.setStyleSheet("background-color: #87CEEB; color: white; padding: 10px; font-weight: bold; border-radius: 8px;")
        layout.addWidget(module_label)

        # 对话显示区
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background-color: #f0f0f0; border-radius: 8px; padding: 10px;")
        layout.addWidget(self.chat_display)

        # 输入区
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("请输入您的问题...")
        self.input_field.setStyleSheet("border-radius: 8px; padding: 10px; border: 1px solid #ccc;")
        layout.addWidget(self.input_field)

        # 发送按钮
        send_button = QPushButton("发送")
        send_button.setStyleSheet("background-color: #6495ED; color: white; border-radius: 8px;")
        send_button.clicked.connect(self.send_message)
        layout.addWidget(send_button)

    def send_message(self):
        user_message = self.input_field.text()
        if user_message:
            self.chat_display.append(f"你: {user_message}")
            self.input_field.clear()
            # 模拟AI回复
            self.chat_display.append(f"AI: {user_message} 的回复")