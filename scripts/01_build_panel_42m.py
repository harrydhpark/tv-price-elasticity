"""
42-Month (2023.01 ~ 2026.06) Price Elasticity Panel Data Extraction Pipeline
- Scope: Europe Total (20 countries, strictly excluding Poland and Croatia)
- Sources:
  1. Global) GfK+NPD Monthly Raw_2023년.xlsb (2023.01 ~ 2023.12)
  2. Global) GfK+NPD Monthly Raw_2024-202507 (25년 구독)_250910_SL수정 1.xlsb (2024.01 ~ 2024.12)
  3. Global) GfK+NPD Monthly Raw_202501_202606 (26년 구독)_260810.xlsb (2025.01 ~ 2026.06)
- Output: DATA/processed/panel_regression_data_42m.csv
"""
import os
import sys
import numpy as np
import pandas as pd
from pyxlsb import open_workbook

DATA_DIR = r"d:\TV 유럽영업\15. AX Task\2026 AX 실행과제\12. 가격 탄력성 회귀분석\DATA"
OUT_DIR  = os.path.join(DATA_DIR, "processed")
os.makedirs(OUT_DIR, exist_ok=True)

EUROPE_COUNTRIES = {
    'Germany', 'UK', 'France', 'Italy', 'Spain',
    'Austria', 'Netherlands', 'Belgium', 'Portugal', 'Greece',
    'Sweden', 'Denmark', 'Finland', 'Norway', 'Switzerland',
    'Czechia', 'Czech', 'Slovakia', 'Hungary', 'Romania', 'Serbia'
}

EXCLUDED_COUNTRIES = {'POLAND', 'CROATIA'}

RAW_SPECS = [
    {
        "file": os.path.join(DATA_DIR, "Global) GfK+NPD Monthly Raw_2023년.xlsb"),
        "min_ym": 202301,
        "max_ym": 202312,
        "label": "2023 Full Year"
    },
    {
        "file": os.path.join(DATA_DIR, "Global) GfK+NPD Monthly Raw_2024-202507 (25년 구독)_250910_SL수정 1.xlsb"),
        "min_ym": 202401,
        "max_ym": 202412,
        "label": "2024 Full Year"
    },
    {
        "file": os.path.join(DATA_DIR, "Global) GfK+NPD Monthly Raw_202501_202606 (26년 구독)_260810.xlsb"),
        "min_ym": 202501,
        "max_ym": 202606,
        "label": "2025.01 ~ 2026.06 (18M)"
    }
]

def classify_segment(tech_sub, display_tech, miniled_val, wcg_val, model_val):
    ts = (str(tech_sub) if tech_sub is not None else '').strip().upper()
    dt = (str(display_tech) if display_tech is not None else '').strip().upper()
    ml = (str(miniled_val) if miniled_val is not None else '').strip().upper()
    wc = (str(wcg_val) if wcg_val is not None else '').strip().upper()
    md = (str(model_val) if model_val is not None else '').strip().upper()
    
    # 1. OLED
    if 'OLED' in ts or 'OLED' in dt:
        return 'OLED'
    
    # 2. QNED / NanoCell / MiniLED
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

def find_col_indices(sheet):
    col_map = {}
    r_idx = 0
    for r in sheet.rows():
        r_idx += 1
        vals = [str(c.v).strip() if c.v is not None else '' for c in r]
        if 'Country' in vals and any('Sales Units' in v for v in vals):
            for idx, v in enumerate(vals):
                if v == 'Country': col_map['country'] = idx
                elif v == 'Display Technol': col_map['display_tech'] = idx
                elif v == '제품구분': col_map['tech_sub'] = idx  # Exact match for Col 1
                elif v == 'Brand - AD hoc': col_map['brand'] = idx
                elif v == 'Model': col_map['model'] = idx
                elif ('MiniLed BackLit' in v or 'MiniLed' in v) and 'miniled' not in col_map:
                    col_map['miniled'] = idx
                elif v == 'Month': col_map['month'] = idx
                elif v == 'WCG': col_map['wcg'] = idx
                elif v == 'Sales Units': col_map['units'] = idx
                elif v == 'Sales EUR': col_map['eur'] = idx
            return r_idx, col_map
    return None, None

