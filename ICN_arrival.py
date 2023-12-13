import sqlite3
import requests
import os

print("인천 국제 공항의 입국장 현황 DB를 업데이트 중입니다.")

def update_db(terno):
    url = 'http://apis.data.go.kr/B551177/StatusOfArrivals/getArrivalsCongestion'
    params = {
        'serviceKey': 'DlosI+3UAm8PeofaukL5IheIbfZ7RgaGQPXyLhIhXgh3UtdlsixbVroHIony/5JrCCObepUbAh/Z3w3L2eSglw==',
        'numOfRows': '40',
        'pageNo': '1',
        'terno': terno,
        'airport': '',
        'type': 'json'
    }

    response = requests.get(url, params=params)
    data = response.json()

    items = data['response']['body']['items']
    for entry in items:
        c.execute('''
            INSERT INTO ICN_arrival (terno, entrygate, korean, foreigner, scheduletime, estimatedtime, airport, gatenumber, flightid)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            entry['terno'],
            entry['entrygate'],
            entry['korean'],
            entry['foreigner'],
            entry['scheduletime'],
            entry['estimatedtime'],
            entry['airport'],
            entry['gatenumber'],
            entry['flightid']
        ))

    # 데이터베이스에 변경 내용을 반영
    conn.commit()

 # DB 생성 (오토 커밋)
conn = sqlite3.connect("ICN_arrival.db", isolation_level=None)
# 커서 획득
c = conn.cursor()

# 테이블 생성 (데이터 타입은 TEXT, NUMERIC, INTEGER, REAL, BLOB 등)
c.execute("DROP TABLE IF EXISTS ICN_arrival")
c.execute('''
        CREATE TABLE IF NOT EXISTS ICN_arrival (
        airport TEXT,
        entrygate TEXT,
        estimatedtime TEXT,
        flightid TEXT,
        foreigner TEXT,
        gatenumber TEXT,
        korean TEXT,
        scheduletime TEXT,
        terno TEXT
            )
''')
update_db('T1')
update_db('T2')

conn = sqlite3.connect("ICN_arrival.db")
# 커서 획득
c = conn.cursor()
c.execute("DELETE FROM ICN_arrival WHERE foreigner = 0.0 AND korean = 0.0;")
conn.commit()

print("인천 국제 공항의 입국장별 혼잡도 현황(-2시간 ~ +2시간)을 알려드립니다.")

while True:
    user_input = input("어떤 정보로 검색하시겠습니까?\n 1.터미널 번호 / 2.게이트 번호 / 3.출발지 공항 코드(IATA) / 4.편명 / 5.DB업데이트 / 6.종료: ")

    # Check if the user input is a valid integer
    if not user_input.isdigit():
        print("숫자를 입력해주세요.")
        continue  # 다시 반복문의 처음으로 이동

    # Convert the user input to an integer
    choice = int(user_input)

    # Perform actions based on the user's choice
    if choice == 1:
        os.system('clear')
        print("터미널 번호를 선택했습니다.")
        while True:
            terminal_n = input("터미널을 입력해주세요.(T1/T2):")
            if terminal_n.upper() == "T1":
                os.system('clear')
                print("\n1번 터미널을 선택했습니다.\n")

                # 여기에 where 조건을 추가하여 T1 터미널에 해당하는 데이터만 가져오기
                c.execute("SELECT flightid FROM ICN_arrival WHERE terno = 'T1' AND foreigner != 0 AND korean != 0")
                flight_ids = [row[0] for row in c.fetchall()]
                print("도착 비행기 편명:", flight_ids)

                c.execute("SELECT count(flightid) FROM ICN_arrival WHERE terno = 'T1'")
                flight_count = c.fetchone()[0]
                print("도착 비행편 수:", flight_count)

                c.execute("SELECT SUM(CAST(korean AS INTEGER)) + SUM(CAST(foreigner AS INTEGER)) AS total_passengers FROM ICN_arrival WHERE terno = 'T1'")
                total_passengers = c.fetchone()[0]
                print("도착 인원 총합:", total_passengers)

                c.execute("SELECT gatenumber FROM ICN_arrival WHERE terno = 'T1'")
                gate_numbers = [row[0] for row in c.fetchall()]
                print("gate 목록:", gate_numbers)
                print("\n")
                break
            elif terminal_n.upper() == "T2":
                os.system('clear')
                print("\n2번 터미널을 선택했습니다.\n")

                # 여기에 where 조건을 추가하여 T1 터미널에 해당하는 데이터만 가져오기
                c.execute("SELECT flightid FROM ICN_arrival WHERE terno = 'T2'")
                flight_ids = [row[0] for row in c.fetchall()]
                print("도착 비행기 편명:", flight_ids)

                c.execute("SELECT count(flightid) FROM ICN_arrival WHERE terno = 'T2'")
                flight_count = c.fetchone()[0]
                print("도착 비행편 수:", flight_count)

                c.execute("SELECT SUM(CAST(korean AS INTEGER)) + SUM(CAST(foreigner AS INTEGER)) AS total_passengers FROM ICN_arrival WHERE terno = 'T2'")
                total_passengers = c.fetchone()[0]
                print("도착 인원 총합:", total_passengers)

                c.execute("SELECT gatenumber FROM ICN_arrival WHERE terno = 'T2'")
                gate_numbers = [row[0] for row in c.fetchall()]
                print("gate 목록:", gate_numbers)
                print("\n")
                break
            else:
                print("올바른 터미널을 입력하세요.")
    elif choice == 2:
        os.system('clear')
        print("\n게이트 번호를 선택했습니다.\n")
        gate_n = input("게이트 번호를 입력해주세요.:")

        sql_query = "SELECT SUM(CAST(korean AS INTEGER)) FROM ICN_arrival WHERE gatenumber = ?"
        c.execute(sql_query, (gate_n,))
        result = c.fetchone()
        print("도착한 한국인 승객 수:", result[0])

        sql_query = "SELECT SUM(CAST(foreigner AS INTEGER)) FROM ICN_arrival WHERE gatenumber = ?"
        c.execute(sql_query, (gate_n,))
        result = c.fetchone()
        print("도착한 외국인 승객 수:", result[0])

        sql_query = "SELECT flightid FROM ICN_arrival WHERE gatenumber = ?"
        c.execute(sql_query, (gate_n,))
        flight_ids = [row[0] for row in c.fetchall()]
        print("도착 비행기 편명:", flight_ids)
        print("\n")
    elif choice == 3:
        os.system('clear')
        print("\n출발지 공항 코드를 선택했습니다.\n")
        ap_code = input("출발지 공항 코드(IATA)를 입력해주세요:")
        
        sql_query = "SELECT flightid FROM ICN_arrival WHERE airport = ?"
        c.execute(sql_query, (ap_code,))
        flight_ids = [row[0] for row in c.fetchall()]
        print("도착 비행기 편명:", flight_ids)
        print("\n")
    elif choice == 4:
        os.system('clear')
        print("\n편명을 선택했습니다.\n")
        fl_id = input("편명을 입력해주세요:")
        
        sql_query = "SELECT terno FROM ICN_arrival WHERE flightid = ?"
        c.execute(sql_query, (fl_id,))
        terminal = [row[0] for row in c.fetchall()]
        print("도착 터미널:", terminal)

        sql_query = "SELECT entrygate FROM ICN_arrival WHERE flightid = ?"
        c.execute(sql_query, (fl_id,))
        ent_gate = [row[0] for row in c.fetchall()]
        print("탑승장 코드:", ent_gate)

        sql_query = "SELECT gatenumber FROM ICN_arrival WHERE flightid = ?"
        c.execute(sql_query, (fl_id,))
        gate_numbers = [row[0] for row in c.fetchall()]
        print("gate 번호:", gate_numbers)

        sql_query = "SELECT SUM(CAST(korean AS INTEGER)) FROM ICN_arrival WHERE flightid = ?"
        c.execute(sql_query, (fl_id,))
        result = c.fetchone()
        print("도착한 한국인 승객 수:", result[0])

        sql_query = "SELECT SUM(CAST(foreigner AS INTEGER)) FROM ICN_arrival WHERE flightid = ?"
        c.execute(sql_query, (fl_id,))
        result = c.fetchone()
        print("도착한 외국인 승객 수:", result[0])
        print("\n")
    elif choice == 5:
        os.system('clear')
        print("\n인천 국제 공항의 입국장 현황 DB를 업데이트 중입니다.\n")
        # Update for T1
        update_db('T1')

        # Update for T2
        update_db('T2')
    elif choice == 6:
        os.system('clear')
        print("프로그램을 종료합니다.")
        conn.close()
        break  # while 루프를 빠져나감
