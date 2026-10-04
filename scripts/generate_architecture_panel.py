#!/usr/bin/env python3
"""
Generate Live Panel Configuration and HTML for
Regional Industry-Talent Structural Mismatch Early-Warning System
(區域產業 × 高教人才供需錯配預警系統)
"""
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SKILL_DIR = BASE_DIR / ".agents" / "skills" / "live-panel"
sys.path.insert(0, str(SKILL_DIR / "scripts"))
import livepanel as lp

def generate_config():
    config = {
        "meta": {
            "title": "區域產業 × 高教人才供需錯配預警系統 · 實時架構儀表板",
            "lang": "zh-TW"
        },
        "canvas": {
            "preset": "4:5",
            "width": 1200,
            "height": 1500,
            "duration": 30,
            "fps": 30,
            "preroll": 10
        },
        "theme": {
            "preset": "terminal-dark",
            "font": "\"IBM Plex Mono\", \"JetBrains Mono\", \"Noto Sans TC\", monospace",
            "fontSize": 15,
            "lineHeight": 23,
            "colors": {
                "bg": "#0f1217",
                "bar": "#181d26",
                "line": "#2f3b52",
                "line2": "#232e42",
                "dim": "#64748b",
                "fg": "#e2e8f0",
                "wh": "#ffffff",
                "cy": "#38bdf8",
                "bl": "#3b82f6",
                "gr": "#10b981",
                "pu": "#a855f7",
                "ye": "#f59e0b",
                "re": "#ef4444",
                "hl": "#1e293b",
                "row": "#162032",
                "dots": "#334155"
            }
        },
        "clock": {
            "start": "09:30:00",
            "rate": 1
        },
        "titlebar": {
            "text": "~/taichung-radar — sys-architecture — live-panel v1.0"
        },
        "credit": {
            "text": "區域產業 × 高教人才供需錯配預警系統 · InnoServe 2026 經濟部商工登記資料應用組 · 65題黃金評測 100% · 8/8 ETL 稽核",
            "y": 1488,
            "size": 13,
            "c": "dim"
        },
        "machines": {
            "gcis_ingest": {
                "type": "cycle",
                "period": 4.5,
                "t0": 0.5,
                "log": {"who": "GCIS 母體", "c": "cy"},
                "values": [
                    {"t": "西屯區", "m": "西屯區 29,291 家登記存量 · 精密機械與軟體聚落", "g": "存量第一"},
                    {"t": "北屯區", "m": "北屯區 21,024 家 · 商業服務與貿易物流持續新設", "g": "存量第二"},
                    {"t": "新設動能", "m": "資訊軟體業 113 年新設率 10.94% (+0.413% 5年趨勢)", "g": "動能最強"},
                    {"t": "資本擴張", "m": "半導體綠能業 資本擴張率 9.80% (+0.300% 5年趨勢)", "g": "資本第一"}
                ]
            },
            "moe_talent": {
                "type": "cycle",
                "period": 5.0,
                "t0": 1.2,
                "log": {"who": "高教推估", "c": "re"},
                "values": [
                    {"t": "虎年谷底", "m": "117 年全國大專生源 156,000 人 (-17.02% 生源海嘯)", "g": "提前4年預警"},
                    {"t": "系所競爭", "m": "台中 14 大專 878 系所獨立趨勢外推 · 禁同比例假設", "g": "競爭力異質"},
                    {"t": "UCAN稀釋", "m": "Section 18 多權重稀釋: Primary 1.0 / Secondary 0.5", "g": "防重複灌水"},
                    {"t": "文創告急", "m": "數位文創培育池大跌 -28.4% · 供給動能 Z = -1.8065", "g": "縮減最劇"}
                ]
            },
            "mismatch_state": {
                "type": "cycle",
                "period": 4.0,
                "t0": 2.0,
                "log": {"who": "錯配警示", "c": "ye"},
                "values": [
                    {"t": "Q2 嚴重短缺", "m": "數位文創與觀光休閒: Mismatch = +1.2810 (第二象限)", "g": "🚨 High Warning"},
                    {"t": "Q4 相對過剩", "m": "智慧製造精密機械: Mismatch = -1.7267 (第四象限)", "g": "⚠️ High Warning"},
                    {"t": "Q1 雙重擴張", "m": "資訊軟體業: Mismatch = +0.9296 (產學接軌高熱)", "g": "Medium Warning"},
                    {"t": "確定性驗證", "m": "全流程 5 級回溯鏈鎖定: 數理解釋 100% 溯源", "g": "P1-P5 鎖定"}
                ]
            },
            "jev_guard": {
                "type": "triggers",
                "color": "pu",
                "period": 6.0,
                "on": 3.8,
                "t0": 0.8,
                "callsStart": 142,
                "onText": "審查中",
                "offText": "守門待命",
                "items": [
                    {
                        "name": "錯配諮詢",
                        "adv": ["» 合法意圖: GET_MISMATCH", "» 檢索 7 大產業四象限指標"],
                        "to": "通過"
                    },
                    {
                        "name": "預測股價",
                        "adv": ["» 違規偵測: 未來股價臆測", "» 觸發 P5/§23 拒絕回答 (403)"],
                        "to": "阻斷"
                    },
                    {
                        "name": "空間查詢",
                        "adv": ["» 合法意圖: GET_SPATIAL", "» 西屯區 29,291 家存量解析"],
                        "to": "通過"
                    },
                    {
                        "name": "數值核驗",
                        "adv": ["» Numeric Verifier 反向抽驗", "» 正則比對 100% 通過徽章"],
                        "to": "認證"
                    }
                ],
                "log": {
                    "who": "Jev 守門",
                    "c": "pu",
                    "start": {"m": "{name} · 接收查詢請求，進行範疇合規審查", "g": "審查中"},
                    "end": {"m": "{name} · 審查完畢，政策動作: {to}", "g": "{to}"}
                }
            },
            "cliff_gauge": {
                "type": "gauge",
                "period": 6,
                "t0": 0,
                "seed": 42,
                "threshold": 0.5,
                "values": [0.83, 0.83, 0.83, 0.83],
                "decimals": 2,
                "high": {"label": "-17.02% (15.6萬人)", "dest": "生源大谷底"},
                "low": {"label": "-17.02% (15.6萬人)", "dest": "生源大谷底"}
            },
            "benchmark_gauge": {
                "type": "gauge",
                "period": 5,
                "t0": 1,
                "seed": 99,
                "threshold": 0.5,
                "values": [1.0, 1.0, 1.0, 1.0],
                "decimals": 1,
                "high": {"label": "65/65 (100.0%)", "dest": "完美通過"},
                "low": {"label": "65/65 (100.0%)", "dest": "完美通過"}
            }
        },
        "elements": [
            # Top Banner & System Title
            {
                "type": "text",
                "x": 0,
                "y": 68,
                "w": 1200,
                "align": "center",
                "runs": [
                    {"t": "區域產業 × 高教人才供需錯配預警系統", "c": "fg", "b": 1, "size": 22},
                    {"t": "　·　", "c": "dim"},
                    {"t": "實時架構儀表板", "c": "bl", "b": 1, "size": 22}
                ]
            },
            {
                "type": "rule",
                "x": 30,
                "y": 92,
                "w": 1140
            },
            {
                "type": "text",
                "x": 0,
                "y": 116,
                "w": 1200,
                "align": "center",
                "runs": [
                    {"t": "P1-P5 確定性核心", "c": "bl", "b": 1},
                    {"t": " · 經濟部商工登記歷史母體 × 教育部校務公開 UDB × 117 年少子化精算 · JEV 守門決策代理", "c": "dim"}
                ]
            },
            {
                "type": "text",
                "x": 0,
                "y": 142,
                "w": 1200,
                "align": "center",
                "runs": [
                    {"sw": "cy"}, {"t": "官方資料源　", "c": "cy"},
                    {"sw": "bl"}, {"t": "確定性數理引擎　", "c": "bl"},
                    {"sw": "pu"}, {"t": "守門決策代理　", "c": "pu"},
                    {"sw": "ye"}, {"t": "錯配預警信號　", "c": "ye"},
                    {"sw": "gr"}, {"t": "65題黃金評測 100% (Passed)", "c": "gr", "b": 1}
                ]
            },

            # ================= TIER 1: DATA SOURCES (Y: 165 ~ 375, h: 210) =================
            {
                "type": "box",
                "x": 30,
                "y": 165,
                "w": 360,
                "h": 210,
                "color": "cy",
                "pad": [10, 14, 14],
                "lines": [
                    {"runs": [{"t": "經濟部 GCIS 商工行政登記母體", "c": "cy", "b": 1, "size": 16}]},
                    {"t": "• 臺中市登記母體: 159,170 家 (109-113年)", "c": "fg"},
                    {"t": "• 8碼統編正規化 · 門市/分公司去噪清洗", "c": "dim"},
                    {"t": "• 29 行政區地址正則萃取比對", "c": "dim"},
                    {"t": "• 營業代碼固定規則映射 7 大目標產業", "c": "fg"},
                    {"t": "• 匯整新設、增資、解散、存量時間序列", "c": "dim"},
                    {"runs": [{"t": "狀態: ", "c": "dim"}, {"t": "✓ 母體已載入 100%", "c": "gr", "b": 1}]}
                ]
            },
            {
                "type": "box",
                "x": 420,
                "y": 165,
                "w": 360,
                "h": 210,
                "color": "cy",
                "pad": [10, 14, 14],
                "lines": [
                    {"runs": [{"t": "教育部 UDB 校務平臺 × UCAN", "c": "cy", "b": 1, "size": 16}]},
                    {"t": "• 臺中市轄區 14 所大專校院 / 878 個系所", "c": "fg"},
                    {"t": "• 連續 5 年在學學生數與新生註冊率歷程", "c": "dim"},
                    {"t": "• Section 18 廣泛適用系所多權重稀釋", "c": "bl", "b": 1},
                    {"t": "• Primary (1.0) / Secondary (0.5) 映射", "c": "dim"},
                    {"t": "• 排除企管/跨域系所重複灌水偏差", "c": "dim"},
                    {"runs": [{"t": "學門映射: ", "c": "dim"}, {"t": "1,294 筆精準對照", "c": "cy", "b": 1}]}
                ]
            },
            {
                "type": "box",
                "x": 810,
                "y": 165,
                "w": 360,
                "h": 210,
                "color": "re",
                "pad": [10, 14, 14],
                "lines": [
                    {"runs": [{"t": "內政部人口與少子化精算底盤", "c": "re", "b": 1, "size": 16}]},
                    {"t": "• 117 學年度大專新生谷底 (虎年世代)", "c": "fg"},
                    {"t": "• 全國適齡生源: 188,000 → 156,000 人", "c": "re", "b": 1},
                    {"runs": [{"t": "• 生源海嘯衝擊: ", "c": "dim"}, {"t": "-17.02% (斷崖下跌)", "c": "re", "b": 1}]},
                    {"t": "• 各系所獨立競爭力趨勢外推 (嚴禁等比)", "c": "dim"},
                    {"t": "• 提前 4 年預警區域各學門供給池萎縮", "c": "dim"},
                    {"runs": [{"t": "衝擊指標: ", "c": "dim"}, {"bar": {"w": 180, "h": 16, "gauge": "cliff_gauge"}}]}
                ]
            },

            # Connecting Wires: Tier 1 -> Tier 2
            {"type": "line", "from": [210, 375], "to": [210, 425], "color": "cy"},
            {"type": "glyph", "x": 210, "y": 427, "ch": "▼", "c": "cy"},
            {"type": "flow", "path": [[210, 375], [210, 425]], "period": 2.5, "offsets": [0.3, 1.5], "color": "cy"},

            {"type": "line", "from": [600, 375], "to": [600, 425], "color": "cy"},
            {"type": "glyph", "x": 600, "y": 427, "ch": "▼", "c": "cy"},
            {"type": "flow", "path": [[600, 375], [600, 425]], "period": 2.5, "offsets": [0.6, 1.8], "color": "cy"},

            {"type": "line", "from": [990, 375], "to": [990, 425], "color": "re"},
            {"type": "glyph", "x": 990, "y": 427, "ch": "▼", "c": "re"},
            {"type": "flow", "path": [[990, 375], [990, 425]], "period": 2.5, "offsets": [0.9, 2.1], "color": "re"},

            # ================= TIER 2: DETERMINISTIC ENGINES (Y: 425 ~ 765, h: 340) =================
            {
                "type": "box",
                "x": 30,
                "y": 425,
                "w": 1140,
                "h": 340,
                "color": "bl",
                "container": True,
                "pad": [10, 16, 16],
                "lines": [
                    {"runs": [
                        {"t": "DETERMINISTIC ENGINES 確定性數理運算核心", "c": "bl", "b": 1, "size": 17},
                        {"t": " (P1-P5 鎖定 · 零黑箱零幻覺 · 100% 數理精算)", "c": "dim"}
                    ]},
                    {"t": "所有指標、推估與錯配向量均由程式精算 · 嚴禁 LLM 參與數值計算或統計推論 · 8 張標準化分析集市 (Data Marts)", "c": "dim"}
                ]
            },
            # Sub-box A: Demand Momentum Engine
            {
                "type": "box",
                "x": 48,
                "y": 485,
                "w": 265,
                "h": 265,
                "color": "bl",
                "pad": [8, 10, 10],
                "lines": [
                    {"runs": [{"t": "產業需求擴張動能", "c": "bl", "b": 1}]},
                    {"t": "Demand Momentum Engine", "c": "dim", "size": 12},
                    {"t": "• 新設公司率 (Entry Rate %)", "c": "fg"},
                    {"t": "  5年趨勢斜率 → Z_entry", "c": "dim"},
                    {"t": "• 資本擴張率 (CapInc %)", "c": "fg"},
                    {"t": "  5年趨勢斜率 → Z_capital", "c": "dim"},
                    {"runs": [{"t": "DemandMomentum(i):", "c": "bl", "b": 1}]},
                    {"t": "  0.5×Z_ent + 0.5×Z_cap", "c": "fg", "b": 1},
                    {"t": "(退場解散僅供風險參考)", "c": "dim", "size": 12},
                    {"runs": [{"t": "最熱產業: ", "c": "dim"}, {"t": "資訊軟體 (+1.24)", "c": "cy", "b": 1}]}
                ]
            },
            # Sub-box B: Talent Supply Engine
            {
                "type": "box",
                "x": 328,
                "y": 485,
                "w": 265,
                "h": 265,
                "color": "bl",
                "pad": [8, 10, 10],
                "lines": [
                    {"runs": [{"t": "高教人才供給推估", "c": "bl", "b": 1}]},
                    {"t": "Talent Supply Engine", "c": "dim", "size": 12},
                    {"t": "• 117 年 18 歲大專適齡生源", "c": "fg"},
                    {"t": "  × 各系所市占率 Share(d)", "c": "dim"},
                    {"t": "  × 新生註冊率外推 Reg(d)", "c": "dim"},
                    {"t": "  × UCAN 稀釋權重 W(d,i)", "c": "dim"},
                    {"runs": [{"t": "SupplyMomentum(i):", "c": "bl", "b": 1}]},
                    {"t": "  培育池增長率 → Z_supply", "c": "fg", "b": 1},
                    {"t": "(禁止全系所等比例衰退)", "c": "dim", "size": 12},
                    {"runs": [{"t": "供給斷崖: ", "c": "dim"}, {"t": "數位文創 (-1.81)", "c": "re", "b": 1}]}
                ]
            },
            # Sub-box C: Mismatch Engine
            {
                "type": "box",
                "x": 608,
                "y": 485,
                "w": 265,
                "h": 265,
                "color": "ye",
                "pad": [8, 10, 10],
                "lines": [
                    {"runs": [{"t": "供需錯配四象限預警", "c": "ye", "b": 1}]},
                    {"t": "Mismatch Early-Warning", "c": "dim", "size": 12},
                    {"runs": [{"t": "向量: ", "c": "dim"}, {"t": "Z_demand - Z_supply", "c": "ye", "b": 1}]},
                    {"t": "• Q1: 雙重擴張 (產學俱熱)", "c": "fg"},
                    {"t": "• Q2: 嚴重短缺 🚨 (High)", "c": "re", "b": 1},
                    {"t": "• Q3: 雙重收縮 (產業轉型)", "c": "dim"},
                    {"t": "• Q4: 相對過剩 (過度集中) ⚠️", "c": "ye", "b": 1},
                    {"t": "預警分級: High / Med / Low", "c": "dim"},
                    {"runs": [{"t": "警示: ", "c": "dim"}, {"t": "文創(+1.28) 精機(-1.73)", "c": "re", "b": 1}]}
                ]
            },
            # Sub-box D: Traceability Engine
            {
                "type": "box",
                "x": 888,
                "y": 485,
                "w": 265,
                "h": 265,
                "color": "gr",
                "pad": [8, 10, 10],
                "lines": [
                    {"runs": [{"t": "5級全流程佐證回溯鏈", "c": "gr", "b": 1}]},
                    {"t": "Traceability Engine (P4)", "c": "dim", "size": 12},
                    {"t": "① Result: 錯配預警訊號", "c": "fg"},
                    {"t": "  ↓ ② 指標: 需求與供給動能", "c": "dim"},
                    {"t": "  ↓ ③ 計算: Z-Score 精算公式", "c": "dim"},
                    {"t": "  ↓ ④ Table: 8 張集市寬表", "c": "dim"},
                    {"t": "  ↓ ⑤ Source: GCIS/UDB 母體", "c": "fg"},
                    {"t": "• 提供完整 JSON 佐證物件", "c": "dim"},
                    {"runs": [{"t": "可信度: ", "c": "dim"}, {"t": "100% 確定性可驗證", "c": "gr", "b": 1}]}
                ]
            },

            # Connecting Wires: Tier 2 -> Tier 3
            {"type": "line", "from": [480, 765], "to": [480, 815], "color": "bl"},
            {"type": "glyph", "x": 480, "y": 817, "ch": "▼", "c": "bl"},
            {"type": "flow", "path": [[480, 765], [480, 815]], "period": 2.2, "offsets": [0.4, 1.5], "color": "bl"},

            {"type": "line", "from": [740, 765], "to": [740, 815], "color": "ye"},
            {"type": "glyph", "x": 740, "y": 817, "ch": "▼", "c": "ye"},
            {"type": "flow", "path": [[740, 765], [740, 815]], "period": 2.2, "offsets": [0.7, 1.8], "color": "ye"},

            # ================= TIER 3: GUARDED AI AGENT (Y: 815 ~ 1075, h: 260) =================
            {
                "type": "box",
                "x": 30,
                "y": 815,
                "w": 1140,
                "h": 260,
                "color": "pu",
                "container": True,
                "pad": [10, 16, 16],
                "lines": [
                    {"runs": [
                        {"t": "GUARDED AI DECISION AGENT PIPELINE", "c": "pu", "b": 1, "size": 17},
                        {"t": " (Agent 01–05 五道確定性護欄 · LLM 絕不計算 P2)", "c": "dim"}
                    ]},
                    {"t": "嚴格依據真實數據結構化詮釋 · 反向字面數值核驗 · 杜絕大語言模型數值幻覺與非確定性妄言", "c": "dim"}
                ]
            },
            # Stage 1: Scope Guard
            {
                "type": "box",
                "x": 50,
                "y": 875,
                "w": 345,
                "h": 185,
                "color": "pu",
                "pad": [8, 10, 10],
                "lines": [
                    {"runs": [{"t": "Agent 01: Scope Guard (Jev 守門)", "c": "pu", "b": 1}]},
                    {"t": "• 政策合規範圍審查 (Policy Boundary)", "c": "fg"},
                    {"t": "• 阻斷預測未來股價 / 職缺人數", "c": "dim"},
                    {"t": "• 阻斷非台中市與非高教提問", "c": "dim"},
                    {"t": "• 違規即刻攔截回傳 403 政策拒絕", "c": "re", "b": 1},
                    {"runs": [{"t": "守門狀態: ", "c": "dim"}, {"t": "{jev_guard.status}", "c": "pu", "b": 1}, {"t": " ({jev_guard.calls} 次調用)", "c": "dim"}]}
                ]
            },
            # Stage 2: Intent & Tool Router
            {
                "type": "box",
                "x": 415,
                "y": 875,
                "w": 345,
                "h": 185,
                "color": "pu",
                "pad": [8, 10, 10],
                "lines": [
                    {"runs": [{"t": "Agent 02 & 03: 意圖與確定性路由", "c": "pu", "b": 1}]},
                    {"t": "• Intent Router: 8 大確定性意圖分流", "c": "fg"},
                    {"t": "  MISMATCH / DYNAMICS / SPATIAL...", "c": "dim"},
                    {"t": "• Tool Router: 零幻覺調度 SQLite", "c": "fg"},
                    {"t": "  直接讀取 8 張實體分析集市寬表", "c": "dim"},
                    {"runs": [{"t": "調度延遲: ", "c": "dim"}, {"t": "< 5 ms (高併發記憶體快取)", "c": "gr", "b": 1}]}
                ]
            },
            # Stage 3: Explanation & Numeric Verifier
            {
                "type": "box",
                "x": 780,
                "y": 875,
                "w": 370,
                "h": 185,
                "color": "gr",
                "pad": [8, 10, 10],
                "lines": [
                    {"runs": [{"t": "Agent 04 & 05: 生成與反向數值核驗", "c": "gr", "b": 1}]},
                    {"t": "• Explanation Gen: 綁定數據字典組織文本", "c": "dim"},
                    {"t": "• Numeric Verifier (反向字面核驗):", "c": "gr", "b": 1},
                    {"t": "  正則反查文本中每一項數字", "c": "fg"},
                    {"t": "  比對底層 Data Mart 100% 一致方放行", "c": "fg"},
                    {"runs": [{"t": "核驗標章: ", "c": "dim"}, {"t": "[數值核驗通過] (100% 吻合)", "c": "gr", "b": 1}]}
                ]
            },

            # Connecting Wires: Tier 3 -> Tier 4
            {"type": "line", "from": [600, 1075], "to": [600, 1115], "color": "bl"},
            {"type": "glyph", "x": 600, "y": 1117, "ch": "▼", "c": "bl"},
            {"type": "flow", "path": [[600, 1075], [600, 1115]], "period": 2.0, "offsets": [0.5, 1.5], "color": "bl"},

            # ================= TIER 4: FRONTEND COCKPIT UI (Y: 1115 ~ 1265, h: 150) =================
            {
                "type": "box",
                "x": 30,
                "y": 1115,
                "w": 1140,
                "h": 150,
                "color": "bl",
                "pad": [8, 14, 14],
                "lines": [
                    {"runs": [
                        {"t": "DECISION COCKPIT UI 前端戰情室", "c": "bl", "b": 1, "size": 16},
                        {"t": " (Impeccable × Lieflat Charts 淺色紙質系規範 · 0 Anti-patterns)", "c": "dim"}
                    ]},
                    {"runs": [
                        {"t": "① Hello IR 乾淨問問入口", "c": "fg", "b": 1},
                        {"t": " (單一搜尋框 + Jev 守門反查)　　", "c": "dim"},
                        {"t": "② 雙軸動能氣壓計", "c": "fg", "b": 1},
                        {"t": " (Z_demand vs Z_supply 膠囊直條對比)", "c": "dim"}
                    ]},
                    {"runs": [
                        {"t": "③ 台中 29 區空間存量分析", "c": "fg", "b": 1},
                        {"t": " (西屯 29,291 家 / 水平膠囊長條)　", "c": "dim"},
                        {"t": "④ 供需錯配四象限觀測儀", "c": "fg", "b": 1},
                        {"t": " (零軸交叉散布圖 + 7大產業佐證卡)", "c": "dim"}
                    ]},
                    {"runs": [
                        {"t": "⑤ Lupi Editorial 表格", "c": "fg", "b": 1},
                        {"t": " (IBM Plex Mono 等寬數字排版 + 輕量彩點膠囊)　", "c": "dim"},
                        {"t": "評測認證: ", "c": "dim"},
                        {"bar": {"w": 140, "h": 16, "gauge": "benchmark_gauge"}},
                        {"t": " 65/65 (100%)", "c": "gr", "b": 1}
                    ]}
                ]
            },

            # ================= TIER 5: REAL-TIME TELEMETRY LOG (Y: 1285 ~ 1470, h: 185) =================
            {
                "type": "log",
                "x": 30,
                "y": 1285,
                "w": 1140,
                "rows": 4,
                "padTop": 14,
                "padBottom": 20,
                "padLeft": 16,
                "title": "REAL-TIME TELEMETRY LOG 實時系統遙測日誌",
                "titleX": 25,
                "titleW": 340,
                "cols": [
                    {"key": "time", "x": 0},
                    {"key": "who", "x": 100},
                    {"key": "m", "x": 220},
                    {"key": "g", "x": 880}
                ]
            }
        ]
    }
    return config

def main():
    cfg = generate_config()
    out_dir = BASE_DIR / "architecture"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    cfg_path = out_dir / "config.json"
    with open(cfg_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    print(f"✓ Saved config to {cfg_path}")

    # Build standalone HTML
    out_html = out_dir / "index.html"
    lp.build_page(cfg_path, out_html)
    print(f"✓ Built standalone HTML: {out_html}")

    # Also save to ui/architecture.html so it can be served via server.py
    ui_html = BASE_DIR / "ui" / "architecture.html"
    lp.build_page(cfg_path, ui_html)
    print(f"✓ Built UI entry: {ui_html}")

if __name__ == "__main__":
    main()
