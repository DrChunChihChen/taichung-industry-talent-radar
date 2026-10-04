# 區域產業 × 高教人才供需錯配預警系統 (System Specification v1.0)
## Regional Industry–Talent Structural Mismatch Early-Warning System
### 2026 InnoServe 資訊應用服務創新競賽【經濟部商工登記資料應用組 (GCIS-OD)】

[![InnoServe 2026](https://img.shields.io/badge/Competition-InnoServe_2026_GCIS--OD-blue.svg)](https://innoserveawards.tca.org.tw/advertise26_GCIS-OD.htm)
[![Golden Benchmark](https://img.shields.io/badge/Golden_Benchmark-65%2F65_Passed_(100%25)-emerald.svg)](benchmark/golden_questions.json)
[![ETL Quality](https://img.shields.io/badge/ETL_Quality_Audit-8%2F8_Passed-success.svg)](tests/test_etl_quality.py)
[![Impeccable Design](https://img.shields.io/badge/Design_Audit-0_Anti--patterns-brightgreen.svg)](ui/index.html)
[![Deterministic Engine](https://img.shields.io/badge/Principles-P1--P5_Guaranteed-orange.svg)](docs/SYSTEM_SPECIFICATION.md)

---

## 📌 快速交接與規格文件導覽 (Documentation Index)

為協助團隊交接與競賽答辯，本專案提供全套三份高規格技術文件：

| 文件名稱 | 主要內容 | 適用對象 |
| :--- | :--- | :--- |
| ⚡ **[系統實時動態架構儀表板](architecture/index.html)** | **live-panel** 打造之動態終端監控架構（導線粒子動效、實時遙測日誌、狀態機翻轉） | 競賽評審、架構師、技術團隊 |
| 📘 **[完整系統規劃書](docs/SYSTEM_SPECIFICATION.md)** | 系統願景、P1–P5 五大原則、資料架構、數理公式推導、四象限錯配矩陣、Agent 五道護欄、Lieflat 前端規範 | 指導教授、競賽評審、架構師 |
| 💻 **[檔案與資料庫架構規格書](docs/FILE_SPECIFICATION.md)** | 完整目錄樹狀圖、Python 模組職責表、SQLite 8 張表完整資料字典、Data Mart CSV 規格、RESTful API 規格 | 後端開發者、資料工程師 |
| 🚀 **[學生交接手冊與競賽衝刺指南](docs/STUDENT_HANDOVER_GUIDE.md)** | 3 分鐘快速本機跑起來、一鍵重跑資料管線、新產業/新工具擴充教學、評審必考 QA 題庫攻防秘笈 | 接手學生團隊、參賽答辯者 |

---

## 一、系統核心價值與實證問題

本系統整合**經濟部商工行政開放平臺（GCIS）公司登記歷史母體**、**教育部校務資訊公開平臺（MOE UDB）**、**內政部戶政司人口推估（少子化生源精算）**與**教育部 UCAN 大專校院就業職能架構**，為地方治理與高教決策建立「區域產業動能 × 高教人才供給」分析架構。

本系統的核心目標不是預測短期職缺，而是建立：
> **Regional Industry–Talent Structural Mismatch Early-Warning System（區域產業 × 高教人才結構性錯配預警系統）**

### 核心回答四大實證問題：
1. **台中市哪些產業正在顯著擴張或動能收縮？**（依據新設率 Entry Rate 與資本擴張率 Capital Expansion Rate）
2. **哪些行政區的特定產業活動較強？**（以西屯、潭子、南屯、大雅等 29 行政區之需求端企業存量與動能展現）
3. **與各產業相關的高教人才供給至 117 學年度可能如何變化？**（少子化虎年海嘯谷底生源池萎縮 -17.02% 與各系所異質消長）
4. **哪些產業出現「產業擴張動能」與「人才供給動能」不同步的結構性警示？**（Mismatch = Demand - Supply 四象限警示）

---

## 二、系統遵循之五項核心原則 (Design Principles)

```
┌─────────────────────────────────────────────────────────────┐
│                    FIVE SYSTEM PRINCIPLES                   │
├─────────────────────────────────────────────────────────────┤
│ P1. Deterministic First (確定性第一，數字全由程式精算)     │
│ P2. LLM Does Not Calculate (LLM 絕對不計算任何數值)         │
│ P3. LLM Does Not Classify (產業與學門映射一律依固定規則表)  │
│ P4. Traceable (所有輸出具備 5 級確定性佐證回溯鏈)          │
│ P5. Warning, Not Prediction (定位為結構性預警，非就業預測)  │
└─────────────────────────────────────────────────────────────┘
```

---

## 三、快速開始（3 分鐘啟動）

### 1. 安裝環境需求
```bash
# 建議 Python 3.10 或更高版本
pip install fastapi uvicorn pandas numpy requests
```

### 2. 啟動本機伺服器
```bash
python3 server.py
```
打開瀏覽器訪問：**`http://127.0.0.1:8888`**。

### 3. 一鍵全流程重跑管線與驗證
```bash
python3 pipeline/run_full_pipeline.py
```
自動執行 8 步驟：資料庫初始化 $\rightarrow$ GCIS 洗淨 $\rightarrow$ MOE UDB 提取 $\rightarrow$ UCAN 稀釋 $\rightarrow$ 數理引擎精算 $\rightarrow$ ETL 品質測試 $\rightarrow$ 65 題基準驗證。

---

## 四、前端介面與視覺系統實拍 (Impeccable × Lieflat Charts)

系統遵循 `pbakaus/impeccable` 規範與 `larashero3-dotcom/lieflat-charts` 設計哲學，採用**紙質米白溫潤淺色系（Warm Paper Ivory `#FAF8F5`）**、**四段式圖表架構**、**Lupi Editorial 表格**與 **Glance 巨幅數字**：

### 1. 首頁問問入口（Hello IR 乾淨入口 + Glance KPI + Dual Momentum Barometer）
![Hello IR 首頁](reports/lieflat_overview_full.png)

### 2. 產業動態觀測（Entry Rate 折線圖 + 增資膠囊直條圖）
![產業動態觀測](reports/lieflat_dynamics_tab.png)

### 3. 台中 29 區空間地圖（行政區企業存量排行與水平膠囊長條圖）
![台中空間地圖](reports/lieflat_map_tab.png)

### 4. 高教生源推估（117 年虎年大谷底生源海嘯對比）
![高教生源推估](reports/lieflat_supply_tab.png)

### 5. 供需錯配四象限觀測儀（零軸交叉散布圖與 7 大目標產業佐證卡片）
![供需錯配四象限](reports/lieflat_mismatch_tab.png)

### 6. 守門型 AI 決策代理人 (Jev 守門 + 數值核驗徽章)
![AI 決策代理人](reports/lieflat_agent_tab.png)

### 7. 系統實時動態架構儀表板 (Live-Panel Architecture Diagram)
> 由 **`ythx-101/live-panel`** 技能編譯生成之純 HTML/CSS/JS 實時動態監控架構頁面，具備固定佈局、高亮導線粒子動效、即時滾動遙測日誌與狀態機翻轉。

![系統實時動態架構儀表板](reports/architecture_live_panel.png)

👉 **線上動態體驗入口**：[architecture/index.html](architecture/index.html) 或本機訪問 `http://127.0.0.1:8888/architecture`

---

## 五、七大目標產業定義與動能基準 (113年度)

| 產業代碼 | 目標產業名稱 | 登記存量 | 新設率 | 資本擴張率 | 需求動能 ($Z_{demand}$) | 供給動能 ($Z_{supply}$) | 錯配值 ($Mismatch$) | 象限與預警 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`IND_ICT`** | 資訊軟體與數位科技 | 22,065 | 10.94% | 7.76% | **+1.2416** | +0.3120 | **+0.9296** | Q1: 雙重擴張 (Medium) |
| **`IND_SEM`** | 半導體與綠能科技 | 13,524 | 7.70% | 9.80% | **+1.0392** | +1.2829 | **-0.2437** | Q1: 雙重擴張 (Low) |
| **`IND_BIOMED`**| 生技醫療與精準健康 | 10,184 | 7.82% | 7.29% | **+0.5272** | +0.1373 | **+0.3899** | Q1: 雙重擴張 (Low) |
| **`IND_PRO_FIN`**| 專業商管與金融服務 | 23,229 | 6.08% | 4.67% | **-0.3674** | -0.1062 | **-0.2612** | Q3: 雙重收縮 (Low) |
| **`IND_TOUR_CULT`**| 數位文創與觀光休閒 | 15,044 | 6.30% | 3.72% | **-0.5255** | -1.8065 | **+1.2810** | **Q2: 嚴重短缺 (High)** |
| **`IND_MFG`** | 智慧製造與精密機械 | 45,998 | 3.54% | 4.30% | **-0.9466** | +0.7801 | **-1.7267** | **Q4: 相對過剩 (High)** |
| **`IND_TRADE_LOG`**| 國際貿易與現代物流 | 24,240 | 3.84% | 3.91% | **-0.9684** | -0.6006 | **-0.3678** | Q3: 雙重收縮 (Low) |

---

## 六、代碼品質與驗收標準

- **Impeccable 原生檢查**：
  ```bash
  ./.agents/skills/impeccable/scripts/impeccable detect ui/index.html
  # Exit Code: 0, 0 anti-patterns, 0 warnings
  ```
- **黃金標準 65 題評測**：
  ```bash
  python3 benchmark/run_benchmark.py
  # Total: 65, Passed: 65, Accuracy: 100.0%
  ```
- **ETL 品質稽核**：
  ```bash
  python3 tests/test_etl_quality.py
  # Checks Passed: 8/8 (100.0%)
  ```

---

## 七、版權與參賽宣告

本專案由參賽團隊為 **2026 InnoServe Awards** 開發，依據經濟部商工行政開放平臺資料與教育部校務資訊公開平臺規範建置。未經授權禁止商業轉載。
