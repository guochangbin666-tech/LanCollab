import socket
import threading
import json
import struct
import time
import pyautogui
from utils.screen_capture import ScreenCapturer

class SharingServer:
    def __init__(self, port=50002):
        self.port = port
        self.running = False
        self.connections = {}  # IP: (socket, thread)
        self.lock = threading.Lock()

    def start_sharing(self, window_title, target_ip):
        # Establish a TCP connection to the target
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((target_ip, self.port))
            
            # Start sending screen data
            thread = threading.Thread(target=self._send_screen, args=(sock, window_title), daemon=True)
            thread.start()
            # Start receiving input events
            input_thread = threading.Thread(target=self._receive_input, args=(sock,), daemon=True)
            input_thread.start()
            
            with self.lock:
                self.connections[target_ip] = (sock, thread, input_thread)
            return True
        except Exception as e:
            print(f"Sharing server error: {e}")
            return False

    def stop_sharing(self, target_ip=None):
        with self.lock:
            if target_ip:
                if target_ip in self.connections:
                    sock, t1, t2 = self.connections.pop(target_ip)
                    sock.close()
            else:
                for ip, (sock, t1, t2) in self.connections.items():
                    sock.close()
                self.connections.clear()

    def _send_screen(self, sock, window_title):
        capturer = ScreenCapturer(window_title)
        self.current_window_rect = capturer.get_window_rect()
        while True:
            try:
                self.current_window_rect = capturer.get_window_rect()
                data = capturer.capture()
                if data:
                    # Send size first, then data
                    size = len(data)
                    sock.sendall(struct.pack(">L", size) + data)
                time.sleep(0.05)  # ~20 FPS
            except Exception as e:
                print(f"Send screen error: {e}")
                break

    def _receive_input(self, sock):
        while True:
            try:
                # Receive input event (JSON)
                size_data = sock.recv(4)
                if not size_data: break
                size = struct.unpack(">L", size_data)[0]
                data = sock.recv(size).decode('utf-8')
                event = json.loads(data)
                self._handle_event(event)
            except Exception as e:
                print(f"Receive input error: {e}")
                break

    def _handle_event(self, event):
        etype = event.get("type")
        if not hasattr(self, 'current_window_rect') or not self.current_window_rect:
            return

        top = self.current_window_rect['top']
        left = self.current_window_rect['left']

        if etype == "mouse_move":
            rx, ry = event.get("rel_pos")
            pyautogui.moveTo(left + rx, top + ry)
        elif etype == "mouse_click":
            rx, ry = event.get("rel_pos")
            button = event.get("button", "left")
            pyautogui.click(left + rx, top + ry, button=button)
        elif etype == "key_press":
            key = event.get("key")
            pyautogui.press(key)

from utils.qt_compat import QObject, Signal

class SharingClient(QObject):
    frame_received = Signal(bytes)

    def __init__(self, port=50002):
        super().__init__()
        self.port = port
        self.running = False

    def start_listening(self):
        self.running = True
        self.listen_thread = threading.Thread(target=self._listen, daemon=True)
        self.listen_thread.start()

    def stop_listening(self):
        self.running = False

    def _listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', self.port))
        sock.listen(1)
        
        while self.running:
            try:
                conn, addr = sock.accept()
                print(f"Accepted connection from {addr}")
                # Start a thread to receive screen and send input
                threading.Thread(target=self._handle_connection, args=(conn,), daemon=True).start()
            except Exception as e:
                print(f"Listen error: {e}")

    def _handle_connection(self, conn):
        # This is for the recipient's side
        # Need a way to display the screen and capture input
        # For now, let's just implement the protocol
        # Input events will be sent back through 'conn'
        self.current_conn = conn
        
        while True:
            try:
                # Receive screen frame
                size_data = conn.recv(4)
                if not size_data: break
                size = struct.unpack(">L", size_data)[0]
                frame_data = b""
                while len(frame_data) < size:
                    chunk = conn.recv(min(size - len(frame_data), 4096))
                    if not chunk: break
                    frame_data += chunk
                
                self.frame_received.emit(frame_data)
                    
            except Exception as e:
                print(f"Handle connection error: {e}")
                break

    def send_input_event(self, event):
        if hasattr(self, "current_conn"):
            try:
                data = json.dumps(event).encode('utf-8')
                size = len(data)
                self.current_conn.sendall(struct.pack(">L", size) + data)
            except Exception as e:
                print(f"Send input event error: {e}")
