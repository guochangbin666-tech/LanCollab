try:
    from PySide6 import QtWidgets, QtCore, QtGui
    from PySide6.QtCore import Signal, Slot, Qt, QTimer, QPoint, QObject
    from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                                 QLabel, QListWidget, QListWidgetItem, QPushButton, 
                                 QHBoxLayout, QDialog, QLineEdit, QCheckBox, QMessageBox)
    from PySide6.QtGui import QIcon, QAction, QImage, QPixmap, QMouseEvent, QKeyEvent
    PYSIDE6 = True
except ImportError:
    from PySide2 import QtWidgets, QtCore, QtGui
    from PySide2.QtCore import Signal, Slot, Qt, QTimer, QPoint, QObject
    from PySide2.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                                 QLabel, QListWidget, QListWidgetItem, QPushButton, 
                                 QHBoxLayout, QDialog, QLineEdit, QCheckBox, QMessageBox, QAction)
    from PySide2.QtGui import QIcon, QImage, QPixmap, QMouseEvent, QKeyEvent
    PYSIDE6 = False

# Helper for position handling in mouse events
def get_event_pos(event):
    if PYSIDE6:
        return event.position().toPoint()
    else:
        return event.pos()
