"""
ETL Module: MOE UDB Extraction & Department Indicators Mart (System Spec Section 4.1, 12, 13, 14)
Calculates:
- Department historical enrollment and share trend (109-113)
- Department registration rate trend (109-113)
- Projected students to 117 academic year
- Triggers UCAN career mapping generation for all departments
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import (
    BASE_ACADEMIC_YEAR, TARGET_PROJECTION_YEAR, HISTORICAL_YEARS,
    RAW_DATA_DIR, MARTS_DATA_DIR, PROCESSED_DATA_DIR
)
from database.db_manager import db
from etl.extract_demographics import get_freshmen_estimate
from etl.map_ucan_careers import build_all_ucan_mappings

TAICHUNG_SCHOOLS = [
    "國立臺中科技大學", "逢甲大學", "國立中興大學", "國立勤益科技大學", "東海大學",
    "靜宜大學", "亞洲大學", "朝陽科技大學", "弘光科技大學", "中臺科技大學",
    "嶺東科技大學", "僑光科技大學", "中山醫學大學", "中國醫藥大學"
]

def clean_registration_rate(val: Any) -> float:
    """Converts registration rate string/number to clean percentage float (0.0 to 100.0)"""
    if pd.isna(val):
        return 90.0
    s = str(val).replace("%", "").strip()
    try:
        f = float(s)
        if f > 100.0:
            return 100.0
        if f < 0.0:
            return 0.0
        return round(f, 2)
    except ValueError:
        return 90.0

def extract_moe_udb_data() -> pd.DataFrame:
    f_stu = RAW_DATA_DIR / "moe_udb_cache" / "學1-1.正式學籍在學學生人數-以「系(所)」統計.csv"
    f_reg = RAW_DATA_DIR / "moe_udb_cache" / "學12-1.新生(含境外生)註冊率-以「系(所)」統計.csv"

    print("Loading MOE UDB raw data...")
    df_stu_raw = pd.read_csv(f_stu)
    df_reg_raw = pd.read_csv(f_reg, low_memory=False)

    # Filter for Taichung universities and historical years (109-113)
    stu_tc = df_stu_raw[
        df_stu_raw["學校名稱"].isin(TAICHUNG_SCHOOLS) &
        df_stu_raw["學年度"].isin(HISTORICAL_YEARS)
    ].copy()

    # Aggregate total enrolled students per (學年度, 學校代碼, 學校名稱, 系所代碼, 系所名稱)
    dept_agg = stu_tc.groupby(
        ["學年度", "學校統計處代碼", "學校名稱", "系所代碼", "系所名稱"]
    )["在學學生數小計"].sum().reset_index()

    # Process registration rates
    reg_tc = df_reg_raw[
        df_reg_raw["學校名稱"].isin(TAICHUNG_SCHOOLS) &
        df_reg_raw["學年度"].isin(HISTORICAL_YEARS)
    ].copy()
    reg_tc["reg_rate_clean"] = reg_tc["當學年度新生註冊率(%)D=〔(C+E)/(A-B+E)〕＊100％"].apply(clean_registration_rate)
    reg_agg = reg_tc.groupby(
        ["學年度", "學校統計處代碼", "學校名稱", "系所代碼", "系所名稱"]
    )["reg_rate_clean"].mean().reset_index()

    # Merge student counts with registration rate
    merged = pd.merge(
        dept_agg, reg_agg,
        on=["學年度", "學校統計處代碼", "學校名稱", "系所代碼", "系所名稱"],
        how="left"
    )
    merged["reg_rate_clean"] = merged["reg_rate_clean"].fillna(92.5)

    # Compute TotalRelevantStudents per year for DepartmentShare(d, t)
    yearly_totals = merged.groupby("學年度")["在學學生數小計"].sum().to_dict()
    merged["department_share"] = merged.apply(
        lambda r: round(r["在學學生數小計"] / yearly_totals[r["學年度"]], 6), axis=1
    )

    # Demographic baseline: Freshmen 113 vs 117
    freshmen_113 = get_freshmen_estimate(BASE_ACADEMIC_YEAR)
    freshmen_117 = get_freshmen_estimate(TARGET_PROJECTION_YEAR)
    demo_ratio = freshmen_117 / freshmen_113  # ~0.8298 (-17.02%)

    print(f"Demographic factor 113 -> 117: {demo_ratio:.4f}")

    # Estimate department trends for projection to 117
    # For each department, calculate 109-113 share growth and registration trend
    records = []
    unique_depts = merged[["學校統計處代碼", "學校名稱", "系所代碼", "系所名稱"]].drop_duplicates()

    for _, dept in unique_depts.iterrows():
        inst_id = str(dept["學校統計處代碼"])
        inst_name = str(dept["學校名稱"])
        d_id = str(dept["系所代碼"])
        d_name = str(dept["系所名稱"])

        dept_hist = merged[
            (merged["學校名稱"] == inst_name) &
            (merged["系所名稱"] == d_name)
        ].sort_values("學年度")

        if len(dept_hist) == 0:
            continue

        latest_row = dept_hist.iloc[-1]
        curr_students = latest_row["在學學生數小計"]
        curr_share = latest_row["department_share"]
        curr_reg_rate = latest_row["reg_rate_clean"]

        # Department Share Trend (P3 / Section 13: independent calculation per department)
        if len(dept_hist) >= 3:
            shares = dept_hist["department_share"].values
            years = np.arange(len(shares))
            slope, _ = np.polyfit(years, shares, 1)
            # Project share to 117 (+4 years from 113)
            proj_share = max(0.00001, curr_share + slope * 4)
        else:
            proj_share = curr_share

        # Registration rate trend to 117 (Section 14)
        if len(dept_hist) >= 3:
            regs = dept_hist["reg_rate_clean"].values
            slope_reg, _ = np.polyfit(np.arange(len(regs)), regs, 1)
            proj_reg_rate = min(100.0, max(50.0, curr_reg_rate + slope_reg * 4))
        else:
            proj_reg_rate = curr_reg_rate

        # ProjectedStudents(d, 117) = DemographicFactor * (proj_share / curr_share) * (proj_reg / curr_reg) * curr_students
        share_factor = proj_share / curr_share if curr_share > 0 else 1.0
        reg_factor = (proj_reg_rate / curr_reg_rate) if curr_reg_rate > 0 else 1.0
        
        # Bounded projection
        proj_students_117 = round(curr_students * demo_ratio * share_factor * reg_factor, 1)
        freshmen_admitted = int(round(curr_students / 4.0))

        # Add records for historical years
        for _, h_row in dept_hist.iterrows():
            records.append({
                "academic_year": int(h_row["學年度"]),
                "institution_id": inst_id,
                "institution_name": inst_name,
                "department_id": d_id,
                "department_name": d_name,
                "enrolled_students": int(h_row["在學學生數小計"]),
                "freshmen_admitted": int(round(h_row["在學學生數小計"] / 4.0)),
                "registration_rate": round(float(h_row["reg_rate_clean"]), 2),
                "department_share": round(float(h_row["department_share"]), 6),
                "projected_students_117": proj_students_117,
                "updated_at": "2026-10-01"
            })

    df_final = pd.DataFrame(records)
    out_csv = MARTS_DATA_DIR / "department_indicators_mart.csv"
    df_final.to_csv(out_csv, index=False, encoding="utf-8-sig")

    db.init_db()
    db.write_df(df_final, "department_indicators_mart", if_exists="replace")
    print(f"Department Indicators Mart built: {len(df_final)} rows saved to {out_csv} and DB.")

    # Now trigger build of UCAN mapping mart for all unique departments across all years
    print("Building UCAN Career Mappings for all departments...")
    unique_all = df_final[
        ["department_id", "department_name", "institution_id", "institution_name"]
    ].drop_duplicates()
    build_all_ucan_mappings(unique_all)

    return df_final

if __name__ == "__main__":
    extract_moe_udb_data()
