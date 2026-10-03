"""
AI Agent Module 01: Scope Guard (System Spec Section 24)
Validates whether the user's question belongs to:
- 招生 (Admission / Enrollment)
- 人口 (Demographics / Age 18 Population / Fertility)
- 系所 (University Departments / Curricula)
- 產業 (Industry Dynamics / Momentum)
- 企業 (Company Registration / Tax ID / Capital)
- 人才供給 (Talent Supply / Projections / UCAN)
- 錯配 (Mismatch Signals / Warning Levels)

If outside scope -> Returns OUT_OF_SCOPE with helpful explanation.
"""
import re
from typing import Dict, Any, Tuple

IN_SCOPE_KEYWORDS = [
    # 招生 / 系所
    "招生", "新生", "註冊率", "在學", "系所", "學系", "學校", "中科", "大專", "學生數", "學年度",
    "逢甲", "中興", "勤益", "東海", "靜宜", "亞洲", "朝陽", "弘光", "中臺", "嶺東", "僑光", "商管",
    "工學院", "資工", "機械", "國貿", "企管", "生醫", "財金", "多媒體",
    # 人口 / 生源
    "人口", "少子化", "18歲", "117", "虎年", "生源", "新生推估", "出生",
    # 產業 / 動能
    "產業", "擴張", "動能", "新設", "設立", "設立率", "資本", "增資", "解散", "歇業", "家數", "存量",
    "精密機械", "智慧製造", "資訊軟體", "數位科技", "半導體", "綠能", "生技醫療", "金融服務", "國際貿易", "現代物流", "文創",
    # 行政區 / 空間
    "行政區", "西屯", "南屯", "北屯", "潭子", "大雅", "豐原", "梧棲", "烏日", "大里", "太平", "台中",
    # 企業 / 統編
    "公司", "統編", "企業", "資本額", "核准設立", "登記", "台積電", "友達", "大立光", "上銀",
    # 人才供給 / UCAN
    "人才", "供給", "推估", "ucan", "職涯", "就業途徑", "培育", "稀釋", "權重",
    # 錯配 / 預警
    "錯配", "預警", "缺工", "短缺", "過剩", "失衡", "信號", "強度", "風險", "燈號"
]

def check_scope(query: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Checks whether a query is within the domain scope.
    """
    q = (query or "").strip().lower()
    if not q:
        return False, {
            "status": "OUT_OF_SCOPE",
            "message": "請輸入與台中市產業動能、高教人才供給、少子化生源或供需錯配預警相關的問題。"
        }
    
    # Check if query matches in-scope keywords
    matched = any(k in q for k in IN_SCOPE_KEYWORDS)
    if not matched:
        return False, {
            "status": "OUT_OF_SCOPE",
            "message": "提問超出本預警系統範圍。本系統專注於「台中市區域產業動能 × 高教人才供給結構性錯配預警」，請詢問產業動能、系所生源、117推估或統編核對。"
        }
        
    return True, {"status": "IN_SCOPE"}
