import os
import sys
import winreg as reg

def set_autostart(app_name, exe_path, enable=True):
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_ALL_ACCESS)
        if enable:
            reg.SetValueEx(key, app_name, 0, reg.REG_SZ, exe_path)
        else:
            try:
                reg.DeleteValue(key, app_name)
            except FileNotFoundError:
                pass
        reg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Failed to set autostart: {e}")
        return False

def is_autostart_enabled(app_name):
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_READ)
        reg.QueryValueEx(key, app_name)
        reg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False