all_records = []
countries_seen = set()

print("=================================================================", flush=True)
print("  STEP 1: EXTRACTING 42-MONTH EUROPE TV PANEL DATA (2023.01 ~ 2026.06)", flush=True)
print("=================================================================", flush=True)

for spec in RAW_SPECS:
    fpath = spec['file']
    min_ym = spec['min_ym']
    max_ym = spec['max_ym']
    label  = spec['label']
    print(f"\nProcessing {label}: {os.path.basename(fpath)} (Target YM: {min_ym} ~ {max_ym})", flush=True)
    
    with open_workbook(fpath) as wb:
        sname = 'Raw'
        for s in wb.sheets:
            if s.lower() == 'raw':
                sname = s
                break
        
        with wb.get_sheet(sname) as sheet:
            hdr_row, col_map = find_col_indices(sheet)
            print(f"  Header identified at row {hdr_row}. Column map:")
            for k, v in sorted(col_map.items()):
                print(f"    - {k:<13}: Col {v}")
            
            c_country = col_map['country']
            c_tech = col_map.get('display_tech', 0)
            c_sub = col_map.get('tech_sub', 1)
            c_brand = col_map['brand']
            c_model = col_map['model']
            c_miniled = col_map['miniled']
            c_month = col_map['month']
            c_wcg = col_map['wcg']
            c_units = col_map['units']
            c_eur = col_map['eur']
            max_c = max(col_map.values())
            
            count = 0
            file_matched = 0
            for row in sheet.rows():
                count += 1
                if count <= hdr_row:
                    continue
                if len(row) <= max_c:
                    continue
                
                # Fast early country check
                c_val = row[c_country].v
                if not c_val:
                    continue
                cntry = str(c_val).strip()
                if cntry not in EUROPE_COUNTRIES:
                    continue
                if cntry == 'Czech':
                    cntry = 'Czechia'
                
                # Fast month check
                m_val = row[c_month].v
                if not m_val:
                    continue
                try:
                    ym = int(float(m_val))
                except (ValueError, TypeError):
                    continue
                    
                if not (min_ym <= ym <= max_ym):
                    continue
                    
                u_val = row[c_units].v
                e_val = row[c_eur].v
                if u_val is None or e_val is None:
                    continue
                try:
                    units = float(u_val)
                    eur = float(e_val)
                except (ValueError, TypeError):
                    continue
                    
                if units <= 0 or eur <= 0:
                    continue
                    
                yr = ym // 100
                m  = ym % 100
                
                tech_v = row[c_tech].v
                sub_v  = row[c_sub].v
                brd_v  = row[c_brand].v
                md_v   = row[c_model].v
                ml_v   = row[c_miniled].v
                wc_v   = row[c_wcg].v
                
                seg = classify_segment(sub_v, tech_v, ml_v, wc_v, md_v)
                if seg in ('Other',):
                    continue
                    
                norm_brd = normalize_brand(brd_v)
                all_records.append((cntry, seg, norm_brd, yr, m, ym, units, eur))
                countries_seen.add(cntry)
                file_matched += 1
                
                if count % 300000 == 0:
                    print(f"    Rows scanned: {count:,}, Matched: {file_matched:,}", flush=True)
                    
            print(f"  --> File matched records: {file_matched:,} (Total scanned: {count:,})", flush=True)

print(f"\nExtraction complete! Total records across all 3 periods: {len(all_records):,}", flush=True)
print(f"Matched European Countries ({len(countries_seen)}): {sorted(countries_seen)}", flush=True)

df_raw = pd.DataFrame(all_records, columns=[
    'country', 'segment', 'brand', 'year', 'month', 'ym', 'units', 'eur'
])

