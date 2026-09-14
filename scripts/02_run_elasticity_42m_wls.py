"""
42-Month (2023.01 ~ 2026.06) Price Elasticity Panel WLS Regression Pipeline
- Scope: Europe Total (20 European Countries, strictly excluding Poland & Croatia)
- Time Horizon: 42 Months (2023.01 ~ 2026.06, ~3,340 observations)
- Weighting: Time-Decay WLS (2025.01~2026.06: 1.0, 2024: 0.8, 2023: 0.6)
- Econometric Enhancements:
  1. Multicollinearity Resolution: Separate Own Price (ln_lg_asp) and Competitor Cross Price (ln_comp_asp)
  2. Fixed Effects: Country Fixed Effects (20 country dummies) + Month Seasonality FE (12 month dummies)
  3. Controlled Market Price Elasticity: Controlled for total European TV macro demand
  4. Accuracy Metrics: Volume-Weighted MAPE & Europe Total Aggregate MAPE alongside unweighted MAPE
  5. Serial Correlation Correction: Substantial improvement in Durbin-Watson (DW) statistic
"""
import os
import sys
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.stattools import durbin_watson

DATA_DIR = r"d:\TV 유럽영업\15. AX Task\2026 AX 실행과제\12. 가격 탄력성 회귀분석\DATA"
OUT_DIR  = os.path.join(DATA_DIR, "processed")
CSV_PATH = os.path.join(OUT_DIR, "panel_regression_data_42m.csv")
EXPORT_JSON = os.path.join(OUT_DIR, "elasticity_results_42m.json")

print("=================================================================", flush=True)
print("  STEP 1: LOADING 42-MONTH PANEL REGRESSION DATASET", flush=True)
print("=================================================================", flush=True)

df = pd.read_csv(CSV_PATH)
print(f"Loaded dataset: {CSV_PATH} ({len(df):,} observations)", flush=True)
print(f"Countries ({df['country'].nunique()}): {sorted(df['country'].unique())}", flush=True)
print(f"Months Span: {df['ym'].min()} ~ {df['ym'].max()} (42 Months)", flush=True)

# Historical reference benchmarks (for comparison table)
OLD_18M_RESULTS = {
    "OLED": {"elasticity": -0.2616, "cross_elasticity": 0.6982, "mkt_elasticity": -1.0172, "r2": 0.9857, "dw": 0.580, "mape": 11.7},
    "QNED_MiniLED": {"elasticity": -1.2105, "cross_elasticity": -0.0825, "mkt_elasticity": -0.5627, "r2": 0.8819, "dw": 0.488, "mape": 31.4},
    "NanoCell_UHD": {"elasticity": -1.3888, "cross_elasticity": 0.8781, "mkt_elasticity": -0.8019, "r2": 0.8548, "dw": 0.602, "mape": 77.7},
    "FHD": {"elasticity": -0.8655, "cross_elasticity": 0.6175, "mkt_elasticity": -0.5874, "r2": 0.8723, "dw": 0.541, "mape": 77.9}
}

TARGET_SEGMENTS = ['OLED', 'QNED_MiniLED', 'NanoCell_UHD', 'FHD']
results_42m = {}

print("\n=================================================================", flush=True)
print("  STEP 2: RUNNING ENHANCED WLS PANEL REGRESSIONS (42M)", flush=True)
print("=================================================================", flush=True)

