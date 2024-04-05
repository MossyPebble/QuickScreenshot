import sstool
import keyboard, sys, cv2, os
import numpy as np
import pyautogui as p

from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal

form_class = uic.loadUiType("GUI.ui")[0]

class WindowClass(QMainWindow, form_class) :

    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        self.thread = ScreenshotThread(self)
        self.thread.saved.connect(self.plus)
        self.thread.start()
        
        self.pushButton_minus: QPushButton
        self.pushButton_plus: QPushButton
        self.textEdit_name: QTextEdit
        self.textEdit_number: QTextEdit
        self.textEdit_path: QTextEdit

        self.number = 1
        self.textEdit_number.setText(str(self.number))

        self.pushButton_plus.clicked.connect(self.plus)
        self.pushButton_minus.clicked.connect(self.minus)

        self.textEdit_name.textChanged.connect(self.get_path)
        self.textEdit_number.textChanged.connect(self.get_path)
        self.textEdit_path.textChanged.connect(self.get_path)

    def get_path(self):
        self.path = self.textEdit_path.toPlainText() + "\\" + self.textEdit_name.toPlainText() + self.textEdit_number.toPlainText() + ".jpg"
        self.thread.path = self.path
        
    def plus(self):
        self.number += 1
        self.textEdit_number.setText(str(self.number))

    def minus(self):
        self.number -= 1
        self.textEdit_number.setText(str(self.number))

class ScreenshotThread(sstool.Screenshot, QThread):
    saved = pyqtSignal()
    def __init__(self, parent, path=" "):
        QThread.__init__(self, parent)
        sstool.Screenshot.__init__(self, path)

    def save(self):

        print(f"Screenshot saved as {self.path}")
        
        extension = os.path.splitext(self.path)[1] # 이미지 확장자
        
        result, encoded_img = cv2.imencode(extension, self.screenshot)
        
        if result:
            with open(self.path, mode='w+b') as f:
                encoded_img.tofile(f)

        cv2.destroyAllWindows()
        self.saved.emit()

if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv) 

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass() 

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()