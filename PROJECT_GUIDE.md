# LG TV 유럽 가격 탄력성 회귀분석 및 2027년 1분기 시뮬레이터 프로젝트 지침서 (PROJECT_GUIDE)

> **프로젝트명**: LGE Europe TV 2027년 1분기 가격 탄력성 회귀분석 및 경쟁사 대응 시뮬레이터  
> **부서 / 과제**: LGE Europe TV 영업 / 15. AX Task 2026 실행과제 #12  
> **최종 갱신일**: 2026-09-07  
> **작성자 / POC**: Harry Park (`harry.park@lge.com`)

---

## 1. 프로젝트 개요 및 추진 배경

### 1.1 프로젝트 목적
유럽 20개국 TV 시장의 18개월(2025.01 ~ 2026.06) 실제 판매 데이터(GfK + NPD 월별 실적)를 기반으로 계량경제학적 다변량 패널 회귀분석(Multivariate Panel Log-Log OLS)을 수행하여, **4대 핵심 제품군별 자체 가격 탄력성, 시장가격 탄력성, 프리미엄 탄력성, 시장규모 탄력성**을 도출하고, 이를 바탕으로 **2027년 1분기(2027 Q1) LG 가격 인상률 및 경쟁사 반응 시나리오(Case 1, 2, 3)에 따른 수량, 매출액, ASP, 시장점유율(M/S)을 정밀 예측**하는 의사결정 시뮬레이터를 구축·운영합니다.

### 1.2 핵심 분석 범위 및 기준
- **분석 대상 기간 (Regression Panel)**: 2025년 1월 ~ 2026년 6월 (총 18개월)
- **시뮬레이션 기준 시점 (Baseline)**: **2026년 1분기 (2026 Q1 실적)**
- **예측 타깃 시점 (Prediction Target)**: **2027년 1분기 (2027 Q1 예측)**
- **분석 대상 권역**: 유럽 20개국 (독일, 영국, 프랑스, 이탈리아, 스페인, 오스트리아, 네덜란드, 벨기에, 포르투갈, 그리스, 스웨덴, 덴마크, 핀란드, 노르웨이, 스위스, 체코, 슬로바키아, 헝가리, 루마니아, 세르비아)
- **제외 국가 (Explicitly Excluded)**: **폴란드(Poland), 크로아티아(Croatia)** (사용자 명시 지침에 따라 전수 제외)

---

## 2. 제품군 세그먼트 체계 (Segmentation Standard)

GfK+NPD 원천 데이터(18개월 640만 대 규모)의 방대한 스펙 필드를 분석하여 아래 4대 카테고리로 표준화합니다:

| 세그먼트 코드 | 화면 표기 명칭 | 분류 로직 및 포함 제품군 | 경제학적 가격 탄력성 특성 |
| :--- | :--- | :--- | :--- |
| **`OLED`** | **OLED TV** | `Tech_Sub` 또는 `Display_Tech`에 'OLED' 포함 | **극비탄력적 ($|\beta_1| = 0.2616$)**<br>가격 인하 시 판매량 증대 효과 미미, 프리미엄 믹스 고수 및 브랜드 가치 보존 전략 최적 |
| **`QNED_MiniLED`** | **QNED / MiniLED / NanoCell** | MiniLED, Quantum Dot, QD, QNED 포함 모델 + **NanoCell 계열 통합** (`NANO` 모델명, `NANOCELL` WCG) | **완만 탄력적 ($|\beta_1| = 1.2105$)**<br>경쟁사(Samsung Neo QLED 등)와 직접 경합, 시장 전체 수축 효과와 상대가격 격차 간 절충 필요 |
| **`NanoCell_UHD`** | **일반 UHD 4K** | NanoCell이 아닌 순수 4K UHD LCD TV (`Tech_Sub`='UHD' / '4K') | **탄력적 ($|\beta_1| = 1.3888$)**<br>대형 보급형 주력 세그먼트, 중국계(TCL, Hisense) 가격 공세에 매우 민감하여 가격 경쟁력 유지 필수 |
| **`FHD`** | **FHD 이하** | FHD, HD, 1080p 해상도 엔트리/세컨드 TV | **비탄력적 ($|\beta_1| = 0.8655$)**<br>소형 교체 수요 위주 안정 시장, 마진 확보 중심 방어 전략 |

