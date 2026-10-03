"""
ETL Module: Industry Classification Rules (System Spec Section 8)
Maps MOEA Business Item Codes (營業項目代碼) to 7 Target Industries.
Principles:
- P1: Deterministic First
- P3: LLM Does Not Classify (fixed mapping rules only)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from typing import Dict, Any, List
from config import TARGET_INDUSTRIES, PROCESSED_DATA_DIR
from database.db_manager import db

# Explicit business item code mappings according to Ministry of Economic Affairs standard classification
BUSINESS_CODE_MAPPINGS = [
    # IND_MFG: 智慧製造與精密機械
    {"business_code": "CA02010", "business_name": "金屬結構及建築組件製造業", "industry_id": "IND_MFG", "industry_name": "智慧製造與精密機械", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "CB01010", "business_name": "機械設備製造業", "industry_id": "IND_MFG", "industry_name": "智慧製造與精密機械", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "CB01020", "business_name": "事務機械設備製造業", "industry_id": "IND_MFG", "industry_name": "智慧製造與精密機械", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "CB01030", "business_name": "污染防治設備製造業", "industry_id": "IND_MFG", "industry_name": "智慧製造與精密機械", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "CB01990", "business_name": "其他機械製造業", "industry_id": "IND_MFG", "industry_name": "智慧製造與精密機械", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "CC01080", "business_name": "電子零組件製造業", "industry_id": "IND_MFG", "industry_name": "智慧製造與精密機械", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "CD01030", "business_name": "汽車及其零件製造業", "industry_id": "IND_MFG", "industry_name": "智慧製造與精密機械", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "CD01040", "business_name": "機車及其零件製造業", "industry_id": "IND_MFG", "industry_name": "智慧製造與精密機械", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "CD01060", "business_name": "航空器及其零件製造業", "industry_id": "IND_MFG", "industry_name": "智慧製造與精密機械", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "F113010", "business_name": "機械器具批發業", "industry_id": "IND_MFG", "industry_name": "智慧製造與精密機械", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "F213080", "business_name": "機械器具零售業", "industry_id": "IND_MFG", "industry_name": "智慧製造與精密機械", "mapping_rule": "EXACT_CODE", "version": "v1.0"},

    # IND_ICT: 資訊軟體與數位科技
    {"business_code": "I301010", "business_name": "資訊軟體服務業", "industry_id": "IND_ICT", "industry_name": "資訊軟體與數位科技", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "I301020", "business_name": "資料處理服務業", "industry_id": "IND_ICT", "industry_name": "資訊軟體與數位科技", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "I301030", "business_name": "電子資訊供應服務業", "industry_id": "IND_ICT", "industry_name": "資訊軟體與數位科技", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "IZ13010", "business_name": "網路認證服務業", "industry_id": "IND_ICT", "industry_name": "資訊軟體與數位科技", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "F118010", "business_name": "資訊軟體批發業", "industry_id": "IND_ICT", "industry_name": "資訊軟體與數位科技", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "F218010", "business_name": "資訊軟體零售業", "industry_id": "IND_ICT", "industry_name": "資訊軟體與數位科技", "mapping_rule": "EXACT_CODE", "version": "v1.0"},

    # IND_SEM: 半導體與綠能科技
    {"business_code": "CC01110", "business_name": "電腦及其週邊設備製造業", "industry_id": "IND_SEM", "industry_name": "半導體與綠能科技", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "CC01120", "business_name": "數據儲存及處理設備製造業", "industry_id": "IND_SEM", "industry_name": "半導體與綠能科技", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "D101060", "business_name": "再生能源自用發電設備業", "industry_id": "IND_SEM", "industry_name": "半導體與綠能科技", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "E601010", "business_name": "電器承裝業", "industry_id": "IND_SEM", "industry_name": "半導體與綠能科技", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "IG03010", "business_name": "能源技術服務業", "industry_id": "IND_SEM", "industry_name": "半導體與綠能科技", "mapping_rule": "EXACT_CODE", "version": "v1.0"},

    # IND_BIOMED: 生技醫療與精準健康
    {"business_code": "CF01010", "business_name": "醫療器材製造業", "industry_id": "IND_BIOMED", "industry_name": "生技醫療與精準健康", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "C802040", "business_name": "西藥製造業", "industry_id": "IND_BIOMED", "industry_name": "生技醫療與精準健康", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "F108031", "business_name": "醫療器材批發業", "industry_id": "IND_BIOMED", "industry_name": "生技醫療與精準健康", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "F208031", "business_name": "醫療器材零售業", "industry_id": "IND_BIOMED", "industry_name": "生技醫療與精準健康", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "IG01010", "business_name": "生物技術服務業", "industry_id": "IND_BIOMED", "industry_name": "生技醫療與精準健康", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "IZ09010", "business_name": "臨床試驗服務業", "industry_id": "IND_BIOMED", "industry_name": "生技醫療與精準健康", "mapping_rule": "EXACT_CODE", "version": "v1.0"},

    # IND_PRO_FIN: 專業商管與金融服務
    {"business_code": "I102010", "business_name": "投資顧問業", "industry_id": "IND_PRO_FIN", "industry_name": "專業商管與金融服務", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "I103010", "business_name": "企業管理顧問業", "industry_id": "IND_PRO_FIN", "industry_name": "專業商管與金融服務", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "IZ12010", "business_name": "人力派遣業", "industry_id": "IND_PRO_FIN", "industry_name": "專業商管與金融服務", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "I401010", "business_name": "一般廣告服務業", "industry_id": "IND_PRO_FIN", "industry_name": "專業商管與金融服務", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "H701010", "business_name": "租賃業", "industry_id": "IND_PRO_FIN", "industry_name": "專業商管與金融服務", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "I101010", "business_name": "投資商業及會計服務業", "industry_id": "IND_PRO_FIN", "industry_name": "專業商管與金融服務", "mapping_rule": "EXACT_CODE", "version": "v1.0"},

    # IND_TRADE_LOG: 國際貿易與現代物流
    {"business_code": "F401010", "business_name": "國際貿易業", "industry_id": "IND_TRADE_LOG", "industry_name": "國際貿易與現代物流", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "G801010", "business_name": "倉儲業", "industry_id": "IND_TRADE_LOG", "industry_name": "國際貿易與現代物流", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "G101010", "business_name": "汽車貨運業", "industry_id": "IND_TRADE_LOG", "industry_name": "國際貿易與現代物流", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "G201010", "business_name": "水上運輸業", "industry_id": "IND_TRADE_LOG", "industry_name": "國際貿易與現代物流", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "F101040", "business_name": "批發業", "industry_id": "IND_TRADE_LOG", "industry_name": "國際貿易與現代物流", "mapping_rule": "EXACT_CODE", "version": "v1.0"},

    # IND_TOUR_CULT: 數位文創與觀光休閒
    {"business_code": "J503010", "business_name": "廣播電視節目製作及發行業", "industry_id": "IND_TOUR_CULT", "industry_name": "數位文創與觀光休閒", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "I501010", "business_name": "產品設計業", "industry_id": "IND_TOUR_CULT", "industry_name": "數位文創與觀光休閒", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "J701010", "business_name": "電子遊戲場業", "industry_id": "IND_TOUR_CULT", "industry_name": "數位文創與觀光休閒", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "J901010", "business_name": "觀光旅館業", "industry_id": "IND_TOUR_CULT", "industry_name": "數位文創與觀光休閒", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "J601010", "business_name": "藝文展演服務業", "industry_id": "IND_TOUR_CULT", "industry_name": "數位文創與觀光休閒", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
    {"business_code": "IZ15010", "business_name": "會議及展覽服務業", "industry_id": "IND_TOUR_CULT", "industry_name": "數位文創與觀光休閒", "mapping_rule": "EXACT_CODE", "version": "v1.0"},
]

def load_industry_rules() -> pd.DataFrame:
    df = pd.DataFrame(BUSINESS_CODE_MAPPINGS)
    csv_path = PROCESSED_DATA_DIR / "industry_mapping_rules.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    
    # Write to DB
    db.init_db()
    db.write_df(df, "industry_mapping_rules", if_exists="replace")
    print(f"Loaded {len(df)} industry mapping rules into DB and {csv_path}")
    return df

def map_code_to_industry(business_code: str) -> Dict[str, Any]:
    """Deterministic lookup from business item code to target industry"""
    code = (business_code or "").strip().upper()
    for item in BUSINESS_CODE_MAPPINGS:
        if item["business_code"] == code:
            return {
                "matched": True,
                "industry_id": item["industry_id"],
                "industry_name": item["industry_name"],
                "business_name": item["business_name"]
            }
    # Prefix-based fallback rules
    if code.startswith("CB") or code.startswith("CA") or code.startswith("CD"):
        return {"matched": True, "industry_id": "IND_MFG", "industry_name": "智慧製造與精密機械", "business_name": "製造業相關代碼"}
    if code.startswith("I3"):
        return {"matched": True, "industry_id": "IND_ICT", "industry_name": "資訊軟體與數位科技", "business_name": "資訊服務相關代碼"}
    if code.startswith("CC") or code.startswith("D1"):
        return {"matched": True, "industry_id": "IND_SEM", "industry_name": "半導體與綠能科技", "business_name": "半導體綠能相關代碼"}
    if code.startswith("CF") or code.startswith("C8"):
        return {"matched": True, "industry_id": "IND_BIOMED", "industry_name": "生技醫療與精準健康", "business_name": "醫療生技相關代碼"}
    if code.startswith("I1") or code.startswith("H"):
        return {"matched": True, "industry_id": "IND_PRO_FIN", "industry_name": "專業商管與金融服務", "business_name": "金融顧問相關代碼"}
    if code.startswith("F4") or code.startswith("G"):
        return {"matched": True, "industry_id": "IND_TRADE_LOG", "industry_name": "國際貿易與現代物流", "business_name": "貿易物流相關代碼"}
    if code.startswith("J"):
        return {"matched": True, "industry_id": "IND_TOUR_CULT", "industry_name": "數位文創與觀光休閒", "business_name": "文創觀光相關代碼"}
    
    return {"matched": False, "industry_id": "UNKNOWN", "industry_name": "未對應產業", "business_name": "未對應項目"}

if __name__ == "__main__":
    load_industry_rules()
