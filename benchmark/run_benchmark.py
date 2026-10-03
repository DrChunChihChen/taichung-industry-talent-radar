"""
Benchmark Generation & Validation Runner (System Spec Section 29 & 30)
Generates:
- benchmark/golden_questions.json (65+ benchmark questions with canonical golden answers)
Executes:
- Full evaluation testing 100% numeric accuracy against golden values.
"""
import sys
import json
import math
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import BENCHMARK_DIR, REPORT_DIR
from database.db_manager import db
from agent.agent_service import agent_service
from agent.numeric_verifier import extract_numbers_from_text

GOLDEN_QUESTIONS_FILE = BENCHMARK_DIR / "golden_questions.json"

def build_golden_questions() -> List[Dict[str, Any]]:
    # Fetch exact ground truth values from the database
    mom_rows = {r["industry_id"]: r for r in db.fetch_all("SELECT * FROM industry_momentum_mart")}
    sup_rows = {r["industry_id"]: r for r in db.fetch_all("SELECT * FROM talent_supply_mart")}
    mis_rows = {r["industry_id"]: r for r in db.fetch_all("SELECT * FROM mismatch_signal_mart")}
    dist_xitun = db.fetch_all("SELECT SUM(ending_stock) as s, SUM(opening_count) as o, SUM(capital_increase_count) as c FROM industry_dynamics_mart WHERE district='西屯區' AND year=113")[0]
    dist_nantun = db.fetch_all("SELECT SUM(ending_stock) as s, SUM(opening_count) as o, SUM(capital_increase_count) as c FROM industry_dynamics_mart WHERE district='南屯區' AND year=113")[0]
    dist_beitun = db.fetch_all("SELECT SUM(ending_stock) as s, SUM(opening_count) as o, SUM(capital_increase_count) as c FROM industry_dynamics_mart WHERE district='北屯區' AND year=113")[0]
    demo_117 = db.fetch_one("SELECT * FROM demographics_projection WHERE academic_year = 117")
    demo_113 = db.fetch_one("SELECT * FROM demographics_projection WHERE academic_year = 113")

    questions = [
        # --- 15 Required Specific Questions (Section 29) ---
        # 5 Industry Dynamics Questions
        {
            "question_id": "BM_IND_01",
            "category": "Industry Dynamics",
            "question": "請問台中市智慧製造與精密機械產業在113年的新設公司率（Entry Rate）為多少？",
            "intent": "INDUSTRY_QUERY",
            "expected_tool": "get_industry_momentum",
            "expected_value": round(mom_rows["IND_MFG"]["entry_rate"] * 100, 2),
            "expected_unit": "%",
            "expected_source": "GCIS_BATCH",
            "tolerance": 0.05
        },
        {
            "question_id": "BM_IND_02",
            "category": "Industry Dynamics",
            "question": "請問資訊軟體與數位科技產業在台中市的需求擴張動能主分數（Demand Momentum）是多少？",
            "intent": "INDUSTRY_QUERY",
            "expected_tool": "get_industry_momentum",
            "expected_value": mom_rows["IND_ICT"]["demand_momentum"],
            "expected_unit": "score",
            "expected_source": "GCIS_BATCH",
            "tolerance": 0.05
        },
        {
            "question_id": "BM_IND_03",
            "category": "Industry Dynamics",
            "question": "請問半導體與綠能科技產業在台中市113年的資本擴張率（Capital Rate）為多少？",
            "intent": "INDUSTRY_QUERY",
            "expected_tool": "get_industry_momentum",
            "expected_value": round(mom_rows["IND_SEM"]["capital_rate"] * 100, 2),
            "expected_unit": "%",
            "expected_source": "GCIS_BATCH",
            "tolerance": 0.05
        },
        {
            "question_id": "BM_IND_04",
            "category": "Industry Dynamics",
            "question": "請問生技醫療與精準健康產業在台中市的需求擴張動能（Demand Momentum）數值是多少？",
            "intent": "INDUSTRY_QUERY",
            "expected_tool": "get_industry_momentum",
            "expected_value": mom_rows["IND_BIOMED"]["demand_momentum"],
            "expected_unit": "score",
            "expected_source": "GCIS_BATCH",
            "tolerance": 0.05
        },
        {
            "question_id": "BM_IND_05",
            "category": "Industry Dynamics",
            "question": "請問國際貿易與現代物流產業113年的歇業解散率（Exit Rate，風險參考值）為多少？",
            "intent": "INDUSTRY_QUERY",
            "expected_tool": "get_industry_momentum",
            "expected_value": round(mom_rows["IND_TRADE_LOG"]["exit_rate"] * 100, 2),
            "expected_unit": "%",
            "expected_source": "GCIS_BATCH",
            "tolerance": 0.05
        },

        # 3 District Questions
        {
            "question_id": "BM_DIST_01",
            "category": "District Spatial",
            "question": "請問西屯區在113年度的登記企業總存量為多少家？",
            "intent": "DISTRICT_QUERY",
            "expected_tool": "get_district_industry",
            "expected_value": dist_xitun["s"],
            "expected_unit": "家",
            "expected_source": "GCIS_BATCH",
            "tolerance": 1.0
        },
        {
            "question_id": "BM_DIST_02",
            "category": "District Spatial",
            "question": "請問南屯區在113年度的新設公司總數為多少家？",
            "intent": "DISTRICT_QUERY",
            "expected_tool": "get_district_industry",
            "expected_value": dist_nantun["o"],
            "expected_unit": "家",
            "expected_source": "GCIS_BATCH",
            "tolerance": 1.0
        },
        {
            "question_id": "BM_DIST_03",
            "category": "District Spatial",
            "question": "請問北屯區在113年度的增資公司總數為多少家？",
            "intent": "DISTRICT_QUERY",
            "expected_tool": "get_district_industry",
            "expected_value": dist_beitun["c"],
            "expected_unit": "家",
            "expected_source": "GCIS_BATCH",
            "tolerance": 1.0
        },

        # 3 Supply Projection Questions
        {
            "question_id": "BM_SUP_01",
            "category": "Supply Projection",
            "question": "請問少子化衝擊下，117學年度全國大專新生預估人數是多少人？",
            "intent": "DEMOGRAPHIC_QUERY",
            "expected_tool": "get_demographic_projection",
            "expected_value": demo_117["national_freshmen_estimate"],
            "expected_unit": "人",
            "expected_source": "MOE_PROJECTION",
            "tolerance": 1.0
        },
        {
            "question_id": "BM_SUP_02",
            "category": "Supply Projection",
            "question": "請問113學年度至117學年度全國新生縮減差額預估為多少人？",
            "intent": "DEMOGRAPHIC_QUERY",
            "expected_tool": "get_demographic_projection",
            "expected_value": abs(demo_117["national_freshmen_estimate"] - demo_113["national_freshmen_estimate"]),
            "expected_unit": "人",
            "expected_source": "MOE_PROJECTION",
            "tolerance": 1.0
        },
        {
            "question_id": "BM_SUP_03",
            "category": "Supply Projection",
            "question": "請問資訊軟體與數位科技產業在117學年度的高教人才供給推估量是多少人？",
            "intent": "SUPPLY_QUERY",
            "expected_tool": "get_industry_supply",
            "expected_value": int(sup_rows["IND_ICT"]["projected_supply_117"]),
            "expected_unit": "人",
            "expected_source": "MOE_UDB_UCAN",
            "tolerance": 5.0
        },

        # 4 Mismatch Questions
        {
            "question_id": "BM_MIS_01",
            "category": "Mismatch Warning",
            "question": "請問智慧製造與精密機械產業的錯配強度數值（Mismatch）是多少？",
            "intent": "MISMATCH_QUERY",
            "expected_tool": "get_mismatch_signal",
            "expected_value": mis_rows["IND_MFG"]["mismatch"],
            "expected_unit": "score",
            "expected_source": "MISMATCH_ENGINE",
            "tolerance": 0.05
        },
        {
            "question_id": "BM_MIS_02",
            "category": "Mismatch Warning",
            "question": "請問資訊軟體與數位科技產業的供需錯配數值（Mismatch）是多少？",
            "intent": "MISMATCH_QUERY",
            "expected_tool": "get_mismatch_signal",
            "expected_value": mis_rows["IND_ICT"]["mismatch"],
            "expected_unit": "score",
            "expected_source": "MISMATCH_ENGINE",
            "tolerance": 0.05
        },
        {
            "question_id": "BM_MIS_03",
            "category": "Mismatch Warning",
            "question": "請問數位文創與觀光休閒產業的錯配數值（Mismatch）是多少？",
            "intent": "MISMATCH_QUERY",
            "expected_tool": "get_mismatch_signal",
            "expected_value": mis_rows["IND_TOUR_CULT"]["mismatch"],
            "expected_unit": "score",
            "expected_source": "MISMATCH_ENGINE",
            "tolerance": 0.05
        },
        {
            "question_id": "BM_MIS_04",
            "category": "Mismatch Warning",
            "question": "請問生技醫療與精準健康產業的錯配數值（Mismatch）是多少？",
            "intent": "MISMATCH_QUERY",
            "expected_tool": "get_mismatch_signal",
            "expected_value": mis_rows["IND_BIOMED"]["mismatch"],
            "expected_unit": "score",
            "expected_source": "MISMATCH_ENGINE",
            "tolerance": 0.05
        }
    ]

    # --- 50 Educational / Department / Employer Verification Questions ---
    # 10 Company Verification Questions
    flagships = db.fetch_all("SELECT company_id, company_name, capital FROM companies LIMIT 10")
    for idx, comp in enumerate(flagships):
        questions.append({
            "question_id": f"BM_COMP_{idx+1:02d}",
            "category": "Company Verification",
            "question": f"請核實統一編號 {comp['company_id']} 的登記公司名稱與狀態",
            "intent": "COMPANY_VERIFY",
            "expected_tool": "verify_company",
            "expected_value": float(comp["company_id"]),
            "expected_unit": "tax_id",
            "expected_source": "GCIS_API",
            "tolerance": 0.0
        })

    # 20 Department Enrolled Students & Registration Rate Questions
    sample_depts = db.fetch_all("SELECT institution_name, department_name, enrolled_students, registration_rate, projected_students_117 FROM department_indicators_mart WHERE academic_year = 113 LIMIT 20")
    for idx, dept in enumerate(sample_depts[:10]):
        questions.append({
            "question_id": f"BM_DEPT_STU_{idx+1:02d}",
            "category": "Department Student",
            "question": f"請問{dept['institution_name']}{dept['department_name']}在113學年度的在學學生數是多少人？",
            "intent": "DEPARTMENT_QUERY",
            "expected_tool": "get_department_projection",
            "expected_value": float(dept["enrolled_students"]),
            "expected_unit": "人",
            "expected_source": "MOE_UDB",
            "tolerance": 1.0
        })
    for idx, dept in enumerate(sample_depts[10:20]):
        questions.append({
            "question_id": f"BM_DEPT_REG_{idx+1:02d}",
            "category": "Department Registration",
            "question": f"請問{dept['institution_name']}{dept['department_name']}的新生註冊率是多少？",
            "intent": "DEPARTMENT_QUERY",
            "expected_tool": "get_department_projection",
            "expected_value": float(dept["registration_rate"]),
            "expected_unit": "%",
            "expected_source": "MOE_UDB",
            "tolerance": 0.1
        })

    # 10 Department 117 Projection Questions
    for idx, dept in enumerate(sample_depts[:10]):
        questions.append({
            "question_id": f"BM_DEPT_117_{idx+1:02d}",
            "category": "Department 117 Projection",
            "question": f"請問{dept['institution_name']}{dept['department_name']}至117學年度的推估生源是多少人？",
            "intent": "DEPARTMENT_QUERY",
            "expected_tool": "get_department_projection",
            "expected_value": float(dept["projected_students_117"]),
            "expected_unit": "人",
            "expected_source": "PROJECTION_ENGINE",
            "tolerance": 1.0
        })

    # 10 Additional District & Industry Questions
    more_dists = ["大雅區", "潭子區", "豐原區", "梧棲區", "烏日區", "大里區", "太平區", "西區", "北區", "南區"]
    for idx, dist_name in enumerate(more_dists):
        d_row = db.fetch_all("SELECT SUM(ending_stock) as s FROM industry_dynamics_mart WHERE district=? AND year=113", (dist_name,))[0]
        questions.append({
            "question_id": f"BM_EXTRA_DIST_{idx+1:02d}",
            "category": "District Spatial",
            "question": f"請問{dist_name}在113年度的企業總存量是多少家？",
            "intent": "DISTRICT_QUERY",
            "expected_tool": "get_district_industry",
            "expected_value": float(d_row["s"]),
            "expected_unit": "家",
            "expected_source": "GCIS_BATCH",
            "tolerance": 1.0
        })

    with open(GOLDEN_QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(questions)} Golden Benchmark Questions in {GOLDEN_QUESTIONS_FILE}")
    return questions

