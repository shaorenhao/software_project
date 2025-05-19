import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, QPoint


class  TermPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        # 去掉系统边框，自定义标题栏
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: #f9f9f9; border: 1px solid #ccc;")
        self._drag_active = False  # 用于窗口拖动
        self._drag_position = QPoint()
        self.setup_ui()

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
        self.title_label = QLabel("术语解析助手")
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

        # 支持关键词展示 - 高度贴近，仅占 25px
        self.keywords_label = QLabel("支持关键词：")
        self.keywords_label.setStyleSheet("padding: 0px 5px; font-size: 12px; color: #555555;")
        self.keywords_label.setFixedHeight(25)  # 减小高度
        main_layout.addWidget(self.keywords_label)

        # 对话区 - 占据主要高度
        self.dialogue_area = QTextEdit()
        self.dialogue_area.setReadOnly(True)
        self.dialogue_area.setStyleSheet(
            "background-color: #ffffff; border: 1px solid #ccc; border-radius: 0px;"
        )
        main_layout.addWidget(self.dialogue_area)

        # 输入区 - 高度贴近，仅占 60px，高度适中
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(5, 5, 5, 5)
        input_layout.setSpacing(5)

        self.input_entry = QLineEdit()
        self.input_entry.setPlaceholderText("请输入您的问题...")
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

        self.setLayout(main_layout)

        # 绑定发送事件
        self.send_button.clicked.connect(self.on_send)
        self.input_entry.returnPressed.connect(self.on_send)

    def on_send(self):
        text = self.input_entry.text().strip()
        if text:
            # 模拟发送内容
            self.dialogue_area.append(f"<b>我：</b> {text}")
            reply = f"这是概念解析助手的回复：{text}"
            self.dialogue_area.append(f"<b>助手：</b> {reply}\n")
            self.input_entry.clear()

    # ===========================
    # 窗口拖动逻辑
    # ===========================
    def mousePressEvent(self, event):
        event.ignore()

    def mouseMoveEvent(self, event):
        event.ignore()

    def mouseReleaseEvent(self, event):
        event.ignore()



# if __name__ == "__main__":
#     app = QApplication(sys.argv)

#     # 测试窗口
#     window = ConceptPage()
#     window.resize(700, 800)  # 宽度 700，高度 800，与主窗口高度保持一致
#     window.show()

#     sys.exit(app.exec())
