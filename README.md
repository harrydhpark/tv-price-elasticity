# LG TV Europe — 2027 Q1 Price Elasticity Simulator & Regression Analysis
> **LGE Europe TV Sales / 2026 AX Execution Task #12**  
> 18-Month (2025.01 ~ 2026.06) 20 European Countries Panel Regression & 2027 Q1 Competitor Scenario Decision Engine

---

## 📌 Executive Summary

This project establishes an econometric pricing intelligence system for LG Electronics Europe TV Business. By applying multivariate Log-Log OLS panel regression across 20 European markets over 18 months, we estimate **Own Price Elasticity ($\beta_1$)**, **Market Price Elasticity ($\beta_{mkt}$)**, **Relative Price Premium Elasticity ($\beta_2$)**, and **Market Size Elasticity ($\beta_3$)** for 4 distinct TV segments:
1. **OLED TV**
2. **QNED / MiniLED / NanoCell** (NanoCell integrated)
3. **Standard UHD 4K**
4. **FHD & Entry**

Based on the 2026 Q1 baseline dataset, the system simulates 2027 Q1 Sales Volume (Units), Revenue (Sales Value, €M), Average Selling Price (ASP), and Market Share (M/S %) under **3 Competitor Follow Scenarios**:
- **Case 1 (100% Equal Follow)**: Competitors follow LG price hike 100% across all segments.
- **Case 2 (75% Follow for Non-OLED)**: OLED 100% follow, Non-OLED 75% follow.
- **Case 3 (50% Follow for Non-OLED)**: OLED 100% follow, Non-OLED 50% follow.

---

## 🔬 Regression Model Diagnostics (18M Panel OLS)

$$\ln(Q_{LG, c, t}) = \alpha + \beta_1 \ln(P_{LG, c, t}) + \beta_2 \ln\left(\frac{P_{LG, c, t}}{P_{Comp, c, t}}\right) + \beta_3 \ln(MktSize_{c, t}) + \beta_4 t + \beta_5 \text{IsQ4}_{c, t} + \epsilon_{c, t}$$

| Segment | Own Elasticity ($\beta_1$) | Market Price Elasticity ($\beta_{mkt}$) | Premium Elasticity ($\beta_2$) | Market Size Elasticity ($\beta_3$) | $p$-value | $R^2$ | Vol MAPE | DW | Economic Characteristics |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **OLED TV** | **-0.2616** | **-1.6277** | -0.6982 | 0.9133 | 0.0002 | **0.986** | 11.7% | 0.580 | Highly inelastic ($|\beta_1| < 1$). Avoid price cuts; preserve premium brand mix. |
| **QNED / MiniLED / NanoCell** | **-1.2105** | **-1.8451** | +0.0825 | 0.8420 | < 0.0001 | **0.882** | 31.4% | 0.488 | Moderately elastic ($|\beta_1| \approx 1.2$). Direct competition with Neo QLED. |
| **Standard UHD 4K** | **-1.3888** | **-1.2604** | -0.8781 | 1.0245 | < 0.0001 | **0.855** | 77.7% | 0.602 | Highly elastic ($|\beta_1| > 1$). Large volume segment; price competitiveness essential. |
| **FHD & Entry** | **-0.8655** | **-1.4829** | -0.6175 | 1.1671 | 0.0052 | **0.872** | 77.9% | 0.541 | Inelastic ($|\beta_1| < 1$). Stable entry replacement demand; margin defense strategy. |

*Note: Poland and Croatia are strictly excluded from all calculations per business requirements.*

---

## 🎛️ Simulation Engine: Market Share Decomposition Model

1. **Market Average Price Inflation ($\Delta P_{mkt}$)**:
   $$\Delta P_{mkt} = (MS_{base} \times \Delta P_{LG}) + ((1 - MS_{base}) \times \Delta P_{comp})$$
2. **Market Volume Contraction ($g_{mkt}$)**:
   $$g_{mkt} = \beta_{mkt} \times \Delta P_{mkt}$$
   $$Q_{mkt}^{new} = Q_{mkt}^{base} \times (1 + g_{mkt})$$
3. **Relative Price Premium Change ($\Delta \text{Premium}$)**:
   $$\Delta \text{Premium} = \frac{1 + \Delta P_{LG}}{1 + \Delta P_{comp}} - 1$$
4. **LG Market Share Evolution ($MS_{LG}^{new}$)**:
   $$MS_{LG}^{new} = MS_{LG}^{base} \times (1 + \gamma \times \Delta \text{Premium})$$
5. **LG Projected Units & Revenue**:
   $$Q_{LG}^{new} = Q_{mkt}^{new} \times MS_{LG}^{new}$$
   $$\text{Revenue}_{LG}^{new} = Q_{LG}^{new} \times (ASP_{LG}^{base} \times (1 + \Delta P_{LG}))$$

---

## 💻 Dashboard Architecture & Features

- **File**: `dashboard/index.html` (Zero-dependency standalone HTML)
- **Offline Capable**: All baseline data and model parameters are directly embedded.
- **Top Regression Diagnostics Table**: Immediate visibility into econometric indicators.
- **Single-Select Interactive Radio Banner**: Switch seamlessly between Case 1, Case 2, and Case 3.
- **1:1 Contrast Bar Charts**: 2026 Q1 actual vs. selected Case 2027 Q1 forecast for Volume and Value.
- **Incremental Summary Table (Diff & YoY %)**: Clear breakdown of $\Delta$ Units (k) and $\Delta$ Revenue (€M).
- **Comprehensive 3-Case Comparison Table**: Side-by-side comparison across all scenarios.
- **Quick Preset Buttons**: `[전체 +5% (기본)]`, `[차등 인상]`, `[0% (동결)]` with a zero-change alert banner.

---

## 🚀 Repository Structure

```
├── .gitignore
├── README.md
├── PROJECT_GUIDE.md                                      # Detailed operational guide
├── LG_TV_유럽_가격탄력성_회귀분석_경쟁대응_보고서.docx   # Executive Word Report
├── DATA/
│    └── processed/
│         ├── elasticity_results_18m.json                 # Regression parameters DB
│         └── panel_regression_data_18m.csv               # Processed 18M panel data
├── dashboard/
│    ├── index.html                                       # Standalone interactive dashboard
│    ├── simulation_data.json                             # 2026 Q1 baseline & metadata
│    └── report_assets/                                   # High-resolution chart figures
└── scripts/
     ├── 01_run_elasticity_18m.py                         # Panel OLS regression pipeline
     ├── 02_build_q1_sim_data.py                          # 2026 Q1 baseline builder
     └── 03_generate_redesigned_dashboard.py              # Standalone dashboard compiler
```

---

## 🛠️ Execution Pipeline

```powershell
# 1. Run 18M Panel Regression
python scripts/01_run_elasticity_18m.py

# 2. Build 2026 Q1 Baseline Dataset
python scripts/02_build_q1_sim_data.py

# 3. Compile Standalone Dashboard
python scripts/03_generate_redesigned_dashboard.py
```
