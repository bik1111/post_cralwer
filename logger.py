import os
import datetime
import pytz

error_log_dir = "error_log"  # 오류 로그 폴더 경로

# 오류 로그 파일을 매 실행마다 새롭게 생성
def create_error_log():
    if not os.path.exists(error_log_dir):
        os.makedirs(error_log_dir)

    kst = pytz.timezone('Asia/Seoul')  # KST 시간대 설정
    timestamp = datetime.datetime.now(kst).strftime("%Y%m%d_%H%M%S")
    return os.path.join(error_log_dir, f"error_log_{timestamp}.txt")

error_log_path = create_error_log()

def log_error(index, tracking_number, mail_merge, reason):
    error_message = f"오류 행 번호: {index + 2}, 등기번호: {tracking_number}, 보내는 분: {mail_merge}, 오류 원인: {reason}\n"
    print(f"❌ Error: {error_message}")
    with open(error_log_path, "a") as error_file:
        error_file.write(error_message)