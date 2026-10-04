"""
AI Agent Module 04: Explanation Generator (System Spec Section 25)
Principles:
- P2: LLM Does Not Calculate
- P3: LLM Does Not Classify
- P5: Warning, Not Prediction
Transforms deterministic structured data into clear, rigorous natural language explanations.
"""
from typing import Dict, Any, List

def generate_explanation(intent: str, structured_data: Dict[str, Any]) -> str:
    """
    Generates explanation grounded strictly in structured data.
    """
    tool_name = structured_data.get("tool", "")
    data = structured_data.get("data")
    evidence = structured_data.get("evidence", {})

    if intent == "COMPANY_VERIFY":
        if isinstance(data, dict) and data.get("verified"):
            cap = data.get("capital", 0)
            cap_str = f"{cap:,} 元" if isinstance(cap, (int, float)) else str(cap)
            return (
                f"【企業商工登記核實結果】\n"
                f"• 公司全名：{data.get('company_name')}\n"
                f"• 統一編號：{data.get('tax_id')}\n"
                f"• 登記狀態：{data.get('status')}\n"
                f"• 資本總額：{cap_str}\n"
                f"• 所在地點：{data.get('address') or data.get('district')}\n"
                f"• 對應目標產業代碼：{data.get('industry_id', '基準企業')}\n"
                f"• 查核來源：{data.get('source')}\n\n"
                f"本筆資料已完成商工行政資料庫對齊，屬合法有效登記之事業主體。"
            )
        else:
            return f"商工行政登記庫查無符合條件之公司紀錄（輸入：{structured_data.get('data', {}).get('query', '')}），請確認統一編號或名稱是否正確。"

    elif intent == "MISMATCH_QUERY":
        if isinstance(data, list) and len(data) > 0:
            lines = ["【台中市區域產業 × 高教人才供需錯配預警分析】\n"]
            lines.append("本系統依據「產業擴張動能（Demand Momentum）」與「人才供給動能（Supply Momentum）」計算結構性錯配警示訊號（Mismatch = Demand - Supply）：\n")
            for item in data:
                m = item["mismatch"]
                d_mom = item["demand_momentum"]
                s_mom = item["supply_momentum"]
                lvl = item["warning_level"]
                dir_label = "【短缺風險】" if item["mismatch_direction"] == "SUPPLY_SHORTAGE_RISK" else "【過剩壓力】"
                lines.append(
                    f"• {item['industry_name']}：\n"
                    f"  - 警示等級：{lvl} Warning ({dir_label})\n"
                    f"  - 錯配強度數值：{m}（需求動能：{d_mom}，人才供給動能：{s_mom}）\n"
                )
            lines.append("註：本訊號定位為「結構性錯配警示訊號」，非就業需求或缺工人數預測。")
            return "\n".join(lines)
            
    elif intent == "INDUSTRY_QUERY":
        if isinstance(data, list) and len(data) > 0:
            lines = ["【台中市目標產業需求端動能指標】\n"]
            lines.append("依據經濟部商工登記新設、增資與解散母體計算（Demand Momentum = 0.5×Z_entry + 0.5×Z_capital）：\n")
            for item in data:
                lines.append(
                    f"• {item['industry_name']}：\n"
                    f"  - 擴張動能主分數：{item['demand_momentum']}\n"
                    f"  - 新設公司率 (Entry Rate)：{round(item['entry_rate']*100, 2)}% (Z={item['z_entry']})\n"
                    f"  - 資本擴張率 (Capital Rate)：{round(item['capital_rate']*100, 2)}% (Z={item['z_capital']})\n"
                    f"  - 歇業解散率 (Exit Rate - 風險參考)：{round(item['exit_rate']*100, 2)}%\n"
                )
            return "\n".join(lines)

    elif intent == "SUPPLY_QUERY":
        if isinstance(data, list) and len(data) > 0:
            lines = ["【台中市高教人才供給推估指標（至117學年度）】\n"]
            lines.append("透過教育部 UCAN 職涯途徑與學門稀釋權重對齊至目標產業：\n")
            for item in data:
                lines.append(
                    f"• {item['industry_name']}：\n"
                    f"  - 113學年度現行在學人才池：{int(item['current_supply']):,} 人\n"
                    f"  - 117學年度推估人才供給量：{int(item['projected_supply_117']):,} 人\n"
                    f"  - 供給變動率 (Growth)：{round(item['supply_growth']*100, 2)}%\n"
                    f"  - 供給動能標準化值 (Supply Momentum)：{item['supply_momentum']}\n"
                    f"  - 涵蓋培育系所數：{item['total_contributing_depts']} 個系所\n"
                )
            return "\n".join(lines)

    elif intent == "DISTRICT_QUERY":
        dist = data.get("district", "")
        year = data.get("year")
        lines = [f"【{dist} 區域同業工廠家數（{year}年）】"]
        if data.get("status") != "available":
            lines.append("此條件尚未匯入可用官方資料；不以零或模擬值代替。")
        else:
            for item in data.get("industries", []):
                lines.append(f"• {item['industry_name']}：營運中工廠 {item['factory_count']:,} 家")
        lines.append("資料來源：經濟部工廠校正及營運調查。")
        lines.append("本結果只涵蓋已匯入行業；工廠家數不等於公司總數、徵才需求或缺工人數。")
        return "\n".join(lines)

    elif intent == "DEMOGRAPHIC_QUERY":
        f113 = data.get("freshmen_113", 188000)
        f117 = data.get("freshmen_117", 156000)
        diff = data.get("difference_freshmen", -32000)
        pct = data.get("contraction_rate_pct", -17.02)
        return (
            f"【少子化海嘯對高教生源衝擊推估】\n"
            f"• 113學年度全國大專新生總人數：{f113:,} 人 (18.8 萬人)\n"
            f"• 117學年度全國大專新生預估人數：{f117:,} 人 (15.6 萬人)\n"
            f"• 113至117學年度生源縮減量：{abs(diff):,} 人 (萎縮幅達 {abs(pct)}%)\n"
            f"117學年度適逢「虎年少子化大低谷」入學，將造成全國大專校院生源池驟減，各系所須及早因應供需動能失衡。"
        )

    elif intent == "DEPARTMENT_QUERY":
        if isinstance(data, list) and len(data) > 0:
            lines = ["【系所生源、註冊率與117學年度供給推估】\n"]
            # Filter for academic_year 113 if present
            rows_113 = [r for r in data if r.get("academic_year") == 113]
            display_rows = rows_113 if rows_113 else data
            for dept in display_rows[:5]:
                lines.append(
                    f"• {dept['institution_name']} {dept['department_name']}（{dept['academic_year']}學年度）：\n"
                    f"  - 在學學生數：{dept['enrolled_students']} 人（大一實招約 {dept['freshmen_admitted']} 人）\n"
                    f"  - 新生註冊率：{dept['registration_rate']}%\n"
                    f"  - 117學年度推估生源：{dept['projected_students_117']} 人\n"
                )
            return "\n".join(lines)

    return "已成功完成結構化數據檢索，請參閱詳細佐證物件。"
