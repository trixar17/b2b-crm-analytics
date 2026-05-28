"""
============================================================================
 Synthetic Data Generator
============================================================================
 Purpose
   - Create a synthetic dataset that simulates CRM data.
   - Designed for a Tableau dashboard portfolio.

 Reference Date
   - 2026-05-01 (assumed "today")
   - Data range: 2024-05-01 ~ 2026-04-30 (trailing 24 months)

 Output
   - 7 CSV files in ./data/
   - Encoded as UTF-8 with BOM (prevents Korean character corruption
     when imported into Tableau)
   - Star Schema layout:
        Dimensions: dim_partner, dim_product, dim_date
        Facts     : fact_sales, fact_traffic, fact_promotion, fact_crm

 Author : Sunghoon Jun
 Updated: 2026-05-28
============================================================================
"""

# 데이터 분석 및 엑셀 저장을 위한 라이브러리 불러오기
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta


# ------------------------------------------------------------
# 0. 난수 시드 고정
# ------------------------------------------------------------
# 재현 가능한 샘플 데이터를 만들기 위한 설정
np.random.seed(42)
random.seed(42)

# ------------------------------------------------------------
# 1. Hospital Master 데이터 생성
# ------------------------------------------------------------
# 병원/약국 마스터 데이터의 총 개수
num_hospitals = 800

# 병원 유형 목록
# 실제 영업 CRM 데이터에서 관리할 수 있는 고객 유형을 가정
hospital_types = ['상급종합병원', '종합병원', '의원', '약국']

# 각 병원 유형이 생성될 비율
# 상급종합병원 5%, 종합병원 15%, 의원 50%, 약국 30%
type_proportions = [0.05, 0.15, 0.50, 0.30]

# 병원/약국이 위치할 지역 목록
regions = [
    '서울 강남구',
    '서울 종로구',
    '서울 마포구',
    '경기 성남시',
    '경기 수원시',
    '부산 해운대구',
    '대구 중구',
    '대전 서구',
    '광주 동구'
]

# 각 지역별 생성 비율
# 서울 강남구, 종로구, 경기 성남시 등 수도권의 비중을 상대적으로 높게 설정
regions_weights = [0.25, 0.15, 0.10, 0.15, 0.10, 0.09, 0.06, 0.05, 0.05]

# 병원 유형을 지정된 비율에 따라 800개 랜덤 생성
hospital_type_choices = np.random.choice(
    hospital_types,
    size=num_hospitals,
    p=type_proportions
)

# 지역을 지정된 비율에 따라 800개 랜덤 생성
region_choices = np.random.choice(
    regions,
    size=num_hospitals,
    p=regions_weights
)

# 병원명 생성에 사용할 단어 목록
med_names = [
    '서울', '국민', '삼성', '연세', '대웅', '바른', '성모',
    '중앙', '우리', '미래', '하나', '정성', '푸른', '행복'
]

# 의원명 생성 시 사용할 진료과 목록
specialties = ['내과', '이비인후과', '소아청소년과', '정형외과', '가정의학과']

# 병원 마스터 데이터를 저장할 리스트
hospital_data = []

# 리드 생성 시작 기준일
# 각 병원/약국이 CRM에 처음 등록된 날짜를 만들기 위한 기준 날짜
start_date = datetime(2024, 1, 1)

