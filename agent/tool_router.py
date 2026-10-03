"""
AI Agent Module 03: Deterministic Tool Router (System Spec Section 24)
Directly calls deterministic engine functions without LLM computation.
Returns structured JSON data along with audit evidence.
"""
import sys
import json
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.db_manager import db
from engine.industry_momentum import get_industry_momentum
from engine.talent_supply import get_talent_supply, get_department_projection
from engine.mismatch_engine import get_mismatch_signal
from engine.gcis_live_verifier import verify_company_live
from engine.evidence_engine import build_evidence_object

def get_district_industry(district: str = "西屯區", year: int = 113) -> Dict[str, Any]:
    """
    Returns district-level demand-side metrics strictly (Section 23).
    No district-level talent shortage percentages!
    """
    sql = """
        SELECT 
            year, district, industry_id,
            opening_count, dissolution_count, capital_increase_count,
            beginning_stock, ending_stock,
            entry_rate, capital_expansion_rate, exit_rate
        FROM industry_dynamics_mart
        WHERE district = ? AND year = ?
        ORDER BY ending_stock DESC
    """
    rows = db.fetch_all(sql, (district, year))
    
    total_stock = sum(r["ending_stock"] for r in rows)
    total_openings = sum(r["opening_count"] for r in rows)
    total_cap_inc = sum(r["capital_increase_count"] for r in rows)
    
    return {
        "district": district,
        "year": year,
        "total_ending_stock": total_stock,
        "total_openings": total_openings,
        "total_capital_increases": total_cap_inc,
        "industries": rows,
        "evidence": build_evidence_object(
            intent="DISTRICT_QUERY",
            indicator_name=f"{district}需求端企業動態",
            calculation_steps=[
                f"Sum(ending_stock) in {district} for year {year} = {total_stock}",
                f"Sum(opening_count) in {district} for year {year} = {total_openings}"
            ],
            source_tables=["industry_dynamics_mart"],
            official_sources=["經濟部商工行政資料開放平臺公司登記批次資料"],
            geography=f"台中市{district}"
        )
    }

def get_demographics_data(target_year: int = 117) -> Dict[str, Any]:
    """Returns demographic cohort data to target academic year"""
    rows = db.fetch_all("SELECT * FROM demographics_projection ORDER BY academic_year")
    y113 = db.fetch_one("SELECT * FROM demographics_projection WHERE academic_year = 113")
    y117 = db.fetch_one("SELECT * FROM demographics_projection WHERE academic_year = 117")
    
    diff_freshmen = y117["national_freshmen_estimate"] - y113["national_freshmen_estimate"]
    pct_freshmen = round(diff_freshmen / y113["national_freshmen_estimate"] * 100, 2)
    
    return {
        "academic_year": target_year,
        "history": rows,
        "freshmen_113": y113["national_freshmen_estimate"],
        "freshmen_117": y117["national_freshmen_estimate"],
        "difference_freshmen": diff_freshmen,
        "contraction_rate_pct": pct_freshmen,
        "evidence": build_evidence_object(
            intent="DEMOGRAPHIC_QUERY",
            indicator_name="少子化高教入學生源衝擊推估",
            calculation_steps=[
                f"113學年度大專新生人數 = {y113['national_freshmen_estimate']:,} 人",
                f"117學年度大專新生人數 = {y117['national_freshmen_estimate']:,} 人",
                f"生源縮減差額 = {diff_freshmen:,} 人 ({pct_freshmen}%)"
            ],
            source_tables=["demographics_projection"],
            official_sources=["內政部戶政司人口統計", "教育部統計處大專校院學生推估報告"]
        )
    }

