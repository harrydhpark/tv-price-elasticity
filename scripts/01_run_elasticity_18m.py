"""
18-Month (2025.01 ~ 2026.06) Price Elasticity Panel Regression Pipeline
- Scope: Europe Total (Excluding Poland and Croatia)
- Source: Global) GfK+NPD Monthly Raw_202501_202606 (26년 구독)_260810.xlsb
- Segmentation:
  1. OLED
  2. QNED_MiniLED (QNED, MiniLED, NanoCell combined)
  3. NanoCell_UHD (Standard Non-NanoCell 4K UHD LCD)
  4. FHD (Pure FHD / HD)
- Model: Multivariate Log-Log OLS
  ln(LG_Units) = const + b1*ln(LG_ASP) + b2*ln(Price_Premium) + b3*ln(Market_Size) + b4*TimeTrend + b5*IsQ4
"""
import os
import sys
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.stattools import durbin_watson
from pyxlsb import open_workbook

DATA_DIR = r"d:\TV 유럽영업\15. AX Task\2026 AX 실행과제\12. 가격 탄력성 회귀분석\DATA"
OUT_DIR  = os.path.join(DATA_DIR, "processed")
DASHBOARD_DIR = r"d:\TV 유럽영업\15. AX Task\2026 AX 실행과제\12. 가격 탄력성 회귀분석\dashboard"
os.makedirs(OUT_DIR, exist_ok=True)

RAW_FILE = os.path.join(DATA_DIR, "Global) GfK+NPD Monthly Raw_202501_202606 (26년 구독)_260810.xlsb")

# Precise European Countries in Raw Data (Excluding Poland & Croatia)
EUROPE_COUNTRIES = {
    'Germany', 'UK', 'France', 'Italy', 'Spain',
    'Austria', 'Netherlands', 'Belgium', 'Portugal', 'Greece',
    'Sweden', 'Denmark', 'Finland', 'Norway', 'Switzerland',
    'Czechia', 'Czech', 'Slovakia', 'Hungary', 'Romania', 'Serbia'
}

EXCLUDED_COUNTRIES = {'POLAND', 'CROATIA'}

def classify_segment(tech_sub, display_tech, miniled_val, wcg_val, model_val):
    ts = (str(tech_sub) if tech_sub is not None else '').strip().upper()
    dt = (str(display_tech) if display_tech is not None else '').strip().upper()
    ml = (str(miniled_val) if miniled_val is not None else '').strip().upper()
    wc = (str(wcg_val) if wcg_val is not None else '').strip().upper()
    md = (str(model_val) if model_val is not None else '').strip().upper()
    
    # 1. OLED
    if 'OLED' in ts or 'OLED' in dt:
        return 'OLED'
    
    # 2. QNED / NanoCell / MiniLED (User confirmed: NanoCell bundled into QNED/MiniLED)
    is_nano = ('NANO' in md) or ('NANOCELL' in wc) or ('NANO' in wc) or ('NANO' in ts)
    is_qned_miniled = ('MINILED' in ml and 'NO' not in ml) or ('QUANTUM' in wc) or ('QD' in wc) or ('QNED' in ts) or ('MINI' in ts)
    
    if is_nano or is_qned_miniled:
        return 'QNED_MiniLED'
        
    # 3. Standard UHD 4K (Non-NanoCell standard 4K)
    if 'UHD' in ts or '4K' in ts:
        return 'NanoCell_UHD'
        
    # 4. FHD / HD
    if 'FHD' in ts or '1080' in ts or ('HD' in ts and 'UHD' not in ts):
        return 'FHD'
        
    if 'LCD' in dt:
        return 'NanoCell_UHD'
        
    return 'Other'

def normalize_brand(brand):
    if brand is None:
        return 'Other'
    b = str(brand).strip().upper()
    if b == 'LG' or b.startswith('01. LG') or 'LG ' in b:
        return 'LG'
    if 'SAMSUNG' in b:
        return 'Samsung'
    if 'SONY' in b:
        return 'Sony'
    if 'TCL' in b:
        return 'TCL'
    if 'HISENSE' in b:
        return 'Hisense'
    return 'Other'

