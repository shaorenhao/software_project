# CasePage.py
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QSizePolicy, QSplitter
)
from PyQt6.QtCore import Qt, QPoint
from CaseAgent import CaseAgent

class CasePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: #f9f9f9; border: 1px solid #ccc;")
        self._drag_active = False
        self._drag_position = QPoint()
        self.agent = CaseAgent()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Custom title bar
        self.title_bar = QWidget(self)
        self.title_bar.setStyleSheet("background-color: #007acc;")
        self.title_bar.setFixedHeight(40)
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(10, 0, 10, 0)
        title_layout.setSpacing(0)

        self.title_label = QLabel("例题解析助手")
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

        # Splitter for question and analysis areas
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setStyleSheet("QSplitter::handle { background: #ccc; }")

        # Question area
        self.question_area = QTextEdit()
        self.question_area.setReadOnly(True)
        self.question_area.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #ccc;
                padding: 10px;
                font-size: 14px;
                color: black;
            }
        """)
        splitter.addWidget(self.question_area)

        # Analysis area
        self.analysis_area = QTextEdit()
        self.analysis_area.setReadOnly(True)
        self.analysis_area.setStyleSheet("""
            QTextEdit {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                padding: 10px;
                font-size: 14px;
                color: black;
            }
        """)
        splitter.addWidget(self.analysis_area)

        splitter.setSizes([200, 300])
        main_layout.addWidget(splitter)

        # Button area
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(5, 5, 5, 5)
        button_layout.setSpacing(10)

        self.generate_btn = QPushButton("随机出题")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_question)
        button_layout.addWidget(self.generate_btn)

        self.analyze_btn = QPushButton("题目解析")
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        self.analyze_btn.clicked.connect(self.analyze_question)
        button_layout.addWidget(self.analyze_btn)

        # Input area
        self.input_entry = QLineEdit()
        self.input_entry.setPlaceholderText("输入要解析的问题...")
        self.input_entry.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #007acc;
                border-radius: 4px;
                color: black;
            }
        """)
        button_layout.addWidget(self.input_entry)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def generate_question(self):
        """Generate and display a random question"""
        question = self.agent.generate_question()
        self.question_area.setHtml(f"<b>题目：</b><br>{question}")

    def analyze_question(self):
        """Analyze the current or input question"""
        input_text = self.input_entry.text().strip()
        if input_text:
            analysis = self.agent.analyze_question(input_text)
        else:
            analysis = self.agent.analyze_question()
        
        self.analysis_area.setHtml(analysis)
        self.input_entry.clear()

    def mousePressEvent(self, event):
        event.ignore()

    def mouseMoveEvent(self, event):
        event.ignore()

    def mouseReleaseEvent(self, event):
        event.ignore()