---

## 3. 계량경제학 모형 체계 및 추정 결과 (42M Panel WLS)

### 3.1 42개월 유럽 20개국 패널 WLS 회귀분석 모형식
각 세그먼트 $i$ 및 국가 $c$, 월 $t$에 대해 다음과 같은 다변량 Log-Log 계량 모형을 시간 가중 최소제곱법(WLS) 및 국가/계절 고정효과(Country & Month FE)로 추정합니다:

$$\ln(Q_{LG, c, t}) = \alpha_c + \beta_1 \ln(P_{LG, c, t}) + \beta_2 \ln(P_{Comp, c, t}) + \beta_3 \ln(MktSize_{c, t}) + \sum_{m=2}^{12} \gamma_m \text{MonthDummy}_{m, t} + \delta \cdot t + \epsilon_{c, t}$$

- **$\beta_1$ (자체 가격 탄력성, Own Price Elasticity)**: LG 독자 가격 인상 시 판매수량 변화율 (이론적 부호 음수 $< 0$)
- **$\beta_2$ (경쟁사 교차 가격 탄력성, Cross Price Elasticity)**: 경쟁사 평균 가격 인상 시 LG 판매수량 변동률 (이론적 부호 양수 $> 0$, 상대가격 방어력)
- **$\beta_3$ (시장규모 탄력성, Market Size Elasticity)**: 거시 시장 규모 변동 시 LG 수량 변동률 (1.0에 가까울수록 시장 추종)
- **$\beta_{mkt}$ (시장가격 탄력성, Market Price Elasticity)**: 시장 전체 평균 ASP 변동에 따른 세그먼트 총수요 변동률. 유럽 전체 TV 총수요 규모($\ln(\text{Total\_TV\_Units})$)를 통제한 패널 WLS 추정치 반영 ($\ln(\text{MktUnits}) = \alpha_c + \beta_{mkt} \ln(\text{MktASP}) + \beta_{tot} \ln(\text{Total\_TV\_Units}) + \text{Month Dummies} + \text{trend} + \epsilon$)
- **시간 가중(Time-Decay WLS)**: 최신 18개월(2025~2026.06) 가중치 1.0, 2024년 0.8, 2023년 0.6 적용으로 구조적 변화 왜곡 최소화.

### 3.2 통계적 검정 및 진단 지표 요약 (42M WLS vs 18M OLS 비교)

| 제품군 (Segment) | 모형 구분 | 자체 탄력성 ($\beta_1$) | 경쟁사 교차 ($\beta_2$) | 시장가격 탄력성 ($\beta_{mkt}$) | 설명력 ($R^2$) | 잔차자기상관 (DW) | 가중 MAPE (핵심) | EU 총합 MAPE |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **OLED TV** | **신규 42M WLS** | **-0.6838** | **+1.0586** | **-1.0968** | **0.993** | **1.339** | **6.1%** | **3.2%** |
| *(비교: 기존 18M OLS)* | *과거 18M* | *-0.2616* | *+0.6982* | *-1.0172* | *0.986* | *0.580* | *11.7%* | *-* |
| **QNED / MiniLED** | **신규 42M WLS** | **-1.9038** | **+2.7402** | **-1.1455** | **0.871** | **0.620** | **18.5%** | **11.6%** |
| *(비교: 기존 18M OLS)* | *과거 18M* | *-1.2105* | *-0.0825 (역전)* | *-0.5627* | *0.882* | *0.488* | *31.4%* | *-* |
| **일반 UHD 4K** | **신규 42M WLS** | **-1.7337** | **+1.3707** | **-0.5385** | **0.932** | **1.068** | **17.0%** | **9.3%** |
| *(비교: 기존 18M OLS)* | *과거 18M* | *-1.3888* | *+0.8781* | *-0.8019* | *0.855* | *0.602* | *77.7% (왜곡)* | *-* |
| **FHD 이하** | **신규 42M WLS** | **-1.5581** | **+0.8460** | **-0.6479** | **0.878** | **0.516** | **44.3%** | **12.4%** |
| *(비교: 기존 18M OLS)* | *과거 18M* | *-0.8655* | *+0.6175* | *-0.5874* | *0.872* | *0.541* | *77.9% (왜곡)* | *-* |

