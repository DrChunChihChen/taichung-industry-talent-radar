"""
ETL Module: Company Cleaning Pipeline (System Spec Section 7)
Principles:
- 7.1 Company Name Normalization
- 7.2 Company ID Normalization (8 digits string)
- 7.3 Address -> District (Taichung 29 districts, UNKNOWN logged to error log)
"""
import re
import json
from typing import Dict, Any, Tuple, Optional
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import TARGET_CITY, TAICHUNG_DISTRICTS, PROCESSED_DATA_DIR

ERROR_LOG_PATH = PROCESSED_DATA_DIR / "etl_company_cleaning_errors.json"
cleaning_errors = []

def normalize_company_name(raw_name: str) -> Tuple[str, bool]:
    """
    Normalizes company name by removing or tagging branches, stores, offices.
    Returns: (normalized_name, is_branch_or_store)
    """
    if not raw_name or not isinstance(raw_name, str):
        return ("", False)
    
    name = raw_name.strip()
    # Normalize full-width spaces and parentheses
    name = re.sub(r"[\s\u3000]+", "", name)
    name = re.sub(r"[（\(].*?[）\)]", "", name)
    
    branch_pattern = re.compile(r"(分公司|門市|營業所|辦事處|加盟店|.{1,3}廠|研發處|營運處)$")
    is_branch = bool(branch_pattern.search(name))
    
    cleaned_name = branch_pattern.sub("", name)
    # Remove prefix tags like ASML) or PAPAGO_
    cleaned_name = re.sub(r"^.*?[\)_＿\-]", "", cleaned_name)
    
    return (cleaned_name.strip(), is_branch)

def normalize_company_id(raw_id: Any) -> Optional[str]:
    """
    Unified 8-digit unified business number (string).
    Validates format: exactly 8 numeric digits.
    """
    if raw_id is None:
        return None
    val = str(raw_id).strip()
    # If floating point representation like 22099131.0
    if "." in val:
        val = val.split(".")[0]
    # Pad to 8 digits if necessary (for leading zeros)
    if len(val) < 8 and val.isdigit():
        val = val.zfill(8)
    if len(val) == 8 and val.isdigit():
        return val
    return None

def parse_address_to_district(address: str) -> Tuple[str, str, bool]:
    """
    Parses address to (city, district, is_valid).
    If unrecognized, returns ("台中市", "UNKNOWN", False) and logs error.
    """
    if not address or not isinstance(address, str):
        err = {"address": str(address), "error": "EMPTY_OR_INVALID_ADDRESS"}
        cleaning_errors.append(err)
        return (TARGET_CITY, "UNKNOWN", False)
    
    addr = address.replace("臺中市", "台中市").strip()
    
    # Check if city is Taichung
    if "台中市" not in addr and not any(d in addr for d in TAICHUNG_DISTRICTS):
        err = {"address": address, "error": "NOT_TAICHUNG_CITY"}
        cleaning_errors.append(err)
        return ("其他縣市", "UNKNOWN", False)
    
    for district in TAICHUNG_DISTRICTS:
        if district in addr:
            return (TARGET_CITY, district, True)
    
    # Check 2-letter district matching (e.g. 西屯, 南屯)
    for district in TAICHUNG_DISTRICTS:
        prefix = district[:-1]  # '西屯' from '西屯區'
        if prefix in addr:
            return (TARGET_CITY, district, True)
            
    err = {"address": address, "error": "DISTRICT_UNKNOWN"}
    cleaning_errors.append(err)
    return (TARGET_CITY, "UNKNOWN", False)

def save_cleaning_error_log():
    with open(ERROR_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(cleaning_errors, f, ensure_ascii=False, indent=2)
    print(f"Logged {len(cleaning_errors)} cleaning errors to {ERROR_LOG_PATH}")

if __name__ == "__main__":
    test_cases = [
        "臺中市西屯區臺灣大道三段99號",
        "台中市潭子區建國路1號(臺中加工出口區)",
        "台中市南屯區精科路10號分公司",
        "台北市大安區信義路二段"
    ]
    for c in test_cases:
        norm_name, is_br = normalize_company_name("某某精密機械股份有限公司潭子廠")
        city, dist, valid = parse_address_to_district(c)
        print(f"Addr: {c} -> {city}, {dist}, Valid={valid} | Name norm: {norm_name} (branch={is_br})")
    tax_test = normalize_company_id(22099131)
    print(f"Tax ID norm: 22099131 -> {tax_test}")