def run_benchmark_validation() -> Dict[str, Any]:
    print("="*60)
    print("Executing Section 30 Benchmark Validation Suite...")
    if not GOLDEN_QUESTIONS_FILE.exists():
        build_golden_questions()

    with open(GOLDEN_QUESTIONS_FILE, "r", encoding="utf-8") as f:
        golden_list = json.load(f)

    total_q = len(golden_list)
    passed_q = 0
    failed_q = 0
    eval_results = []

    for item in golden_list:
        qid = item["question_id"]
        q_text = item["question"]
        expected_intent = item["intent"]
        expected_val = float(item["expected_value"])
        tolerance = float(item["tolerance"])
        unit = item.get("expected_unit", "")

        # Process through full agent pipeline
        res = agent_service.process_query(q_text)
        ans_text = res["answer"]
        routed_intent = res["intent"]

        # Extract all numbers from generated answer
        extracted_nums = extract_numbers_from_text(ans_text)

        # Check numeric match against expected_val
        matched = False
        for num in extracted_nums:
            if abs(num - expected_val) <= tolerance or (expected_val != 0 and abs(num - expected_val) / abs(expected_val) <= 0.01):
                matched = True
                break

        intent_correct = (routed_intent == expected_intent)
        q_passed = matched and intent_correct

        if q_passed:
            passed_q += 1
            eval_status = "PASS"
        else:
            failed_q += 1
            eval_status = "FAIL"

        eval_results.append({
            "question_id": qid,
            "category": item["category"],
            "question": q_text,
            "expected_intent": expected_intent,
            "routed_intent": routed_intent,
            "expected_value": expected_val,
            "matched_in_answer": matched,
            "status": eval_status
        })

    accuracy_rate = round((passed_q / total_q) * 100.0, 2)
    print(f"Benchmark Run Complete: {passed_q}/{total_q} Passed ({accuracy_rate}%)")

    benchmark_report = {
        "timestamp": "2026-10-03T19:35:00",
        "total_questions": total_q,
        "passed": passed_q,
        "failed": failed_q,
        "accuracy_rate_pct": accuracy_rate,
        "results": eval_results
    }

    report_path = REPORT_DIR / "benchmark_accuracy_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(benchmark_report, f, ensure_ascii=False, indent=2)

    # Markdown benchmark report
    md_path = REPORT_DIR / "Benchmark_Validation_Report.md"
    md_lines = [
        "# Benchmark Validation Report (System Spec Section 29 & 30)",
        f"**Accuracy Rate**: **{accuracy_rate}%** ({passed_q}/{total_q} Passed)  ",
        f"**Target**: 100% Numeric Accuracy  \n",
        "| Question ID | Category | Question | Expected Intent | Actual Intent | Expected Value | Status |",
        "|:---:|:---|:---|:---:|:---:|:---:|:---:|"
    ]
    for r in eval_results:
        st = "✅ PASS" if r["status"] == "PASS" else "❌ FAIL"
        md_lines.append(f"| {r['question_id']} | {r['category']} | {r['question'][:30]}... | {r['expected_intent']} | {r['routed_intent']} | {r['expected_value']} | {st} |")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"Report saved to {report_path} and {md_path}")
    return benchmark_report

if __name__ == "__main__":
    build_golden_questions()
    run_benchmark_validation()
