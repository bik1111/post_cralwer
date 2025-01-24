import post_crawler as pc
import os
import pandas as pd

data_xlsx = "data.xlsx"
out_dir = "output_dir_pdf"

df = pd.read_excel(data_xlsx)  # 엑셀 파일을 DataFrame으로 읽기
count = 1

if out_dir not in os.listdir():
    os.mkdir(out_dir)

crawler = pc.crawler()

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
        print(f"Invalid tracking number: {tracking_number}")
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

    # key2가 유효하지 않으면 건너뜀
    if not key2:
        print(f"Invalid key2 for {mail_merge}")
        continue

    key1 = "울"  # 고정값

    # 크롤링 실행
    try:
        if not crawler.save_pdf_file_withhout_masking(tracking_number, key1, key2, selector, output_path):
            print(f"{tracking_number} has wrong information")
            out_log = f"line was {mail_merge} key2 was {key2}\n\n"
            print(out_log)
            with open("errored_ids.txt", "a") as error_log:
                error_log.write(out_log)
            continue
    except Exception as e:
        print(f"Error occurred for {tracking_number}: {e}")
        continue

    count += 1

crawler.kill()