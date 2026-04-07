import socket
import threading
import json
import time
from utils.qt_compat import QObject, Signal

class DiscoveryManager(QObject):
    user_found = Signal(dict)
    user_lost = Signal(str)  # IP or ID

    def __init__(self, username, room_code, port=50001):
        super().__init__()
        self.username = username
        self.room_code = room_code
        self.port = port
        self.running = False
        self.peers = {}  # IP: {username, last_seen}
        self.lock = threading.Lock()

    def start(self):
        self.running = True
        # Listen for UDP broadcasts
        self.listen_thread = threading.Thread(target=self._listen, daemon=True)
        self.listen_thread.start()
        # Periodically broadcast presence
        self.broadcast_thread = threading.Thread(target=self._broadcast, daemon=True)
        self.broadcast_thread.start()
        # Monitor for timeouts
        self.monitor_thread = threading.Thread(target=self._monitor, daemon=True)
        self.monitor_thread.start()

    def stop(self):
        self.running = False

    def _broadcast(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        while self.running:
            try:
                data = json.dumps({
                    "type": "hello",
                    "username": self.username,
                    "room_code": self.room_code
                }).encode('utf-8')
                sock.sendto(data, ('<broadcast>', self.port))
            except Exception as e:
                print(f"Broadcast error: {e}")
            time.sleep(3)

    def _listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', self.port))
        sock.settimeout(1.0)
        
        while self.running:
            try:
                data, addr = sock.recvfrom(1024)
                payload = json.loads(data.decode('utf-8'))
                if payload.get("room_code") == self.room_code and payload.get("type") == "hello":
                    ip = addr[0]
                    username = payload.get("username")
                    with self.lock:
                        if ip not in self.peers:
                            self.user_found.emit({"ip": ip, "username": username})
                        self.peers[ip] = {"username": username, "last_seen": time.time()}
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Listen error: {e}")

    def _monitor(self):
        while self.running:
            now = time.time()
            with self.lock:
                to_remove = []
                for ip, info in self.peers.items():
                    if now - info["last_seen"] > 10:  # Timeout after 10s
                        to_remove.append(ip)
                for ip in to_remove:
                    del self.peers[ip]
                    self.user_lost.emit(ip)
            time.sleep(5)
