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

# Helper for application execution
def exec_app(app):
    if PYSIDE6:
        return app.exec()
    else:
        return app.exec_()

# Helper for dialog execution
def exec_dialog(dialog):
    if PYSIDE6:
        return dialog.exec()
    else:
        return dialog.exec_()

# Helper for global position
def get_global_pos(event):
    if PYSIDE6:
        return event.globalPosition().toPoint()
    else:
        return event.globalPos()