> **고도화 성과 요약**:
> 1. **다중공선성 및 부호 역전 해소**: QNED 프리미엄 탄력성이 과거 +0.0825(비유의, p=0.47)에서 자체 -1.9038, 경쟁사 +2.7402로 경제학적 이론에 완벽히 부합하게 정상화.
> 2. **잔차 자기상관(DW) 비약적 개선**: 국가 고정효과(Country FE) 및 12개 월 계절성 더미 도입으로 DW가 OLED 0.58 -> 1.34, UHD 0.60 -> 1.07로 대폭 정상화.
> 3. **MAPE 오차율 정상화**: 소형국 착시 왜곡을 제거한 판매량 가중 MAPE(Volume-Weighted MAPE) 도입으로 일반 UHD 77.7% -> 17.0%, OLED 6.1%로 실무 활용 수준 달성.

---

## 4. 2027 Q1 예측 알고리즘 및 4대 시나리오 (Simulation Logic)

### 4.1 경쟁사 가격 반응 4대 시나리오 정의
LG전자가 2027년 1분기에 가격 인상($\Delta P_{LG}$)을 단행할 때, 경쟁사의 가격 인상 추종률($\text{followRate}$)은 다음과 같이 정의됩니다:

1. **Case 1 (100% 동등 인상)**:
   - **OLED**: 100% 동등 인상 ($\Delta P_{comp} = 1.0 \times \Delta P_{LG}$)
   - **기타 제품군 (QNED, UHD, FHD)**: 100% 동등 인상 ($\Delta P_{comp} = 1.0 \times \Delta P_{LG}$)
   - *특징: 상대가격 비율이 유지되어 LG 시장점유율(M/S) 변동이 최소화되며, 시장 전체 가격 상승에 따른 총수요 축소분만 반영.*
2. **Case 2 (75% 수준 인상)**:
   - **OLED**: 100% 동등 인상 ($\Delta P_{comp} = 1.0 \times \Delta P_{LG}$)
   - **기타 제품군 (QNED, UHD, FHD)**: 75% 수준 인상 ($\Delta P_{comp} = 0.75 \times \Delta P_{LG}$)
   - *특징: LG의 상대가격 프리미엄이 소폭 확대되어 점유율이 완만하게 하락.*
3. **Case 3 (50% 수준 인상)**:
   - **OLED**: 100% 동등 인상 ($\Delta P_{comp} = 1.0 \times \Delta P_{LG}$)
   - **기타 제품군 (QNED, UHD, FHD)**: 50% 수준 인상 ($\Delta P_{comp} = 0.50 \times \Delta P_{LG}$)
   - *특징: 경쟁사가 공격적으로 가격차를 벌려 LG의 상대가격 프리미엄이 크게 확대되고 점유율 이탈 폭이 가속화되는 리스크 시나리오.*
4. **Case 4 (전 제품 경쟁사 동결 / 단독 인상)**:
   - **전 제품군 (OLED 포함)**: 0% 판가 동결 ($\Delta P_{comp} = 0.0 \times \Delta P_{LG}$)
   - *특징: 경쟁사가 판가를 전혀 올리지 않고 전 제품에서 동결하여 LG의 상대가격 프리미엄이 극대화되고 전 제품군에서 브랜드 전환 이탈이 최대로 발생하는 극한 리스크 시나리오.*

### 4.2 시장 점유율 분해 연산 메커니즘 (Market Share Decomposition Model)

1. **시장 평균 가격 변동률 ($\Delta P_{mkt}$)**:
   $$\Delta P_{mkt} = (MS_{base} \times \Delta P_{LG}) + ((1 - MS_{base}) \times \Delta P_{comp})$$
2. **시장 전체 수요 성장률 ($g_{mkt}$)**: 회귀분석으로 도출된 **시장가격 탄력성($\beta_{mkt}$)** 적용
   $$g_{mkt} = \beta_{mkt} \times \Delta P_{mkt}$$
   $$Q_{mkt}^{new} = Q_{mkt}^{base} \times (1 + g_{mkt})$$