# ------------------------------------------------------------
# 1-1. 병원/약국 800개 생성 루프
# ------------------------------------------------------------
for i in range(num_hospitals):
    # 병원 ID 생성
    # 예: H0001, H0002, ..., H0800
    h_id = f'H{i+1:04d}'

    # 미리 랜덤 생성해둔 병원 유형과 지역을 가져옵니다.
    h_type = hospital_type_choices[i]
    reg = region_choices[i]

    # 병원 이름의 기본 조합 생성
    # 예: 서울삼성, 연세대웅, 미래중앙 등
    base_name = random.choice(med_names) + random.choice(med_names)

    # 병원 유형에 따라 병원명 형식을 다르게 생성
    if h_type == '상급종합병원':
        # 상급종합병원 예: 삼성서울대학교병원
        h_name = f"{base_name}대학교병원"

    elif h_type == '종합병원':
        # 종합병원 예: 연세중앙의료원
        h_name = f"{base_name}의료원"

    elif h_type == '의원':
        # 의원 예: 바른성모내과의원
        h_name = f"{base_name}{random.choice(specialties)}의원"

    else:
        # 약국 예: 대웅미래온누리약국 또는 하나정성정문약국
        h_name = (
            f"{base_name}온누리약국"
            if random.random() > 0.5
            else f"{base_name}정문약국"
        )

    # CRM에 리드가 등록된 시점을 랜덤하게 생성
    # 기준일인 2024-01-01부터 최대 500일 후까지 랜덤 설정
    lead_days_built = random.randint(0, 500)
    lead_date = start_date + timedelta(days=lead_days_built)

    # --------------------------------------------------------
    # Funnel Stage 생성
    # --------------------------------------------------------
    # 병원/약국이 CRM 영업 퍼널에서 어느 단계에 있는지 가정
    #
    # Untouched:
    #   아직 방문 활동도 주문도 없는 상태
    #
    # Visited_No_Order:
    #   영업 방문은 있었지만 주문은 발생하지 않은 상태
    #
    # Converted:
    #   방문 이후 실제 주문까지 발생한 상태
    #
    # 비율:
    #   Untouched 20%
    #   Visited_No_Order 35%
    #   Converted 45%
    funnel_stage = np.random.choice(
        ['Untouched', 'Visited_No_Order', 'Converted'],
        p=[0.20, 0.35, 0.45]
    )

    # 고객 프로필 초기값
    # 주문 전환되지 않은 고객은 별도 프로필이 없으므로 'None'으로 설정
    profile = 'None'

    # 주문 전환 고객(Converted)에 대해서만 고객 행동 프로필을 부여
    if funnel_stage == 'Converted':
        # Loyal:
        #   꾸준히 주문하는 충성 고객
        #
        # Churned:
        #   초반에는 주문했지만 일정 기간 후 이탈한 고객
        #
        # Sporadic:
        #   간헐적으로 주문하는 고객
        profile = np.random.choice(
            ['Loyal', 'Churned', 'Sporadic'],
            p=[0.5, 0.25, 0.25]
        )

    # 생성된 병원/약국 정보를 리스트에 저장
    hospital_data.append({
        'hospital_id': h_id,
        'hospital_name': h_name,
        'hospital_type': h_type,
        'region': reg,
        'lead_date': lead_date,
        # funnel_stage와 profile은 이후 활동/주문 데이터 생성을 위한 내부용 컬럼
        'funnel_stage': funnel_stage,
        'profile': profile
    })

# 병원 마스터 리스트를 DataFrame으로 변환
df_hospital = pd.DataFrame(hospital_data)

# ------------------------------------------------------------
# 2. Sales Activity Log / Order Fact 데이터 생성 준비
# ------------------------------------------------------------

# 영업 활동 로그 데이터를 저장할 리스트
activity_data = []

# 주문 데이터를 저장할 리스트
order_data = []

# 제품 카테고리와 선택 비율
# 대웅제약 제품을 가정한 구성
products = {
    '펙수클루': 0.3,
    '엔블로': 0.25,
    '우루사': 0.25,
    '올메텍': 0.1,
    '임팩타민': 0.1
}

# 제품명 리스트
prod_list = list(products.keys())

# 제품 선택 확률 리스트
prod_weights = list(products.values())

# 데이터 생성 기준 현재일
# 이 날짜 이후의 방문/주문은 생성하지 않도록 제한합니다.
current_date = datetime(2026, 5, 20)

# 활동 ID와 주문 ID 생성을 위한 카운터
act_id_counter = 1
ord_id_counter = 1

