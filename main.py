import sys
import os
import threading
from utils.qt_compat import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QLabel, QListWidget, QListWidgetItem, QPushButton, QHBoxLayout,
                             QIcon, QAction, Qt, Signal)
import pystray
from PIL import Image, ImageDraw

from network.discovery import DiscoveryManager
from network.server_client import SharingServer, SharingClient
from ui.main_window import MainWindow
from ui.floating_button import FloatingButton
from ui.preview_window import PreviewWindow
from utils.config import Config
from utils.autostart import set_autostart

class LanCollabApp:
    def __init__(self, q_app):
        self.q_app = q_app
        self.config = Config.load()
        
        # Set autostart if enabled
        if self.config.get("autostart", True):
            exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(sys.argv[0])
            set_autostart("LanCollab", exe_path, True)
        
        # Core components
        self.discovery = DiscoveryManager(self.config["username"], self.config["room_code"])
        self.server = SharingServer()
        self.client = SharingClient()
        
        # UI
        self.main_window = MainWindow()
        self.main_window.discovery = self.discovery
        self.main_window.server = self.server
        self.main_window.client = self.client
        
        self.floating_btn = FloatingButton(self.main_window)
        self.floating_btn.request_sharing.connect(self._initiate_sharing)
        
        # Setup Client to listen for incoming sharing requests
        self.client.frame_received.connect(self._show_preview)
        self.client.start_listening()
        
        self.preview_window = None

    def _initiate_sharing(self, window_title, target_ip):
        print(f"Initiating sharing: {window_title} with {target_ip}")
        success = self.server.start_sharing(window_title, target_ip)
        if success:
            print(f"Sharing started successfully with {target_ip}")
        else:
            print(f"Failed to start sharing with {target_ip}")

    def _show_preview(self, frame_data):
        # Create preview window if it doesn't exist
        if not self.preview_window or not self.preview_window.isVisible():
            # Use QThread/Signal for thread safety if needed
            # For now, let's just create it on demand
            from ui.preview_window import PreviewWindow
            self.preview_window = PreviewWindow(self.client)
            self.preview_window.show()
        # Hand off frame data
        self.preview_window._on_frame_received(frame_data)

    def run(self):
        self.main_window.show()
        self.floating_btn.show()
        sys.exit(self.q_app.exec())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Check for another instance (optional)
    # ...

    lan_collab = LanCollabApp(app)
    lan_collab.run()
