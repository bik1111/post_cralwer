import os
import pandas as pd
from crawler_module import Crawler  # 클래스 직접 import
from logger import log_error
import time

data_xlsx = "test.xlsx"
out_dir = "output_dir_pdf"


df = pd.read_excel(data_xlsx)  # 엑셀 파일을 DataFrame으로 읽기
count = 1

if out_dir not in os.listdir():
    os.mkdir(out_dir)

crawler = Crawler()

done_list = []
temp = os.listdir(out_dir)


# 엑셀 파일의 각 행(row)을 반복
for index, row in df.iterrows():
    # B열(등기번호)와 C열(연번), D열(메일머지1)만 사용
    tracking_number = str(row['등기번호']).strip()
    serial_number = str(row['연번']).strip()
    mail_merge = str(row['메일머지1']).strip()
    output_path = f"{out_dir}/{tracking_number}.pdf"  # 저장할 PDF 경로
    selector = "#print"  # 저장할 영역의 CSS Selector

    print("Tracking Number:", tracking_number, "Serial Number:", serial_number)

    # 등기번호 유효성 검사 (숫자 13자리)
    if len(tracking_number) != 13 or not tracking_number.isdigit():
        log_error(index, tracking_number, mail_merge, "등기번호 조회 요건(13자리 수)에 맞지 않는 등기번호 입니다.")
        time.sleep(0.5)
        continue
    # 중복 처리 방지
    if tracking_number + ".pdf" in done_list:
        print(f"Already processed: {tracking_number}")
        continue

    # 마스킹 해제를 위한 단어 찾기
    if mail_merge.startswith("(주)") or mail_merge.startswith("㈜"):
        # (주) 또는 ㈜가 있으면 공백을 제거하고 그 다음 글자 추출
        clean_name = mail_merge.replace("(주)", "").replace("㈜", "").strip()
        key2 = clean_name[0] if len(clean_name) > 0 else ""
    else:
        # (주) 또는 ㈜가 없으면 두 번째 글자 추출
        key2 = mail_merge[1] if len(mail_merge) > 1 else ""

    key1 = "울"  # 고정값

    # 크롤링 실행
    try:
        crawler.save_pdf_file_withhout_masking(index, tracking_number, key1, key2, selector, output_path)
    except Exception as e:
        print(f"❌ Error: {e}")
        continue

    count += 1

crawler.kill()