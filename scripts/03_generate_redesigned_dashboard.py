import os
import json

DATA_DIR = r"d:\TV 유럽영업\15. AX Task\2026 AX 실행과제\12. 가격 탄력성 회귀분석\DATA"
DASHBOARD_DIR = r"d:\TV 유럽영업\15. AX Task\2026 AX 실행과제\12. 가격 탄력성 회귀분석\dashboard"
SIM_JSON_PATH = os.path.join(DASHBOARD_DIR, "simulation_data.json")
INDEX_HTML_PATH = os.path.join(DASHBOARD_DIR, "index.html")

with open(SIM_JSON_PATH, 'r', encoding='utf-8') as f:
    sim_data = json.load(f)

json_str = json.dumps(sim_data, indent=2, ensure_ascii=False)

html_content = f'''<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LG TV Europe — 2027년 1분기 가격 탄력성 시뮬레이터 (2026 Q1 vs 2027 Q1 예측)</title>
  <!-- Chart.js CDN -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <style>
    :root {{
      --bg-main: #0B0F19;
      --bg-card: #151C2C;
      --border-color: #26334D;
      --text-main: #F1F5F9;
      --text-muted: #94A3B8;
      --primary: #A50034;
      --primary-hover: #C4003E;
      --accent-blue: #38BDF8;
      --accent-green: #34D399;
      --accent-purple: #A78BFA;
      --accent-amber: #F59E0B;
      --accent-teal: #2DD4BF;
      --danger: #F87171;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans KR', sans-serif;
      background-color: var(--bg-main);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }}

    header {{
      background-color: rgba(21, 28, 44, 0.95);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border-color);
      padding: 0.85rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 100;
    }}

    .header-left {{
      display: flex;
      align-items: center;
      gap: 1.2rem;
    }}
    .header-logo {{
      width: 38px;
      height: 38px;
      background: linear-gradient(135deg, var(--primary), #E11D48);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 1.1rem;
      color: #fff;
      box-shadow: 0 4px 12px rgba(165, 0, 52, 0.4);
    }}
    .header-title-group h1 {{
      font-size: 1.25rem;
      font-weight: 700;
      letter-spacing: -0.02em;
    }}
    .header-title-group p {{
      font-size: 0.78rem;
      color: var(--text-muted);
      margin-top: 2px;
    }}

    .header-badges {{
      display: flex;
      gap: 0.6rem;
      align-items: center;
    }}
    .badge {{
      padding: 0.35rem 0.75rem;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
    }}
    .badge-primary {{
      background-color: rgba(165, 0, 52, 0.2);
      color: #FDA4AF;
      border: 1px solid rgba(165, 0, 52, 0.4);
    }}
    .badge-blue {{
      background-color: rgba(56, 189, 248, 0.15);
      color: var(--accent-blue);
      border: 1px solid rgba(56, 189, 248, 0.3);
    }}
    .btn-fullscreen {{
      background: transparent;
      border: 1px solid var(--border-color);
      color: var(--text-muted);
      padding: 0.4rem 0.8rem;
      border-radius: 6px;
      font-size: 0.78rem;
      cursor: pointer;
      transition: all 0.2s;
    }}
    .btn-fullscreen:hover {{
      color: var(--text-main);
      border-color: var(--text-muted);
    }}

    .app-body {{
      display: flex;
      flex: 1;
      overflow: hidden;
    }}

    /* Sidebar */
    aside.sidebar {{
      width: 320px;
      background-color: var(--bg-card);
      border-right: 1px solid var(--border-color);
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 1.2rem;
      overflow-y: auto;
      flex-shrink: 0;
    }}

    .card {{
      background-color: #121826;
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 1.1rem;
    }}
    .card-title {{
      font-size: 0.85rem;
      font-weight: 700;
      color: var(--text-main);
      margin-bottom: 0.85rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .card-title .tag {{
      font-size: 0.7rem;
      color: var(--text-muted);
      font-weight: normal;
    }}

    .control-group {{
      margin-bottom: 1rem;
    }}
    .control-group:last-child {{
      margin-bottom: 0;
    }}
    .control-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.82rem;
      margin-bottom: 0.35rem;
    }}
    .control-label {{
      font-weight: 600;
      color: #E2E8F0;
    }}
    .control-val {{
      font-weight: 700;
      font-size: 0.85rem;
      color: var(--accent-blue);
      background-color: rgba(56, 189, 248, 0.1);
      padding: 2px 6px;
      border-radius: 4px;
    }}

    input[type="range"] {{
      width: 100%;
      height: 6px;
      border-radius: 3px;
      background: #2D3748;
      outline: none;
      -webkit-appearance: none;
    }}
    input[type="range"]::-webkit-slider-thumb {{
      -webkit-appearance: none;
      width: 16px;
      height: 16px;
      border-radius: 50%;
      background: var(--primary);
      cursor: pointer;
      border: 2px solid #FFF;
      box-shadow: 0 0 8px rgba(165, 0, 52, 0.6);
      transition: transform 0.1s;
    }}
    input[type="range"]::-webkit-slider-thumb:hover {{
      transform: scale(1.15);
    }}

    .select-custom {{
      width: 100%;
      background-color: #1E283D;
      border: 1px solid var(--border-color);
      color: var(--text-main);
      padding: 0.55rem;
      border-radius: 8px;
      font-size: 0.82rem;
      outline: none;
      cursor: pointer;
    }}
    .select-custom:focus {{
      border-color: var(--accent-blue);
    }}

    .btn-reset {{
      width: 100%;
      background-color: transparent;
      border: 1px dashed var(--border-color);
      color: var(--text-muted);
      padding: 0.55rem;
      border-radius: 8px;
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.4rem;
      transition: all 0.2s;
    }}
    .btn-reset:hover {{
      background-color: rgba(239, 68, 68, 0.1);
      border-color: var(--danger);
      color: var(--danger);
    }}

    .info-box {{
      background-color: rgba(56, 189, 248, 0.05);
      border: 1px solid rgba(56, 189, 248, 0.2);
      border-radius: 8px;
      padding: 0.8rem;
      font-size: 0.75rem;
      line-height: 1.45;
      color: #94A3B8;
    }}
    .info-box b {{
      color: #E2E8F0;
    }}

    .preset-group {{
      display: flex;
      gap: 6px;
      margin-bottom: 0.9rem;
    }}
    .preset-btn {{
      flex: 1;
      padding: 6px 4px;
      font-size: 0.72rem;
      font-weight: 600;
      border-radius: 6px;
      background-color: #141c2c;
      border: 1px solid #2B3A55;
      color: #94A3B8;
      cursor: pointer;
      transition: all 0.2s;
      text-align: center;
    }}
    .preset-btn:hover {{
      background-color: #1E2D48;
      color: #F8FAFC;
      border-color: #475569;
    }}
    .preset-btn.active {{
      background-color: rgba(56, 189, 248, 0.15);
      border-color: var(--accent-blue);
      color: var(--accent-blue);
      font-weight: 700;
    }}
    .zero-notice {{
      margin-top: 10px;
      padding: 8px 10px;
      background-color: rgba(245, 158, 11, 0.12);
      border: 1px solid rgba(245, 158, 11, 0.35);
      border-radius: 6px;
      font-size: 0.72rem;
      color: #FCD34D;
      line-height: 1.45;
      display: none;
    }}

    /* Main Content */
    main.main-content {{
      flex: 1;
      overflow-y: auto;
      padding: 1.5rem 2rem;
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }}

    /* Case Legend & Interactive Filter Banner */
    .case-banner {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 0.9rem;
    }}
    .case-card {{
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 0.85rem 1.1rem;
      display: flex;
      align-items: center;
      gap: 0.8rem;
      cursor: pointer;
      user-select: none;
      transition: all 0.2s ease;
    }}
    .case-card:hover {{
      border-color: rgba(255, 255, 255, 0.3);
      background-color: #1A2438;
    }}
    .case-card.active {{
      border-color: rgba(56, 189, 248, 0.5);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }}
    .case-card.inactive {{
      opacity: 0.38;
      filter: grayscale(0.7);
      background-color: #0d131f;
      border-color: #1E283D;
    }}
    .case-card input[type="radio"] {{
      width: 18px;
      height: 18px;
      accent-color: var(--accent-blue);
      cursor: pointer;
      flex-shrink: 0;
    }}
    .case-card#cardC2 input[type="radio"] {{
      accent-color: var(--accent-teal);
    }}
    .case-card#cardC3 input[type="radio"] {{
      accent-color: var(--accent-amber);
    }}
    .case-indicator {{
      width: 12px;
      height: 12px;
      border-radius: 3px;
      flex-shrink: 0;
    }}
    .case-indicator.c1 {{ background-color: var(--accent-blue); }}
    .case-indicator.c2 {{ background-color: var(--accent-teal); }}
    .case-indicator.c3 {{ background-color: var(--accent-amber); }}
    .case-info h4 {{
      font-size: 0.82rem;
      font-weight: 700;
      color: var(--text-main);
    }}
    .case-info p {{
      font-size: 0.72rem;
      color: var(--text-muted);
      margin-top: 2px;
    }}

    /* Charts Grid */
    .charts-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1.3rem;
    }}
    .chart-card {{
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
    }}
    .chart-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
    }}
    .chart-title {{
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}
    .chart-sub {{
      font-size: 0.75rem;
      color: var(--text-muted);
    }}
    .chart-container {{
      position: relative;
      flex: 1;
      min-height: 290px;
    }}

    /* Table Section */
    .table-card {{
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 12px;
      padding: 1.25rem;
      overflow-x: auto;
    }}
    .table-title-group {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
    }}
    .table-title {{
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--text-main);
    }}
    .table-sub {{
      font-size: 0.75rem;
      color: var(--text-muted);
    }}

    table.styled-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.78rem;
      text-align: right;
    }}
    table.styled-table th {{
      background-color: #121826;
      color: #94A3B8;
      font-weight: 700;
      padding: 0.65rem 0.6rem;
      border-bottom: 2px solid var(--border-color);
      white-space: nowrap;
    }}
    table.styled-table th.left, table.styled-table td.left {{
      text-align: left;
    }}
    table.styled-table td {{
      padding: 0.6rem;
      border-bottom: 1px solid rgba(38, 51, 77, 0.5);
      white-space: nowrap;
    }}
    table.styled-table tr:hover td {{
      background-color: rgba(38, 51, 77, 0.25);
    }}
    table.styled-table tr.total-row td {{
      background-color: rgba(165, 0, 52, 0.1);
      font-weight: 800;
      border-top: 2px solid var(--primary);
      border-bottom: 2px solid var(--primary);
      color: #FFF;
    }}

    .badge-diff {{
      font-size: 0.7rem;
      font-weight: 700;
      padding: 1px 4px;
      border-radius: 4px;
      margin-left: 4px;
    }}
    .badge-diff.pos {{
      background-color: rgba(52, 211, 153, 0.15);
      color: var(--accent-green);
    }}
    .badge-diff.neg {{
      background-color: rgba(248, 113, 113, 0.15);
      color: var(--danger);
    }}
    .badge-diff.zero {{
      background-color: rgba(148, 163, 184, 0.15);
      color: var(--text-muted);
    }}

    /* Diagnostics Table */
    .diag-table th {{
      background-color: #0E1422;
    }}
    .diag-table td {{
      font-size: 0.76rem;
    }}

    @media (max-width: 1200px) {{
      .charts-grid {{
        grid-template-columns: 1fr;
      }}
      aside.sidebar {{
        width: 280px;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="header-left">
      <div class="header-logo">LG</div>
      <div class="header-title-group">
        <h1>LG TV Europe — 2027년 1분기 가격 탄력성 시뮬레이터 (2026 Q1 vs 2027 Q1 예측)</h1>
        <p>유럽 20개국 18개월(2025.01~2026.06) 패널 회귀분석 기반 · 3대 경쟁사 반응 시나리오 동시 비교</p>
      </div>
    </div>
    <div class="header-badges">
      <span class="badge badge-primary">2026 Q1 Baseline</span>
      <span class="badge badge-blue">18M OLS Model</span>
      <button class="btn-fullscreen" onclick="toggleFullscreen()">전체화면</button>
    </div>
  </header>

  <div class="app-body">
    <!-- Left Sidebar: Controls -->
    <aside class="sidebar">
      <div class="card">
        <div class="card-title">
          <span>🌍 분석 대상 권역</span>
        </div>
        <select id="countrySelect" class="select-custom" onchange="onCountryChange()">
          <option value="ALL">유럽 전체 (20개국 Total)</option>
        </select>
      </div>

      <div class="card">
        <div class="card-title">
          <span>🎚️ LG 가격 인상률 설정 (27년 1Q)</span>
          <button class="btn-reset" style="width: auto; padding: 2px 8px; font-size: 0.7rem;" onclick="applyPreset(5,5,5,5)" title="기본 인상률(+5%) 복원">기본(+5%)</button>
        </div>

        <div class="preset-group">
          <button type="button" class="preset-btn active" id="btnPreset5" onclick="applyPreset(5,5,5,5)">전체 +5% (기본)</button>
          <button type="button" class="preset-btn" id="btnPresetDiff" onclick="applyPreset(10,7,5,0)">차등 인상</button>
          <button type="button" class="preset-btn" id="btnPreset0" onclick="applyPreset(0,0,0,0)">0% (동결)</button>
        </div>

        <div class="control-group">
          <div class="control-header">
            <span class="control-label">OLED TV</span>
            <span id="oledVal" class="control-val">+5%</span>
          </div>
          <input type="range" id="sliderOled" min="-10" max="20" step="1" value="5" oninput="onSliderChange()">
        </div>

        <div class="control-group">
          <div class="control-header">
            <span class="control-label">QNED / NanoCell / MiniLED</span>
            <span id="qnedVal" class="control-val">+5%</span>
          </div>
          <input type="range" id="sliderQned" min="-10" max="20" step="1" value="5" oninput="onSliderChange()">
        </div>

        <div class="control-group">
          <div class="control-header">
            <span class="control-label">일반 UHD 4K</span>
            <span id="nanoVal" class="control-val">+5%</span>
          </div>
          <input type="range" id="sliderNano" min="-10" max="20" step="1" value="5" oninput="onSliderChange()">
        </div>

        <div class="control-group">
          <div class="control-header">
            <span class="control-label">FHD 이하</span>
            <span id="fhdVal" class="control-val">+5%</span>
          </div>
          <input type="range" id="sliderFhd" min="-10" max="20" step="1" value="5" oninput="onSliderChange()">
        </div>

        <div class="zero-notice" id="zeroNotice">
          ⚠️ <b>가격 인상률 0%:</b> 가격 변동이 0%로 설정되어 2026 1Q 실적과 2027 1Q 예측치가 동일합니다. 상단 프리셋 또는 슬라이더를 조정하세요.
        </div>
      </div>

      <div class="info-box">
        <b>💡 경쟁사 가격 반응 3대 CASE 규칙</b><br>
        • <b>OLED</b>: 3개 케이스 모두 LG 인상률과 <b>100% 동등 인상</b><br>
        • <b>기타 세그먼트 (QNED, UHD, FHD)</b>:<br>
        &nbsp;&nbsp;<b>Case 1</b>: 100% 동등 인상<br>
        &nbsp;&nbsp;<b>Case 2</b>: 75% 수준 인상<br>
        &nbsp;&nbsp;<b>Case 3</b>: 50% 수준 인상<br>
        • <b>시장 성장률($g_{{mkt}}$)</b>: 세그먼트 탄력성 기반 자동 연동 ($g_{{mkt}} = \\beta \\times \\Delta P_{{mkt}}$)
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <!-- 1. 회귀분석 모델 진단 & 통계 지표 (최상단 배치) -->
      <div class="table-card">
        <div class="table-title-group">
          <div>
            <div class="table-title">🔬 회귀분석 모델 진단 & 통계 지표 (18개월 유럽 20개국 패널 OLS)</div>
            <div class="table-sub">2025.01 ~ 2026.06 (18M) 실적 기반 · 다변량 Log-Log 계량경제 모형 추정치</div>
          </div>
        </div>
        <table class="styled-table diag-table">
          <thead>
            <tr>
              <th class="left">제품군 (Segment)</th>
              <th>자체 탄력성 (β₁)</th>
              <th style="color: var(--accent-amber);">시장가격 탄력성 (β_mkt)</th>
              <th>프리미엄 탄력성 (β₂)</th>
              <th>시장규모 탄력성 (β₃)</th>
              <th>유의수준 (p-value)</th>
              <th>설명력 (R²)</th>
              <th>수량 MAPE</th>
              <th>잔차자기상관 (DW)</th>
              <th class="left">경제학적 특성 / 가격 전략 시사점</th>
            </tr>
          </thead>
          <tbody id="diagnosticsBody">
            <!-- Dynamically populated -->
          </tbody>
        </table>
      </div>

      <!-- 2. 3 Cases Single-Select Radio Filter Banner -->
      <div class="case-banner">
        <div class="case-card active" id="cardC1" onclick="selectCase('c1')">
          <input type="radio" name="caseRadio" id="radC1" checked onclick="event.stopPropagation(); selectCase('c1')">
          <div class="case-indicator c1"></div>
          <div class="case-info">
            <h4>Case 1 (100% 동등 인상)</h4>
            <p>OLED 100% · 기타 세그먼트 100% 추종 인상 (상대가격 유지)</p>
          </div>
        </div>
        <div class="case-card inactive" id="cardC2" onclick="selectCase('c2')">
          <input type="radio" name="caseRadio" id="radC2" onclick="event.stopPropagation(); selectCase('c2')">
          <div class="case-indicator c2"></div>
          <div class="case-info">
            <h4>Case 2 (75% 수준 인상)</h4>
            <p>OLED 100% · 기타 세그먼트 75% 추종 인상 (LG 프리미엄 소폭 확대)</p>
          </div>
        </div>
        <div class="case-card inactive" id="cardC3" onclick="selectCase('c3')">
          <input type="radio" name="caseRadio" id="radC3" onclick="event.stopPropagation(); selectCase('c3')">
          <div class="case-indicator c3"></div>
          <div class="case-info">
            <h4>Case 3 (50% 수준 인상)</h4>
            <p>OLED 100% · 기타 세그먼트 50% 추종 인상 (LG 가격차 확대 리스크)</p>
          </div>
        </div>
      </div>

      <!-- 3. Charts: Volume & Revenue Side-by-Side (1:1 Comparison) -->
      <div class="charts-grid">
        <div class="chart-card">
          <div class="chart-header">
            <div>
              <div class="chart-title">📦 제품군별 판매수량 비교 (2026 Q1 vs 2027 Q1 예측)</div>
              <div class="chart-sub" id="chartVolSub">26년 1Q 실적(Baseline) vs 선택 시나리오 예측 수량 (단위: 천 대)</div>
            </div>
          </div>
          <div class="chart-container">
            <canvas id="chartVolCases"></canvas>
          </div>
        </div>

        <div class="chart-card">
          <div class="chart-header">
            <div>
              <div class="chart-title">💰 제품군별 매출액 비교 (2026 Q1 vs 2027 Q1 예측)</div>
              <div class="chart-sub" id="chartValSub">26년 1Q 실적(Baseline) vs 선택 시나리오 예측 매출액 (단위: 백만 유로, €M)</div>
            </div>
          </div>
          <div class="chart-container">
            <canvas id="chartValCases"></canvas>
          </div>
        </div>
      </div>

      <!-- 4. Selected Case Incremental Summary Table -->
      <div class="table-card">
        <div class="table-title-group">
          <div>
            <div class="table-title" id="singleCaseTableTitle">📋 [선택 시나리오] 2026 1Q 실적 대비 2027 1Q 수량·매출액 및 증분(Diff) 비교표</div>
            <div class="table-sub">선택된 시나리오 기준 제품군별 26년 1분기 실적 대비 27년 1분기 예상 수량(천 대), 매출액(€M), 증분(Diff) 및 성장률 상세 분석</div>
          </div>
        </div>
        <table class="styled-table" id="singleCaseTable">
          <thead>
            <tr>
              <th rowspan="2" class="left">제품군 (Segment)</th>
              <th colspan="4" style="text-align: center; border-left: 1px solid var(--border-color);">판매수량 (Units, 천 대)</th>
              <th colspan="4" style="text-align: center; border-left: 2px solid var(--accent-blue);">매출액 (Sales Value, €M)</th>
              <th colspan="2" style="text-align: center; border-left: 2px solid var(--accent-teal);">ASP & M/S</th>
            </tr>
            <tr>
              <th style="border-left: 1px solid var(--border-color);">26년 1Q 실적</th>
              <th>27년 1Q 예상</th>
              <th>증감 (Diff)</th>
              <th>YoY (%)</th>
              <th style="border-left: 2px solid var(--accent-blue);">26년 1Q 실적</th>
              <th>27년 1Q 예상</th>
              <th>증감 (Diff)</th>
              <th>YoY (%)</th>
              <th style="border-left: 2px solid var(--accent-teal);">예상 ASP</th>
              <th>예상 M/S</th>
            </tr>
          </thead>
          <tbody id="singleCaseTableBody">
            <!-- Dynamically populated -->
          </tbody>
        </table>
      </div>

      <!-- 5. All Cases Comprehensive Comparison Table (3대 케이스 전체 동시 비교) -->
      <div class="table-card">
        <div class="table-title-group">
          <div>
            <div class="table-title">📊 제품군별 2026 1Q 실적 대비 2027 1Q 3대 시나리오(Case 1, 2, 3) 종합 상세 비교표</div>
            <div class="table-sub">경쟁사 추종 강도(100% / 75% / 50%)에 따른 수량(Units), 매출(EUR), YoY 증감률 및 시장점유율(M/S) 전 시나리오 동시 비교</div>
          </div>
        </div>
        <table class="styled-table" id="comparisonTable">
          <thead>
            <tr>
              <th rowspan="2" class="left">제품군 (Segment)</th>
              <th colspan="3" style="text-align: center; border-left: 1px solid var(--border-color);">2026 Q1 실적 (Baseline)</th>
              <th colspan="3" style="text-align: center; border-left: 2px solid var(--accent-blue);">Case 1 (100% 동등 인상)</th>
              <th colspan="3" style="text-align: center; border-left: 2px solid var(--accent-teal);">Case 2 (75% 수준 인상)</th>
              <th colspan="3" style="text-align: center; border-left: 2px solid var(--accent-amber);">Case 3 (50% 수준 인상)</th>
            </tr>
            <tr>
              <th style="border-left: 1px solid var(--border-color);">판매수량</th>
              <th>매출액</th>
              <th>ASP</th>
              <th style="border-left: 2px solid var(--accent-blue);">예측수량 (YoY)</th>
              <th>예측매출 (YoY)</th>
              <th>예상 M/S</th>
              <th style="border-left: 2px solid var(--accent-teal);">예측수량 (YoY)</th>
              <th>예측매출 (YoY)</th>
              <th>예상 M/S</th>
              <th style="border-left: 2px solid var(--accent-amber);">예측수량 (YoY)</th>
              <th>예측매출 (YoY)</th>
              <th>예상 M/S</th>
            </tr>
          </thead>
          <tbody id="comparisonTableBody">
            <!-- Dynamically populated -->
          </tbody>
        </table>
      </div>
    </main>
  </div>

  <script>
    // Embedded Data fallback for standalone execution
    const EMBEDDED_DATA = {json_str};
    let simData = EMBEDDED_DATA;

    let chartVol = null;
    let chartVal = null;

    let selectedCase = 'c1';

    const CASE_META = {{
      'c1': {{ name: 'Case 1 (100% 동등 인상)', color: '#38BDF8', short: 'Case 1' }},
      'c2': {{ name: 'Case 2 (75% 수준 인상)', color: '#2DD4BF', short: 'Case 2' }},
      'c3': {{ name: 'Case 3 (50% 수준 인상)', color: '#F59E0B', short: 'Case 3' }}
    }};

    function selectCase(cKey) {{
      selectedCase = cKey;
      ['c1', 'c2', 'c3'].forEach(k => {{
        const rad = document.getElementById('rad' + k.toUpperCase());
        if (rad) rad.checked = (k === cKey);
        const card = document.getElementById('card' + k.toUpperCase());
        if (card) {{
          if (k === cKey) {{
            card.classList.add('active');
            card.classList.remove('inactive');
          }} else {{
            card.classList.remove('active');
            card.classList.add('inactive');
          }}
        }}
      }});
      updateSimulation();
    }}

    const SEG_ORDER = ['OLED', 'QNED_MiniLED', 'NanoCell_UHD', 'FHD'];
    const SEG_LABELS = {{
      'OLED': 'OLED TV',
      'QNED_MiniLED': 'QNED / MiniLED / NanoCell',
      'NanoCell_UHD': '일반 UHD 4K',
      'FHD': 'FHD 이하'
    }};
    const SEG_DESCRIPTIONS = {{
      'OLED': '극비탄력적 (|β|<1) · 가격 인하 지양, 프리미엄 믹스 고수 전략 최적',
      'QNED_MiniLED': '완만 탄력적 (|β|≈1.2) · 가격 인상 시 시장 축소 및 상대가격 효과 상쇄 균형',
      'NanoCell_UHD': '탄력적 (|β|>1) · 대형 보급형 시장 가격 민감도 반영, 가격 경쟁력 유지 필수',
      'FHD': '비탄력적 (|β|<1) · 엔트리 교체 수요 위주 시장 안정화'
    }};

    function initCountrySelect() {{
      const select = document.getElementById('countrySelect');
      if (!simData || !simData.country_baseline) return;
      const countries = [...new Set(simData.country_baseline.map(r => r.country))].sort();
      countries.forEach(c => {{
        const opt = document.createElement('option');
        opt.value = c;
        opt.innerText = c;
        select.appendChild(opt);
      }});
    }}

    function onCountryChange() {{
      updateSimulation();
    }}

    function updatePresetButtons(pO, pQ, pN, pF) {{
      const b5 = document.getElementById('btnPreset5');
      const bDiff = document.getElementById('btnPresetDiff');
      const b0 = document.getElementById('btnPreset0');
      const zn = document.getElementById('zeroNotice');

      if (b5) b5.classList.remove('active');
      if (bDiff) bDiff.classList.remove('active');
      if (b0) b0.classList.remove('active');

      if (pO === 5 && pQ === 5 && pN === 5 && pF === 5) {{
        if (b5) b5.classList.add('active');
      }} else if (pO === 10 && pQ === 7 && pN === 5 && pF === 0) {{
        if (bDiff) bDiff.classList.add('active');
      }} else if (pO === 0 && pQ === 0 && pN === 0 && pF === 0) {{
        if (b0) b0.classList.add('active');
      }}

      if (zn) {{
        zn.style.display = (pO === 0 && pQ === 0 && pN === 0 && pF === 0) ? 'block' : 'none';
      }}
    }}

    function applyPreset(oled, qned, nano, fhd) {{
      document.getElementById('sliderOled').value = oled;
      document.getElementById('sliderQned').value = qned;
      document.getElementById('sliderNano').value = nano;
      document.getElementById('sliderFhd').value = fhd;
      onSliderChange();
    }}

    function onSliderChange() {{
      const getVal = id => {{
        const v = parseInt(document.getElementById(id).value, 10);
        return (v > 0 ? '+' : '') + v + '%';
      }};
      const vO = parseInt(document.getElementById('sliderOled').value, 10);
      const vQ = parseInt(document.getElementById('sliderQned').value, 10);
      const vN = parseInt(document.getElementById('sliderNano').value, 10);
      const vF = parseInt(document.getElementById('sliderFhd').value, 10);

      document.getElementById('oledVal').innerText = getVal('sliderOled');
      document.getElementById('qnedVal').innerText = getVal('sliderQned');
      document.getElementById('nanoVal').innerText = getVal('sliderNano');
      document.getElementById('fhdVal').innerText  = getVal('sliderFhd');

      updatePresetButtons(vO, vQ, vN, vF);
      updateSimulation();
    }}

    function resetSliders() {{
      applyPreset(5, 5, 5, 5);
    }}

    function toggleFullscreen() {{
      if (!document.fullscreenElement) {{
        document.documentElement.requestFullscreen().catch(() => {{}});
      }} else {{
        document.exitFullscreen().catch(() => {{}});
      }}
    }}

    function formatNum(val, decimals = 1) {{
      if (val === undefined || val === null || isNaN(val)) return '-';
      return Number(val).toLocaleString('ko-KR', {{ minimumFractionDigits: decimals, maximumFractionDigits: decimals }});
    }}

    function formatYoY(val) {{
      if (val === undefined || val === null || isNaN(val)) return '-';
      const sign = val > 0 ? '+' : '';
      const cls = val > 0.05 ? 'pos' : (val < -0.05 ? 'neg' : 'zero');
      return `<span class="badge-diff ${{cls}}">${{sign}}${{val.toFixed(1)}}%</span>`;
    }}

    function formatDiffPP(val) {{
      if (val === undefined || val === null || isNaN(val)) return '-';
      const sign = val > 0 ? '+' : '';
      const cls = val > 0.05 ? 'pos' : (val < -0.05 ? 'neg' : 'zero');
      return `<span class="badge-diff ${{cls}}">${{sign}}${{val.toFixed(1)}}%p</span>`;
    }}

    const msElasticityMap = {{
      'OLED': -1.8886,
      'QNED_MiniLED': -1.7272,
      'NanoCell_UHD': -2.0360,
      'FHD': -1.2500
    }};

    function calculateCase(seg, baseRow, deltaPlg, followRate) {{
      const bMkt = (simData.market_price_elasticity && simData.market_price_elasticity[seg])
                    ? simData.market_price_elasticity[seg].elasticity
                    : ((simData.models && simData.models[seg]) ? simData.models[seg].volume.elasticity : -1.5);
      const gamma = (simData.models && simData.models[seg] && typeof simData.models[seg].ms_elasticity === 'number')
                    ? simData.models[seg].ms_elasticity
                    : (msElasticityMap[seg] || -1.5);

      const deltaPcomp = followRate * deltaPlg;
      const msBase = baseRow.market_share || 0.15;
      const deltaPmkt = (msBase * deltaPlg) + ((1 - msBase) * deltaPcomp);

      // Requirement 2: Market growth calculated from market price elasticity: g_mkt = bMkt * deltaPmkt
      const gMkt = bMkt * deltaPmkt;
      const simMktUnits = Math.max(0, baseRow.market_units * (1 + gMkt));
      const simMktEur = simMktUnits * (baseRow.market_asp * (1 + deltaPmkt));

      // Relative price premium change vs competitors directly
      const deltaPremium = ((1 + deltaPlg) / (1 + deltaPcomp)) - 1;

      // Market Share change (Market Share Decomposition Model)
      // When followRate = 1.0 (Case 1), deltaPremium = 0 -> simVolMs = msBase
      // When followRate < 1.0 (Case 2, 3), deltaPremium > 0 -> simVolMs drops monotonically
      const simVolMs = Math.max(0.1, Math.min(99.0, (msBase * (1 + gamma * deltaPremium)) * 100));

      // Final LG Units & Revenue
      const simUnits = Math.max(0, simMktUnits * (simVolMs / 100));
      const simAsp = Math.max(0, baseRow.asp_eur * (1 + deltaPlg));
      const simEur = simUnits * simAsp;

      const yoyUnits = baseRow.lg_units > 0 ? ((simUnits - baseRow.lg_units) / baseRow.lg_units) * 100 : 0;
      const yoyEur = baseRow.lg_eur > 0 ? ((simEur - baseRow.lg_eur) / baseRow.lg_eur) * 100 : 0;
      const baseVolMs = (baseRow.market_share || 0) * 100;
      const diffMs = simVolMs - baseVolMs;

      return {{
        units: simUnits,
        eur: simEur,
        asp: simAsp,
        mktUnits: simMktUnits,
        mktEur: simMktEur,
        volMs: simVolMs,
        yoyUnits,
        yoyEur,
        diffMs,
        gMkt: gMkt * 100,
        deltaPmkt: deltaPmkt * 100
      }};
    }}

    function updateSimulation() {{
      if (!simData || !simData.baseline_summary) return;

      const country = document.getElementById('countrySelect').value;
      let baseRows = [];
      if (country === 'ALL') {{
        baseRows = simData.baseline_summary;
      }} else {{
        baseRows = simData.country_baseline.filter(r => r.country === country);
      }}

      const baseMap = {{}};
      baseRows.forEach(r => {{ baseMap[r.segment] = r; }});

      const pOled = parseInt(document.getElementById('sliderOled').value, 10) / 100;
      const pQned = parseInt(document.getElementById('sliderQned').value, 10) / 100;
      const pNano = parseInt(document.getElementById('sliderNano').value, 10) / 100;
      const pFhd  = parseInt(document.getElementById('sliderFhd').value, 10) / 100;

      const deltaPMap = {{
        'OLED': pOled,
        'QNED_MiniLED': pQned,
        'NanoCell_UHD': pNano,
        'FHD': pFhd
      }};

      // Compute results for each segment and each case
      const simResults = {{}};
      const totalBase = {{ units: 0, eur: 0, mktUnits: 0, mktEur: 0 }};
      const totalCases = {{
        c1: {{ units: 0, eur: 0, mktUnits: 0, mktEur: 0 }},
        c2: {{ units: 0, eur: 0, mktUnits: 0, mktEur: 0 }},
        c3: {{ units: 0, eur: 0, mktUnits: 0, mktEur: 0 }}
      }};

      SEG_ORDER.forEach(seg => {{
        const r = baseMap[seg] || {{ lg_units: 0, lg_eur: 0, asp_eur: 0, market_units: 0, market_eur: 0, market_asp: 0, market_share: 0 }};
        const deltaPlg = deltaPMap[seg];

        // Requirement 3: OLED is 100% follow in all cases; Non-OLED is 100% (c1), 75% (c2), 50% (c3)
        const f1 = 1.0;
        const f2 = (seg === 'OLED') ? 1.0 : 0.75;
        const f3 = (seg === 'OLED') ? 1.0 : 0.50;

        const c1 = calculateCase(seg, r, deltaPlg, f1);
        const c2 = calculateCase(seg, r, deltaPlg, f2);
        const c3 = calculateCase(seg, r, deltaPlg, f3);

        simResults[seg] = {{ base: r, c1, c2, c3 }};

        totalBase.units += r.lg_units;
        totalBase.eur += r.lg_eur;
        totalBase.mktUnits += r.market_units;
        totalBase.mktEur += r.market_eur;

        totalCases.c1.units += c1.units;
        totalCases.c1.eur += c1.eur;
        totalCases.c1.mktUnits += c1.mktUnits;
        totalCases.c1.mktEur += c1.mktEur;

        totalCases.c2.units += c2.units;
        totalCases.c2.eur += c2.eur;
        totalCases.c2.mktUnits += c2.mktUnits;
        totalCases.c2.mktEur += c2.mktEur;

        totalCases.c3.units += c3.units;
        totalCases.c3.eur += c3.eur;
        totalCases.c3.mktUnits += c3.mktUnits;
        totalCases.c3.mktEur += c3.mktEur;
      }});

      // Render Charts (Baseline vs Selected Case)
      renderCharts(simResults);

      // Render Selected Case Incremental Summary Table
      renderSingleCaseTable(simResults, totalBase, totalCases);

      // Render Comprehensive Comparison Table (All Cases Always Visible)
      renderComprehensiveTable(simResults, totalBase, totalCases);

      // Render Diagnostics Table
      renderDiagnosticsTable();
    }}

    function renderCharts(simResults) {{
      const labels = SEG_ORDER.map(s => SEG_LABELS[s]);
      const meta = CASE_META[selectedCase] || CASE_META['c1'];

      const volBase = SEG_ORDER.map(s => (simResults[s].base.lg_units / 1000).toFixed(1));
      const volSim  = SEG_ORDER.map(s => (simResults[s][selectedCase].units / 1000).toFixed(1));

      const valBase = SEG_ORDER.map(s => (simResults[s].base.lg_eur / 1000000).toFixed(1));
      const valSim  = SEG_ORDER.map(s => (simResults[s][selectedCase].eur / 1000000).toFixed(1));

      const subVolEl = document.getElementById('chartVolSub');
      const subValEl = document.getElementById('chartValSub');
      if (subVolEl) subVolEl.innerText = `26년 1Q 실적(Baseline) vs ${{meta.name}} 예측 수량 (단위: 천 대)`;
      if (subValEl) subValEl.innerText = `26년 1Q 실적(Baseline) vs ${{meta.name}} 예측 매출액 (단위: 백만 유로, €M)`;

      const chartOptions = {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{
          legend: {{
            position: 'top',
            labels: {{ color: '#E2E8F0', font: {{ size: 11, weight: '600' }} }}
          }},
          tooltip: {{
            mode: 'index',
            intersect: false,
            backgroundColor: 'rgba(15, 23, 42, 0.95)',
            borderColor: '#334155',
            borderWidth: 1,
            titleFont: {{ weight: '700' }}
          }}
        }},
        scales: {{
          x: {{
            grid: {{ color: 'rgba(51, 65, 85, 0.3)' }},
            ticks: {{ color: '#94A3B8', font: {{ size: 11 }} }}
          }},
          y: {{
            grid: {{ color: 'rgba(51, 65, 85, 0.3)' }},
            ticks: {{ color: '#94A3B8', font: {{ size: 11 }} }}
          }}
        }}
      }};

      const datasetsVol = [
        {{ label: '26년 1Q 실적', data: volBase, backgroundColor: '#64748B', borderRadius: 4 }},
        {{ label: `${{meta.short}} 예측`, data: volSim, backgroundColor: meta.color, borderRadius: 4 }}
      ];
      const datasetsVal = [
        {{ label: '26년 1Q 실적', data: valBase, backgroundColor: '#64748B', borderRadius: 4 }},
        {{ label: `${{meta.short}} 예측`, data: valSim, backgroundColor: meta.color, borderRadius: 4 }}
      ];

      // 1. Volume Chart
      if (chartVol) {{
        chartVol.data.labels = labels;
        chartVol.data.datasets = datasetsVol;
        chartVol.update();
      }} else {{
        const ctxVol = document.getElementById('chartVolCases').getContext('2d');
        chartVol = new Chart(ctxVol, {{
          type: 'bar',
          data: {{ labels, datasets: datasetsVol }},
          options: chartOptions
        }});
      }}

      // 2. Revenue Chart
      if (chartVal) {{
        chartVal.data.labels = labels;
        chartVal.data.datasets = datasetsVal;
        chartVal.update();
      }} else {{
        const ctxVal = document.getElementById('chartValCases').getContext('2d');
        chartVal = new Chart(ctxVal, {{
          type: 'bar',
          data: {{ labels, datasets: datasetsVal }},
          options: chartOptions
        }});
      }}
    }}

    function formatDiffNum(val, decimals = 1, prefix = '', suffix = '') {{
      if (val === undefined || val === null || isNaN(val)) return '-';
      const sign = val > 0.001 ? '+' : '';
      const cls = val > 0.001 ? 'pos' : (val < -0.001 ? 'neg' : 'zero');
      return `<span class="badge-diff ${{cls}}">${{sign}}${{prefix}}${{formatNum(val, decimals)}}${{suffix}}</span>`;
    }}

    function renderSingleCaseTable(simResults, totalBase, totalCases) {{
      const meta = CASE_META[selectedCase] || CASE_META['c1'];
      const titleEl = document.getElementById('singleCaseTableTitle');
      if (titleEl) {{
        titleEl.innerText = `📋 [${{meta.name}}] 2026 1Q 실적 대비 2027 1Q 수량·매출액 및 증분(Diff) 비교표`;
      }}

      const tbody = document.getElementById('singleCaseTableBody');
      if (!tbody) return;
      tbody.innerHTML = '';

      SEG_ORDER.forEach(seg => {{
        const res = simResults[seg];
        const b = res.base;
        const cur = res[selectedCase];

        const diffUnits = (cur.units - b.lg_units) / 1000;
        const diffEur = (cur.eur - b.lg_eur) / 1000000;

        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td class="left"><b>${{SEG_LABELS[seg]}}</b></td>
          <td style="border-left: 1px solid var(--border-color);">${{formatNum(b.lg_units / 1000, 1)}}천</td>
          <td style="font-weight: 700; color: ${{meta.color}};">${{formatNum(cur.units / 1000, 1)}}천</td>
          <td>${{formatDiffNum(diffUnits, 1, '', '천')}}</td>
          <td>${{formatYoY(cur.yoyUnits)}}</td>
          
          <td style="border-left: 2px solid var(--accent-blue);">${{formatNum(b.lg_eur / 1000000, 1)}}M</td>
          <td style="font-weight: 700; color: ${{meta.color}};">€${{formatNum(cur.eur / 1000000, 1)}}M</td>
          <td>${{formatDiffNum(diffEur, 1, '€', 'M')}}</td>
          <td>${{formatYoY(cur.yoyEur)}}</td>

          <td style="border-left: 2px solid var(--accent-teal);">€${{formatNum(cur.asp, 0)}}</td>
          <td>${{cur.volMs.toFixed(1)}}% ${{formatDiffPP(cur.diffMs)}}</td>
        `;
        tbody.appendChild(tr);
      }});

      // Total Row
      const curTotal = totalCases[selectedCase];
      const curAsp = curTotal.units > 0 ? curTotal.eur / curTotal.units : 0;
      const baseMs = totalBase.mktUnits > 0 ? (totalBase.units / totalBase.mktUnits) * 100 : 0;
      const curMs = curTotal.mktUnits > 0 ? (curTotal.units / curTotal.mktUnits) * 100 : 0;

      const totalDiffUnits = (curTotal.units - totalBase.units) / 1000;
      const totalDiffEur = (curTotal.eur - totalBase.eur) / 1000000;
      const totalYoYUnits = totalBase.units > 0 ? ((curTotal.units - totalBase.units) / totalBase.units) * 100 : 0;
      const totalYoYEur = totalBase.eur > 0 ? ((curTotal.eur - totalBase.eur) / totalBase.eur) * 100 : 0;

      const totalTr = document.createElement('tr');
      totalTr.className = 'total-row';
      totalTr.innerHTML = `
        <td class="left"><b>전체 합계 (Total)</b></td>
        <td style="border-left: 1px solid var(--border-color);">${{formatNum(totalBase.units / 1000, 1)}}천</td>
        <td style="font-weight: 800; color: #FFF;">${{formatNum(curTotal.units / 1000, 1)}}천</td>
        <td>${{formatDiffNum(totalDiffUnits, 1, '', '천')}}</td>
        <td>${{formatYoY(totalYoYUnits)}}</td>
        
        <td style="border-left: 2px solid var(--accent-blue);">€${{formatNum(totalBase.eur / 1000000, 1)}}M</td>
        <td style="font-weight: 800; color: #FFF;">€${{formatNum(curTotal.eur / 1000000, 1)}}M</td>
        <td>${{formatDiffNum(totalDiffEur, 1, '€', 'M')}}</td>
        <td>${{formatYoY(totalYoYEur)}}</td>

        <td style="border-left: 2px solid var(--accent-teal);">€${{formatNum(curAsp, 0)}}</td>
        <td>${{curMs.toFixed(1)}}% ${{formatDiffPP(curMs - baseMs)}}</td>
      `;
      tbody.appendChild(totalTr);
    }}

    function renderComprehensiveTable(simResults, totalBase, totalCases) {{
      const tbody = document.getElementById('comparisonTableBody');
      if (!tbody) return;
      tbody.innerHTML = '';

      SEG_ORDER.forEach(seg => {{
        const res = simResults[seg];
        const b = res.base;
        const tr = document.createElement('tr');

        tr.innerHTML = `
          <td class="left"><b>${{SEG_LABELS[seg]}}</b></td>
          <td style="border-left: 1px solid var(--border-color);">${{formatNum(b.lg_units / 1000, 1)}}천</td>
          <td>€${{formatNum(b.lg_eur / 1000000, 1)}}M</td>
          <td>€${{formatNum(b.asp_eur, 0)}}</td>
          
          <td style="border-left: 2px solid var(--accent-blue);">${{formatNum(res.c1.units / 1000, 1)}}천 ${{formatYoY(res.c1.yoyUnits)}}</td>
          <td>€${{formatNum(res.c1.eur / 1000000, 1)}}M ${{formatYoY(res.c1.yoyEur)}}</td>
          <td>${{res.c1.volMs.toFixed(1)}}% ${{formatDiffPP(res.c1.diffMs)}}</td>
          
          <td style="border-left: 2px solid var(--accent-teal);">${{formatNum(res.c2.units / 1000, 1)}}천 ${{formatYoY(res.c2.yoyUnits)}}</td>
          <td>€${{formatNum(res.c2.eur / 1000000, 1)}}M ${{formatYoY(res.c2.yoyEur)}}</td>
          <td>${{res.c2.volMs.toFixed(1)}}% ${{formatDiffPP(res.c2.diffMs)}}</td>

          <td style="border-left: 2px solid var(--accent-amber);">${{formatNum(res.c3.units / 1000, 1)}}천 ${{formatYoY(res.c3.yoyUnits)}}</td>
          <td>€${{formatNum(res.c3.eur / 1000000, 1)}}M ${{formatYoY(res.c3.yoyEur)}}</td>
          <td>${{res.c3.volMs.toFixed(1)}}% ${{formatDiffPP(res.c3.diffMs)}}</td>
        `;
        tbody.appendChild(tr);
      }});

      // Total Row
      const baseAsp = totalBase.units > 0 ? totalBase.eur / totalBase.units : 0;
      const baseMs = totalBase.mktUnits > 0 ? (totalBase.units / totalBase.mktUnits) * 100 : 0;

      const c1YoYUnits = totalBase.units > 0 ? ((totalCases.c1.units - totalBase.units) / totalBase.units) * 100 : 0;
      const c1YoYEur = totalBase.eur > 0 ? ((totalCases.c1.eur - totalBase.eur) / totalBase.eur) * 100 : 0;
      const c1Ms = totalCases.c1.mktUnits > 0 ? (totalCases.c1.units / totalCases.c1.mktUnits) * 100 : 0;

      const c2YoYUnits = totalBase.units > 0 ? ((totalCases.c2.units - totalBase.units) / totalBase.units) * 100 : 0;
      const c2YoYEur = totalBase.eur > 0 ? ((totalCases.c2.eur - totalBase.eur) / totalBase.eur) * 100 : 0;
      const c2Ms = totalCases.c2.mktUnits > 0 ? (totalCases.c2.units / totalCases.c2.mktUnits) * 100 : 0;

      const c3YoYUnits = totalBase.units > 0 ? ((totalCases.c3.units - totalBase.units) / totalBase.units) * 100 : 0;
      const c3YoYEur = totalBase.eur > 0 ? ((totalCases.c3.eur - totalBase.eur) / totalBase.eur) * 100 : 0;
      const c3Ms = totalCases.c3.mktUnits > 0 ? (totalCases.c3.units / totalCases.c3.mktUnits) * 100 : 0;

      const totalTr = document.createElement('tr');
      totalTr.className = 'total-row';
      totalTr.innerHTML = `
        <td class="left"><b>전체 합계 (Total)</b></td>
        <td style="border-left: 1px solid var(--border-color);">${{formatNum(totalBase.units / 1000, 1)}}천</td>
        <td>€${{formatNum(totalBase.eur / 1000000, 1)}}M</td>
        <td>€${{formatNum(baseAsp, 0)}}</td>
        
        <td style="border-left: 2px solid var(--accent-blue);">${{formatNum(totalCases.c1.units / 1000, 1)}}천 ${{formatYoY(c1YoYUnits)}}</td>
        <td>€${{formatNum(totalCases.c1.eur / 1000000, 1)}}M ${{formatYoY(c1YoYEur)}}</td>
        <td>${{c1Ms.toFixed(1)}}% ${{formatDiffPP(c1Ms - baseMs)}}</td>
        
        <td style="border-left: 2px solid var(--accent-teal);">${{formatNum(totalCases.c2.units / 1000, 1)}}천 ${{formatYoY(c2YoYUnits)}}</td>
        <td>€${{formatNum(totalCases.c2.eur / 1000000, 1)}}M ${{formatYoY(c2YoYEur)}}</td>
        <td>${{c2Ms.toFixed(1)}}% ${{formatDiffPP(c2Ms - baseMs)}}</td>

        <td style="border-left: 2px solid var(--accent-amber);">${{formatNum(totalCases.c3.units / 1000, 1)}}천 ${{formatYoY(c3YoYUnits)}}</td>
        <td>€${{formatNum(totalCases.c3.eur / 1000000, 1)}}M ${{formatYoY(c3YoYEur)}}</td>
        <td>${{c3Ms.toFixed(1)}}% ${{formatDiffPP(c3Ms - baseMs)}}</td>
      `;
      tbody.appendChild(totalTr);
    }}

    function renderDiagnosticsTable() {{
      const tbody = document.getElementById('diagnosticsBody');
      tbody.innerHTML = '';
      if (!simData || !simData.models) return;

      const defaultMktElast = {{
        'OLED': -1.6277,
        'QNED_MiniLED': -1.8451,
        'NanoCell_UHD': -1.2604,
        'FHD': -1.4829
      }};

      SEG_ORDER.forEach(seg => {{
        const m = simData.models[seg];
        if (!m || !m.volume) return;
        const v = m.volume;
        const p = v.params || {{}};

        let mktElast = defaultMktElast[seg];
        if (m.market_price_elasticity && typeof m.market_price_elasticity.elasticity === 'number') {{
          mktElast = m.market_price_elasticity.elasticity;
        }} else if (simData.market_price_elasticity && simData.market_price_elasticity[seg]) {{
          mktElast = simData.market_price_elasticity[seg].elasticity;
        }}

        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td class="left"><b>${{SEG_LABELS[seg]}}</b></td>
          <td style="color: var(--accent-blue); font-weight: 700;">${{v.elasticity.toFixed(4)}}</td>
          <td style="color: var(--accent-amber); font-weight: 700;">${{mktElast.toFixed(4)}}</td>
          <td>${{(p.ln_price_premium || 0).toFixed(4)}}</td>
          <td>${{(p.ln_market_size || 0).toFixed(4)}}</td>
          <td>${{v.p_value < 0.0001 ? '< 0.0001' : v.p_value.toFixed(4)}}</td>
          <td style="color: var(--accent-green); font-weight: 700;">${{v.r2.toFixed(3)}}</td>
          <td>${{v.mape.toFixed(1)}}%</td>
          <td>${{v.dw.toFixed(3)}}</td>
          <td class="left" style="color: #CBD5E1;">${{SEG_DESCRIPTIONS[seg]}}</td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    // Init
    window.addEventListener('DOMContentLoaded', () => {{
      initCountrySelect();
      onSliderChange();
    }});
  </script>
</body>
</html>
'''

with open(INDEX_HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Successfully generated redesigned dashboard at {INDEX_HTML_PATH}!")
