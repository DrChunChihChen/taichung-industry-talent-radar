"""
ETL Module: UCAN Career Mapping Layer (System Spec Section 15, 16, 17, 18)
Principles:
- Department -> Career / Competency -> UCAN Career Pathway -> Target Industry
- Mapping Types: PRIMARY (weight = 1.0), SECONDARY (weight = 0.5)
- General Department Dilution: Normalized Weight = Raw Weight / sum(Raw Weights)
- Full evidence and source tracking for auditability
"""
import sys
import re
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import TARGET_INDUSTRIES, UCAN_CLUSTERS, PROCESSED_DATA_DIR, MARTS_DATA_DIR
from database.db_manager import db

# Base UCAN mapping taxonomy rules for discipline groups
UCAN_DISCIPLINE_TAXONOMY = [
    {
        "keywords": ["資訊工程", "軟體工程", "資訊科技", "人工智慧", "智慧運算", "數位多媒體", "計算機", "多媒體設計"],
        "primary": {
            "ucan_cluster_id": "UC_IT", "ucan_cluster_name": "資訊科技",
            "ucan_pathway_id": "UC_IT_PW01", "ucan_pathway_name": "軟體開發與系統整合",
            "industry_id": "IND_ICT", "industry_name": "資訊軟體與數位科技",
            "weight": 1.0,
            "evidence": "教育部UCAN職涯就業途徑對照表：資訊工程系所核心能力對應軟體開發與資通訊技術。",
            "source": "MOE_UCAN_OFFICIAL_2024"
        },
        "secondary": {
            "ucan_cluster_id": "UC_STEM", "ucan_cluster_name": "科學、科技、工程與數學",
            "ucan_pathway_id": "UC_STEM_PW02", "ucan_pathway_name": "半導體軟硬體整合",
            "industry_id": "IND_SEM", "industry_name": "半導體與綠能科技",
            "weight": 0.5,
            "evidence": "中科半導體供應鏈IC設計與韌體工程職缺對應資工系所就業途徑。",
            "source": "GCIS_104_EMPIRICAL_ALIGNMENT"
        }
    },
    {
        "keywords": ["機械工程", "機電工程", "自動化工程", "精密機械", "智慧製造", "動力機械", "模具", "工業工程"],
        "primary": {
            "ucan_cluster_id": "UC_MFG", "ucan_cluster_name": "製造",
            "ucan_pathway_id": "UC_MFG_PW01", "ucan_pathway_name": "機電自動化與機械設計",
            "industry_id": "IND_MFG", "industry_name": "智慧製造與精密機械",
            "weight": 1.0,
            "evidence": "教育部UCAN製造學門就業途徑：精密機械與工具機設備研發製造。",
            "source": "MOE_UCAN_OFFICIAL_2024"
        },
        "secondary": {
            "ucan_cluster_id": "UC_STEM", "ucan_cluster_name": "科學、科技、工程與數學",
            "ucan_pathway_id": "UC_STEM_PW01", "ucan_pathway_name": "半導體封裝與設備工程",
            "industry_id": "IND_SEM", "industry_name": "半導體與綠能科技",
            "weight": 0.5,
            "evidence": "中科園區半導體晶圓廠廠務與設備工程師招募管道。",
            "source": "GCIS_104_EMPIRICAL_ALIGNMENT"
        }
    },
    {
        "keywords": ["電機工程", "電子工程", "光電工程", "微電子", "半導體"],
        "primary": {
            "ucan_cluster_id": "UC_STEM", "ucan_cluster_name": "科學、科技、工程與數學",
            "ucan_pathway_id": "UC_STEM_PW01", "ucan_pathway_name": "半導體元件與光電工程",
            "industry_id": "IND_SEM", "industry_name": "半導體與綠能科技",
            "weight": 1.0,
            "evidence": "教育部UCAN職涯途徑：半導體晶圓製造與綠能光電工程開發。",
            "source": "MOE_UCAN_OFFICIAL_2024"
        },
        "secondary": {
            "ucan_cluster_id": "UC_MFG", "ucan_cluster_name": "製造",
            "ucan_pathway_id": "UC_MFG_PW02", "ucan_pathway_name": "智慧控制系統開發",
            "industry_id": "IND_MFG", "industry_name": "智慧製造與精密機械",
            "weight": 0.5,
            "evidence": "工業自動化控制器與智慧伺服馬達驅動電路研發。",
            "source": "MOE_UCAN_OFFICIAL_2024"
        }
    },
    {
        "keywords": ["國際貿易", "國際企業", "航運管理", "物流管理", "行銷與流通", "運輸與物流"],
        "primary": {
            "ucan_cluster_id": "UC_TRANS", "ucan_cluster_name": "運輸、物流與配銷",
            "ucan_pathway_id": "UC_TRANS_PW01", "ucan_pathway_name": "國際運籌與供應鏈管理",
            "industry_id": "IND_TRADE_LOG", "industry_name": "國際貿易與現代物流",
            "weight": 1.0,
            "evidence": "教育部UCAN途徑：台中港自由貿易港區、海運承攬與跨境電商貿易實務。",
            "source": "MOE_UCAN_OFFICIAL_2024"
        },
        "secondary": {
            "ucan_cluster_id": "UC_FIN", "ucan_cluster_name": "金融保險",
            "ucan_pathway_id": "UC_FIN_PW02", "ucan_pathway_name": "貿易融資與外匯風險管理",
            "industry_id": "IND_PRO_FIN", "industry_name": "專業商管與金融服務",
            "weight": 0.5,
            "evidence": "外銷企業信用狀、外幣避險與跨境金融投資顧問職務。",
            "source": "GCIS_104_EMPIRICAL_ALIGNMENT"
        }
    },
    {
        "keywords": ["會計", "財務金融", "金融科技", "財稅", "風險管理", "統計"],
        "primary": {
            "ucan_cluster_id": "UC_FIN", "ucan_cluster_name": "金融保險",
            "ucan_pathway_id": "UC_FIN_PW01", "ucan_pathway_name": "會計審計與專業財務顧問",
            "industry_id": "IND_PRO_FIN", "industry_name": "專業商管與金融服務",
            "weight": 1.0,
            "evidence": "教育部UCAN職涯途徑：會計師事務所審計查核、金融機構企業放款與財務分析。",
            "source": "MOE_UCAN_OFFICIAL_2024"
        },
        "secondary": {
            "ucan_cluster_id": "UC_TRANS", "ucan_cluster_name": "運輸、物流與配銷",
            "ucan_pathway_id": "UC_TRANS_PW02", "ucan_pathway_name": "國際貿易成本精算",
            "industry_id": "IND_TRADE_LOG", "industry_name": "國際貿易與現代物流",
            "weight": 0.5,
            "evidence": "跨國貿易保險、海關報關與保稅成本核算實證。",
            "source": "GCIS_104_EMPIRICAL_ALIGNMENT"
        }
    },
    {
        # General Department: 企業管理 (General Department Dilution rule per Section 18)
        "keywords": ["企業管理", "經營管理", "工商管理", "事業經營"],
        "dilution_mappings": [
            {
                "ucan_cluster_id": "UC_MGMT", "ucan_cluster_name": "企業經營管理",
                "ucan_pathway_id": "UC_MGMT_PW01", "ucan_pathway_name": "營運管理與決策分析",
                "industry_id": "IND_PRO_FIN", "industry_name": "專業商管與金融服務",
                "mapping_type": "PRIMARY", "weight": 1.0,
                "evidence": "企管系核心訓練：企業經營策略與管理顧問職位。",
                "source": "MOE_UCAN_OFFICIAL_2024"
            },
            {
                "ucan_cluster_id": "UC_TRANS", "ucan_cluster_name": "運輸、物流與配銷",
                "ucan_pathway_id": "UC_TRANS_PW01", "ucan_pathway_name": "供應鏈管理",
                "industry_id": "IND_TRADE_LOG", "industry_name": "國際貿易與現代物流",
                "mapping_type": "SECONDARY", "weight": 0.5,
                "evidence": "企管系流向：外銷製造業與物流供應鏈協調專員。",
                "source": "MOE_UCAN_OFFICIAL_2024"
            },
            {
                "ucan_cluster_id": "UC_MFG", "ucan_cluster_name": "製造",
                "ucan_pathway_id": "UC_MFG_PW03", "ucan_pathway_name": "製造業生管與品保",
                "industry_id": "IND_MFG", "industry_name": "智慧製造與精密機械",
                "mapping_type": "SECONDARY", "weight": 0.5,
                "evidence": "中彰投製造業生管、專案經理與行政管理人才流向。",
                "source": "GCIS_104_EMPIRICAL_ALIGNMENT"
            }
        ]
    },
    {
        "keywords": ["醫學", "護理", "醫事檢驗", "藥學", "生物科技", "生物醫學", "物理治療", "健康產業"],
        "primary": {
            "ucan_cluster_id": "UC_HEALTH", "ucan_cluster_name": "醫療保健",
            "ucan_pathway_id": "UC_HEALTH_PW01", "ucan_pathway_name": "生醫研發與健康照護",
            "industry_id": "IND_BIOMED", "industry_name": "生技醫療與精準健康",
            "weight": 1.0,
            "evidence": "教育部UCAN職涯途徑：臨床醫學、生技製藥檢驗與醫療儀器研發。",
            "source": "MOE_UCAN_OFFICIAL_2024"
        },
        "secondary": {
            "ucan_cluster_id": "UC_IT", "ucan_cluster_name": "資訊科技",
            "ucan_pathway_id": "UC_IT_PW03", "ucan_pathway_name": "智慧醫療資訊系統",
            "industry_id": "IND_ICT", "industry_name": "資訊軟體與數位科技",
            "weight": 0.5,
            "evidence": "智慧醫療、穿戴裝置生醫信號處理跨域就業途徑。",
            "source": "MOE_UCAN_OFFICIAL_2024"
        }
    },
    {
        "keywords": ["觀光", "餐旅", "休閒遊憩", "文創", "視覺傳達", "商業設計", "數位媒體設計", "產品設計"],
        "primary": {
            "ucan_cluster_id": "UC_TOUR", "ucan_cluster_name": "休閒與觀光旅遊",
            "ucan_pathway_id": "UC_TOUR_PW01", "ucan_pathway_name": "觀光餐旅與文創展演",
            "industry_id": "IND_TOUR_CULT", "industry_name": "數位文創與觀光休閒",
            "weight": 1.0,
            "evidence": "教育部UCAN職涯途徑：數位媒體設計、視覺行銷與文創會展休閒經營。",
            "source": "MOE_UCAN_OFFICIAL_2024"
        },
        "secondary": {
            "ucan_cluster_id": "UC_IT", "ucan_cluster_name": "資訊科技",
            "ucan_pathway_id": "UC_IT_PW02", "ucan_pathway_name": "UI/UX 人機互動設計",
            "industry_id": "IND_ICT", "industry_name": "資訊軟體與數位科技",
            "weight": 0.5,
            "evidence": "軟體科技業 UI/UX 視覺設計師與互動前端專長流向。",
            "source": "GCIS_104_EMPIRICAL_ALIGNMENT"
        }
    }
]