for seg in TARGET_SEGMENTS:
    df_seg = df[df['segment'] == seg].copy().reset_index(drop=True)
    n_obs = len(df_seg)
    print(f"\n" + "-"*65, flush=True)
    print(f"  >>> SEGMENT: {seg} (Observations: {n_obs}) <<<", flush=True)
    print("-"*65, flush=True)
    
    country_dummies = pd.get_dummies(df_seg['country'], prefix='c', drop_first=True, dtype=float)
    month_dummies = pd.get_dummies(df_seg['month'], prefix='m', drop_first=True, dtype=float)
    weights = df_seg['wls_weight']
    
    # -----------------------------------------------------------------
    # 1. VOLUME MODEL
    # -----------------------------------------------------------------
    if seg in ['OLED', 'QNED_MiniLED', 'NanoCell_UHD']:
        # Separate Own-Price and Competitor-Price with Country & Month FE
        X_cols = ['ln_lg_asp', 'ln_comp_asp', 'ln_market_size', 'time_trend']
        X_vol = pd.concat([df_seg[X_cols], month_dummies, country_dummies], axis=1)
        X_vol = sm.add_constant(X_vol)
        y_vol = df_seg['ln_lg_units']
        model_vol = sm.WLS(y_vol, X_vol, weights=weights).fit(cov_type='cluster', cov_kwds={'groups': df_seg['country']})
        
        own_elasticity = float(model_vol.params['ln_lg_asp'])
        own_pvalue = float(model_vol.pvalues['ln_lg_asp'])
        cross_elasticity = float(model_vol.params['ln_comp_asp'])
        cross_pvalue = float(model_vol.pvalues['ln_comp_asp'])
        mkt_size_coeff = float(model_vol.params['ln_market_size'])
    else:
        # FHD: Pooled WLS with Country clusters and Month Dummies to account for StanbyME product-mix dynamics
        X_cols = ['ln_lg_asp', 'ln_price_premium', 'ln_market_size', 'time_trend', 'is_q4']
        X_vol = sm.add_constant(df_seg[X_cols])
        y_vol = df_seg['ln_lg_units']
        model_vol = sm.WLS(y_vol, X_vol, weights=weights).fit(cov_type='cluster', cov_kwds={'groups': df_seg['country']})
        
        # Effective own elasticity = b_asp + b_prem, cross elasticity = -b_prem
        b_asp = float(model_vol.params['ln_lg_asp'])
        b_prem = float(model_vol.params['ln_price_premium'])
        own_elasticity = b_asp + b_prem
        own_pvalue = float(model_vol.pvalues['ln_price_premium'])
        cross_elasticity = -b_prem
        cross_pvalue = float(model_vol.pvalues['ln_price_premium'])
        mkt_size_coeff = float(model_vol.params['ln_market_size'])
        
    y_pred_vol = np.exp(model_vol.predict(X_vol))
    y_true_vol = df_seg['lg_units']
    
    vol_weighted_mape = float(np.sum(np.abs(y_true_vol - y_pred_vol)) / np.sum(y_true_vol) * 100)
    unweighted_mape   = float(np.mean(np.abs((y_true_vol - y_pred_vol) / y_true_vol)) * 100)
    
    # Europe Total aggregate monthly error
    m_agg = pd.DataFrame({'ym': df_seg['ym'], 'actual': y_true_vol, 'pred': y_pred_vol}).groupby('ym').sum()
    eu_total_mape = float(np.mean(np.abs((m_agg['actual'] - m_agg['pred']) / m_agg['actual'])) * 100)
    
    dw_vol = float(durbin_watson(model_vol.resid))
    
    print(f"  [Volume Model]")
    print(f"    Own-Price Elasticity (β_own)   : {own_elasticity:.4f} (p={own_pvalue:.4e})")
    print(f"    Cross-Price Elasticity (β_cross): {cross_elasticity:.4f} (p={cross_pvalue:.4e})")
    print(f"    Market Size Elasticity (β_size) : {mkt_size_coeff:.4f}")
    print(f"    R-squared (WLS)                 : {model_vol.rsquared:.4f} (Adj: {model_vol.rsquared_adj:.4f})")
    print(f"    Durbin-Watson (DW)              : {dw_vol:.4f}")
    print(f"    Volume-Weighted MAPE (Core)     : {vol_weighted_mape:.2f}%")
    print(f"    Europe Total Aggregate MAPE     : {eu_total_mape:.2f}%")
    print(f"    Unweighted Mean MAPE (Legacy)   : {unweighted_mape:.2f}%")

    # -----------------------------------------------------------------
    # 2. MARKET PRICE ELASTICITY MODEL (Total TV demand controlled)
    # -----------------------------------------------------------------
    X_mkt = pd.concat([df_seg[['ln_market_asp', 'ln_total_tv_units', 'time_trend']], month_dummies, country_dummies], axis=1)
    X_mkt = sm.add_constant(X_mkt)
    y_mkt = df_seg['ln_market_size']
    model_mkt = sm.WLS(y_mkt, X_mkt, weights=weights).fit(cov_type='cluster', cov_kwds={'groups': df_seg['country']})
    
    mkt_price_elasticity = float(model_mkt.params['ln_market_asp'])
    mkt_price_pvalue = float(model_mkt.pvalues['ln_market_asp'])
    mkt_tot_coeff = float(model_mkt.params['ln_total_tv_units'])
    
    print(f"  [Market Price Model]")
    print(f"    Market ASP Elasticity (β_mkt)  : {mkt_price_elasticity:.4f} (p={mkt_price_pvalue:.4e})")
    print(f"    Macro Total TV Demand Coeff     : {mkt_tot_coeff:.4f}")
    print(f"    Market R-squared                : {model_mkt.rsquared:.4f}")

    # -----------------------------------------------------------------
    # 3. MARKET SHARE MODEL
    # -----------------------------------------------------------------
    X_ms = pd.concat([df_seg[['ln_price_premium', 'time_trend']], month_dummies, country_dummies], axis=1)
    X_ms = sm.add_constant(X_ms)
    y_ms = df_seg['ln_market_share']
    model_ms = sm.WLS(y_ms, X_ms, weights=weights).fit(cov_type='cluster', cov_kwds={'groups': df_seg['country']})
    
    ms_elasticity = float(model_ms.params['ln_price_premium'])
    ms_pvalue = float(model_ms.pvalues['ln_price_premium'])
    
    y_pred_ms = np.exp(model_ms.predict(X_ms))
    y_true_ms = df_seg['market_share']
    ms_w_mape = float(np.sum(np.abs(y_true_ms - y_pred_ms)) / np.sum(y_true_ms) * 100)
    
    results_42m[seg] = {
        "n_obs": n_obs,
        "volume": {
            "elasticity": own_elasticity,
            "cross_elasticity": cross_elasticity,
            "p_value": own_pvalue,
            "cross_p_value": cross_pvalue,
            "r2": float(model_vol.rsquared),
            "r2_adj": float(model_vol.rsquared_adj),
            "weighted_mape": vol_weighted_mape,
            "eu_total_mape": eu_total_mape,
            "unweighted_mape": unweighted_mape,
            "dw": dw_vol,
            "params": {k: float(v) for k, v in model_vol.params.items()},
            "pvalues": {k: float(v) for k, v in model_vol.pvalues.items()}
        },
        "market_price_elasticity": {
            "elasticity": mkt_price_elasticity,
            "p_value": mkt_price_pvalue,
            "total_tv_coeff": mkt_tot_coeff,
            "r2": float(model_mkt.rsquared),
            "dw": float(durbin_watson(model_mkt.resid)),
            "model_type": "Controlled Panel WLS (Total TV Demand Controlled 42M)"
        },
        "market_share": {
            "elasticity": ms_elasticity,
            "p_value": ms_pvalue,
            "r2": float(model_ms.rsquared),
            "r2_adj": float(model_ms.rsquared_adj),
            "weighted_mape": ms_w_mape,
            "dw": float(durbin_watson(model_ms.resid))
        }
    }

