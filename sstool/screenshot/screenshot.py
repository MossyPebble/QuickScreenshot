"""
screenshot.py
"""

import cv2, os
import pyautogui as p
import numpy as np
import keyboard, pytesseract, clipboard

__all__ = ['Screenshot']

class Screenshot:

    """
    현재 화면을 캡쳐해 창을 생성하고, 캡쳐한 화면을 저장합니다.
    """

    def __init__(self, path):
        self.screenshot = None

        self.path = path
        self.count = 1

    def run(self):
        keyboard.add_hotkey('ctrl+shift+a', self.take_screenshot)
        keyboard.add_hotkey('ctrl+shift+q', self.transform_image_to_text)
        while True:
            keyboard.wait()

    def take_screenshot(self):

        self.screenshot = p.screenshot()
        self.screenshot = np.array(self.screenshot)
        self.screenshot = cv2.cvtColor(self.screenshot, cv2.COLOR_RGB2BGR)

        x, y, w, h = cv2.selectROI('Screenshot', self.screenshot, False)
        if w and h:
            self.screenshot = self.screenshot[y:y+h, x:x+w]
            try:
                self.save()
            except:
                print("Screenshot failed to save.")
        else:
            print("Image's width and height must be greater than 0.")

    def transform_image_to_text(self):

        self.screenshot = p.screenshot()
        self.screenshot = np.array(self.screenshot)
        self.screenshot = cv2.cvtColor(self.screenshot, cv2.COLOR_RGB2BGR)

        x, y, w, h = cv2.selectROI('Screenshot', self.screenshot, False)
        if w and h:
            self.screenshot = self.screenshot[y:y+h, x:x+w]

            self.screenshot = cv2.cvtColor(self.screenshot, cv2.COLOR_BGR2GRAY)
            self.screenshot = self.screenshot.astype(np.uint8)
            # cv2.imwrite('temp.jpg', self.screenshot)
            self.screenshot = cv2.adaptiveThreshold(self.screenshot, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

            try:
                config = r'--oem 3 --psm 7 -l kor+eng'
                text = pytesseract.image_to_string(self.screenshot, config=config)
                clipboard.copy(text)
                # print(text)
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

        cv2.destroyAllWindows()