def map_department_to_ucan(dept_name: str, dept_id: str = "", inst_name: str = "", inst_id: str = "") -> List[Dict[str, Any]]:
    """
    Deterministically maps a department to UCAN Career Pathways and Target Industries.
    Implements General Department Dilution (Section 18).
    """
    clean_dept = dept_name.strip()
    records = []

    # Check for general department dilution match
    for tax in UCAN_DISCIPLINE_TAXONOMY:
        if "dilution_mappings" in tax:
            if any(k in clean_dept for k in tax["keywords"]):
                total_raw_weight = sum(m["weight"] for m in tax["dilution_mappings"])
                for m in tax["dilution_mappings"]:
                    norm_w = round(m["weight"] / total_raw_weight, 4)
                    records.append({
                        "department_id": dept_id or "DEP_GEN_BA",
                        "department_name": clean_dept,
                        "institution_id": inst_id,
                        "institution_name": inst_name,
                        "ucan_cluster_id": m["ucan_cluster_id"],
                        "ucan_cluster_name": m["ucan_cluster_name"],
                        "ucan_pathway_id": m["ucan_pathway_id"],
                        "ucan_pathway_name": m["ucan_pathway_name"],
                        "industry_id": m["industry_id"],
                        "industry_name": m["industry_name"],
                        "mapping_type": m["mapping_type"],
                        "weight": m["weight"],
                        "normalized_weight": norm_w,
                        "evidence": m["evidence"],
                        "source": m["source"],
                        "version": "v1.0"
                    })
                return records

    # Standard primary / secondary matching
    for tax in UCAN_DISCIPLINE_TAXONOMY:
        if "primary" in tax and any(k in clean_dept for k in tax["keywords"]):
            pri = tax["primary"]
            sec = tax.get("secondary")
            
            raw_weights = [pri["weight"]]
            if sec:
                raw_weights.append(sec["weight"])
            total_raw = sum(raw_weights)
            
            # Primary mapping
            records.append({
                "department_id": dept_id or f"DEP_{abs(hash(clean_dept))%1000000:06d}",
                "department_name": clean_dept,
                "institution_id": inst_id,
                "institution_name": inst_name,
                "ucan_cluster_id": pri["ucan_cluster_id"],
                "ucan_cluster_name": pri["ucan_cluster_name"],
                "ucan_pathway_id": pri["ucan_pathway_id"],
                "ucan_pathway_name": pri["ucan_pathway_name"],
                "industry_id": pri["industry_id"],
                "industry_name": pri["industry_name"],
                "mapping_type": "PRIMARY",
                "weight": pri["weight"],
                "normalized_weight": round(pri["weight"] / total_raw, 4),
                "evidence": pri["evidence"],
                "source": pri["source"],
                "version": "v1.0"
            })
            
            # Secondary mapping
            if sec:
                records.append({
                    "department_id": dept_id or f"DEP_{abs(hash(clean_dept))%1000000:06d}",
                    "department_name": clean_dept,
                    "institution_id": inst_id,
                    "institution_name": inst_name,
                    "ucan_cluster_id": sec["ucan_cluster_id"],
                    "ucan_cluster_name": sec["ucan_cluster_name"],
                    "ucan_pathway_id": sec["ucan_pathway_id"],
                    "ucan_pathway_name": sec["ucan_pathway_name"],
                    "industry_id": sec["industry_id"],
                    "industry_name": sec["industry_name"],
                    "mapping_type": "SECONDARY",
                    "weight": sec["weight"],
                    "normalized_weight": round(sec["weight"] / total_raw, 4),
                    "evidence": sec["evidence"],
                    "source": sec["source"],
                    "version": "v1.0"
                })
            return records

    # Fallback to general professional services
    records.append({
        "department_id": dept_id or "DEP_OTHER",
        "department_name": clean_dept,
        "institution_id": inst_id,
        "institution_name": inst_name,
        "ucan_cluster_id": "UC_MGMT",
        "ucan_cluster_name": "企業經營管理",
        "ucan_pathway_id": "UC_MGMT_PW01",
        "ucan_pathway_name": "綜合事務與專案支援",
        "industry_id": "IND_PRO_FIN",
        "industry_name": "專業商管與金融服務",
        "mapping_type": "PRIMARY",
        "weight": 1.0,
        "normalized_weight": 1.0,
        "evidence": "通識與人文社會系所轉入行政管理與企業綜合服務領域。",
        "source": "MOE_UCAN_DEFAULT_FALLBACK",
        "version": "v1.0"
    })
    return records

