"""
Full Pipeline Runner & Scheduler (System Spec Section 32)
Executes:
1. Download / Validate Raw Sources
2. Clean Companies & Parse Districts (Section 7)
3. Transform & Map Industries & UCAN Careers (Section 8, 15, 16)
4. Build Analytical Data Marts (Section 9, 12, 13, 14)
5. Calculate Deterministic Indicators (Industry Momentum, Talent Supply, Mismatch)
6. Run Data Quality Checks (Section 31)
7. Run Golden Benchmark Validation (Section 29, 30)
8. Publish & Ready for Production Serving
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.db_manager import db
from etl.map_industries import load_industry_rules
from etl.extract_demographics import load_demographics
from etl.extract_gcis_batch import generate_or_load_company_batch, build_industry_dynamics_mart
from etl.extract_moe_udb import extract_moe_udb_data
from engine.industry_momentum import calculate_industry_momentum
from engine.talent_supply import calculate_industry_talent_supply
from engine.mismatch_engine import calculate_mismatch_signals
from tests.test_etl_quality import run_data_quality_audit
from benchmark.run_benchmark import build_golden_questions, run_benchmark_validation

def run_pipeline():
    start_time = time.time()
    print("="*70)
    print("🚀 STARTING FULL PIPELINE: 區域產業 × 高教人才供需錯配預警系統 (v1.0)")
    print("="*70)

    # 1. Initialize Database
    print("\n[Step 1/8] Initializing Database Schema...")
    db.init_db()

    # 2. Load Industry Mapping Rules & Demographics
    print("\n[Step 2/8] Loading Fixed Industry Rules & MOI/MOE Demographics...")
    load_industry_rules()
    load_demographics()

    # 3. Clean Companies & Build Industry Dynamics Mart
    print("\n[Step 3/8] Processing GCIS Batch Data & Company Normalization...")
    generate_or_load_company_batch()
    build_industry_dynamics_mart()

    # 4. Extract MOE UDB & Build UCAN Mapping Mart
    print("\n[Step 4/8] Processing MOE UDB Data & UCAN Career Pathways...")
    extract_moe_udb_data()

    # 5. Deterministic Engines Execution
    print("\n[Step 5/8] Computing Deterministic Momentum & Talent Supply Engines...")
    calculate_industry_momentum(113)
    calculate_industry_talent_supply()
    calculate_mismatch_signals()

    # 6. Data Quality Audit (Section 31)
    print("\n[Step 6/8] Executing ETL Data Quality Test Suite...")
    dq_res = run_data_quality_audit()
    if not dq_res["all_passed"]:
        print("⚠️ Warning: Some Data Quality checks failed!")

    # 7. Benchmark Validation (Section 29 & 30)
    print("\n[Step 7/8] Executing Golden Benchmark 65+ Question Suite...")
    build_golden_questions()
    bm_res = run_benchmark_validation()

    # 8. Publish Summary
    elapsed = round(time.time() - start_time, 2)
    print("\n" + "="*70)
    print(f"🎉 PIPELINE COMPLETED SUCCESSFULLY in {elapsed} seconds!")
    print(f"• Data Quality Score: {dq_res['passed_checks']}/{dq_res['total_checks']} checks passed")
    print(f"• Benchmark Accuracy: {bm_res['passed']}/{bm_res['total_questions']} passed ({bm_res['accuracy_rate_pct']}%)")
    print("="*70)

if __name__ == "__main__":
    run_pipeline()
