import sys
import os
from utils.qt_compat import (QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, 
                              QImage, QPixmap, QMouseEvent, QKeyEvent, Qt, Signal, get_event_pos)
import cv2
import numpy as np

class PreviewWindow(QMainWindow):
    def __init__(self, client):
        super().__init__()
        self.client = client
        
        self.setWindowTitle("局域网实时预览")
        self.resize(800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        self.display_label = QLabel("正在连接...")
        self.display_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.display_label)
        
        self.setMouseTracking(True)
        self.display_label.setMouseTracking(True)

    def _on_frame_received(self, frame_data):
        try:
            # Decode JPEG
            nparr = np.frombuffer(frame_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            # Store original size for mapping
            self.original_width = img.shape[1]
            self.original_height = img.shape[0]
            # Convert to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h, w, ch = img.shape
            bytes_per_line = ch * w
            q_img = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)
            # Update display
            pixmap = QPixmap.fromImage(q_img)
            self.display_label.setPixmap(pixmap.scaled(self.display_label.size(), Qt.KeepAspectRatio))
        except Exception as e:
            print(f"Frame processing error: {e}")

    def _get_mapped_pos(self, event_pos):
        # Map local label coordinates to original screen coordinates
        label_size = self.display_label.size()
        pixmap = self.display_label.pixmap()
        if not pixmap or not hasattr(self, 'original_width'):
            return None
        
        pixmap_size = pixmap.size()
        # Scale factor
        scale_x = self.original_width / pixmap_size.width()
        scale_y = self.original_height / pixmap_size.height()
        
        # Offset (if scaled with KeepAspectRatio)
        offset_x = (label_size.width() - pixmap_size.width()) / 2
        offset_y = (label_size.height() - pixmap_size.height()) / 2
        
        rel_x = (event_pos.x() - offset_x) * scale_x
        rel_y = (event_pos.y() - offset_y) * scale_y
        
        return int(rel_x), int(rel_y)

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = self._get_mapped_pos(get_event_pos(event))
        if pos:
            self.client.send_input_event({
                "type": "mouse_move",
                "rel_pos": pos
            })

    def mousePressEvent(self, event: QMouseEvent):
        pos = self._get_mapped_pos(get_event_pos(event))
        if pos:
            button = "left" if event.button() == Qt.LeftButton else "right"
            self.client.send_input_event({
                "type": "mouse_click",
                "rel_pos": pos,
                "button": button
            })

    def keyPressEvent(self, event: QKeyEvent):
        key = event.text()
        if key:
            self.client.send_input_event({
                "type": "key_press",
                "key": key
            })
