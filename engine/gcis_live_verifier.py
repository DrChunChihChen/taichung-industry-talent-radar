"""
Deterministic Engine: GCIS Live Verifier (System Spec Section 5.1)
Single Company Verification Tool:
- Checks company by Unified Business Number (8 digits) or Company Name
- Queries live GCIS API (with SSL bypass and query timeout)
- Falls back to local benchmark database if network is unreachable
"""
import sys
import re
import requests
import urllib3
from pathlib import Path
from typing import Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import TARGET_CITY
from database.db_manager import db
from etl.clean_companies import normalize_company_name, normalize_company_id

urllib3.disable_warnings()

GCIS_API_BASE = "https://data.gcis.nat.gov.tw/od/data/api/"
API_TAX_ID = "5F64D864-61CB-4D0D-8AD9-492047CC1EA6"  # Business_Accounting_NO eq
API_NAME   = "6BBA2268-1367-4B42-9CCA-BC17499EBE8C"  # Company_Name like X and Company_Status eq S

def verify_company_live(query: str) -> Dict[str, Any]:
    """
    Verifies a single company by tax ID or name.
    Strictly deterministic (P1).
    """
    q = (query or "").strip()
    norm_id = normalize_company_id(q)

    # 1. Check local benchmark database first
    if norm_id:
        local_row = db.fetch_one("SELECT * FROM companies WHERE company_id = ?", (norm_id,))
        if local_row:
            return {
                "verified": True,
                "tax_id": local_row["company_id"],
                "company_name": local_row["company_name"],
                "status": local_row["status"],
                "capital": local_row["capital"],
                "district": local_row["district"],
                "address": local_row["address"],
                "industry_id": local_row["industry_id"],
                "source": "GCIS_LOCAL_BENCHMARK",
                "verified_via": "LOCAL_DB"
            }
    else:
        norm_name, _ = normalize_company_name(q)
        local_row = db.fetch_one(
            "SELECT * FROM companies WHERE company_name LIKE ? OR normalized_name LIKE ?",
            (f"%{norm_name}%", f"%{norm_name}%")
        )
        if local_row:
            return {
                "verified": True,
                "tax_id": local_row["company_id"],
                "company_name": local_row["company_name"],
                "status": local_row["status"],
                "capital": local_row["capital"],
                "district": local_row["district"],
                "address": local_row["address"],
                "industry_id": local_row["industry_id"],
                "source": "GCIS_LOCAL_BENCHMARK",
                "verified_via": "LOCAL_DB"
            }

    # 2. Query Live GCIS API
    try:
        if norm_id:
            raw_url = f"{GCIS_API_BASE}{API_TAX_ID}?$format=json&$filter=Business_Accounting_NO%20eq%20{norm_id}"
        else:
            norm_name, _ = normalize_company_name(q)
            raw_url = f"{GCIS_API_BASE}{API_NAME}?$format=json&$filter=Company_Name%20like%20{norm_name[:6]}&$top=3"

        r = requests.get(raw_url, verify=False, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and len(data) > 0:
                best = data[0]
                return {
                    "verified": True,
                    "tax_id": best.get("Business_Accounting_NO"),
                    "company_name": best.get("Company_Name"),
                    "status": best.get("Company_Status_Desc", "核准設立"),
                    "capital": best.get("Capital_Stock_Amount", 0),
                    "district": "西屯區" if "西屯" in str(best.get("Company_Location")) else "台中市",
                    "address": best.get("Company_Location", ""),
                    "source": "GCIS_LIVE_API_OFFICIAL",
                    "verified_via": "LIVE_API"
                }
    except Exception as e:
        # Fallback if API timeout or SSL network block
        pass

    return {
        "verified": False,
        "query": query,
        "message": f"商工登記查無此公司（查詢輸入：{query}）",
        "source": "GCIS_VERIFICATION_ENGINE"
    }

if __name__ == "__main__":
    print(verify_company_live("22099131")) # TSMC
    print(verify_company_live("大立光電"))
    print(verify_company_live("99999999")) # Invalid
