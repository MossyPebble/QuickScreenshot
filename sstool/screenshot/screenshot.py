'''
screenshot.py
'''

import cv2, os
import pyautogui as p
import numpy as np
import keyboard, pytesseract, clipboard, win32gui, win32con, win32clipboard
from io import BytesIO
import struct

__all__ = ['Screenshot']

class Screenshot:

    """
        현재 화면을 캡쳐해 창을 생성하고, 캡쳐한 화면을 저장합니다.
    """

    def __init__(self, path):
        self.screenshot = None

        self.path = path
        self.count = 1
        self.wating_count = 1

    def run(self):
        # keyboard.add_hotkey('ctrl+shift+a', self.take_screenshot)
        # keyboard.add_hotkey('ctrl+shift+q', self.transform_image_to_text)

        while True:
            # print('Wating for hotkey...', self.wating_count)
            # self.wating_count += 1
            # event = keyboard.read_event()
            # print(event)

            if keyboard.is_pressed("ctrl") and keyboard.is_pressed("shift") and keyboard.is_pressed("a"):
                print('Ctrl + Shift + A')
                self.take_screenshot()

            if keyboard.is_pressed("ctrl") and keyboard.is_pressed("shift") and keyboard.is_pressed("q"):
                print('Ctrl + Shift + Q')
                self.transform_image_to_text()

    def set_clipboard_file(self, file_path):

        # "잘라내기"가 아니라 "복사" 작업임을 알려주기 위한 클립보드 형식을 등록
        cf_preferred_dropeffect = win32clipboard.RegisterClipboardFormat("Preferred DropEffect")
        DROPEFFECT_COPY = 1 # "복사"를 의미하는 값
        effect = struct.pack('I', DROPEFFECT_COPY) # 위 값을 바이너리 데이터로 포장(패킹)

        # 파일 목록 데이터가 시작되는 위치(오프셋)를 알려주는 거
        pFiles = 20

        # CF_HDROP에 필요한 헤더 정보를 만듬 유니코드(UTF-16)를 사용한다고 알려줌
        header = struct.pack('Lllii', pFiles, 0, 0, 0, 1) # pFiles, pt, fNC, fWide

        # 파일 절대 경로를 유니코드 바이트로 바꾸고, 목록의 끝을 알리는 null 문자 두 개를 추가
        files = os.path.abspath(file_path).encode('utf-16-le') + b'\0\0'

        # 헤더랑 파일 경로 데이터를 합쳐서 최종 데이터를 만듬
        data = header + files

        # 이제 클립보드에 데이터를 넣을 거야.
        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32con.CF_HDROP, data)
            win32clipboard.SetClipboardData(cf_preferred_dropeffect, effect)
        finally:
            win32clipboard.CloseClipboard()

    def take_screenshot(self):

        """
            현재 화면을 캡쳐해 창을 생성하고, 캡쳐한 화면을 저장합니다.
        """

        pil_screenshot = p.screenshot(allScreens=True)
        self.screenshot = np.array(pil_screenshot)
        self.screenshot = cv2.cvtColor(self.screenshot, cv2.COLOR_RGB2BGR)

        x, y, w, h = cv2.selectROI('Screenshot', self.screenshot, False)
        hwnd = win32gui.FindWindow(None, 'Screenshot')
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

        if w and h:
            self.screenshot = self.screenshot[y:y+h, x:x+w]
            self.save()
            screenshot_abspath = os.path.abspath(self.path)
            self.set_clipboard_file(screenshot_abspath)
            print(f"Screenshot saved as {screenshot_abspath}")
            print("Screenshot file has been copied to the clipboard.")
        else:
            print("Image's width and height must be greater than 0.")
        
        cv2.destroyAllWindows()
        return

    def transform_image_to_text(self):

        """
            현재 화면을 캡쳐해 창을 생성하고, 캡쳐한 화면을 텍스트로 변환합니다.
        """

        self.screenshot = p.screenshot(allScreens=True)
        self.screenshot = np.array(self.screenshot)
        self.screenshot = cv2.cvtColor(self.screenshot, cv2.COLOR_RGB2BGR)

        x, y, w, h = cv2.selectROI('Screenshot', self.screenshot, False)
        hwnd = win32gui.FindWindow(None, 'Screenshot')
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

        if w and h:
            self.screenshot = self.screenshot[y:y+h, x:x+w]

            self.screenshot = cv2.cvtColor(self.screenshot, cv2.COLOR_BGR2GRAY)
            self.screenshot = self.screenshot.astype(np.uint8)
            # cv2.imwrite('temp.jpg', self.screenshot)
            self.screenshot = cv2.adaptiveThreshold(self.screenshot, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

            try:
                config = r'--oem 3 --psm 6 -l kor+eng'
                text = pytesseract.image_to_string(self.screenshot, config=config)
                clipboard.copy(text)
                print(text)
            except:
                print("Text transformation failed.")
        else:
            print("Image's width and height must be greater than 0.")

        cv2.destroyAllWindows()
        
    def save(self):

        print(f"Screenshot saved as {self.path}")
        # cv2.imwrite(self.path, self.screenshot)
        
        extension = os.path.splitext(self.path)[1] # 이미지 확장자
        
        result, encoded_img = cv2.imencode(extension, self.screenshot)
        
        if result:
            with open(self.path, mode='w+b') as f:
                encoded_img.tofile(f)

if __name__ == "__main__" :
    s = Screenshot('./temp.jpg')
    s.run()