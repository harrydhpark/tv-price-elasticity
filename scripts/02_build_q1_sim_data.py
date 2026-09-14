"""
Build 2026 Q1 Baseline and Simulation Meta-DB for 2027 Q1 Simulator
- Sources:
  1. DATA/processed/elasticity_results_42m.json (42M Panel WLS Regression Models)
  2. DATA/processed/panel_regression_data_42m.csv (42M Panel Dataset for 2026 Q1 Baseline)
- Output: dashboard/simulation_data.json
"""
import os
import json
import pandas as pd
import numpy as np

DATA_DIR = r"d:\TV 유럽영업\15. AX Task\2026 AX 실행과제\12. 가격 탄력성 회귀분석\DATA"
DASHBOARD_DIR = r"d:\TV 유럽영업\15. AX Task\2026 AX 실행과제\12. 가격 탄력성 회귀분석\dashboard"
RESULTS_42M_PATH = os.path.join(DATA_DIR, "processed", "elasticity_results_42m.json")
PANEL_DATA_PATH = os.path.join(DATA_DIR, "processed", "panel_regression_data_42m.csv")
OUT_JSON_PATH = os.path.join(DASHBOARD_DIR, "simulation_data.json")

print("=================================================================", flush=True)
print("  STEP 1: LOADING 42M WLS REGRESSION RESULTS", flush=True)
print("=================================================================", flush=True)

with open(RESULTS_42M_PATH, 'r', encoding='utf-8') as f:
    results_42m = json.load(f)

print(f"Loaded 42M regression results version: {results_42m.get('pipeline_version')}", flush=True)

# Extract market price elasticity from 42m results
market_price_elasticity = {}
for seg, m in results_42m['models'].items():
    if 'market_price_elasticity' in m:
        market_price_elasticity[seg] = m['market_price_elasticity']

# Load panel data and filter 2026 Q1 baseline (Jan, Feb, Mar 2026)
df = pd.read_csv(PANEL_DATA_PATH)
q1 = df[df['ym'].isin([202601, 202602, 202603])].copy()
print(f"Filtered 2026 Q1 Baseline observations: {len(q1)}", flush=True)

# Total Europe baseline
ttl = q1.groupby('segment').agg({
    'lg_units': 'sum',
    'lg_eur': 'sum',
    'market_units': 'sum',
    'market_eur': 'sum'
}).reset_index()

ttl['asp_eur'] = ttl['lg_eur'] / ttl['lg_units']
ttl['market_asp'] = ttl['market_eur'] / ttl['market_units']
ttl['market_share'] = ttl['lg_units'] / ttl['market_units']
ttl['value_ms'] = ttl['lg_eur'] / ttl['market_eur']
ttl['price_premium'] = ttl['asp_eur'] / ttl['market_asp']

baseline_summary = ttl.to_dict(orient='records')

# Country baseline
country_ttl = q1.groupby(['country', 'segment']).agg({
    'lg_units': 'sum',
    'lg_eur': 'sum',
    'market_units': 'sum',
    'market_eur': 'sum'
}).reset_index()

country_ttl['asp_eur'] = country_ttl['lg_eur'] / country_ttl['lg_units']
country_ttl['market_asp'] = country_ttl['market_eur'] / country_ttl['market_units']
country_ttl['market_share'] = country_ttl['lg_units'] / country_ttl['market_units']
country_ttl['value_ms'] = country_ttl['lg_eur'] / country_ttl['market_eur']
country_ttl['price_premium'] = country_ttl['asp_eur'] / country_ttl['market_asp']

country_baseline = country_ttl.to_dict(orient='records')

official_stats_2026q1 = {
    "total_market_units": float(ttl['market_units'].sum()),
    "total_market_eur": float(ttl['market_eur'].sum()),
    "lg_units": float(ttl['lg_units'].sum()),
    "lg_eur": float(ttl['lg_eur'].sum()),
    "lg_volume_ms": float(ttl['lg_units'].sum() / ttl['market_units'].sum() * 100),
    "lg_value_ms": float(ttl['lg_eur'].sum() / ttl['market_eur'].sum() * 100)
}

sim_data = {
    "generated_at": "2026-09-14",
    "pipeline_version": "2.0_42m_wls",
    "regression_period": "2023.01 ~ 2026.06 (42M Panel WLS)",
    "baseline_period": "2026 Q1",
    "target_sim_period": "2027 Q1",
    "market_scope": f"Europe Total ({df['country'].nunique()} countries, excluding Poland & Croatia)",
    "official_stats_2026q1": official_stats_2026q1,
    "competitor_cases": {
        "case1": {
            "name": "Case 1 (100% 동등 인상)",
            "oled_follow_rate": 1.0,
            "non_oled_follow_rate": 1.0,
            "description": "OLED 100% 동등 인상, 기타 제품군 100% 동등 인상"
        },
        "case2": {
            "name": "Case 2 (75% 수준 인상)",
            "oled_follow_rate": 1.0,
            "non_oled_follow_rate": 0.75,
            "description": "OLED 100% 동등 인상, 기타 제품군 75% 수준 인상"
        },
        "case3": {
            "name": "Case 3 (50% 수준 인상)",
            "oled_follow_rate": 1.0,
            "non_oled_follow_rate": 0.50,
            "description": "OLED 100% 동등 인상, 기타 제품군 50% 수준 인상"
        },
        "case4": {
            "name": "Case 4 (전 제품 경쟁사 동결 / 단독 인상)",
            "oled_follow_rate": 0.0,
            "non_oled_follow_rate": 0.0,
            "description": "전 제품군(OLED 포함) 경쟁사 가격 동결 (0% 추종, 단독 인상)"
        }
    },
    "market_price_elasticity": market_price_elasticity,
    "models": results_42m['models'],
    "comparison_table": results_42m['comparison'],
    "baseline_summary": baseline_summary,
    "country_baseline": country_baseline
}

with open(OUT_JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(sim_data, f, indent=2, ensure_ascii=False)

print(f"[SUCCESS] Successfully generated simulation dataset: {OUT_JSON_PATH}", flush=True)
print(f"2026 Q1 Europe Baseline: LG Units = {official_stats_2026q1['lg_units']:,.0f}, Volume M/S = {official_stats_2026q1['lg_volume_ms']:.1f}%", flush=True)
