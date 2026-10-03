"""
Deterministic Engine: Industry Momentum Engine (System Spec Section 10 & 11)
Calculates:
- 10.1 Entry Signal: EntryRate(i,t) and 5-year trend
- 10.2 Capital Signal: CapitalExpansionRate(i,t) and 5-year trend
- 10.3 Exit Signal: ExitRate(i,t) (Risk Reference Only)
- 11. DemandMomentum(i) = 0.5 * Z_entry(i) + 0.5 * Z_capital(i)
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import (
    TARGET_INDUSTRIES, HISTORICAL_YEARS, BASE_ACADEMIC_YEAR,
    DEMAND_MOMENTUM_WEIGHTS, MARTS_DATA_DIR
)
from database.db_manager import db

def calculate_industry_momentum(target_year: int = 113) -> pd.DataFrame:
    """
    Computes industry momentum metrics for Taichung City across all 7 target industries.
    All calculations are 100% deterministic (P1).
    """
    # Fetch aggregated city-wide metrics per year and industry from industry_dynamics_mart
    sql = """
        SELECT 
            year,
            industry_id,
            SUM(opening_count) as total_openings,
            SUM(dissolution_count) as total_dissolutions,
            SUM(capital_increase_count) as total_cap_increases,
            SUM(beginning_stock) as total_beg_stock,
            SUM(ending_stock) as total_end_stock
        FROM industry_dynamics_mart
        GROUP BY year, industry_id
        ORDER BY industry_id, year
    """
    df = db.query_df(sql)

    if df.empty:
        raise ValueError("industry_dynamics_mart is empty. Run ETL first!")

    results = []
    
    # Calculate city-wide rates per industry
    for ind_id, group in df.groupby("industry_id"):
        ind_info = TARGET_INDUSTRIES.get(ind_id, {})
        ind_name = ind_info.get("name", ind_id)
        
        # Sort by year
        group = group.sort_values("year")
        
        # Year 113 (latest target base year)
        latest_row = group[group["year"] == target_year]
        if latest_row.empty:
            latest_row = group.iloc[[-1]]
            
        beg_stock = float(latest_row["total_beg_stock"].values[0])
        openings = float(latest_row["total_openings"].values[0])
        dissolutions = float(latest_row["total_dissolutions"].values[0])
        cap_inc = float(latest_row["total_cap_increases"].values[0])
        
        entry_rate = round(openings / beg_stock, 5) if beg_stock > 0 else 0.0
        capital_rate = round(cap_inc / beg_stock, 5) if beg_stock > 0 else 0.0
        exit_rate = round(dissolutions / beg_stock, 5) if beg_stock > 0 else 0.0
        
        # 5-year Trends (slope of rates over historical years)
        hist_entry_rates = (group["total_openings"] / group["total_beg_stock"]).values
        hist_cap_rates = (group["total_cap_increases"] / group["total_beg_stock"]).values
        
        x_years = np.arange(len(group))
        entry_trend = round(float(np.polyfit(x_years, hist_entry_rates, 1)[0]), 5) if len(group) >= 2 else 0.0
        cap_trend = round(float(np.polyfit(x_years, hist_cap_rates, 1)[0]), 5) if len(group) >= 2 else 0.0
        
        results.append({
            "industry_id": ind_id,
            "industry_name": ind_name,
            "base_year": target_year,
            "entry_rate": entry_rate,
            "entry_trend": entry_trend,
            "capital_rate": capital_rate,
            "capital_trend": cap_trend,
            "exit_rate": exit_rate,
            "beginning_stock": int(beg_stock),
            "ending_stock": int(latest_row["total_end_stock"].values[0])
        })

    res_df = pd.DataFrame(results)

    # Section 11: Standardization Z_entry(i) and Z_capital(i)
    e_mean, e_std = res_df["entry_rate"].mean(), res_df["entry_rate"].std()
    c_mean, c_std = res_df["capital_rate"].mean(), res_df["capital_rate"].std()

    if e_std == 0: e_std = 1.0
    if c_std == 0: c_std = 1.0

    res_df["z_entry"] = round((res_df["entry_rate"] - e_mean) / e_std, 4)
    res_df["z_capital"] = round((res_df["capital_rate"] - c_mean) / c_std, 4)

    # DemandMomentum(i) = 0.5 * Z_entry(i) + 0.5 * Z_capital(i)
    w_entry = DEMAND_MOMENTUM_WEIGHTS["entry"]
    w_cap = DEMAND_MOMENTUM_WEIGHTS["capital"]
    res_df["demand_momentum"] = round(w_entry * res_df["z_entry"] + w_cap * res_df["z_capital"], 4)
    res_df["updated_at"] = "2026-10-01"

    # Persist to database and CSV mart
    out_csv = MARTS_DATA_DIR / "industry_momentum_mart.csv"
    res_df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    db.init_db()
    db.write_df(res_df, "industry_momentum_mart", if_exists="replace")
    print(f"Industry Momentum Mart calculated: {len(res_df)} industries saved to {out_csv} and DB.")
    return res_df

def get_industry_momentum(industry_id: str = "") -> List[Dict[str, Any]]:
    """Query helper returning momentum metrics"""
    if industry_id:
        return db.fetch_all("SELECT * FROM industry_momentum_mart WHERE industry_id = ?", (industry_id,))
    return db.fetch_all("SELECT * FROM industry_momentum_mart ORDER BY demand_momentum DESC")

if __name__ == "__main__":
    df_mom = calculate_industry_momentum(113)
    print(df_mom[["industry_id", "industry_name", "entry_rate", "capital_rate", "z_entry", "z_capital", "demand_momentum"]])
