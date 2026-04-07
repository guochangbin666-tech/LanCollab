import sys
import os
from utils.qt_compat import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QLabel, QListWidget, QListWidgetItem, QPushButton, 
                             QHBoxLayout, QIcon, QAction, Qt, Signal)
import pystray
from PIL import Image, ImageDraw
import threading

from network.discovery import DiscoveryManager
from utils.config import Config
from ui.settings_dialog import SettingsDialog
from utils.autostart import set_autostart

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = Config.load()
        self.discovery = DiscoveryManager(self.config["username"], self.config["room_code"])
        
        self.setWindowTitle("LanCollab - 局域网实时协作")
        self.resize(300, 500)
        
        # UI Setup
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        self.header = QLabel(f"当前用户: {self.config['username']} (房间: {self.config['room_code']})")
        self.header.setStyleSheet("font-weight: bold; padding: 10px;")
        layout.addWidget(self.header)
        
        self.user_list = QListWidget()
        layout.addWidget(self.user_list)
        
        # Bottom Buttons
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("手动刷新")
        refresh_btn.clicked.connect(self._refresh_discovery)
        btn_layout.addWidget(refresh_btn)
        
        settings_btn = QPushButton("设置")
        settings_btn.clicked.connect(self._open_settings)
        btn_layout.addWidget(settings_btn)
        
        layout.addLayout(btn_layout)
        
        # Signals
        self.discovery.user_found.connect(self._add_user)
        self.discovery.user_lost.connect(self._remove_user)
        
        # Tray Icon setup
        self._setup_tray()
        
        self.discovery.start()

    def _open_settings(self):
        dialog = SettingsDialog(self.config, self)
        if dialog.exec() == SettingsDialog.Accepted:
            new_config = dialog.new_config
            # Update autostart
            if new_config["autostart"] != self.config.get("autostart", True):
                exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(sys.argv[0])
                set_autostart("LanCollab", exe_path, new_config["autostart"])
            
            # Save config
            self.config.update(new_config)
            Config.save(self.config)
            
            # Update UI header
            self.header.setText(f"当前用户: {self.config['username']} (房间: {self.config['room_code']})")
            
            # Update Discovery (Restart)
            self.discovery.stop()
            self.discovery.username = self.config["username"]
            self.discovery.room_code = self.config["room_code"]
            self.user_list.clear()
            self.discovery.peers.clear()
            self.discovery.start()

    def _setup_tray(self):
        # Create a simple icon for the tray
        icon_image = self._create_tray_icon()
        menu = pystray.Menu(
            pystray.MenuItem("显示主窗口", self._show_window),
            pystray.MenuItem("退出", self._quit_app)
        )
        self.tray_icon = pystray.Icon("LanCollab", icon_image, "LanCollab", menu)
        
        # Run tray in a separate thread
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def _create_tray_icon(self):
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), (255, 255, 255))
        dc = ImageDraw.Draw(image)
        dc.rectangle([10, 10, 54, 54], fill=(0, 120, 215))
        return image

    def _show_window(self):
        self.show()
        self.activateWindow()

    def _quit_app(self):
        self.discovery.stop()
        self.tray_icon.stop()
        QApplication.quit()

    def _add_user(self, user_info):
        ip = user_info["ip"]
        username = user_info["username"]
        item = QListWidgetItem(f"{username} ({ip})")
        item.setData(Qt.UserRole, ip)
        self.user_list.addItem(item)

    def _remove_user(self, ip):
        for i in range(self.user_list.count()):
            item = self.user_list.item(i)
            if item.data(Qt.UserRole) == ip:
                self.user_list.takeItem(i)
                break

    def _refresh_discovery(self):
        self.user_list.clear()
        self.discovery.peers.clear()

    def closeEvent(self, event):
        # Minimize to tray instead of closing
        event.ignore()
        self.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
