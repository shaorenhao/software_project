import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QCheckBox, QLabel, QPushButton, QMainWindow
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QPalette, QColor
import json
import os

CONFIG_PATH = 'config.json'

class SettingsUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('设置界面')
        self.setGeometry(0, 0, 320, 240)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setStyleSheet("background-color: #f0f0f0; border-radius: 10px;")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title_label = QLabel("设置选项")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 是否启用专属数据库
        self.db_checkbox = QCheckBox('启用专属数据库')
        self.db_checkbox.setFont(QFont("Arial", 12))
        layout.addWidget(self.db_checkbox)

        # 是否启用智能体功能
        self.agent_checkbox = QCheckBox('启用智能体功能')
        self.agent_checkbox.setFont(QFont("Arial", 12))
        layout.addWidget(self.agent_checkbox)

        # 保存按钮
        self.save_button = QPushButton('保存设置')
        self.save_button.setFont(QFont("Arial", 12))
        self.save_button.setStyleSheet("background-color: #007bff; color: #ffffff; padding: 8px; border-radius: 5px;")
        self.save_button.clicked.connect(self.save_config)
        layout.addWidget(self.save_button)

        self.setLayout(layout)
        self.load_config()
        self.center()

    def save_config(self):
        config = {
            'enable_db': self.db_checkbox.isChecked(),
            'enable_agent': self.agent_checkbox.isChecked()
        }
        with open(CONFIG_PATH, 'w') as file:
            json.dump(config, file)
        self.close()

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as file:
                config = json.load(file)
                self.db_checkbox.setChecked(config.get('enable_db', False))
                self.agent_checkbox.setChecked(config.get('enable_agent', False))

    def center(self):
        screen = self.screen().geometry()
        size = self.geometry()
        new_left = (screen.width() - size.width()) // 2
        new_top = (screen.height() - size.height()) // 2
        self.move(QPoint(new_left, new_top))
