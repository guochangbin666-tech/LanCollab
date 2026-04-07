import mss
import numpy as np
import cv2
import zlib
import threading
import time

class ScreenCapturer:
    def __init__(self, window_title):
        self.window_title = window_title
        self.sct = mss.mss()
        self.running = False

    def get_window_rect(self):
        import pygetwindow as gw
        wins = gw.getWindowsWithTitle(self.window_title)
        if wins:
            win = wins[0]
            return {"top": win.top, "left": win.left, "width": win.width, "height": win.height}
        return None

    def capture(self):
        rect = self.get_window_rect()
        if not rect:
            return None
        
        try:
            # Capture the specific window
            img = self.sct.grab(rect)
            # Convert to numpy array
            frame = np.array(img)
            # Resize for performance if needed
            # frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            # Encode as JPEG for compression
            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
            return buffer.tobytes()
        except Exception as e:
            print(f"Capture error: {e}")
            return None
