import screenshot
import sys, cv2, os, json, keyboard

from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal

import fabicon_rc
import SSHManager

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
        self.radioButton_number: QRadioButton

        self.number = 1
        self.textEdit_number.setText(str(self.number))

        self.pushButton_plus.clicked.connect(self.plus)
        self.pushButton_minus.clicked.connect(self.minus)
        
        self.number_use = True
        self.radioButton_number.clicked.connect(lambda: setattr(self, 'number_use', not self.number_use))

        self.textEdit_name.textChanged.connect(self.get_path)
        self.textEdit_number.textChanged.connect(self.get_path)
        self.textEdit_path.textChanged.connect(self.get_path)
        self.radioButton_number.clicked.connect(self.get_path)

        # ssh를 사용하기 위한 components
        self.radioButton_SSHUseFlag: QRadioButton
        self.radioButton_SSHUseFlag.setAutoExclusive(False)
        self.textEdit_SSHDir: QTextEdit
        self.SSHUseFlag = False
        self.SSHDir=''
        self.radioButton_SSHUseFlag.clicked.connect(self.update_SSHUseFlag)
        self.textEdit_SSHDir.textChanged.connect(self.update_SSHDir)

        self.load_settings()

    def closeEvent(self, event):
        self.thread.quit()
        self.save_settings()
        event.accept()

    def get_path(self):
        if self.number_use:
            self.path = self.textEdit_path.toPlainText() + "\\" + self.textEdit_name.toPlainText() + self.textEdit_number.toPlainText() + ".jpg"
        else:
            self.path = self.textEdit_path.toPlainText() + "\\" + self.textEdit_name.toPlainText() + ".jpg"
        self.thread.path = self.path
        self.number = int(self.textEdit_number.toPlainText()) if self.textEdit_number.toPlainText().isdigit() else 1
        
    def plus(self):
        if self.number_use:
            self.number += 1
            self.textEdit_number.setText(str(self.number))

    def minus(self):
        if self.number_use and self.number >= 1:
            self.number -= 1
            self.textEdit_number.setText(str(self.number))

    def save_settings(self):
        settings = {
            'number': self.number,
            'number_use': self.number_use,
            'textEdit_name': self.textEdit_name.toPlainText(),
            'textEdit_number': self.textEdit_number.toPlainText(),
            'textEdit_path': self.textEdit_path.toPlainText(),
            'SSHUseFlag': self.SSHUseFlag,
            'SSHDir': self.SSHDir
        }
        with open('settings.json', 'w') as f:
            json.dump(settings, f)

    def load_settings(self):
        if os.path.exists('settings.json'):
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                self.number = settings.get('number', 1)
                self.number_use = settings.get('number_use', True)
                self.radioButton_number.setChecked(settings.get('number_use', True))
                self.textEdit_name.setPlainText(settings.get('textEdit_name', ''))
                self.textEdit_number.setPlainText(settings.get('textEdit_number', '1'))
                self.textEdit_path.setPlainText(settings.get('textEdit_path', ''))

                self.textEdit_SSHDir.setPlainText(settings.get('SSHDir', ''))
                self.SSHUseFlag = settings.get('SSHUseFlag', False)
                self.radioButton_SSHUseFlag.setChecked(self.SSHUseFlag)

        self.update_SSHUseFlag()
        self.update_SSHDir()

    def update_SSHUseFlag(self):
        self.SSHUseFlag = self.radioButton_SSHUseFlag.isChecked()
        self.thread.SSHUseFlag = self.SSHUseFlag

    def update_SSHDir(self):
        self.SSHDir = self.textEdit_SSHDir.toPlainText()
        self.thread.SSHDir = self.SSHDir

class ScreenshotThread(screenshot.Screenshot, QThread):
    saved = pyqtSignal()
    def __init__(self, parent, path=" "):
        QThread.__init__(self, parent)
        screenshot.Screenshot.__init__(self, path)

    def stop(self):
        keyboard.unhook_all_hotkeys()
        print("Screenshot thread stopped.")

    def save(self):

        print(f"Screenshot saved as {self.path}")
        extension = os.path.splitext(self.path)[1] # 이미지 확장자
        result, encoded_img = cv2.imencode(extension, self.screenshot)
        
        if result:
            with open(self.path, mode='w+b') as f:
                encoded_img.tofile(f)

        cv2.destroyAllWindows()
        self.saved.emit()

        # SSH 서버 저장 
        if self.SSHUseFlag:
            if self.SSHManager == None:
                print("SSHManager is not set. Initializing SSHManager...")
                sshSettingsPath = './SSHSettings.json'
                if os.path.exists(sshSettingsPath):
                    with open(sshSettingsPath, 'r') as f:
                        sshSettings = json.load(f)
                    self.SSHManager = SSHManager.SSHManager(
                        host=sshSettings['Host'],
                        port=sshSettings.get('Port', 22),
                        userId=sshSettings['User'],
                        key_path=sshSettings.get('IdentityFile', None)
                    )
                else:
                    print("SSH settings file not found. Skipping SSH operations.")
                    return
            
            try:
                self.SSHManager.put_file(self.path, self.SSHDir + os.path.basename(self.path))
                print(f"File {self.path} uploaded to SSH server at {self.SSHDir}.")
            except Exception as e:
                print(f"Failed to upload file to SSH server: {e}")
        else: print("SSHUseFlag is False. Skipping SSH upload.")

if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv) 

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass() 

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()