# ------------------------------------------------------------
# 2-1. 병원별 영업 활동 및 주문 데이터 생성
# ------------------------------------------------------------
for idx, row in df_hospital.iterrows():

    # --------------------------------------------------------
    # Case 1. Untouched
    # --------------------------------------------------------
    # 아직 영업 방문도 없고 주문도 없는 병원/약국입니다.
    # 따라서 활동 로그와 주문 데이터를 생성하지 않습니다.
    if row['funnel_stage'] == 'Untouched':
        continue

    # 현재 병원의 ID와 리드 등록일 가져오기
    h_id = row['hospital_id']
    lead_date = row['lead_date']

    # 담당 MR ID 랜덤 배정
    # MR001 ~ MR030 중 하나를 랜덤하게 할당합니다.
    mr_id = f"MR{random.randint(1, 30):03d}"

    # --------------------------------------------------------
    # Case 2. Visited_No_Order
    # --------------------------------------------------------
    # 영업 방문은 있었지만 주문은 없는 고객입니다.
    # 활동 로그만 생성하고 주문 데이터는 생성하지 않습니다.
    if row['funnel_stage'] == 'Visited_No_Order':

        # 방문 횟수는 1~5회 사이로 랜덤 생성
        num_visits = random.randint(1, 5)

        # 첫 방문일은 리드 등록일로부터 1~10일 후로 설정
        loop_date = lead_date + timedelta(days=random.randint(1, 10))

        # 방문 횟수만큼 활동 로그 생성
        for _ in range(num_visits):

            # 방문일이 기준 현재일을 넘으면 더 이상 생성하지 않습니다.
            if loop_date > current_date:
                break

            activity_data.append({
                # 활동 ID 예: ACT00001
                'activity_id': f"ACT{act_id_counter:05d}",

                # 방문 대상 병원 ID
                'hospital_id': h_id,

                # 담당 MR ID
                'mr_id': mr_id,

                # 방문 일시
                'visit_datetime': loop_date,

                # 첫 방문은 '신규 콜', 이후 방문은 '제품 설명회'로 설정
                'activity_type': '신규 콜' if _ == 0 else '제품 설명회'
            })

            # 활동 ID 카운터 증가
            act_id_counter += 1

            # 다음 방문일은 14~30일 후로 설정
            loop_date += timedelta(days=random.randint(14, 30))

        # Visited_No_Order 고객은 주문 생성 없이 다음 병원으로 이동
        continue

    # --------------------------------------------------------
    # Case 3. Converted
    # --------------------------------------------------------
    # 실제 주문까지 발생한 고객

    # 해당 고객의 행동 프로필 가져오기
    profile = row['profile']

    # Churned 고객은 일정 기간만 활동하다가 이탈한 것으로 설정
    # 60~180일 사이의 활동 기간 후 더 이상 활동/주문이 발생하지 않습니다.
    if profile == 'Churned':
        active_days = random.randint(60, 180)

    # Loyal, Sporadic 고객은 매우 긴 활동 가능 기간을 부여
    # 이후 current_date와 비교해서 실제 종료일이 결정
    else:
        active_days = 9999

    # 실제 활동 종료일 계산
    # Churned 고객은 lead_date + active_days가 될 수 있고,
    # 나머지 고객은 current_date까지 활동
    end_activity_date = min(
        lead_date + timedelta(days=active_days),
        current_date
    )

    # 첫 방문일은 리드 등록일로부터 1~5일 후로 설정
    loop_date = lead_date + timedelta(days=random.randint(1, 5))

    # 첫 주문 여부를 판단하는 플래그
    # 첫 활동은 '신규 콜'로 기록하고,
    # 첫 주문일 때는 주문 확률을 더 높게 적용
    first_order = True

    # 활동일이 종료일 이전인 동안 반복적으로 방문/주문 생성
    while loop_date < end_activity_date:

        # 영업 활동 로그 생성
        activity_data.append({
            'activity_id': f"ACT{act_id_counter:05d}",
            'hospital_id': h_id,
            'mr_id': mr_id,
            'visit_datetime': loop_date,

            # 첫 활동이면 '신규 콜'
            # 이후 활동이면 80% 확률로 '정기 방문', 20% 확률로 '제품 설명회'
            'activity_type': (
                '신규 콜'
                if first_order
                else np.random.choice(['정기 방문', '제품 설명회'], p=[0.8, 0.2])
            )
        })

        # 활동 ID 증가
        act_id_counter += 1

        # ----------------------------------------------------
        # 주문 발생 여부 결정
        # ----------------------------------------------------
        # 첫 주문 전에는 주문 발생 확률을 80%로 높게 설정
        #
        # 첫 주문 이후:
        #   Loyal 고객은 70% 확률로 재주문
        #   Sporadic 고객은 30% 확률로 재주문
        #   Churned 고객은 이탈 전까지만 위 로직에 따라 주문 가능
        order_prob = (
            0.8
            if first_order
            else (0.7 if profile == 'Loyal' else 0.3)
        )

        # 랜덤값이 주문 확률보다 작으면 주문 발생
        if random.random() < order_prob:

            # 주문 시간은 방문 후 1~5시간 뒤로 설정
            order_time = loop_date + timedelta(hours=random.randint(1, 5))

            # 한 번 주문 시 1~2개 품목을 주문한다고 가정
            num_items = random.randint(1, 2)

            # 주문 품목 수만큼 주문 데이터 생성
            for _ in range(num_items):

                # 제품 카테고리를 설정된 비율에 따라 랜덤 선택
                prod = np.random.choice(prod_list, p=prod_weights)

                # 매출 금액을 10만 원 ~ 100만 원 사이로 랜덤 생성
                sales_amount = random.randint(100000, 1000000)

                order_data.append({
                    # 주문 ID 예: ORD00001
                    'order_id': f"ORD{ord_id_counter:05d}",

                    # 주문 병원 ID
                    'hospital_id': h_id,

                    # 주문 일시
                    'order_datetime': order_time,

                    # 주문 제품 카테고리
                    'product_category': prod,

                    # 주문 금액
                    'sales_amount': sales_amount
                })

                # 주문 ID 증가
                ord_id_counter += 1

            # 주문이 한 번이라도 발생하면 이후부터는 첫 주문이 아닌 상태로 변경
            first_order = False

        # 다음 방문일은 14~45일 후로 설정
        loop_date += timedelta(days=random.randint(14, 45))

