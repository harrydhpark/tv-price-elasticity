import os
import json
import pandas as pd
import numpy as np

DATA_DIR = r"d:\TV 유럽영업\15. AX Task\2026 AX 실행과제\12. 가격 탄력성 회귀분석\DATA"
DASHBOARD_DIR = r"d:\TV 유럽영업\15. AX Task\2026 AX 실행과제\12. 가격 탄력성 회귀분석\dashboard"
RESULTS_18M_PATH = os.path.join(DATA_DIR, "processed", "elasticity_results_18m.json")
PANEL_DATA_PATH = os.path.join(DATA_DIR, "processed", "panel_regression_data_18m.csv")
OUT_JSON_PATH = os.path.join(DASHBOARD_DIR, "simulation_data.json")

# Load 18m models
with open(RESULTS_18M_PATH, 'r', encoding='utf-8') as f:
    results_18m = json.load(f)

# Market price elasticity stats
market_price_elasticity = {
    "OLED": {
        "elasticity": -1.627655,
        "p_value": 1.58e-08,
        "bse": 0.287951,
        "r2": 0.964184
    },
    "QNED_MiniLED": {
        "elasticity": -1.845079,
        "p_value": 2.53e-14,
        "bse": 0.242133,
        "r2": 0.959044
    },
    "NanoCell_UHD": {
        "elasticity": -1.260353,
        "p_value": 0.001176,
        "bse": 0.388429,
        "r2": 0.973300
    },
    "FHD": {
        "elasticity": -1.482945,
        "p_value": 0.000646,
        "bse": 0.434698,
        "r2": 0.975157
    }
}

for seg, mkt_stat in market_price_elasticity.items():
    if seg in results_18m['models']:
        results_18m['models'][seg]['market_price_elasticity'] = mkt_stat

ms_elasticity_map = {
    "OLED": -1.8886,
    "QNED_MiniLED": -1.7272,
    "NanoCell_UHD": -2.0360,
    "FHD": -1.2500
}
for seg, ms_el in ms_elasticity_map.items():
    if seg in results_18m['models']:
        results_18m['models'][seg]['ms_elasticity'] = ms_el

# Load panel data and filter 2026 Q1
df = pd.read_csv(PANEL_DATA_PATH)
q1 = df[df['ym'].isin([202601, 202602, 202603])].copy()

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
    "generated_at": "2026-09-07",
    "baseline_period": "2026 Q1",
    "target_sim_period": "2027 Q1",
    "market_scope": "Europe Total (20 countries, excluding Poland & Croatia)",
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
        }
    },
    "market_price_elasticity": market_price_elasticity,
    "models": results_18m['models'],
    "comparison_table": results_18m['comparison'],
    "baseline_summary": baseline_summary,
    "country_baseline": country_baseline
}

with open(OUT_JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(sim_data, f, indent=2, ensure_ascii=False)

print(f"Successfully generated {OUT_JSON_PATH} with 2026 Q1 baseline and market price elasticity!")