3. **LG 상대가격 프리미엄 변동률 ($\Delta \text{Premium}$)**:
   $$\Delta \text{Premium} = \frac{1 + \Delta P_{LG}}{1 + \Delta P_{comp}} - 1$$
4. **LG 판매 성장률 및 브랜드 대체 페널티 ($g_{LG}$)**:
   $$g_{LG} = g_{mkt} - (\eta_{switch} \times \Delta \text{Premium})$$
   - $\eta_{switch}$ (브랜드 전환 탄력성): OLED 0.70 (실증 프리미엄 탄력성 $|\beta_2|$ 반영), QNED 3.0, UHD 3.5, FHD 2.5
   - Case 1 (100% 동등 인상): $\Delta \text{Premium} = 0 \implies g_{LG} = g_{mkt}$ (점유율 100% 보존)
   - Case 2, 3, 4: 경쟁사 미추종으로 가격차가 벌어질수록 고객 이탈 페널티($\eta_{switch} \times \Delta \text{Premium}$)가 단조 증가하여 LG 판매수량이 Case 1 > Case 2 > Case 3 > Case 4 순으로 뚜렷하게 감소
5. **최종 LG 판매수량, 매출액 및 시장점유율 산출**:
   $$Q_{LG}^{new} = Q_{LG}^{base} \times (1 + g_{LG})$$
   $$ASP_{LG}^{new} = ASP_{LG}^{base} \times (1 + \Delta P_{LG})$$
   $$\text{Revenue}_{LG}^{new} = Q_{LG}^{new} \times ASP_{LG}^{new}$$
   $$MS_{LG}^{new} = \frac{Q_{LG}^{new}}{Q_{mkt}^{new}} \times 100\%$$

---

## 5. 대시보드 UI/UX 구성 표준 및 조작 규칙

### 5.1 화면 레이아웃 계층 구조
```
[헤더] LG TV Europe — 2027년 1분기 가격 탄력성 시뮬레이터 (2026 Q1 vs 2027 Q1 예측)
├── [좌측 사이드바]
│    ├── 🌍 분석 대상 권역 셀렉트박스 (유럽 전체 20개국 Total 및 개별 20개국 선택)
│    ├── 🎚️ LG 가격 인상률 설정 (27년 1Q)
│    │    ├── 1-클릭 간편 프리셋: [전체 +5% (기본)] / [차등 인상] / [0% (동결)]
│    │    ├── 개별 슬라이더 4종: OLED, QNED/NanoCell, 일반 UHD, FHD (-10% ~ +20%)
│    │    └── 0% 알림 배너 (0% 설정 시 안내)
│    └── 💡 경쟁사 가격 반응 3대 CASE 규칙 정보 카드
└── [우측 메인 영역]
     ├── 1. 🔬 회귀분석 모델 진단 & 통계 지표 표 (최상단 고정 배치)
     ├── 2. 🎛️ Case 1 (100%) | Case 2 (75%) | Case 3 (50%) 단일 선택 라디오 배너
     ├── 3. 📊 제품군별 1:1 대비 차트 (26년 1Q 실적 vs 선택된 Case 예측)
     │    ├── 좌: 판매수량 비교 차트 (천 대)
     │    └── 우: 매출액 비교 차트 (€M)
     └── 4. 📊 제품군별 2026 1Q 대비 2027 1Q 3대 시나리오(Case 1, 2, 3) 종합 상세 비교표
```

### 5.2 주요 UI 컴포넌트 동작 원칙
- **초기 로딩 시 기본값 (+5%)**: 대시보드 접속 시 모든 제품군 슬라이더가 `+5%`로 자동 세팅되어 2026 1Q 실적과 2027 1Q 예측치의 차이($\Delta$)가 즉시 표출됩니다.
- **0% 동결 안내 배너**: 가격 인상률을 0%로 조정하거나 `0% (동결)` 버튼을 누르면 *"⚠️ 가격 인상률 0%: 가격 변동이 0%로 설정되어 2026 1Q 실적과 2027 1Q 예측치가 동일합니다."* 배너가 노출되어 사용자의 오해를 방지합니다.
- **오프라인 무설치 단독 실행**: 외부 인터넷이나 별도 웹서버 없이 `index.html`을 더블 클릭(`file:///`)해도 모든 차트와 계산 엔진이 100% 완벽히 작동하도록 JSON 데이터가 내장(Embedded)되어 있습니다.

