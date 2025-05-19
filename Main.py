from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
    QHBoxLayout, QFrame, QLineEdit, QGridLayout
)

from PyQt6.QtCore import Qt, QPoint, QEvent
import sys
from CommunityPage import CommunityPage  # 假设社区页面类已定义
from ConceptPage import ConceptPage
from CasePage import CasePage
from RequirementPage import RequirementPage
from DesignPage import DesignPage
from TestPage import TestPage
from TermPage import TermPage


class DraggableWindow(QWidget):
    def __init__(self):
        super().__init__()
        self._drag_active = False
        self._drag_position = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if event.pos().y() <= 50:
                self._drag_active = True
                self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_active and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_active = False


class MainScreen(DraggableWindow):
    def __init__(self):
        super().__init__()
        self.resize(600, 800)
        self.setWindowTitle("软件工程学习助手 - 主界面")
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setStyleSheet("background-color: #f0f0f0;")
        self.setup_ui()
        self.center_on_screen()

        # 初始化功能页面，传入主窗口实例 self
        self.function_pages = {
            0: ConceptPage(self),
            1: CasePage(self),
            2: RequirementPage(self),
            3: DesignPage(self),
            4: TestPage(self),
            5: TermPage(self)
        }
        screen_width = QApplication.primaryScreen().geometry().width()
        for page in self.function_pages.values():
            page.setGeometry(-screen_width, 0, screen_width - self.width() - 10, self.height())
            page.hide()
        # 初始化社区窗口，传入主窗口实例 self
        self.community_window = CommunityPage(self)
        self.community_window.hide()  # 初始隐藏

        self._community_shown = False  # 标记社区窗口是否已显示过

    def setup_ui(self):
        # 顶部按钮容器
        self.top_buttons_widget = QWidget(self)
        self.top_buttons_widget.setGeometry(self.width() - 150 - 20, 10, 150, 35)
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(10)
        self.top_buttons_widget.setLayout(top_layout)

        self.sidebar_btn = QPushButton("社区")
        self.sidebar_btn.clicked.connect(self.on_sidebar_clicked)
        self.sidebar_btn.setStyleSheet(self.button_style())
        self.minimize_btn = QPushButton("-")
        self.minimize_btn.clicked.connect(self.showMinimized)
        self.minimize_btn.setStyleSheet(self.button_style())
        self.close_btn = QPushButton("✕")
        self.close_btn.clicked.connect(self.close_all)
        self.close_btn.setStyleSheet(self.close_button_style())

        btn_width = (150 - 20) // 3
        for btn in (self.sidebar_btn, self.minimize_btn, self.close_btn):
            btn.setFixedSize(btn_width, 35)
            top_layout.addWidget(btn)

        # 中心标题，放置在按钮下方
        self.title_label = QLabel("软件工程学习助手", self)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333333;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setGeometry(self.width() // 2 - 100, 50, 200, 40)

        # 功能按钮区域，调整为2*3布局
        self.button_frame = QFrame(self)
        self.button_frame.setGeometry(50, 110, self.width() - 100, 160)
        self.button_frame.setStyleSheet("border: 2px solid #007acc; background-color: #e0e0e0;")
        button_layout = QGridLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(10, 10, 10, 10)

        button_names = ["概念解析", "案例解析", "需求分析", "软件设计", "测试", "术语解析"]
        positions = [(i, j) for i in range(2) for j in range(3)]

        for index, position in enumerate(positions):
            btn = QPushButton(button_names[index])
            btn.setFixedSize(120, 65)
            btn.setStyleSheet("background-color: #007acc; color: #fff; font-weight: bold;")
            btn.clicked.connect(lambda _, idx=index: self.on_button_clicked(idx))
            button_layout.addWidget(btn, *position)

        self.button_frame.setLayout(button_layout)

        # 对话区
        dialogue_height = 400
        self.dialogue_frame = QFrame(self)
        self.dialogue_frame.setGeometry(50, 280, self.width() - 100, dialogue_height)
        self.dialogue_frame.setStyleSheet("background-color: white; border: 2px solid black; border-radius: 8px;")
        self.dialogue_label = QLabel("AI对话内容展示区域", self.dialogue_frame)
        self.dialogue_label.setGeometry(10, 10, self.dialogue_frame.width() - 20, self.dialogue_frame.height() - 50)
        self.dialogue_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 输入区
        self.input_frame = QFrame(self)
        self.input_frame.setGeometry(50, 280 + dialogue_height + 10, self.width() - 100, 60)
        self.input_frame.setStyleSheet("background-color: #e0e0e0; border: 2px solid #007acc; border-radius: 8px;")
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(10, 10, 10, 10)
        input_layout.setSpacing(10)

        self.input_entry = QLineEdit()
        self.input_entry.setStyleSheet("padding: 8px; font-size: 14px;")
        self.input_entry.setPlaceholderText("请输入内容...")
        self.send_btn = QPushButton("发送")
        self.send_btn.setFixedSize(80, 40)  # 调整高度
        self.send_btn.setStyleSheet(self.button_style())
        input_layout.addWidget(self.input_entry)
        input_layout.addWidget(self.send_btn)
        self.input_frame.setLayout(input_layout)
    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange:
            if self.windowState() & Qt.WindowState.WindowMinimized:
                # 主窗口最小化，其他窗口也最小化
                for page in self.function_pages.values():
                    page.showMinimized()
                if self.community_window.isVisible():
                    self.community_window.showMinimized()
            elif self.windowState() == Qt.WindowState.WindowNoState:
                # 主窗口恢复，其他窗口也恢复显示
                for page in self.function_pages.values():
                    if page.isVisible():
                        page.showNormal()
                if self.community_window.isVisible():
                    self.community_window.showNormal()
    def moveEvent(self, event):
        super().moveEvent(event)
        main_pos = self.pos()

        # 先调整功能窗口位置和大小
        screen = QApplication.primaryScreen()
        screen_width = screen.geometry().width()
        main_width = self.width()
        left_space = main_pos.x()
        func_width = min(left_space, 800)
        community_width = 350
        right_space = screen_width - (main_pos.x() + main_width)
        if right_space < community_width + 10:
            func_width = max(0, func_width - (community_width + 10 - right_space))

        for page in self.function_pages.values():
            if page.isVisible():
                func_x = main_pos.x() - func_width - 10
                func_y = main_pos.y()
                page.setGeometry(func_x, func_y, func_width, self.height())

        # 调整社区窗口位置和大小（仅当可见）
        if self.community_window.isVisible():
            community_x = main_pos.x() + main_width + 10
            community_y = main_pos.y()
            self.community_window.setGeometry(community_x, community_y, community_width, self.height())
            
    def on_button_clicked(self, index):
        button_names = ["概念解析", "案例解析", "需求分析", "软件设计", "测试", "术语解析"]
        print(f"跳转到 {button_names[index]}")

        # 隐藏所有功能页面，保证只显示一个
        for page in self.function_pages.values():
            page.hide()

        page = self.function_pages.get(index)
        if page:
        # 确保功能页面宽度和位置由 update_community_position 控制
            page.show()
            self.update_community_position()
            page.raise_()


    def on_sidebar_clicked(self):
        # 初次点击时显示并调整大小
        if not self._community_shown:
            community_width = 350
            community_height = self.height()
            main_pos = self.pos()
            community_x = main_pos.x() + self.width() + 10
            community_y = main_pos.y()
            self.community_window.setGeometry(community_x, community_y, community_width, community_height)
            self.community_window.show()
            self.community_window.raise_()
            self._community_shown = True
        else:
            # 如果已显示，则切换显示/隐藏
            if self.community_window.isVisible():
                self.community_window.hide()
            else:
                self.community_window.show()
                self.community_window.raise_()

    def close_all(self):
        for page in self.function_pages.values():
            page.close()
        self.community_window.close()
        self.close()

    def button_style(self):
        return """
            QPushButton {
                background-color: #007acc; color: white; border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005f99;
            }
        """

    def close_button_style(self):
        return """
            QPushButton {
                background-color: #e81123; color: white; border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b50c1a;
            }
        """

    def center_on_screen(self):
        screen = QApplication.primaryScreen()
        geo = screen.geometry()
        community_width = 350  # 假定社区界面最大宽度
        x = geo.width() - self.width() - community_width - 10  # 主界面右侧留社区宽度+10px间距
        y = (geo.height() - self.height()) // 2
        self.move(x, y)

    
    def update_community_position(self):
        main_pos = self.pos()
        screen = QApplication.primaryScreen()
        screen_width = screen.geometry().width()

        main_width = self.width()
        left_space = main_pos.x()
        func_width = min(left_space, 800)
        community_width = 350
        right_space = screen_width - (main_pos.x() + main_width)
        if right_space < community_width + 10:
            func_width = max(0, func_width - (community_width + 10 - right_space))

        for page in self.function_pages.values():
            if page.isVisible():
                func_x = main_pos.x() - func_width - 10
                func_y = main_pos.y()
                page.setGeometry(func_x, func_y, func_width, self.height())

        if self.community_window.isVisible():
            community_x = main_pos.x() + main_width + 10
            community_y = main_pos.y()
            self.community_window.setGeometry(community_x, community_y, community_width, self.height())




if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainScreen()
    main_window.show()
    sys.exit(app.exec())
