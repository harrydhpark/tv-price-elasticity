import os
import json
import re

DATA_DIR = r"d:\TV 유럽영업\15. AX Task\2026 AX 실행과제\12. 가격 탄력성 회귀분석\DATA"
DASHBOARD_DIR = r"d:\TV 유럽영업\15. AX Task\2026 AX 실행과제\12. 가격 탄력성 회귀분석\dashboard"
SIM_JSON_PATH = os.path.join(DASHBOARD_DIR, "simulation_data.json")
INDEX_HTML_PATH = os.path.join(DASHBOARD_DIR, "index.html")

def update_dashboard():
    if not os.path.exists(SIM_JSON_PATH):
        raise FileNotFoundError(f"Simulation data not found at {SIM_JSON_PATH}")
    
    with open(SIM_JSON_PATH, 'r', encoding='utf-8') as f:
        sim_data = json.load(f)
    
    json_str = json.dumps(sim_data, indent=2, ensure_ascii=False)

    if not os.path.exists(INDEX_HTML_PATH):
        raise FileNotFoundError(f"Dashboard template not found at {INDEX_HTML_PATH}")

    with open(INDEX_HTML_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update Title & Subtitle in HTML
    old_title = '<div class="table-title">🔬 회귀분석 모델 진단 & 통계 지표 (18개월 유럽 20개국 패널 OLS)</div>'
    new_title = '<div class="table-title">🔬 회귀분석 모델 진단 & 통계 지표 (42개월 유럽 20개국 패널 WLS)</div>'
    if old_title in content:
        content = content.replace(old_title, new_title)
        
    old_sub = '<div class="table-sub">2025.01 ~ 2026.06 (18M) 실적 기반 · 다변량 Log-Log 계량경제 모형 (유럽 TV 총수요 통제 계량경제 보정치 반영)</div>'
    new_sub = '<div class="table-sub">2023.01 ~ 2026.06 (42M) 실적 기반 · 시간 가중 회귀(WLS) 및 국가/월 고정효과(Country & Month FE) 적용 다변량 Log-Log 계량경제 모형</div>'
    if old_sub in content:
        content = content.replace(old_sub, new_sub)

    # 2. Update Table Headers
    old_thead_pattern = r'<thead>\s*<tr>\s*<th class="left">제품군 \(Segment\)</th>[\s\S]*?</tr>\s*</thead>'
    new_thead = '''<thead>
            <tr>
              <th class="left">제품군 (Segment)</th>
              <th class="diag-tooltip-th" data-name="자체 탄력성 (β₁)" data-meaning="LG 가격 1% 인상 시 판매량 변동률 (자체 가격 민감도)" data-tip="절댓값이 클수록 가격 변동에 민감하게 반응함">자체 탄력성 (β₁) <span class="info-icon">ℹ️</span></th>
              <th class="diag-tooltip-th" style="color: var(--accent-amber);" data-name="시장가격 탄력성 (β_mkt)" data-meaning="시장 평균가격 1% 변동 시 시장 총수요 변화율" data-tip="전체 시장이 동반 인상될 때의 총수요 위축 강도">시장가격 탄력성 (β_mkt) <span class="info-icon">ℹ️</span></th>
              <th class="diag-tooltip-th" data-name="경쟁사 교차탄력성 (β_cross)" data-meaning="경쟁사 가격 1% 인상 시 LG 판매량 증가율 (상대가격 방어력)" data-tip="양수 값이 클수록 경쟁사 인상 시 LG로의 반사이익이 큼">경쟁사 교차탄력성 (β_cross) <span class="info-icon">ℹ️</span></th>
              <th class="diag-tooltip-th" data-name="설명력 (R²)" data-meaning="가격 및 시장 요인이 판매량 변화를 설명하는 비율" data-tip="1에 가까울수록 예측력과 모델 적합도가 높음">설명력 (R²) <span class="info-icon">ℹ️</span></th>
              <th class="diag-tooltip-th" data-name="잔차자기상관 (DW)" data-meaning="더빈-왓슨 통계량(2.0에 가까울수록 자기상관 없음)" data-tip="기존 0.5 수준에서 국가/계절 고정효과로 1.0~1.34로 대폭 개선">잔차자기상관 (DW) <span class="info-icon">ℹ️</span></th>
              <th class="diag-tooltip-th" style="color: var(--primary);" data-name="가중 오차율 (Weighted MAPE)" data-meaning="유럽 전체 판매량 가중 절대 오차율" data-tip="소형국 왜곡을 배제한 실제 유럽 비즈니스 실질 예측 정밀도">가중 MAPE <span class="info-icon">ℹ️</span></th>
              <th class="diag-tooltip-th" style="color: var(--accent-teal);" data-name="유럽 총합 오차율 (EU Total MAPE)" data-meaning="유럽 20개국 합산 판매량의 월별 예측 오차율" data-tip="유럽 총괄 영업 의사결정에 직결되는 국가 합산 정밀도">EU 총합 MAPE <span class="info-icon">ℹ️</span></th>
              <th class="left">회귀 분석 결과 / 가격 전략 시사점</th>
            </tr>
          </thead>'''
    content, count_th = re.subn(old_thead_pattern, new_thead, content, count=1)

    # 3. Update renderDiagnosticsTable in JavaScript
    old_diag_pattern = r'(function renderDiagnosticsTable\(\) \{[\s\S]*?tr\.innerHTML = `)([\s\S]*?)(`;\s*\n\s*tbody\.appendChild\(tr\);)'
    new_tr_content = """
          <td class="left"><b>${SEG_LABELS[seg]}</b></td>
          <td style="color: var(--accent-blue); font-weight: 700;">${v.elasticity.toFixed(4)}</td>
          <td style="color: var(--accent-amber); font-weight: 700;">${mktElast.toFixed(4)}</td>
          <td style="color: var(--accent-purple); font-weight: 700;">${(v.cross_elasticity !== undefined ? '+' + v.cross_elasticity.toFixed(4) : (p.ln_comp_asp || 0).toFixed(4))}</td>
          <td style="color: var(--accent-green); font-weight: 700;">${v.r2.toFixed(3)}</td>
          <td>${(v.dw || 0).toFixed(3)}</td>
          <td style="color: var(--primary); font-weight: 700;">${(v.weighted_mape !== undefined ? v.weighted_mape.toFixed(1) + '%' : (v.mape || 0).toFixed(1) + '%')}</td>
          <td style="color: var(--accent-teal); font-weight: 600;">${(v.eu_total_mape !== undefined ? v.eu_total_mape.toFixed(1) + '%' : '-')}</td>
          <td class="left" style="color: var(--text-muted); font-size: 0.74rem;">${SEG_DESCRIPTIONS[seg]}</td>"""
    content, count_diag = re.subn(old_diag_pattern, rf"\g<1>{new_tr_content}\g<3>", content, count=1)

    # 4. Inject EMBEDDED_DATA
    pattern = r"(const EMBEDDED_DATA = )(\{[\s\S]*?\})(;\s*\n\s*let simData = EMBEDDED_DATA;)"
    replacement = rf"\g<1>{json_str}\g<3>"

    new_content, count = re.subn(pattern, replacement, content, count=1)
    if count == 0:
        pattern_fallback = r"(const EMBEDDED_DATA = )([\s\S]*?)(;\s*\n\s*let simData = EMBEDDED_DATA;)"
        new_content, count = re.subn(pattern_fallback, rf"\g<1>{json_str}\g<3>", content, count=1)

    if count > 0:
        with open(INDEX_HTML_PATH, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"[SUCCESS] Successfully updated dashboard template and injected 42M simulation data into {INDEX_HTML_PATH}!")
    else:
        print("Warning: Could not locate 'const EMBEDDED_DATA' block in index.html.")

if __name__ == "__main__":
    update_dashboard()
