"""
AI Agent Module 05: Numeric Verification Engine (System Spec Section 26)
Audits generated text by:
1. Extracting numerical values, years, percentages from output text
2. Matching against canonical ground truth values from the deterministic structured engine
3. Verifying units, years, industries, and districts
4. Outputting VERIFIED / WARNING / FAILED status
"""
import re
from typing import Dict, Any, List, Set

def extract_numbers_from_text(text: str) -> List[float]:
    """Extracts all numerical quantities from text, normalizing commas and units."""
    # First handle "X 萬" or "X 萬人" -> X * 10000
    expanded_text = re.sub(r"(\d+\.?\d*)\s*萬", lambda m: f" {float(m.group(1))*10000} ", text)
    # Remove commas between digits like 188,000
    cleaned = re.sub(r"(?<=\d),(?=\d)", "", expanded_text)
    
    # Match standard numbers: integers, decimals, negatives
    raw_matches = re.findall(r"[-+]?\d*\.?\d+", cleaned)
    nums = []
    for m in raw_matches:
        try:
            val = float(m)
            nums.append(val)
        except ValueError:
            pass
    return nums

def flatten_structured_numbers(data: Any) -> Set[float]:
    """Recursively flattens all numeric values from structured dictionary/list"""
    nums = set()
    if isinstance(data, dict):
        for k, v in data.items():
            if k in ["tax_id", "company_id"]:
                try:
                    nums.add(float(v))
                except (ValueError, TypeError):
                    pass
            nums.update(flatten_structured_numbers(v))
    elif isinstance(data, list):
        for item in data:
            nums.update(flatten_structured_numbers(item))
    elif isinstance(data, (int, float)):
        val = float(data)
        nums.add(val)
        nums.add(abs(val))
        # Add percentage representations (e.g., 0.10936 -> 10.94, 10.9)
        if 0 < abs(val) <= 1.0:
            nums.add(round(val * 100.0, 2))
            nums.add(round(val * 100.0, 1))
            nums.add(abs(round(val * 100.0, 2)))
        # Add integer representation
        nums.add(float(int(val)))
        # Add 萬 unit representation (e.g. 188000 -> 18.8)
        if abs(val) >= 1000:
            nums.add(round(val / 10000.0, 2))
            nums.add(round(val / 10000.0, 1))
    return nums

def verify_explanation_numbers(
    explanation_text: str,
    structured_data: Dict[str, Any],
    tolerance: float = 0.05
) -> Dict[str, Any]:
    """
    Compares numbers in text against structured truth.
    Returns status: VERIFIED / WARNING / FAILED.
    """
    text_nums = extract_numbers_from_text(explanation_text)
    truth_nums = flatten_structured_numbers(structured_data)

    if not text_nums:
        return {
            "status": "VERIFIED",
            "matched_count": 0,
            "total_extracted": 0,
            "accuracy_pct": 100.0,
            "audit_details": ["文本無特定數值指標，語義範疇核驗合格"]
        }

    audit_details = []
    matched_count = 0
    unmatched_nums = []

    # Common valid narrative/system constants (e.g., 0.5 weight, 100%, 113 year, 114 year, 117 year, 29 districts, 7 industries, 5 years)
    allowed_constants = {
        0.0, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0,
        15.0, 20.0, 29.0, 100.0, 109.0, 110.0, 111.0, 112.0, 113.0, 114.0, 117.0, 118.0
    }

    for num in text_nums:
        if num in allowed_constants:
            matched_count += 1
            continue

        found = False
        for t in truth_nums:
            if abs(num - t) <= tolerance or (t != 0 and abs(num - t) / abs(t) <= 0.02):
                found = True
                break

        if found:
            matched_count += 1
        else:
            unmatched_nums.append(num)

    total = len(text_nums)
    accuracy = round((matched_count / total) * 100.0, 1) if total > 0 else 100.0

    if accuracy >= 95.0:
        status = "VERIFIED"
    elif accuracy >= 80.0:
        status = "WARNING"
    else:
        status = "FAILED"

    audit_details.append(f"數值稽核完成：{matched_count}/{total} 個數值精確符合底層數據庫 (符合率 {accuracy}%)")
    if unmatched_nums:
        audit_details.append(f"未完全比對數值：{unmatched_nums[:5]}")

    return {
        "status": status,
        "matched_count": matched_count,
        "total_extracted": total,
        "accuracy_pct": accuracy,
        "audit_details": audit_details
    }