# ------------------------------------------------------------
# 3. 리스트 데이터를 DataFrame으로 변환
# ------------------------------------------------------------

# 영업 활동 로그 DataFrame 생성
df_activity = pd.DataFrame(activity_data)

# 주문 Fact DataFrame 생성
df_order = pd.DataFrame(order_data)

# ------------------------------------------------------------
# 4. 외부 공개용 Hospital Master 정리
# ------------------------------------------------------------
# funnel_stage와 profile은 데이터 생성을 위한 내부 로직 컬럼
# 실제 포트폴리오에는 노출하지 않기 위해 제거
df_hospital_clean = df_hospital.drop(columns=['funnel_stage', 'profile'])

# ------------------------------------------------------------
# 5. 엑셀 파일로 저장
# ------------------------------------------------------------

# 저장할 엑셀 파일명
output_filename = "crm_portfolio_data.xlsx"

# ExcelWriter를 사용해 여러 개의 시트를 하나의 엑셀 파일로 저장합니다.
with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:

    # 병원/약국 마스터 테이블 저장
    df_hospital_clean.to_excel(
        writer,
        sheet_name='Hospital_Master',
        index=False
    )

    # 영업 활동 로그 테이블 저장
    df_activity.to_excel(
        writer,
        sheet_name='Sales_Activity_Log',
        index=False
    )

    # 주문 Fact 테이블 저장
    df_order.to_excel(
        writer,
        sheet_name='Order_Fact',
        index=False
    )

# ------------------------------------------------------------
# 6. 생성 결과 확인
# ------------------------------------------------------------

# 활동 로그가 존재하는 병원/약국 수 출력
print(f"Hospitals with Activities: {df_activity['hospital_id'].nunique()}")

# 주문이 발생한 병원/약국 수 출력
print(f"Hospitals with Orders: {df_order['hospital_id'].nunique()}")
