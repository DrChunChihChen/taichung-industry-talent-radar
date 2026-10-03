"""
AI Agent Module 02: Intent Router (System Spec Section 24)
Classifies user query into one of 7 canonical intents:
1. COMPANY_VERIFY
2. DEPARTMENT_QUERY
3. DEMOGRAPHIC_QUERY
4. DISTRICT_QUERY
5. MISMATCH_QUERY
6. SUPPLY_QUERY
7. INDUSTRY_QUERY
"""
import re
from typing import Dict, Any, Tuple
from config import TAICHUNG_DISTRICTS, TARGET_INDUSTRIES
from database.db_manager import db

# Cache departments and institutions for instant extraction
_DEPT_CACHE = None

def get_dept_cache():
    global _DEPT_CACHE
    if _DEPT_CACHE is None:
        rows = db.fetch_all("SELECT DISTINCT institution_name, department_name FROM department_indicators_mart")
        # Sort departments by name length descending for maximal match
        _DEPT_CACHE = sorted(rows, key=lambda x: len(x["department_name"]), reverse=True)
    return _DEPT_CACHE

def route_intent(query: str) -> Dict[str, Any]:
    q = (query or "").strip()
    
    # 1. Company Verification (Tax ID: 8 digits, or contains 統編, 公司核對, 登記狀況)
    has_8digit = bool(re.search(r"\b\d{8}\b", q))
    if has_8digit or any(k in q for k in ["核對公司", "查統編", "統一編號", "公司登記狀態", "查證公司", "登記現況"]):
        match = re.search(r"\b\d{8}\b", q)
        tax_id = match.group(0) if match else ""
        return {
            "intent": "COMPANY_VERIFY",
            "confidence": 1.0,
            "params": {"tax_id": tax_id, "query_term": q}
        }

    # 2. Check for Specific University Department Query FIRST
    # If the user specifically mentions a school or department, prioritize DEPARTMENT_QUERY
    dept_cache = get_dept_cache()
    matched_inst = ""
    matched_dept = ""
    for item in dept_cache:
        d_name = item["department_name"]
        i_name = item["institution_name"]
        if d_name in q and (i_name in q or len(d_name) >= 4):
            matched_inst = i_name if i_name in q else ""
            matched_dept = d_name
            break

    if matched_dept:
        # Check if asking specifically about 117 projection, students, or registration rate
        return {
            "intent": "DEPARTMENT_QUERY",
            "confidence": 0.98,
            "params": {
                "institution_name": matched_inst,
                "department_name": matched_dept,
                "query_term": q
            }
        }

    # 3. Check for Demographic Queries (National Freshmen Pool, 117 Tiger year, etc.)
    if any(k in q for k in ["少子化", "18歲", "大專新生", "全國新生", "新生人數", "生源縮減", "縮減差額", "虎年"]):
        return {
            "intent": "DEMOGRAPHIC_QUERY",
            "confidence": 0.95,
            "params": {"target_year": 117 if "117" in q else 113}
        }

    # 4. Check for District / Spatial Queries
    matched_district = None
    sorted_districts = sorted(TAICHUNG_DISTRICTS, key=lambda x: len(x), reverse=True)
    for d in sorted_districts:
        if d in q or (len(d) >= 3 and d[:-1] in q):
            matched_district = d
            break
            
    if matched_district and any(k in q for k in ["區", "聚落", "分布", "家數", "活動", "空間", "地圖", "動能", "存量", "新設"]):
        return {
            "intent": "DISTRICT_QUERY",
            "confidence": 0.95,
            "params": {"district": matched_district}
        }

    # 5. Check for Mismatch & Warning queries
    if any(k in q for k in ["錯配", "預警", "警示", "失衡", "短缺風險", "過剩壓力", "象限", "強度"]):
        matched_ind = None
        for ind_id, ind_info in TARGET_INDUSTRIES.items():
            if ind_info["name"] in q or ind_id in q or any(k in q for k in ind_info["name"].split("與")):
                matched_ind = ind_id
                break
        return {
            "intent": "MISMATCH_QUERY",
            "confidence": 0.95,
            "params": {"industry_id": matched_ind or ""}
        }

    # 6. Check for Talent Supply Queries
    if any(k in q for k in ["人才供給", "供給動能", "培育量", "供給推估", "ucan", "就業途徑", "供給成長率"]):
        matched_ind = None
        for ind_id, ind_info in TARGET_INDUSTRIES.items():
            if ind_info["name"] in q or ind_id in q:
                matched_ind = ind_id
                break
        return {
            "intent": "SUPPLY_QUERY",
            "confidence": 0.90,
            "params": {"industry_id": matched_ind or ""}
        }

    # 7. Check for Industry Dynamics / Momentum Queries
    if any(k in q for k in ["新設公司率", "新設率", "新設公司", "增資率", "資本擴張率", "解散率", "歇業解散", "產業動能", "擴張動能", "資本擴張"]):
        matched_ind = None
        for ind_id, ind_info in TARGET_INDUSTRIES.items():
            if ind_info["name"] in q or ind_id in q:
                matched_ind = ind_id
                break
        return {
            "intent": "INDUSTRY_QUERY",
            "confidence": 0.90,
            "params": {"industry_id": matched_ind or ""}
        }

    # Generic Department query fallback
    if any(k in q for k in ["系", "系所", "註冊率", "在學學生", "學生數", "招生"]):
        return {
            "intent": "DEPARTMENT_QUERY",
            "confidence": 0.85,
            "params": {"query_term": q}
        }

    # Default fallback
    return {
        "intent": "MISMATCH_QUERY",
        "confidence": 0.70,
        "params": {"industry_id": ""}
    }