def execute_tool(intent: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic Tool Router entry point.
    """
    if intent == "COMPANY_VERIFY":
        q = params.get("tax_id") or params.get("query_term", "")
        res = verify_company_live(q)
        evidence = build_evidence_object(
            intent="COMPANY_VERIFY",
            indicator_name="企業統編與商工登記真偽驗證",
            calculation_steps=["透過經濟部商工行政資料平臺API與本地核准設立基準檔直接比對"],
            source_tables=["companies"],
            official_sources=["經濟部商工行政資料開放平臺 API (Company_Status / Business_Accounting_NO)"],
            verification_status="VERIFIED" if res.get("verified") else "FAILED"
        )
        return {"tool": "verify_company", "data": res, "evidence": evidence}

    elif intent == "MISMATCH_QUERY":
        ind_id = params.get("industry_id", "")
        rows = get_mismatch_signal(ind_id)
        evidence = json.loads(rows[0]["evidence_json"]) if rows else {}
        return {"tool": "get_mismatch_signal", "data": rows, "evidence": evidence}

    elif intent == "INDUSTRY_QUERY":
        ind_id = params.get("industry_id", "")
        rows = get_industry_momentum(ind_id)
        evidence = build_evidence_object(
            intent="INDUSTRY_QUERY",
            indicator_name="產業擴張動能指標 (Demand Momentum)",
            calculation_steps=[
                "DemandMomentum = 0.5 * Z_entry + 0.5 * Z_capital",
                "ExitRate 僅供風險參考，不計入擴張動能"
            ],
            source_tables=["industry_momentum_mart", "industry_dynamics_mart"],
            official_sources=["經濟部商工行政資料開放平臺（GCIS）公司登記歷史母體"]
        )
        return {"tool": "get_industry_momentum", "data": rows, "evidence": evidence}

    elif intent == "SUPPLY_QUERY":
        ind_id = params.get("industry_id", "")
        rows = get_talent_supply(ind_id)
        evidence = build_evidence_object(
            intent="SUPPLY_QUERY",
            indicator_name="高教人才供給動能指標 (Supply Momentum)",
            calculation_steps=[
                "IndustrySupply = Sum(ProjectedStudents(d) * NormalizedWeight(d, i))",
                "SupplyGrowth = ProjectedSupply(117) / CurrentSupply(113) - 1",
                "SupplyMomentum = Standardize(SupplyGrowth)"
            ],
            source_tables=["talent_supply_mart", "ucan_mapping_mart", "department_indicators_mart"],
            official_sources=["教育部 UDB 校務資訊公開平臺", "教育部 UCAN 職涯架構對照表"]
        )
        return {"tool": "get_industry_supply", "data": rows, "evidence": evidence}

    elif intent == "DISTRICT_QUERY":
        dist = params.get("district", "西屯區")
        res = get_district_industry(dist, 113)
        return {"tool": "get_district_industry", "data": res, "evidence": res["evidence"]}

    elif intent == "DEMOGRAPHIC_QUERY":
        res = get_demographics_data(117)
        return {"tool": "get_demographic_projection", "data": res, "evidence": res["evidence"]}

    elif intent == "DEPARTMENT_QUERY":
        dept_name = params.get("department_name", "")
        inst_name = params.get("institution_name", "")
        q_term = params.get("query_term", "")
        
        rows = []
        if dept_name:
            rows = get_department_projection(dept_name=dept_name, inst_name=inst_name)
        elif q_term:
            rows = get_department_projection(dept_name=q_term)
            
        if not rows:
            rows = db.fetch_all("SELECT * FROM department_indicators_mart WHERE academic_year = 113 LIMIT 15")
            
        evidence = build_evidence_object(
            intent="DEPARTMENT_QUERY",
            indicator_name="系所生源、註冊率與117學年度供給推估",
            calculation_steps=[
                "ProjectedStudents(d, 117) = Age18Factor * ShareTrend * RegTrend * CurrentStudents",
                "禁止假設所有系所同比例下降 (Section 13)"
            ],
            source_tables=["department_indicators_mart"],
            official_sources=["教育部大專校院校務資訊公開平台（UDB）學生數與註冊率報表"]
        )
        return {"tool": "get_department_projection", "data": rows, "evidence": evidence}

    # Fallback
    rows = get_mismatch_signal()
    return {"tool": "get_mismatch_signal", "data": rows, "evidence": json.loads(rows[0]["evidence_json"]) if rows else {}}