---

## 6. 스크립트 파이프라인 및 실행 방법

모든 파이프라인 스크립트는 `d:\TV 유럽영업\15. AX Task\2026 AX 실행과제\12. 가격 탄력성 회귀분석\scripts\` 폴더에 관리됩니다.

### 실행 환경 및 파이썬 경로
- 파이썬 실행기: `C:\Users\harry.park\.gemini\antigravity\python_portable\python.exe`

### 순차 파이프라인 실행 안내

```powershell
# 1단계: 42개월(2023.01~2026.06) 유럽 20개국 원천 데이터 추출 및 패널 통합
C:\Users\harry.park\.gemini\antigravity\python_portable\python.exe "d:\TV 유럽영업\15. AX Task\2026 AX 실행과제\12. 가격 탄력성 회귀분석\scripts\01_build_panel_42m.py"

# 2단계: 42개월 패널 WLS 회귀분석(자체/교차 분리, 국가/월 FE, 가중 MAPE) 수행
C:\Users\harry.park\.gemini\antigravity\python_portable\python.exe "d:\TV 유럽영업\15. AX Task\2026 AX 실행과제\12. 가격 탄력성 회귀분석\scripts\02_run_elasticity_42m_wls.py"

# 3단계: 2026년 1분기 Baseline 집계 및 시뮬레이션 데이터셋(simulation_data.json) 생성
C:\Users\harry.park\.gemini\antigravity\python_portable\python.exe "d:\TV 유럽영업\15. AX Task\2026 AX 실행과제\12. 가격 탄력성 회귀분석\scripts\02_build_q1_sim_data.py"

# 4단계: 인터랙티브 독립형 대시보드(index.html) 재컴파일 및 EMBEDDED_DATA 주입
C:\Users\harry.park\.gemini\antigravity\python_portable\python.exe "d:\TV 유럽영업\15. AX Task\2026 AX 실행과제\12. 가격 탄력성 회귀분석\scripts\03_generate_redesigned_dashboard.py"
```

---

## 7. 주요 파일 및 디렉토리 구조

```
d:\TV 유럽영업\15. AX Task\2026 AX 실행과제\12. 가격 탄력성 회귀분석\
├── PROJECT_GUIDE.md                                      # 본 프로젝트 통합 지침서
├── LG_TV_유럽_가격탄력성_회귀분석_경쟁대응_보고서.docx   # Word 최종 보고서
├── DATA\
│    ├── Global) GfK+NPD Monthly Raw_2023년.xlsb          # 2023년 원천 데이터
│    ├── Global) GfK+NPD Monthly Raw_2024-202507.xlsb     # 2024년 원천 데이터
│    ├── Global) GfK+NPD Monthly Raw_202501_202606.xlsb   # 2025~2026 원천 데이터
│    └── processed\
│         ├── elasticity_results_42m.json                 # 42M WLS 회귀분석 통계 지표 및 계수 DB
│         └── panel_regression_data_42m.csv               # 42개월 패널 분석용 가공 데이터
├── dashboard\
│    ├── index.html                                       # 최종 배포용 독립형 대시보드 (오프라인 지원)
│    ├── simulation_data.json                             # 2026 Q1 Baseline 및 42M 모델 메타 DB
│    └── report_assets\                                   # 보고서 및 대시보드용 고해상도 차트 이미지
└── scripts\
     ├── 01_build_panel_42m.py                            # 42개월 패널 원천 추출/통합 빌더
     ├── 02_run_elasticity_42m_wls.py                     # 42M WLS 패널 회귀분석 엔진
     ├── 02_build_q1_sim_data.py                          # 2026 Q1 Baseline 데이터 빌더
     └── 03_generate_redesigned_dashboard.py              # 대시보드 컴파일러
```
