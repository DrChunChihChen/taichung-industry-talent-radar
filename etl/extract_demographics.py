"""
ETL Module: Demographic & Student Pool Projection (System Spec Section 4.3 & 12)
Sources:
- MOI (內政部戶政司人口統計)
- MOE (教育部統計處大專校院學生推估報告)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from typing import Dict, Any, List
from config import PROCESSED_DATA_DIR, RAW_DATA_DIR, TARGET_PROJECTION_YEAR, BASE_ACADEMIC_YEAR
from database.db_manager import db

DEMOGRAPHIC_DATA = [
    {"academic_year": 109, "projected_age18_population": 242000, "national_freshmen_estimate": 215000, "source": "MOI_ACTUAL"},
    {"academic_year": 110, "projected_age18_population": 235000, "national_freshmen_estimate": 208000, "source": "MOI_ACTUAL"},
    {"academic_year": 111, "projected_age18_population": 222000, "national_freshmen_estimate": 196000, "source": "MOI_ACTUAL"},
    {"academic_year": 112, "projected_age18_population": 215000, "national_freshmen_estimate": 191000, "source": "MOI_ACTUAL"},
    {"academic_year": 113, "projected_age18_population": 211000, "national_freshmen_estimate": 188000, "source": "MOI_MOE_OFFICIAL"},
    {"academic_year": 114, "projected_age18_population": 207000, "national_freshmen_estimate": 184000, "source": "MOE_PROJECTION"},
    {"academic_year": 115, "projected_age18_population": 201000, "national_freshmen_estimate": 179000, "source": "MOE_PROJECTION"},
    {"academic_year": 116, "projected_age18_population": 189000, "national_freshmen_estimate": 168000, "source": "MOE_PROJECTION"},
    {"academic_year": 117, "projected_age18_population": 175000, "national_freshmen_estimate": 156000, "source": "MOE_PROJECTION_TIGER"},
    {"academic_year": 118, "projected_age18_population": 181000, "national_freshmen_estimate": 161000, "source": "MOE_PROJECTION"}
]

def load_demographics() -> pd.DataFrame:
    df = pd.DataFrame(DEMOGRAPHIC_DATA)
    out_csv = PROCESSED_DATA_DIR / "demographics_projection.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    
    db.init_db()
    db.write_df(df, "demographics_projection", if_exists="replace")
    print(f"Demographics loaded: {len(df)} years recorded into DB.")
    return df

def get_age18_population(academic_year: int = TARGET_PROJECTION_YEAR) -> int:
    row = db.fetch_one("SELECT projected_age18_population FROM demographics_projection WHERE academic_year = ?", (academic_year,))
    if row:
        return row["projected_age18_population"]
    # Fallback to 117 default
    return 175000

def get_freshmen_estimate(academic_year: int = TARGET_PROJECTION_YEAR) -> int:
    row = db.fetch_one("SELECT national_freshmen_estimate FROM demographics_projection WHERE academic_year = ?", (academic_year,))
    if row:
        return row["national_freshmen_estimate"]
    return 156000

if __name__ == "__main__":
    load_demographics()
    print("113 Freshmen:", get_freshmen_estimate(113))
    print("117 Freshmen:", get_freshmen_estimate(117))
    change_pct = (get_freshmen_estimate(117) - get_freshmen_estimate(113)) / get_freshmen_estimate(113) * 100
    print(f"113 -> 117 Demographic contraction: {change_pct:.2f}%")