print("=== STEP 1: FAST EXTRACTING 18-MONTH EUROPE DATA ===", flush=True)
print(f"Source file: {RAW_FILE}", flush=True)
print(f"Target European Countries ({len(EUROPE_COUNTRIES)}): {sorted(EUROPE_COUNTRIES)}", flush=True)
print(f"Explicitly Excluded Countries: {EXCLUDED_COUNTRIES}", flush=True)

all_records = []
countries_matched = set()
count = 0
matched = 0

with open_workbook(RAW_FILE) as wb:
    sheet_name = 'Raw'
    for s in wb.sheets:
        if s.lower() == 'raw':
            sheet_name = s
            break
    
    with wb.get_sheet(sheet_name) as sheet:
        # Col indices:
        # 0: Display Technol, 1: 제품구분, 2: Country, 4: 지역, 5: 권역
        # 16: Brand - AD hoc, 20: Model, 29: MiniLed BackLit, 35: Month, 36: WCG
        # 39: Sales Units, 42: Sales EUR
        for row in sheet.rows():
            count += 1
            if count % 150000 == 0:
                print(f"  Rows scanned: {count:,}, Europe matched: {matched:,}", flush=True)
                
            if count <= 2:  # Row 0 blank, Row 1 header
                continue
            if len(row) <= 42:
                continue
            
            # FAST EARLY FILTER: check Country first!
            cntry_raw = row[2].v
            if not cntry_raw:
                continue
            cntry = str(cntry_raw).strip()
            
            if cntry not in EUROPE_COUNTRIES:
                continue
                
            # Month check
            mo_v = row[35].v
            if not mo_v:
                continue
            try:
                ym = int(float(mo_v))
            except (ValueError, TypeError):
                continue
                
            if not (202501 <= ym <= 202606):
                continue
                
            un_v = row[39].v
            eu_v = row[42].v
            if un_v is None or eu_v is None:
                continue
            try:
                units = float(un_v)
                eur = float(eu_v)
            except (ValueError, TypeError):
                continue
                
            if units <= 0 or eur <= 0:
                continue
                
            yr = ym // 100
            m = ym % 100
            
            tech_v = row[0].v
            sub_v = row[1].v
            brd_v = row[16].v
            md_v = row[20].v
            ml_v = row[29].v
            wc_v = row[36].v
            
            seg = classify_segment(sub_v, tech_v, ml_v, wc_v, md_v)
            if seg in ('Other',):
                continue
                
            norm_brd = normalize_brand(brd_v)
            all_records.append((cntry, seg, norm_brd, yr, m, ym, units, eur))
            countries_matched.add(cntry)
            matched += 1

print(f"\nExtraction complete! Total scanned: {count:,}, Total matched: {matched:,}", flush=True)
print(f"Countries Extracted ({len(countries_matched)}): {sorted(countries_matched)}", flush=True)

df_raw = pd.DataFrame(all_records, columns=[
    'country', 'segment', 'brand', 'year', 'month', 'ym', 'units', 'eur'
])

print("\n=== STEP 2: AGGREGATING MARKET & LG METRICS ===", flush=True)
# Group total market
market_agg = df_raw.groupby(['country', 'segment', 'year', 'month', 'ym'], as_index=False).agg(
    market_units=('units', 'sum'),
    market_eur=('eur', 'sum')
)
market_agg['market_asp'] = market_agg['market_eur'] / market_agg['market_units']

# Group brand level
brand_agg = df_raw.groupby(['country', 'segment', 'brand', 'year', 'month', 'ym'], as_index=False).agg(
    brand_units=('units', 'sum'),
    brand_eur=('eur', 'sum')
)
brand_agg['brand_asp'] = brand_agg['brand_eur'] / brand_agg['brand_units']

# Extract LG
lg_data = brand_agg[brand_agg['brand'] == 'LG'].copy().rename(columns={
    'brand_units': 'lg_units',
    'brand_eur': 'lg_eur',
    'brand_asp': 'lg_asp'
})

