"""
Deterministic Engine: Talent Supply Projection Engine (System Spec Section 12, 17, 18, 19)
Calculates:
- Current Talent Supply (113) per target industry
- Projected Talent Supply (117) per target industry via UCAN Career Pathway weights & dilution
- SupplyGrowth(i) = ProjectedSupply(i, 117) / CurrentSupply(i) - 1
- SupplyMomentum(i) = Standardize(SupplyGrowth(i))
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import (
    TARGET_INDUSTRIES, BASE_ACADEMIC_YEAR, TARGET_PROJECTION_YEAR,
    MARTS_DATA_DIR
)
from database.db_manager import db

def calculate_industry_talent_supply() -> pd.DataFrame:
    """
    Computes industry talent supply by aggregating department projections
    weighted through UCAN Career Mapping (Section 17 & 18).
    """
    # Join department_indicators_mart (year 113) with ucan_mapping_mart
    sql = f"""
        SELECT 
            u.industry_id,
            u.industry_name,
            d.department_name,
            d.institution_name,
            d.enrolled_students as curr_students,
            d.projected_students_117 as proj_students,
            u.weight as raw_weight,
            u.normalized_weight
        FROM ucan_mapping_mart u
        INNER JOIN department_indicators_mart d 
            ON u.department_name = d.department_name 
            AND u.institution_name = d.institution_name
        WHERE d.academic_year = {BASE_ACADEMIC_YEAR}
    """
    df = db.query_df(sql)

    if df.empty:
        raise ValueError("No joined UCAN & Department data found! Check ETL pipeline.")

    # Calculate contribution: Supply = Students * Normalized Weight
    df["curr_contrib"] = df["curr_students"] * df["normalized_weight"]
    df["proj_contrib"] = df["proj_students"] * df["normalized_weight"]

    results = []
    for ind_id, ind_info in TARGET_INDUSTRIES.items():
        sub = df[df["industry_id"] == ind_id]
        ind_name = ind_info["name"]
        
        curr_supply = round(float(sub["curr_contrib"].sum()), 2)
        proj_supply = round(float(sub["proj_contrib"].sum()), 2)
        dept_count = int(sub["department_name"].nunique())
        
        if curr_supply > 0:
            growth = round((proj_supply / curr_supply) - 1.0, 5)
        else:
            growth = 0.0
            
        results.append({
            "industry_id": ind_id,
            "industry_name": ind_name,
            "current_supply": curr_supply,
            "projected_supply_117": proj_supply,
            "supply_growth": growth,
            "total_contributing_depts": dept_count
        })

    res_df = pd.DataFrame(results)

    # Standardize SupplyGrowth(i) into SupplyMomentum(i)
    g_mean = res_df["supply_growth"].mean()
    g_std = res_df["supply_growth"].std()
    if g_std == 0: g_std = 1.0

    res_df["supply_momentum"] = round((res_df["supply_growth"] - g_mean) / g_std, 4)
    res_df["updated_at"] = "2026-10-01"

    # Persist to database and CSV
    out_csv = MARTS_DATA_DIR / "industry_supply_mart.csv"
    res_df.to_csv(out_csv, index=False, encoding="utf-8-sig")

    db.init_db()
    db.write_df(res_df, "talent_supply_mart", if_exists="replace")
    print(f"Talent Supply Mart calculated: {len(res_df)} industries saved to {out_csv} and DB.")
    return res_df

def get_talent_supply(industry_id: str = "") -> List[Dict[str, Any]]:
    if industry_id:
        return db.fetch_all("SELECT * FROM talent_supply_mart WHERE industry_id = ?", (industry_id,))
    return db.fetch_all("SELECT * FROM talent_supply_mart ORDER BY supply_momentum ASC")

def get_department_projection(dept_name: str = "", inst_name: str = "") -> List[Dict[str, Any]]:
    """Helper to query department level historical trend and 117 projections"""
    conditions = []
    params = []
    if dept_name:
        conditions.append("department_name LIKE ?")
        params.append(f"%{dept_name}%")
    if inst_name:
        conditions.append("institution_name LIKE ?")
        params.append(f"%{inst_name}%")
        
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    sql = f"""
        SELECT 
            academic_year, institution_name, department_name, 
            enrolled_students, freshmen_admitted, registration_rate, 
            department_share, projected_students_117
        FROM department_indicators_mart
        {where_clause}
        ORDER BY institution_name, department_name, academic_year
    """
    return db.fetch_all(sql, tuple(params))

if __name__ == "__main__":
    df_sup = calculate_industry_talent_supply()
    print(df_sup[["industry_id", "industry_name", "current_supply", "projected_supply_117", "supply_growth", "supply_momentum"]])
