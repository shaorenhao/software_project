import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QScrollArea, QFrame
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QTextCursor
from SettingsUI import SettingsUI
import json
import os
from api import LLMClient

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("软件助手")
        self.llm_client = None
        self.setGeometry(200, 200, 820, 620)
        self.initUI()
        self.load_config()

    def initUI(self):
        # 设置字体
        font = QFont("微软雅黑", 12)
        self.setFont(font)

        # 主容器
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # 标题栏
        header_layout = QHBoxLayout()
        ai_label = QLabel("DeepSeek-R1-Distill-Qwen-7B")
        ai_label.setFont(QFont("微软雅黑", 16, QFont.Weight.Bold))
        ai_label.setStyleSheet("font-weight: bold; font-size: 18px; background-color: #87CEEB; color: white; padding: 5px 10px; border-radius: 8px;")
        header_layout.addWidget(ai_label)

        settings_button = QPushButton("⚙ 设置")
        settings_button.setFixedSize(80, 35)
        settings_button.setStyleSheet("background-color: #FFA07A; color: white; border-radius: 8px; font-weight: bold;")
        settings_button.clicked.connect(self.open_settings)
        header_layout.addStretch()
        header_layout.addWidget(settings_button)

        # 对话区
        self.display_area = QTextEdit()
        self.display_area.setReadOnly(True)
        self.display_area.setMinimumHeight(300)
        self.display_area.setStyleSheet("background-color: #f0f0f0; border-radius: 8px; padding: 10px; border: 1px solid #ccc;")

        # 输入区
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("请输入您的问题...")
        self.input_field.setStyleSheet("border-radius: 8px; padding: 10px; border: 1px solid #ccc;")
        self.input_field.returnPressed.connect(self.send_message)

        send_button = QPushButton("发送")
        send_button.setFixedSize(80, 40)
        send_button.setStyleSheet("background-color: #6495ED; color: white; border-radius: 8px;")
        send_button.clicked.connect(self.send_message)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(send_button)

        # 布局排列
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.display_area)
        main_layout.addLayout(input_layout)

    def load_config(self):
        """加载API密钥和其他配置"""
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                config = json.load(f)
                api_key = config.get('api_key', '')
                self.llm_client = LLMClient(api_key="sk-nnnbfontekeesozhffpmluqdajbwzqvxeskyevmxwfignhgh")

    def send_message(self):
        message = self.input_field.text()
        if message:
            self.display_user_message(message)
            self.input_field.clear()
            
            if self.llm_client:
                # 显示"正在思考..."提示
                thinking_msg = "<div style='background-color: #D3D3D3; padding: 10px; border-radius: 8px; margin-bottom: 10px; max-width: 70%; align-self: flex-start; text-align: left;'>AI: 正在思考...</div>"
                self.display_area.append(thinking_msg)
                
                # 获取滚动条位置
                scroll_bar = self.display_area.verticalScrollBar()
                scroll_pos = scroll_bar.value()
                
                # 发送消息到LLM
                QTimer.singleShot(100, lambda: self.get_llm_response(message, scroll_pos))
            else:
                self.display_model_message("错误: 未配置API密钥，请在设置中添加")

    def get_llm_response(self, message, scroll_pos):
        """获取LLM回复并更新UI"""
        try:
            response = self.llm_client.chat_completion([
                {"role": "user", "content": message}
            ])
            
            if response and 'choices' in response and len(response['choices']) > 0:
                # # 移除"正在思考..."消息
                # cursor = self.display_area.textCursor()
                # cursor.movePosition(QTextCursor.MoveOperation.End)
                # cursor.select(QTextCursor.SelectionType.Document)
                # cursor.removeSelectedText()
                
                # 添加实际回复
                reply = response['choices'][0]['message']['content']
                self.display_model_message(reply)
                
                # 恢复滚动位置
                scroll_bar = self.display_area.verticalScrollBar()
                scroll_bar.setValue(scroll_pos)
            else:
                self.display_model_message("错误: 无法获取有效的回复")
        except Exception as e:
            self.display_model_message(f"错误: {str(e)}")

    def display_user_message(self, message):
        user_message = f"<div style='background-color: #87CEEB; padding: 10px; border-radius: 8px; margin-bottom: 10px; max-width: 70%; align-self: flex-end; color: #fff; text-align: right;'>你: {message}</div>"
        self.display_area.append(user_message)

    def display_model_message(self, message):
        model_message = f"<div style='background-color: #D3D3D3; padding: 10px; border-radius: 8px; margin-bottom: 10px; max-width: 70%; align-self: flex-start; text-align: left;'>{message}</div>"
        self.display_area.append(model_message)

    def open_settings(self):
        self.settings_window = SettingsUI()
        self.settings_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec())
