import PyInstaller.__main__
import os
import sys

def build():
    # Detect if we are in PySide6 or PySide2 environment
    try:
        import PySide6
        qt_lib = 'PySide6'
    except ImportError:
        qt_lib = 'PySide2'

    print(f"Building for {qt_lib} ({'32-bit' if sys.maxsize <= 2**31-1 else '64-bit'})...")

    # PyInstaller options
    options = [
        'main.py',
        '--name=LanCollab',
        '--onefile',
        '--windowed',
        '--add-data=ui;ui',
        '--add-data=network;network',
        '--add-data=office;office',
        '--add-data=utils;utils',
        f'--hidden-import={qt_lib}.QtCore',
        f'--hidden-import={qt_lib}.QtGui',
        f'--hidden-import={qt_lib}.QtWidgets',
        '--hidden-import=pystray',
        '--hidden-import=PIL',
        '--hidden-import=mss',
        '--hidden-import=pygetwindow',
        '--hidden-import=win32gui',
        '--hidden-import=win32process',
        '--hidden-import=pywin32',
        '--hidden-import=pyautogui',
        '--hidden-import=cv2',
        '--hidden-import=numpy',
    ]
    
    PyInstaller.__main__.run(options)

if __name__ == "__main__":
    build()