print("\n=================================================================", flush=True)
print("  STEP 2: AGGREGATING PANEL METRICS & COMPETITOR SEPARATION", flush=True)
print("=================================================================", flush=True)

# 1. Total TV Market by (country, year, month, ym) across all segments
tv_total_agg = df_raw.groupby(['country', 'year', 'month', 'ym'], as_index=False).agg(
    total_tv_units=('units', 'sum'),
    total_tv_eur=('eur', 'sum')
)

# 2. Segment Total Market
market_agg = df_raw.groupby(['country', 'segment', 'year', 'month', 'ym'], as_index=False).agg(
    market_units=('units', 'sum'),
    market_eur=('eur', 'sum')
)
market_agg['market_asp'] = market_agg['market_eur'] / market_agg['market_units']

# 3. LG Aggregation
lg_agg = df_raw[df_raw['brand'] == 'LG'].groupby(['country', 'segment', 'year', 'month', 'ym'], as_index=False).agg(
    lg_units=('units', 'sum'),
    lg_eur=('eur', 'sum')
)
lg_agg['lg_asp'] = lg_agg['lg_eur'] / lg_agg['lg_units']

# Merge Market & LG
merged = pd.merge(market_agg, lg_agg, on=['country', 'segment', 'year', 'month', 'ym'], how='inner')

# Merge Total TV Demand (for macro control)
merged = pd.merge(merged, tv_total_agg, on=['country', 'year', 'month', 'ym'], how='left')

# 4. Competitor Metrics (Market minus LG)
merged['comp_units'] = merged['market_units'] - merged['lg_units']
merged['comp_eur']   = merged['market_eur'] - merged['lg_eur']
# Safety check: if comp_units <= 0 (e.g., 100% LG share), fallback to market_asp
merged['comp_asp']   = np.where(merged['comp_units'] > 0, merged['comp_eur'] / merged['comp_units'], merged['market_asp'])

# Derived ratios
merged['market_share'] = merged['lg_units'] / merged['market_units']
merged['price_premium_ratio'] = merged['lg_asp'] / merged['comp_asp']
merged['price_to_market_ratio'] = merged['lg_asp'] / merged['market_asp']

# Time Trend (2023.01 = 1, ..., 2026.06 = 42)
merged['time_trend'] = (merged['year'] - 2023) * 12 + merged['month']
merged['is_q4'] = merged['month'].isin([10, 11, 12]).astype(int)

# Time weight (WLS weights: 2025.01~2026.06 = 1.0, 2024 = 0.8, 2023 = 0.6)
def assign_wls_weight(ym):
    if ym >= 202501:
        return 1.0
    elif ym >= 202401:
        return 0.8
    else:
        return 0.6

merged['wls_weight'] = merged['ym'].apply(assign_wls_weight)

# Log transforms
merged['ln_lg_units'] = np.log(merged['lg_units'])
merged['ln_lg_eur'] = np.log(merged['lg_eur'])
merged['ln_lg_asp'] = np.log(merged['lg_asp'])
merged['ln_comp_asp'] = np.log(merged['comp_asp'])
merged['ln_market_asp'] = np.log(merged['market_asp'])
merged['ln_market_size'] = np.log(merged['market_units'])
merged['ln_total_tv_units'] = np.log(merged['total_tv_units'])
merged['ln_price_premium'] = np.log(merged['price_premium_ratio'])
merged['ln_market_share'] = np.log(merged['market_share'])

csv_path = os.path.join(OUT_DIR, "panel_regression_data_42m.csv")
merged.to_csv(csv_path, index=False, encoding='utf-8-sig')

print(f"\n[SUCCESS] Saved 42-Month Panel Regression Dataset: {csv_path}", flush=True)
print(f"Total Rows: {len(merged):,} country-month-segment observations", flush=True)
print(f"Years: {sorted(merged['year'].unique())}", flush=True)
print(f"Months Span: {merged['ym'].min()} ~ {merged['ym'].max()} (42 Months)", flush=True)
print(f"Segments Count:\n{merged['segment'].value_counts()}", flush=True)
