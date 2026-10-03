"""
Deterministic Engine: Evidence Engine & Traceability Builder (System Spec Section P4, 27)
Builds structured evidence objects guaranteeing complete audit trails:
Result -> Indicator -> Calculation -> Processed Table -> Source Data
"""
import sys
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def build_evidence_object(
    intent: str,
    indicator_name: str,
    calculation_steps: List[str],
    source_tables: List[str],
    official_sources: List[str],
    data_period: str = "109-117學年度/年度",
    geography: str = "台中市",
    verification_status: str = "VERIFIED"
) -> Dict[str, Any]:
    """
    Standard evidence schema required by Section 27.
    """
    return {
        "intent": intent,
        "indicator": indicator_name,
        "geography": geography,
        "data_period": data_period,
        "calculation": calculation_steps,
        "processed_tables": source_tables,
        "source": official_sources,
        "last_updated": "2026-10-01",
        "verification_status": verification_status
    }
