import sys
import os
import time
from utils.qt_compat import (QApplication, QWidget, QPushButton, QVBoxLayout, 
                              QListWidget, QListWidgetItem, QDialog, Qt, QTimer, QPoint, Signal,
                              get_global_pos, exec_dialog)
import pygetwindow as gw
import win32gui
import win32process

class FloatingButton(QWidget):
    request_sharing = Signal(str, str)  # Window title, Target IP

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(60, 60)
        
        self.btn = QPushButton("🚀", self)
        self.btn.setFixedSize(50, 50)
        self.btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 120, 215, 0.8);
                color: white;
                border-radius: 25px;
                font-size: 24px;
            }
            QPushButton:hover {
                background-color: rgba(0, 120, 215, 1.0);
            }
        """)
        self.btn.clicked.connect(self._on_click)
        
        self.current_window = None
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self._check_windows)
        self.check_timer.start(1000)
        
        self.drag_pos = None

    def _check_windows(self):
        try:
            active_win = gw.getActiveWindow()
            if active_win:
                title = active_win.title.lower()
                if (".docx" in title or ".xlsx" in title or ".pdf" in title) and ("word" in title or "excel" in title or "pdf" in title or "adobe" in title or "foxit" in title):
                    self.current_window = active_win
                    # Position button at top-right of the window
                    rect = active_win._rect
                    self.move(rect.right - 80, rect.top + 50)
                    self.show()
                    return
            self.hide()
        except Exception:
            self.hide()

    def _on_click(self):
        # Show online users to share with
        dialog = ShareDialog(self.main_window.discovery.peers, self)
        if exec_dialog(dialog) == QDialog.Accepted:
            target_ip = dialog.selected_ip
            if self.current_window:
                self.request_sharing.emit(self.current_window.title, target_ip)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = get_global_pos(event) - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.drag_pos:
            self.move(get_global_pos(event) - self.drag_pos)
            event.accept()

class ShareDialog(QDialog):
    def __init__(self, peers, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择共享目标")
        self.setFixedSize(250, 300)
        self.selected_ip = None
        
        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        for ip, info in peers.items():
            item = QListWidgetItem(f"{info['username']} ({ip})")
            item.setData(Qt.UserRole, ip)
            self.list_widget.addItem(item)
        layout.addWidget(self.list_widget)
        
        btn_layout = QVBoxLayout()
        share_btn = QPushButton("开始共享")
        share_btn.clicked.connect(self._accept)
        btn_layout.addWidget(share_btn)
        layout.addLayout(btn_layout)

    def _accept(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            self.selected_ip = selected_items[0].data(Qt.UserRole)
            self.accept()
        else:
            self.reject()
