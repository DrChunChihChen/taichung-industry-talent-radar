"""
系統全局配置與常數定義
區域產業 × 高教人才供需錯配預警系統 (System Specification v1.0)
"""
import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MARTS_DATA_DIR = DATA_DIR / "marts"
DB_PATH = BASE_DIR / "database" / "mismatch_system.db"
BENCHMARK_DIR = BASE_DIR / "benchmark"
REPORT_DIR = BASE_DIR / "reports"

os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
os.makedirs(MARTS_DATA_DIR, exist_ok=True)
os.makedirs(BASE_DIR / "database", exist_ok=True)
os.makedirs(BENCHMARK_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# Target Projection Year
BASE_ACADEMIC_YEAR = 113
TARGET_PROJECTION_YEAR = 117
HISTORICAL_YEARS = [109, 110, 111, 112, 113]

# Target Geography
TARGET_CITY = "台中市"
TAICHUNG_DISTRICTS = [
    "中區", "東區", "南區", "西區", "北區", "西屯區", "南屯區", "北屯區",
    "豐原區", "東勢區", "大甲區", "清水區", "沙鹿區", "梧棲區", "后里區",
    "神岡區", "潭子區", "大雅區", "新社區", "石岡區", "外埔區", "大安區",
    "烏日區", "大肚區", "龍井區", "霧峰區", "太平區", "大里區", "和平區"
]

# 6-8 Target Industries (MVP uses 7 representative industries)
TARGET_INDUSTRIES = {
    "IND_MFG": {
        "id": "IND_MFG",
        "name": "智慧製造與精密機械",
        "en_name": "Smart Manufacturing & Precision Machinery",
        "description": "涵蓋數控工具機、自動化設備、機器人、航太零件與精密金屬組件製造。",
        "color": "#3B82F6",  # Blue
        "business_codes": ["CA02010", "CB01010", "CB01990", "CC01080", "CD01030", "F113010", "F213080"]
    },
    "IND_ICT": {
        "id": "IND_ICT",
        "name": "資訊軟體與數位科技",
        "en_name": "Information Software & Digital Tech",
        "description": "涵蓋軟體設計、雲端運算、人工智慧開發、SaaS 與資通訊系統整合服務。",
        "color": "#8B5CF6",  # Purple
        "business_codes": ["I301010", "I301020", "I301030", "I501010", "IZ13010"]
    },
    "IND_SEM": {
        "id": "IND_SEM",
        "name": "半導體與綠能科技",
        "en_name": "Semiconductor & Green Energy",
        "description": "涵蓋晶圓製造週邊、封測組裝、綠能發電工程、儲能與光電科技供應鏈。",
        "color": "#10B981",  # Emerald
        "business_codes": ["CC01110", "CC01120", "D101060", "E601010", "IG03010"]
    },
    "IND_BIOMED": {
        "id": "IND_BIOMED",
        "name": "生技醫療與精準健康",
        "en_name": "Biomedical & Healthcare",
        "description": "涵蓋高階醫療器材、智慧輔具、製藥研發、生技檢驗與數位健康照護。",
        "color": "#EC4899",  # Pink
        "business_codes": ["CF01010", "C802040", "F108031", "F208031", "IG01010", "IZ09010"]
    },
    "IND_PRO_FIN": {
        "id": "IND_PRO_FIN",
        "name": "專業商管與金融服務",
        "en_name": "Professional Business & Financial Services",
        "description": "涵蓋會計審計、財務顧問、企業經營管理顧問、法律科技與數據行銷。",
        "color": "#F59E0B",  # Amber
        "business_codes": ["I102010", "I103010", "IZ12010", "I401010", "H701010"]
    },
    "IND_TRADE_LOG": {
        "id": "IND_TRADE_LOG",
        "name": "國際貿易與現代物流",
        "en_name": "International Trade & Modern Logistics",
        "description": "涵蓋進出口跨境貿易、台中港海運承攬、智慧倉儲與冷鏈供應鏈管理。",
        "color": "#06B6D4",  # Cyan
        "business_codes": ["F401010", "G801010", "G101010", "G201010", "F101040"]
    },
    "IND_TOUR_CULT": {
        "id": "IND_TOUR_CULT",
        "name": "數位文創與觀光休閒",
        "en_name": "Digital Culture & Tourism Leisure",
        "description": "涵蓋數位多媒體娛樂、IP 授權開發、會展觀光與高附加價值生活休閒體驗。",
        "color": "#F97316",  # Orange
        "business_codes": ["J503010", "J701010", "J901010", "J601010", "IZ15010"]
    }
}

# UCAN Framework Clusters
UCAN_CLUSTERS = {
    "UC_IT": "資訊科技",
    "UC_MFG": "製造",
    "UC_MGMT": "企業經營管理",
    "UC_FIN": "金融保險",
    "UC_HEALTH": "醫療保健",
    "UC_TRANS": "運輸、物流與配銷",
    "UC_ARTS": "藝文、影音傳播與藝術",
    "UC_MKT": "行銷與銷售",
    "UC_STEM": "科學、科技、工程與數學",
    "UC_TOUR": "休閒與觀光旅遊"
}

# System Weights & Thresholds
DEMAND_MOMENTUM_WEIGHTS = {
    "entry": 0.5,
    "capital": 0.5
}

MAPPING_TYPE_WEIGHTS = {
    "PRIMARY": 1.0,
    "SECONDARY": 0.5
}

WARNING_THRESHOLDS = {
    "HIGH": 1.0,
    "MEDIUM": 0.5,
    "LOW": 0.0
}
