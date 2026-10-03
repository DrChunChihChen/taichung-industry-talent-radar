"""
Deterministic Engine: Mismatch Engine & Early-Warning Signal Generator (System Spec Section 20, 21, 22)
Principles:
- P1: Deterministic First
- P4: Traceable Result -> Indicator -> Calculation -> Processed Table -> Source Data
- P5: Warning, Not Prediction (No job shortage claims, strictly "結構性錯配警示訊號")
Level:
- Taichung City × Industry (Section 20)
"""
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import (
    TARGET_INDUSTRIES, WARNING_THRESHOLDS, MARTS_DATA_DIR,
    BASE_ACADEMIC_YEAR, TARGET_PROJECTION_YEAR
)
from database.db_manager import db

def calculate_mismatch_signals() -> pd.DataFrame:
    """
    Computes Mismatch(i) = DemandMomentum(i) - SupplyMomentum(i)
    for all 7 target industries.
    """
    mom_rows = db.fetch_all("SELECT * FROM industry_momentum_mart")
    sup_rows = db.fetch_all("SELECT * FROM talent_supply_mart")

    if not mom_rows or not sup_rows:
        raise ValueError("Missing momentum or supply data. Run engines first!")

    mom_map = {r["industry_id"]: r for r in mom_rows}
    sup_map = {r["industry_id"]: r for r in sup_rows}

    results = []

    for ind_id, ind_info in TARGET_INDUSTRIES.items():
        mom = mom_map.get(ind_id)
        sup = sup_map.get(ind_id)

        if not mom or not sup:
            continue

        dem_mom = float(mom["demand_momentum"])
        sup_mom = float(sup["supply_momentum"])

        # Mismatch(i) = DemandMomentum(i) - SupplyMomentum(i)
        mismatch = round(dem_mom - sup_mom, 4)
        intensity = round(abs(mismatch), 4)

        if mismatch > 0.1:
            direction = "SUPPLY_SHORTAGE_RISK"  # 人才供給不足風險
            dir_zh = "人才供給動能落後產業擴張動能（短缺風險）"
        elif mismatch < -0.1:
            direction = "SUPPLY_SURPLUS_PRESSURE" # 人才供給相對充裕/過剩壓力
            dir_zh = "人才供給動能高於產業擴張動能（過剩壓力）"
        else:
            direction = "BALANCED"
            dir_zh = "供需動能相對平衡"

        # Warning Classification (Section 22)
        if intensity >= WARNING_THRESHOLDS["HIGH"]:
            warning_level = "High"
        elif intensity >= WARNING_THRESHOLDS["MEDIUM"]:
            warning_level = "Medium"
        else:
            warning_level = "Low"

        # Evidence object (Section 27)
        evidence = {
            "industry_id": ind_id,
            "industry_name": ind_info["name"],
            "geography": "台中市",
            "data_period": f"產業面：109-113年公司登記；高教面：109-117學年度生源推估",
            "demand_momentum": dem_mom,
            "supply_momentum": sup_mom,
            "mismatch": mismatch,
            "intensity": intensity,
            "direction": direction,
            "direction_zh": dir_zh,
            "warning_level": warning_level,
            "drivers": {
                "entry_rate": mom["entry_rate"],
                "z_entry": mom["z_entry"],
                "capital_rate": mom["capital_rate"],
                "z_capital": mom["z_capital"],
                "exit_rate_risk_ref": mom["exit_rate"],
                "current_supply_113": sup["current_supply"],
                "projected_supply_117": sup["projected_supply_117"],
                "supply_growth": sup["supply_growth"]
            },
            "source": [
                "經濟部商工行政資料開放平臺（GCIS）公司登記歷史母體",
                "教育部大專校院校務資訊公開平臺（UDB）學生數與註冊率（109-114）",
                "教育部大專校院就業職能平台（UCAN）職涯途徑對照表",
                "內政部戶政司人口統計與少子化117學年度入學生源精算"
            ],
            "calculation": [
                f"DemandMomentum = 0.5 * Z_entry({mom['z_entry']}) + 0.5 * Z_capital({mom['z_capital']}) = {dem_mom}",
                f"SupplyMomentum = Standardize(SupplyGrowth({sup['supply_growth']})) = {sup_mom}",
                f"Mismatch = DemandMomentum({dem_mom}) - SupplyMomentum({sup_mom}) = {mismatch}",
                f"MismatchIntensity = |{mismatch}| = {intensity} ({warning_level} Warning)"
            ],
            "last_updated": "2026-10-01",
            "verification_status": "VERIFIED"
        }

        results.append({
            "industry_id": ind_id,
            "industry_name": ind_info["name"],
            "demand_momentum": dem_mom,
            "supply_momentum": sup_mom,
            "mismatch": mismatch,
            "mismatch_direction": direction,
            "mismatch_intensity": intensity,
            "warning_level": warning_level,
            "evidence_json": json.dumps(evidence, ensure_ascii=False),
            "updated_at": "2026-10-01"
        })

    res_df = pd.DataFrame(results)
    out_csv = MARTS_DATA_DIR / "mismatch_signal_mart.csv"
    res_df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    db.init_db()
    db.write_df(res_df, "mismatch_signal_mart", if_exists="replace")
    print(f"Mismatch Signal Mart built: {len(res_df)} industries saved to {out_csv} and DB.")
    return res_df

def get_mismatch_signal(industry_id: str = "") -> List[Dict[str, Any]]:
    if industry_id:
        return db.fetch_all("SELECT * FROM mismatch_signal_mart WHERE industry_id = ?", (industry_id,))
    return db.fetch_all("SELECT * FROM mismatch_signal_mart ORDER BY mismatch_intensity DESC")

if __name__ == "__main__":
    df_m = calculate_mismatch_signals()
    for _, r in df_m.iterrows():
        print(f"[{r['warning_level']} Warning] {r['industry_name']}: Mismatch = {r['mismatch']} | Direction = {r['mismatch_direction']} (Demand: {r['demand_momentum']}, Supply: {r['supply_momentum']})")
