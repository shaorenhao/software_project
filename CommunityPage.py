import requests
import time
import json
import logging
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QLabel, QTextEdit,
    QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class CommunityPage(QWidget):
    new_message_received = pyqtSignal(str)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.resize(400, 800)
        self.setWindowTitle("社区交流")
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setStyleSheet("""
            background-color: #f9f9f9; 
            border: 2px solid #007acc; 
            border-radius: 8px;
        """)
        self.last_fetch_time = 0  # 记录上次获取消息的时间戳
        self.init_ui()

        # 连接信号到槽函数
        self.new_message_received.connect(self.append_message)

        # 首次加载数据
        self.fetch_messages()

    def init_ui(self):
        # 顶部按钮区域（关闭按钮和更新按钮）
        self.top_buttons_widget = QWidget(self)
        top_layout = QHBoxLayout(self.top_buttons_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(10)

        self.update_btn = QPushButton("更新")
        self.update_btn.setFixedSize(60, 35)
        self.update_btn.clicked.connect(self.fetch_messages)
        self.update_btn.setStyleSheet(self.button_style())

        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(40, 35)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setStyleSheet(self.close_button_style())

        top_layout.addWidget(self.update_btn)
        top_layout.addStretch()
        top_layout.addWidget(self.close_btn)
        self.top_buttons_widget.setGeometry(10, 10, self.width() - 20, 40)

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
        self.top_buttons_widget.setGeometry(10, 10, self.width() - 20, 40)

    def send_message(self):
        message = self.input_entry.toPlainText().strip()
        if message:
            try:
                # 替换为你的华为云服务器IP
                api_url = "http://113.44.148.120:5000/messages"
                response = requests.post(api_url, json={"message": message})
                response.raise_for_status()

                # 显示自己发送的消息
                time_str = time.strftime("%H:%M", time.localtime())
                self.new_message_received.emit(f"我 [{time_str}]: {message}")

                # 发送成功后立即更新消息
                self.fetch_messages()

            except requests.exceptions.RequestException as e:
                self.new_message_received.emit(f"发送失败: {str(e)}")
            except Exception as e:
                logging.error(f"发送消息异常: {e}")
                self.new_message_received.emit("发送失败: 未知错误")
            finally:
                self.input_entry.clear()

    def fetch_messages(self):
        """手动获取消息（由更新按钮触发）"""
        try:
            # 显示加载中状态
            self.new_message_received.emit("正在获取最新消息...")

            # 构建请求URL
            api_url = f"http://113.44.148.120:5000/messages?timestamp={self.last_fetch_time}"
            logging.info(f"请求URL: {api_url}")

            # 发送请求
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()

            # 清除"正在获取"消息
            cursor = self.chat_display.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            cursor.movePosition(cursor.MoveOperation.StartOfLine)
            cursor.removeSelectedText()
            self.chat_display.setTextCursor(cursor)

            # 解析JSON响应
            try:
                new_messages = response.json()
                logging.info(f"获取到 {len(new_messages)} 条新消息")
            except json.JSONDecodeError as e:
                error_msg = f"解析消息失败: 服务器返回非JSON数据: {response.text[:100]}"
                logging.error(error_msg)
                self.new_message_received.emit(error_msg)
                return

            # 处理消息列表
            if not new_messages:
                self.new_message_received.emit("没有新消息")
                return

            # 按时间排序（确保消息按顺序显示）
            new_messages.sort(key=lambda x: x.get("timestamp", 0))

            for msg in new_messages:
                # 安全获取消息字段
                timestamp = msg.get("timestamp", 0)
                sender = msg.get("sender", "未知用户")
                message = msg.get("message", "")

                # 格式化时间
                if timestamp > 0:
                    time_str = time.strftime("%H:%M", time.localtime(timestamp))
                else:
                    time_str = "未知时间"

                # 构建完整消息并发送信号
                message_text = f"{sender} [{time_str}]: {message}"
                self.new_message_received.emit(message_text)

            # 更新最后获取时间
            timestamps = [msg.get("timestamp", 0) for msg in new_messages]
            if timestamps and max(timestamps) > self.last_fetch_time:
                self.last_fetch_time = max(timestamps)
                logging.info(f"更新last_fetch_time为: {self.last_fetch_time}")

        except requests.exceptions.Timeout:
            error_msg = "错误: 请求超时，请检查网络连接"
            logging.warning(error_msg)
            self.new_message_received.emit(error_msg)
        except requests.exceptions.ConnectionError:
            error_msg = "错误: 无法连接到服务器，请检查IP和端口"
            logging.error(error_msg)
            self.new_message_received.emit(error_msg)
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP错误: {e.response.status_code}"
            logging.error(error_msg)
            self.new_message_received.emit(error_msg)
        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            logging.exception(error_msg)  # 记录完整堆栈信息
            self.new_message_received.emit(error_msg)
    def append_message(self, message):
        """在主线程安全地更新UI"""
        self.chat_display.append(message)

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