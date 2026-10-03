"""
AI Agent Service: End-to-End Orchestrator (System Spec Section 24, 25, 26, 27)
Coordinates:
- Agent 01: Scope Guard
- Agent 02: Intent Router
- Agent 03: Deterministic Tool Router
- Agent 04: Explanation Generator
- Agent 05: Numeric Verification Engine
"""
import sys
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent.jev_model import jev_model
from agent.scope_guard import check_scope
from agent.intent_router import route_intent
from agent.tool_router import execute_tool
from agent.explanation_gen import generate_explanation
from agent.numeric_verifier import verify_explanation_numbers

class EarlyWarningAgentService:
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Processes user natural language request through the full deterministic guardrail pipeline.
        """
        q = (user_query or "").strip()

        # Step 0: Jev Model System-1 Decision (Validity & Correctness Check)
        jev_decision = jev_model.evaluate(q)
        if not jev_decision["is_valid_query"]:
            return {
                "query": q,
                "status": "REJECTED_BY_JEV",
                "answer": f"【Jev 決策模型判定：未通過有效性審核】\n{jev_decision['reason']}\n\n💡 建議您可以探索以下合規主題：\n1. 「台中市哪一個產業出現最高等級的人才供給不足預警？」\n2. 「智慧製造與精密機械的供需過剩壓力為何？」\n3. 「請查證統編 22099131 的公司登記現況」\n4. 「117學年度少子化對全國新生人數的衝擊推估是多少？」\n5. 「西屯區在113年度的企業存量與新設動能如何？」",
                "intent": "REJECTED_BY_JEV",
                "tool": "none",
                "jev_decision": jev_decision,
                "structured_data": {},
                "evidence": {
                    "source": ["Jev-1 System-1 決策元件 (TypeSafe AI)", "系統範疇安全守門員"],
                    "verification_status": "REJECTED_BY_JEV"
                },
                "verification": {
                    "status": "REJECTED",
                    "accuracy_pct": 0.0,
                    "audit_details": [f"Jev 判定拒絕：{jev_decision['reason']} (置信度 {jev_decision['confidence']})"]
                }
            }

        # Step 1: Agent 01 Scope Guard
        in_scope, scope_info = check_scope(q)
        if not in_scope:
            return {
                "query": q,
                "status": "OUT_OF_SCOPE",
                "answer": scope_info["message"],
                "intent": "OUT_OF_SCOPE",
                "tool": "none",
                "jev_decision": jev_decision,
                "structured_data": {},
                "evidence": {
                    "source": ["系統範疇安全守門員（Scope Guard）"],
                    "verification_status": "REJECTED_OUT_OF_SCOPE"
                },
                "verification": {
                    "status": "FAILED",
                    "accuracy_pct": 0.0,
                    "audit_details": ["提問超出系統分析範疇"]
                }
            }

        # Step 2: Agent 02 Intent Router
        routed = route_intent(q)
        intent = routed["intent"]
        params = routed["params"]

        # Step 3: Agent 03 Deterministic Tool Router
        tool_res = execute_tool(intent, params)
        tool_name = tool_res["tool"]
        structured_data = tool_res["data"]
        evidence = tool_res["evidence"]

        # Step 4: Agent 04 Explanation Generator
        explanation = generate_explanation(intent, tool_res)

        # Step 5: Agent 05 Numeric Verification Engine
        verification = verify_explanation_numbers(explanation, structured_data)

        # Update evidence with verification status
        evidence["verification_status"] = verification["status"]

        return {
            "query": q,
            "status": "SUCCESS",
            "intent": intent,
            "tool": tool_name,
            "answer": explanation,
            "jev_decision": jev_decision,
            "structured_data": structured_data,
            "evidence": evidence,
            "verification": verification
        }

agent_service = EarlyWarningAgentService()

if __name__ == "__main__":
    queries = [
        "台中市哪一個產業出現最高等級的人才供給不足預警？",
        "請查證統編 22099131 的公司登記現況",
        "西屯區的企業存量與新設動能如何？",
        "117學年度少子化對全國新生人數的衝擊推估是多少？",
        "今天天氣如何？" # Out of scope
    ]
    for q in queries:
        print("="*60)
        print("Q:", q)
        res = agent_service.process_query(q)
        print("Status:", res["status"], "| Intent:", res["intent"], "| Verification:", res["verification"]["status"])
        print("A:\n", res["answer"])