def build_all_ucan_mappings(dept_df: pd.DataFrame) -> pd.DataFrame:
    """Builds and stores UCAN Career Mapping table in SQLite and CSV."""
    all_mappings = []
    seen = set()

    for _, row in dept_df.iterrows():
        dept_name = str(row["department_name"]).strip()
        dept_id = str(row["department_id"]).strip()
        inst_name = str(row["institution_name"]).strip()
        inst_id = str(row["institution_id"]).strip()

        key = (inst_name, dept_name)
        if key in seen:
            continue
        seen.add(key)

        maps = map_department_to_ucan(dept_name, dept_id, inst_name, inst_id)
        all_mappings.extend(maps)

    df_ucan = pd.DataFrame(all_mappings)
    out_csv = MARTS_DATA_DIR / "dept_ucan_industry_mapping.csv"
    df_ucan.to_csv(out_csv, index=False, encoding="utf-8-sig")

    db.init_db()
    db.write_df(df_ucan, "ucan_mapping_mart", if_exists="replace")
    print(f"UCAN Mapping Mart built: {len(df_ucan)} records saved to {out_csv} and DB.")
    return df_ucan

if __name__ == "__main__":
    sample_depts = [
        {"department_id": "02112005", "department_name": "多媒體設計系", "institution_id": "0021", "institution_name": "國立臺中科技大學"},
        {"department_id": "04131016", "department_name": "企業管理學系", "institution_id": "0006", "institution_name": "國立中興大學"},
        {"department_id": "07141010", "department_name": "機械工程系", "institution_id": "0022", "institution_name": "國立勤益科技大學"},
        {"department_id": "04111015", "department_name": "國際貿易與經營系", "institution_id": "0021", "institution_name": "國立臺中科技大學"}
    ]
    df_sample = pd.DataFrame(sample_depts)
    build_all_ucan_mappings(df_sample)
