from PyQt6.QtWidgets import (
    QWidget, QPushButton, QLabel, QTextEdit,
    QHBoxLayout, QVBoxLayout
)
from PyQt6.QtCore import Qt

class CommunityPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.resize(400, 800)
        self.setWindowTitle("社区页面")
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setStyleSheet("""
            background-color: #f9f9f9; 
            border: 2px solid #007acc; 
            border-radius: 8px;
        """)

        self.init_ui()

    def init_ui(self):
        # 顶部按钮区域（只保留关闭按钮）
        self.top_buttons_widget = QWidget(self)
        top_layout = QHBoxLayout(self.top_buttons_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(10)

        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(40, 35)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setStyleSheet(self.close_button_style())

        top_layout.addStretch()
        top_layout.addWidget(self.close_btn)
        self.top_buttons_widget.setGeometry(self.width() - 70, 10, 70, 40)

        # 标题
        self.title_label = QLabel("社区交流", self)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")

        # 主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 60, 10, 10)
        self.main_layout.setSpacing(10)

        self.main_layout.addWidget(self.title_label)

        # 社区聊天展示区
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet(
            "background-color: white; border: 1px solid #ccc; border-radius: 5px;"
        )
        self.main_layout.addWidget(self.chat_display, stretch=7)

        # 输入区和发送按钮布局
        input_layout = QHBoxLayout()
        self.input_entry = QTextEdit()
        self.input_entry.setPlaceholderText("请输入消息...")
        self.input_entry.setStyleSheet(
            "border: 1px solid #ccc; border-radius: 5px; font-size: 14px; padding: 5px;"
        )
        self.input_entry.setFixedHeight(80)
        self.input_entry.installEventFilter(self)

        self.send_btn = QPushButton("发送")
        self.send_btn.setFixedSize(70, 80)
        self.send_btn.setStyleSheet(self.button_style())
        self.send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.input_entry)
        input_layout.addWidget(self.send_btn)

        self.main_layout.addLayout(input_layout)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.top_buttons_widget.move(self.width() - 70, 10)

    def send_message(self):
        message = self.input_entry.toPlainText().strip()
        if message:
            self.chat_display.append(f"我: {message}")
            self.input_entry.clear()

    def button_style(self):
        return """
            QPushButton {
                background-color: #007acc; 
                color: white; 
                border-radius: 5px; 
                font-weight: bold; 
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005f99;
            }
        """

    def close_button_style(self):
        return """
            QPushButton {
                background-color: #e81123; 
                color: white; 
                border-radius: 5px; 
                font-weight: bold; 
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #b50c1a;
            }
        """

    def eventFilter(self, obj, event):
        from PyQt6.QtGui import QKeyEvent
        if obj == self.input_entry and event.type() == QKeyEvent.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    return False  # 允许换行
                else:
                    self.send_message()
                    return True
        return super().eventFilter(obj, event)