# Merge
merged = pd.merge(
    market_agg,
    lg_data[['country', 'segment', 'year', 'month', 'ym', 'lg_units', 'lg_eur', 'lg_asp']],
    on=['country', 'segment', 'year', 'month', 'ym'],
    how='inner'
)

# Derived variables
merged['market_share'] = merged['lg_units'] / merged['market_units']
merged['price_premium_ratio'] = merged['lg_asp'] / merged['market_asp']
# 2025.01 = 1, ..., 2026.06 = 18
merged['time_trend'] = (merged['year'] - 2025) * 12 + merged['month']
merged['is_q4'] = merged['month'].isin([10, 11, 12]).astype(int)

# Log transforms
merged['ln_lg_units'] = np.log(merged['lg_units'])
merged['ln_lg_eur'] = np.log(merged['lg_eur'])
merged['ln_lg_asp'] = np.log(merged['lg_asp'])
merged['ln_market_share'] = np.log(merged['market_share'])
merged['ln_market_size'] = np.log(merged['market_units'])
merged['ln_price_premium'] = np.log(merged['price_premium_ratio'])

csv_path = os.path.join(OUT_DIR, "panel_regression_data_18m.csv")
merged.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f"Saved panel regression dataset: {csv_path} ({len(merged)} country-month-segment observations)", flush=True)

# Historical baseline (2023~2025 3-year model) for comparison:
HISTORICAL_RESULTS = {
    "OLED": {"elasticity": -0.4130, "p_value": 0.0092, "r2": 0.9566, "ms_elasticity": -1.2666},
    "QNED_MiniLED": {"elasticity": -2.3572, "p_value": 0.0000, "r2": 0.6413, "ms_elasticity": -0.0981},
    "NanoCell_UHD": {"elasticity": -2.3473, "p_value": 0.0000, "r2": 0.4421, "ms_elasticity": -1.3849},
    "FHD": {"elasticity": -3.7891, "p_value": 0.0000, "r2": 0.6262, "ms_elasticity": -4.3775}
}

print("\n=== STEP 3: OLS PANEL REGRESSION MODELING (18M) ===", flush=True)
TARGET_SEGMENTS = ['OLED', 'QNED_MiniLED', 'NanoCell_UHD', 'FHD']
results_18m = {}

