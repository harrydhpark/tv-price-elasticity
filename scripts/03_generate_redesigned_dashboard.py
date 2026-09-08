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

    pattern = r"(const EMBEDDED_DATA = )(\{[\s\S]*?\})(;\s*\n\s*let simData = EMBEDDED_DATA;)"
    replacement = rf"\g<1>{json_str}\g<3>"

    new_content, count = re.subn(pattern, replacement, content, count=1)
    if count == 0:
        pattern_fallback = r"(const EMBEDDED_DATA = )([\s\S]*?)(;\s*\n\s*let simData = EMBEDDED_DATA;)"
        new_content, count = re.subn(pattern_fallback, rf"\g<1>{json_str}\g<3>", content, count=1)

    if count > 0:
        with open(INDEX_HTML_PATH, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Successfully injected latest simulation data into {INDEX_HTML_PATH}!")
    else:
        print("Warning: Could not locate 'const EMBEDDED_DATA' block in index.html. No changes made.")

if __name__ == "__main__":
    update_dashboard()