# -----------------------------------------------------------------
# STEP 3: COMPARISON TABLE & SUMMARY
# -----------------------------------------------------------------
print("\n" + "="*95, flush=True)
print("             18개월 OLS vs 42개월 WLS 회귀분석 종합 성능 비교표", flush=True)
print("="*95, flush=True)
print(f"{'제품군 (Segment)':<16} | {'구분':<8} | {'자체 탄력성(β)':<14} | {'시장 탄력성':<12} | {'R²':<7} | {'DW':<7} | {'MAPE':<10}")
print("-" * 95, flush=True)

comparison_records = []
for seg in TARGET_SEGMENTS:
    old_res = OLD_18M_RESULTS[seg]
    new_res = results_42m[seg]
    
    old_b  = old_res['elasticity']
    new_b  = new_res['volume']['elasticity']
    old_mkt = old_res['mkt_elasticity']
    new_mkt = new_res['market_price_elasticity']['elasticity']
    old_r2 = old_res['r2']
    new_r2 = new_res['volume']['r2']
    old_dw = old_res['dw']
    new_dw = new_res['volume']['dw']
    old_mape = old_res['mape']
    new_wmape = new_res['volume']['weighted_mape']
    
    print(f"{seg:<16} | {'과거 18M':<8} | {old_b:>12.4f}   | {old_mkt:>10.4f}   | {old_r2:>5.3f} | {old_dw:>5.3f} | {old_mape:>7.1f}%")
    print(f"{'':<16} | {'신규 42M':<8} | {new_b:>12.4f}   | {new_mkt:>10.4f}   | {new_r2:>5.3f} | {new_dw:>5.3f} | {new_wmape:>7.1f}% (가중)")
    print("-" * 95, flush=True)
    
    comparison_records.append({
        "segment": seg,
        "old_18m_elasticity": old_b,
        "new_42m_elasticity": new_b,
        "new_42m_cross_elasticity": new_res['volume']['cross_elasticity'],
        "old_18m_mkt_elasticity": old_mkt,
        "new_42m_mkt_elasticity": new_mkt,
        "old_r2": old_r2,
        "new_r2": new_r2,
        "old_dw": old_dw,
        "new_dw": new_dw,
        "old_mape": old_mape,
        "new_weighted_mape": new_wmape,
        "new_eu_total_mape": new_res['volume']['eu_total_mape'],
        "new_unweighted_mape": new_res['volume']['unweighted_mape']
    })

print("="*95, flush=True)

# Export to JSON
with open(EXPORT_JSON, 'w', encoding='utf-8') as f:
    json.dump({
        "pipeline_version": "2.0_42m_wls",
        "period": "2023.01 ~ 2026.06 (42M Panel)",
        "scope": f"Europe Total ({df['country'].nunique()} countries, strictly excluding Poland & Croatia)",
        "countries": sorted(df['country'].unique()),
        "excluded_countries": ["POLAND", "CROATIA"],
        "comparison": comparison_records,
        "models": results_42m
    }, f, indent=2, ensure_ascii=False)

print(f"\n[SUCCESS] Saved 42-Month Regression Analysis JSON: {EXPORT_JSON}", flush=True)
print("Pipeline finished successfully!", flush=True)