for seg in TARGET_SEGMENTS:
    df_seg = merged[merged['segment'] == seg].copy()
    n_obs = len(df_seg)
    print(f"\n=======================================================", flush=True)
    print(f"Segment: {seg} (Observations: {n_obs})", flush=True)
    print(f"=======================================================", flush=True)
    
    if n_obs < 15:
        print(f"  Warning: Insufficient observations for {seg}", flush=True)
        continue
        
    # 1. Volume Model: ln(LG_Units) = const + b1*ln(LG_ASP) + b2*ln(Price_Premium) + b3*ln(Market_Size) + b4*TimeTrend + b5*IsQ4
    X_cols_vol = ['ln_lg_asp', 'ln_price_premium', 'ln_market_size', 'time_trend', 'is_q4']
    X_vol = sm.add_constant(df_seg[X_cols_vol])
    y_vol = df_seg['ln_lg_units']
    model_vol = sm.OLS(y_vol, X_vol).fit()
    
    # Predictions & MAPE
    y_pred_vol = np.exp(model_vol.predict(X_vol))
    y_true_vol = df_seg['lg_units']
    mape_vol = float(np.mean(np.abs((y_true_vol - y_pred_vol) / y_true_vol)) * 100)
    
    # 2. Value Model: ln(LG_EUR)
    X_val = sm.add_constant(df_seg[X_cols_vol])
    y_val = df_seg['ln_lg_eur']
    model_val = sm.OLS(y_val, X_val).fit()
    y_pred_val = np.exp(model_val.predict(X_val))
    y_true_val = df_seg['lg_eur']
    mape_val = float(np.mean(np.abs((y_true_val - y_pred_val) / y_true_val)) * 100)
    
    # 3. Market Share Model: ln(Market_Share) = const + g1*ln(Price_Premium) + g2*TimeTrend + g3*IsQ4
    X_cols_ms = ['ln_price_premium', 'time_trend', 'is_q4']
    X_ms = sm.add_constant(df_seg[X_cols_ms])
    y_ms = df_seg['ln_market_share']
    model_ms = sm.OLS(y_ms, X_ms).fit()
    y_pred_ms = np.exp(model_ms.predict(X_ms))
    y_true_ms = df_seg['market_share']
    mape_ms = float(np.mean(np.abs((y_true_ms - y_pred_ms) / y_true_ms)) * 100)
    
    # Coefficients & stats
    vol_elasticity = float(model_vol.params.get('ln_lg_asp', -1.0))
    vol_pvalue = float(model_vol.pvalues.get('ln_lg_asp', 0.05))
    ms_elasticity = float(model_ms.params.get('ln_price_premium', -1.0))
    ms_pvalue = float(model_ms.pvalues.get('ln_price_premium', 0.05))
    
    print(model_vol.summary())
    
    results_18m[seg] = {
        "n_obs": n_obs,
        "volume": {
            "elasticity": vol_elasticity,
            "p_value": vol_pvalue,
            "r2": float(model_vol.rsquared),
            "r2_adj": float(model_vol.rsquared_adj),
            "mape": mape_vol,
            "dw": float(durbin_watson(model_vol.resid)),
            "params": {k: float(v) for k, v in model_vol.params.items()},
            "pvalues": {k: float(v) for k, v in model_vol.pvalues.items()}
        },
        "value": {
            "r2": float(model_val.rsquared),
            "r2_adj": float(model_val.rsquared_adj),
            "mape": mape_val,
            "dw": float(durbin_watson(model_val.resid)),
            "params": {k: float(v) for k, v in model_val.params.items()}
        },
        "market_share": {
            "elasticity": ms_elasticity,
            "p_value": ms_pvalue,
            "r2": float(model_ms.rsquared),
            "r2_adj": float(model_ms.rsquared_adj),
            "mape": mape_ms,
            "dw": float(durbin_watson(model_ms.resid)),
            "params": {k: float(v) for k, v in model_ms.params.items()}
        }
    }

# Comparison Table
print("\n" + "="*85, flush=True)
print("             자체 가격 탄력성 (Own-Price Elasticity β) 비교 분석표", flush=True)
print("="*85, flush=True)
print(f"{'제품군 (Segment)':<18} | {'과거 23~25년 β':<14} | {'신규 18개월 β':<14} | {'변동치 (Δ)':<12} | {'p-value':<10} | {'R²':<8}")
print("-" * 85, flush=True)

comparison_records = []
for seg in TARGET_SEGMENTS:
    old_b = HISTORICAL_RESULTS[seg]['elasticity']
    new_b = results_18m[seg]['volume']['elasticity']
    delta = new_b - old_b
    pval = results_18m[seg]['volume']['p_value']
    r2 = results_18m[seg]['volume']['r2']
    print(f"{seg:<18} | {old_b:>12.4f}   | {new_b:>12.4f}   | {delta:>+10.4f}   | {pval:>8.4f}   | {r2:>6.3f}")
    comparison_records.append({
        "segment": seg,
        "historical_elasticity": old_b,
        "new_18m_elasticity": new_b,
        "delta": delta,
        "p_value": pval,
        "r2": r2,
        "mape": results_18m[seg]['volume']['mape']
    })
print("="*85, flush=True)

# Export comparison and model json
export_path = os.path.join(OUT_DIR, "elasticity_results_18m.json")
with open(export_path, 'w', encoding='utf-8') as f:
    json.dump({
        "period": "2025.01 ~ 2026.06 (18M)",
        "scope": f"Europe Total ({len(countries_matched)} countries, excluding Poland & Croatia)",
        "countries": sorted(countries_matched),
        "excluded_countries": list(EXCLUDED_COUNTRIES),
        "comparison": comparison_records,
        "models": results_18m
    }, f, indent=2, ensure_ascii=False)

print(f"\nSaved regression analysis JSON: {export_path}", flush=True)
print("Pipeline finished successfully!", flush=True)
