from random import randint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from modules.selenium import *
import config
import slack

import time
import webbrowser

chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'

############# 자동 예매 원하는 설정으로 변경 ##############

member_number = config.srt_member_number # 회원번호
password= config.srt_member_password # 비밀번호
arrival = "수서" # 출발지
departure = "천안아산" # 도착지
standard_date = "20240329" # 기준날짜 ex) 20221101
standard_time = "18" # 기준 시간 ex) 00 - 22 // 2의 배수로 입력
skip_of_trains = 4 # 시작지점 위에서부터 1이면 스킵 없음 2면 1스킵
number_of_trains = 6 # 상단에서부터 조회할 기차수  maximum = 11

#################################################################

# reserved = False
target_reserved_cnt = 2 # 두장 예약해야함
now_reserved_cnt = 0

print("--------------- Start SRT Macro ---------------")

# webdriver 파일의 경로 입력
# 같은 디렉토리에 있기 때문에 chromedriver.exe파일 이름만 써줌
print("selenium version : ", get_selenium_version())

# selenium 버전에 따른 webdriver 분기
v1, v2, v3 = get_selenium_version().split(".")
driver = webdriver.Chrome("chromedriver") if int(v1) < 4 else webdriver.Chrome()

# 이동을 원하는 페이지 주소 입력
driver.get('https://etk.srail.co.kr/cmc/01/selectLoginForm.do')
driver.implicitly_wait(15)


# 회원번호 매핑
driver.find_element(By.ID, 'srchDvNm01').send_keys(member_number)

# 비밀번호 매핑
driver.find_element(By.ID, 'hmpgPwdCphd01').send_keys(password)

# 확인 버튼 클릭
driver.find_element(By.XPATH, '/html/body/div/div[4]/div/div[2]/form/\
    fieldset/div[1]/div[1]/div[2]/div/div[2]/input').click()
driver.implicitly_wait(5)

driver.get('https://etk.srail.kr/hpg/hra/01/selectScheduleList.do')
driver.implicitly_wait(5)


# 출발지 입력
dep_stn = driver.find_element(By.ID, 'dptRsStnCdNm')
dep_stn.clear()
dep_stn.send_keys(arrival)

# 도착지 입력
arr_stn = driver.find_element(By.ID, 'arvRsStnCdNm')
arr_stn.clear()
arr_stn.send_keys(departure)

# 날짜 드롭다운 리스트 보이게
# elm_dptDt = driver.find_element(By.ID, "dptDt")
# driver.execute_script("arguments[0].setAttribute('style','display: True;)", elm_dptDt)

Select(driver.find_element(By.ID,"dptDt")).select_by_value(standard_date)

# 출발 시간
# eml_dptTm = driver.find_element(By.ID, "dptTm")
# driver.execute_script("arguments[0].setAttribbute('style','display:True;')", eml_dptTm)

Select(driver.find_element(By.ID, "dptTm")).select_by_visible_text(standard_time)

# 조회하기 버튼
driver.find_element(By.XPATH, "//input[@value='조회하기']").click()


train_list = driver.find_elements(By.CSS_SELECTOR, "#result-form > fieldset > \
div.tbl_wrap.th_thead > table > tbody > tr")

print(train_list)
time_arr_18 = ['18:00', '18:05','18:24','18:37','19:00','20:00']

while True: 


    try:
        for i in range(skip_of_trains, number_of_trains):
            standard_seat = driver.find_element(By.CSS_SELECTOR, f"#result-form > fieldset > div.tbl_wrap.th_thead > table > tbody > tr:nth-child({i}) > td:nth-child(7)").text

            if "예약하기" in standard_seat:
                print("예약 가능 클릭")
                driver.find_element(By.XPATH, f"/html/body/div[1]/div[4]/div/div[3]/div[1]/\
                form/fieldset/div[6]/table/tbody/tr[{i}]/td[7]/a/span").click()
                driver.implicitly_wait(3)

                if driver.find_elements(By.ID, 'isFalseGotoMain'):
                    reserved = True
                    now_reserved_cnt += 1
                    print('예약 성공')

                    channel_id = "stock"

                    msg = "예약알림" + time_arr_18[i]

                    token = config.slack_token
                    # 메시지 전송
                    response = slack.post_message(token, channel_id, msg)

                    webbrowser.get(chrome_path).open("https://etk.srail.kr/hpg/hra/02/selectReservationList.do?pageId=TK0102010000")
                    break

                else:
                    print("잔여석 없음. 다시 검색")
                    driver.back() #뒤로가기
                    driver.implicitly_wait(5)

    except Exception as e: 
        print(e)
        print('잔여석 조회 불가')
        pass
    
    if now_reserved_cnt < target_reserved_cnt:
        try:
        # 다시 조회하기
            submit = driver.find_element(By.XPATH, "/html/body/div/div[4]/div/div[2]/form/fieldset/div[2]/input")
            driver.execute_script("arguments[0].click();", submit)
            print("새로고침")

        except: 
            print("잔여석 없음 #2. 초기화")
            driver.back() #뒤로가기
            driver.implicitly_wait(5)

            driver.refresh() #새로고침
            driver.implicitly_wait(5)
            pass

        # 5초 대기
        driver.implicitly_wait(10)
        time.sleep(5)

    else:
        time.sleep(1000)
        break


