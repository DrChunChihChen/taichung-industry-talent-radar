"""
Data Quality Test Suite (System Spec Section 31)
Verifies:
1. Duplicate company ID
2. Missing district
3. Unknown business code
4. Negative company stock
5. Impossible registration rate (< 0 or > 100)
6. Missing department mapping
7. Missing UCAN mapping
8. Industry supply = NULL

Generates ETL Quality Report (JSON and Markdown).
"""
import sys
import json
from pathlib import Path
from typing import Dict, Any, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import DB_PATH, REPORT_DIR, TARGET_INDUSTRIES, TAICHUNG_DISTRICTS
from database.db_manager import db

def run_data_quality_audit() -> Dict[str, Any]:
    print("Running Section 31 ETL Data Quality Tests...")
    report = {
        "timestamp": "2026-10-03T19:30:00",
        "total_checks": 8,
        "passed_checks": 0,
        "failed_checks": 0,
        "details": []
    }

    # Check 1: Duplicate company ID
    dup_row = db.fetch_one("SELECT company_id, COUNT(*) as c FROM companies GROUP BY company_id HAVING c > 1")
    passed_1 = dup_row is None
    report["details"].append({
        "check_id": "DQ_01",
        "name": "Duplicate Company ID",
        "status": "PASS" if passed_1 else "FAIL",
        "message": "無重複統編" if passed_1 else f"發現重複統編: {dup_row['company_id']}"
    })

    # Check 2: Missing district
    missing_dist = db.fetch_all("SELECT COUNT(*) as c FROM companies WHERE district IS NULL OR district = '' OR district = 'UNKNOWN'")
    cnt_dist = missing_dist[0]["c"]
    passed_2 = cnt_dist == 0
    report["details"].append({
        "check_id": "DQ_02",
        "name": "Missing or Unknown District in Companies",
        "status": "PASS" if passed_2 else "FAIL",
        "message": "全數公司行政區均有效對齊" if passed_2 else f"有 {cnt_dist} 家公司行政區缺失或為UNKNOWN"
    })

    # Check 3: Unknown business code
    unk_code = db.fetch_all("SELECT COUNT(*) as c FROM industry_mapping_rules WHERE industry_id = 'UNKNOWN'")
    cnt_code = unk_code[0]["c"]
    passed_3 = cnt_code == 0
    report["details"].append({
        "check_id": "DQ_03",
        "name": "Unknown Business Code Mapping",
        "status": "PASS" if passed_3 else "FAIL",
        "message": "營業代碼映射規則完整無空缺" if passed_3 else f"有 {cnt_code} 筆未對應項目"
    })

    # Check 4: Negative company stock in Dynamics Mart
    neg_stock = db.fetch_all("SELECT COUNT(*) as c FROM industry_dynamics_mart WHERE beginning_stock < 0 OR ending_stock < 0")
    cnt_neg = neg_stock[0]["c"]
    passed_4 = cnt_neg == 0
    report["details"].append({
        "check_id": "DQ_04",
        "name": "Negative Company Stock",
        "status": "PASS" if passed_4 else "FAIL",
        "message": "企業存量數值均非負數" if passed_4 else f"存在 {cnt_neg} 筆負數存量"
    })

    # Check 5: Impossible registration rate
    imp_reg = db.fetch_all("SELECT COUNT(*) as c FROM department_indicators_mart WHERE registration_rate < 0.0 OR registration_rate > 100.0")
    cnt_reg = imp_reg[0]["c"]
    passed_5 = cnt_reg == 0
    report["details"].append({
        "check_id": "DQ_05",
        "name": "Impossible Registration Rate (Range 0-100%)",
        "status": "PASS" if passed_5 else "FAIL",
        "message": "註冊率均介於 0% 至 100% 之間" if passed_5 else f"存在 {cnt_reg} 筆超常註冊率"
    })

    # Check 6: Missing department mapping
    missing_dept = db.fetch_all("""
        SELECT COUNT(DISTINCT d.department_name) as c 
        FROM department_indicators_mart d
        LEFT JOIN ucan_mapping_mart u ON d.department_name = u.department_name
        WHERE u.department_name IS NULL
    """)
    cnt_m_dept = missing_dept[0]["c"]
    passed_6 = cnt_m_dept == 0
    report["details"].append({
        "check_id": "DQ_06",
        "name": "Missing Department UCAN Mapping",
        "status": "PASS" if passed_6 else "FAIL",
        "message": "所有系所皆已映射至 UCAN 職涯途徑" if passed_6 else f"有 {cnt_m_dept} 個系所未映射"
    })

    # Check 7: Missing UCAN mapping weights
    null_weights = db.fetch_all("SELECT COUNT(*) as c FROM ucan_mapping_mart WHERE weight IS NULL OR normalized_weight IS NULL OR normalized_weight <= 0")
    cnt_w = null_weights[0]["c"]
    passed_7 = cnt_w == 0
    report["details"].append({
        "check_id": "DQ_07",
        "name": "Missing or Zero UCAN Mapping Weights",
        "status": "PASS" if passed_7 else "FAIL",
        "message": "UCAN 職涯權重與稀釋權重皆有效" if passed_7 else f"有 {cnt_w} 筆無效權重"
    })

    # Check 8: Industry supply = NULL or empty
    null_sup = db.fetch_all("SELECT COUNT(*) as c FROM talent_supply_mart WHERE current_supply IS NULL OR projected_supply_117 IS NULL OR current_supply <= 0")
    cnt_sup = null_sup[0]["c"]
    passed_8 = cnt_sup == 0
    report["details"].append({
        "check_id": "DQ_08",
        "name": "Industry Talent Supply Null/Empty",
        "status": "PASS" if passed_8 else "FAIL",
        "message": "7大目標產業人才供給池均完整推估" if passed_8 else f"有 {cnt_sup} 筆缺失"
    })

    passes = sum(1 for d in report["details"] if d["status"] == "PASS")
    fails = len(report["details"]) - passes
    report["passed_checks"] = passes
    report["failed_checks"] = fails
    report["all_passed"] = (fails == 0)

    # Save to report files
    out_json = REPORT_DIR / "etl_quality_report.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # Markdown report
    out_md = REPORT_DIR / "ETL_Quality_Report.md"
    lines = [
        "# ETL Data Quality Audit Report (System Spec Section 31)",
        f"**Audit Time**: {report['timestamp']}  ",
        f"**Result**: {'🟢 ALL PASS' if report['all_passed'] else '🔴 FAILED'} ({passes}/{len(report['details'])} Passed)\n",
        "| Check ID | Verification Item | Status | Details |",
        "|:---:|:---|:---:|:---|"
    ]
    for d in report["details"]:
        icon = "✅ PASS" if d["status"] == "PASS" else "❌ FAIL"
        lines.append(f"| {d['check_id']} | {d['name']} | {icon} | {d['message']} |")

    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"ETL Quality Report generated: {passes}/{len(report['details'])} checks passed!")
    print(f"Saved to {out_json} and {out_md}")
    return report

if __name__ == "__main__":
    run_data_quality_audit()
