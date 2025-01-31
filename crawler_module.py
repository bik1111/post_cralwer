from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
import pyautogui
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
# from bs4 import BeautifulSoup
from PIL import Image
from logger import log_error

__all__ = ["Crawler"]


def make_url(tracking_number):
    base_url = 'https://service.epost.go.kr/trace.RetrieveDomRigiTraceList.comm?sid1='
    return f"{base_url}{tracking_number}&displayHeader=s"

class Crawler():
    def __init__(self):
        service = Service()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--window-position=0,0")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument(
            'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36'
        )
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def kill(self):
        self.driver.quit()

    def save_pdf_file_withhout_masking(self, index, tracking_number, key1, key2, selector, output_path):
        url = make_url(tracking_number)
        self.driver.get(url)
        # 조회 실패 메시지가 있는지 확인

        # 필수 selector 값 확인
        selectors = ["#print > table > tbody > tr > td:nth-child(2)",
                     "#print > table > tbody > tr > td:nth-child(3)",]

        for sel in selectors:
            try:
                element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, sel))
                )
                if not element.text.strip():  # 값이 비어있다면
                    log_error(index, tracking_number, key2, f"등기번호 13자리 수는 유효하나 보내는 분/접수일자와 받는 분이 조회되지 않습니다.")
                    time.sleep(0.5)
                    return False

            except TimeoutException:
                if self.log_error:
                    log_error(index, tracking_number, key2, f"Element not found: {sel}")
                return False

        # 기존 마스킹 해제 로직
        if not self.unlock_masking(tracking_number, key1, key2, selector, output_path):
            return False
        return True

    def unlock_masking(self, tracking_number, key1, key2, selector, output_path):
            mask_button_selector = "#print > div.title_wrap.ma_t_10 > p > span > a:nth-child(1)"
            confirm_button_selector = "#btnOk"
            try:
                # 메인 창 핸들 저장
                main_window = self.driver.current_window_handle

                # 마스크 해제 버튼 클릭
                mask_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, mask_button_selector))
                )
                mask_button.click()
                print("🖱️ 마스크 해제 버튼 클릭 완료")
                time.sleep(2)

                # 팝업 창 핸들 가져오기
                WebDriverWait(self.driver, 10).until(lambda driver: len(driver.window_handles) > 1)
                popup_window = [handle for handle in self.driver.window_handles if handle != main_window][0]

                # 팝업 창으로 전환
                self.driver.switch_to.window(popup_window)
                print("🔄 팝업창으로 전환 완료")

                # 팝업 창 작업
                key1_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "senderNm_masking"))
                )
                key1_element.clear()
                key1_element.send_keys(key1)
                print(f"📝 보낸 사람 입력 완료: {key1}")

                key2_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "receverNm_masking"))
                )
                key2_element.clear()
                key2_element.send_keys(key2)
                print(f"📝 받는 사람 입력 완료: {key2}")

                confirm_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, confirm_button_selector))
                )
                confirm_button.click()
                print("✅ 확인 버튼 클릭 완료")

                # 메인 창으로 복귀
                self.driver.switch_to.window(main_window)
                print("🔄 메인 창으로 복귀 완료")

                # PDF 저장
                self.save_selector_as_pdf(tracking_number, selector, output_path)
                print(f"✅ PDF 저장 완료: {output_path}")

                return True

            except TimeoutException as e:
                print(f"❌ Timeout 발생: {e}")
                return False
            except NoSuchElementException as e:
                print(f"❌ Element를 찾을 수 없음: {e}")
                return False
            except Exception as e:
                print(f"❌ 알 수 없는 오류 발생: {e}")
                return False

    def save_selector_as_pdf(self, selector, tracking_number, output_path, zoom_level=50):
        try:
            output_folder = "screenshot_saved_files"

            # Create the folder if it doesn't exist
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
                print(f"📁 폴더 생성 완료: {output_folder}")

            # Adjust zoom level to fit the content
            self.driver.execute_script(f"document.body.style.zoom='{zoom_level}%'")
            print(f"🔍 화면 비율 {zoom_level}%로 설정 완료")

            # Get the full height of the page to ensure a complete screenshot
            scroll_height = self.driver.execute_script("return document.body.scrollHeight")
            self.driver.set_window_size(1920, scroll_height)
            print(f"📜 페이지 높이를 {scroll_height}px로 설정 완료")

            # Take a full-page screenshot
            screenshot_path = os.path.join(output_folder, f"screenshot_{tracking_number}.png")
            self.driver.save_screenshot(screenshot_path)
            print(f"📸 전체 페이지 스크린샷 저장 완료: {screenshot_path}")

            # Load the screenshot and save as PDF
            image = Image.open(screenshot_path)

            # Save as PDF without cropping
            image.convert("RGB").save(output_path, "PDF", resolution=100.0, quality=100)
            print(f"✅ PDF 저장 완료: {output_path}")

            # Restore original zoom level
            self.driver.execute_script("document.body.style.zoom='100%'")
            print("🔄 화면 비율 원래대로 복구 완료")

        except Exception as e:
            print(f"❌ PDF 저장 실패: {e}")


    def kill_error_page(self):
        """에러 발생 시 페이지 닫기"""
        error_button = (390, 170)
        quit_button = (400, 10)
        time.sleep(1)
        if self.get_color(error_button) != (255, 255, 255):
            self.click(quit_button)
            return True
        return False

    def get_color(self, location):
        """화면의 특정 좌표 색상 확인"""
        screenshot = pyautogui.screenshot()
        return screenshot.getpixel(location)