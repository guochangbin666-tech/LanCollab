from utils.qt_compat import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QCheckBox, QMessageBox, Qt)

class SettingsDialog(QDialog):
    def __init__(self, current_config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("软件设置")
        self.setFixedWidth(300)
        self.config = current_config
        
        layout = QVBoxLayout(self)
        
        # Username
        layout.addWidget(QLabel("用户昵称:"))
        self.username_edit = QLineEdit(self.config.get("username", ""))
        layout.addWidget(self.username_edit)
        
        # Room Code
        layout.addWidget(QLabel("房间码 (相同房间码才可见):"))
        self.room_code_edit = QLineEdit(self.config.get("room_code", "1234"))
        layout.addWidget(self.room_code_edit)
        
        # Autostart
        self.autostart_check = QCheckBox("开机自启")
        self.autostart_check.setChecked(self.config.get("autostart", True))
        layout.addWidget(self.autostart_check)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self._save)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _save(self):
        new_username = self.username_edit.text().strip()
        new_room_code = self.room_code_edit.text().strip()
        
        if not new_username or not new_room_code:
            QMessageBox.warning(self, "错误", "昵称和房间码不能为空")
            return
            
        self.new_config = {
            "username": new_username,
            "room_code": new_room_code,
            "autostart": self.autostart_check.isChecked()
        }
        self.accept()
