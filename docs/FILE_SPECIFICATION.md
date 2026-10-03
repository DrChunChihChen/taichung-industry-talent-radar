# 檔案與資料庫架構規格書 (File & Database Specification v1.0)

> **專案名稱**：區域產業 × 高教人才供需錯配預警系統  
> **技術棧**：Python 3.10+, SQLite 3, FastAPI, Vanilla JavaScript (ES6+), Chart.js v4, Tailwind CSS  
> **系統規範版本**：v1.0 MVP  

---

## 一、專案檔案結構樹狀圖 (Project Directory Structure)

```text
校務資料-2/
├── README.md                      # 專案總導覽與快速上手指南
├── config.py                      # 全局常數、目錄設定與目標產業定義
├── server.py                      # 系統主伺服器入口 (ASGI / FastAPI 伺服器)
├── skills-lock.json               # 技能鎖定檔
├── database/                      # 資料庫管理模組
│   ├── schema.sql                 # 完整 SQLite DDL 建立指令碼 (8張表)
│   ├── db_manager.py              # SQLite 連線管理與事務封裝 (DatabaseManager)
│   └── mismatch_system.db         # 實體 SQLite 資料庫 (已建置好完整 Mart)
├── data/                          # 數據儲存目錄
│   ├── raw/                       # 官方部會原始檔案 (GCIS, MOE UDB, 內政部人口)
│   ├── processed/                 # 清洗後中介資料 (公司歷程標準化、生源推估檔)
│   └── marts/                     # 分析集市寬表 CSV (供 Engine 與 API 快速查詢)
├── etl/                           # 確定性資料清洗與管線抽取模組
│   ├── extract_demographics.py    # 內政部人口資料抽取與 117 年生源推估
│   ├── extract_gcis_batch.py      # GCIS 登記母體清洗、行政區比對與動態聚合
│   ├── extract_moe_udb.py         # 教育部校務公開資料清洗與系所歷程匯整
│   ├── map_industries.py          # 營業代碼固定規則映射至 7 大目標產業
│   └── map_ucan.py                # 教育部學類與 UCAN 職涯多權重稀釋映射 (Section 18)
├── engine/                        # 確定性數理計算引擎
│   ├── industry_momentum.py       # 產業需求擴張動能計算 (Entry + Capital Z-scores)
│   ├── talent_supply.py           # 117 年高教人才供給推估 (人口效應 × 系所獨立趨勢)
│   ├── mismatch_engine.py         # 供需錯配四象限向量強度計算與等級評定
│   └── evidence_engine.py         # 五級確定性佐證回溯鏈生成器
├── agent/                         # 守門型 AI 決策代理人管線
│   ├── scope_guard.py             # Agent 01: Scope Guard (Jev 守門: 合規範圍檢查)
│   ├── intent_router.py           # Agent 02: Intent Router (8大確定性意圖分流)
│   ├── tool_router.py             # Agent 03: Tool Router (確定性資料檢索通道)
│   ├── explanation_generator.py   # Agent 04: Explanation Generator (無幻覺政策文本生成)
│   ├── numeric_verifier.py        # Agent 05: Numeric Verifier (數值雙向反查校驗器)
│   └── agent_pipeline.py          # 代理人管線整體封裝與協調器 (GuardedAgentPipeline)
├── api/                           # 後端 RESTful API 服務層
│   └── app.py                     # FastAPI 路由定義與端點實作
├── pipeline/                      # 排程與自動化執行模組
│   └── run_full_pipeline.py       # 8 步驟一鍵全流程重跑腳本
├── benchmark/                     # 評測集與品質基準驗證
│   ├── golden_questions.json      # 65 題黃金標準問答資料庫 (涵蓋 6 大業務範疇)
│   └── run_benchmark.py           # 評測自動執行器與精準度計分器
├── tests/                         # 自動化測試套件
│   └── test_etl_quality.py        # 8 項 ETL 資料品質自動稽核測試 (Section 31)
├── reports/                       # 驗證報告與系統截圖
│   ├── Benchmark_Validation_Report.md # 黃金標準測試 100% 正確率報告
│   ├── ETL_Quality_Report.md      # ETL 品質稽核報告 (8/8 通過)
│   └── *.png                      # 前端展示畫面實拍截圖
├── docs/                          # 完整系統技術規劃與學生交接手冊
│   ├── SYSTEM_SPECIFICATION.md    # 系統規劃書 (願景、數學模型、架構規範)
│   ├── FILE_SPECIFICATION.md      # 檔案與資料庫架構規格書 (本文件)
│   └── STUDENT_HANDOVER_GUIDE.md  # 學生交接手冊與答辯攻防指南
└── ui/                            # 前端介面模組
    └── index.html                 # 單一純 HTML (Tailwind + Chart.js + Lieflat)
```

---

## 二、核心代碼檔案職責規格表 (Module Specification)

### 2.1 基礎配置與伺服器 (Root & Infrastructure)

#### `config.py`
- **職責**：集中管理系統全局常數、目錄路徑、目標產業代碼與對照表、權重參數。
- **核心常數**：
  - `BASE_ACADEMIC_YEAR = 113`：分析基期學年度。
  - `TARGET_PROJECTION_YEAR = 117`：少子化虎年谷底目標預警學年度。
  - `HISTORICAL_YEARS = [109, 110, 111, 112, 113]`：5 年連續歷程。
  - `TARGET_INDUSTRIES`：7 大目標產業之代碼、中英名稱、主題色彩與標準營業代碼清單。
  - `TAICHUNG_DISTRICTS`：台中市 29 法定行政區清單。
  - `DEMAND_MOMENTUM_WEIGHTS`：新設率與增資率等權重（0.5 / 0.5）。
  - `MAPPING_TYPE_WEIGHTS`：Primary (1.0) / Secondary (0.5)。

#### `server.py`
- **職責**：ASGI 伺服器啟動腳本，配置靜態資源映射（`/reports` 與前端目錄）並啟動 Uvicorn。
- **預設運行端點**：`http://127.0.0.1:8888`。

---

### 2.2 資料庫層 (Database Layer)

#### `database/schema.sql`
- **職責**：SQLite 資料庫實體綱要 DDL 指令碼，定義 8 張標準化核心表、主鍵、外鍵關聯與查詢索引。

#### `database/db_manager.py`
- **職責**：封裝 SQLite 連線與常用查詢輔助方法。
- **核心介面**：
  - `DatabaseManager(db_path)`：單例化連線管理。
  - `init_db()`：讀取 `schema.sql` 並初始化資料庫結構。
  - `execute_query(sql, params)`：執行 SELECT 查詢並回傳字典陣列（`List[Dict]`）。
  - `execute_commit(sql, params)`：執行 INSERT / UPDATE / DELETE 事務。
  - `bulk_insert(table, records)`：批次寫入資料。

---

### 2.3 確定性 ETL 管線 (ETL Modules)

#### `etl/map_industries.py`
- **職責**：管理固定產業對應規則表（Section 8: Mapping Table），將經濟部營業代碼對齊至 7 大產業。
- **核心函式**：
  - `load_industry_rules() -> pd.DataFrame`：初始化 `industry_mapping_rules` 並寫入 SQLite。
  - `get_industry_by_business_code(code: str) -> Optional[str]`：查表取得產業代碼。

#### `etl/extract_demographics.py`
- **職責**：處理內政部人口統計，計算 109–117 年全國 18 歲大專潛在生源推估（Section 4.3, 12）。
- **核心函式**：
  - `load_demographics() -> pd.DataFrame`：計算基期 113（18.8萬人）與目標年 117（15.6萬人）生源變化，存入 `demographics_projection` 表。

#### `etl/extract_gcis_batch.py`
- **職責**：清洗 GCIS 商工登記歷程（Section 6, 7），過濾台中市資料、標準化 8 碼統編、解析 29 行政區地址，建置 `industry_dynamics_mart`（Section 9）。
- **核心函式**：
  - `extract_district(address: str) -> str`：地址正則比對 29 行政區。
  - `clean_company_batch() -> pd.DataFrame`：過濾分公司門市與非法字串。
  - `build_industry_dynamics_mart() -> pd.DataFrame`：依 `(Year × District × Industry)` 聚合計算新設、增資、解散、存量與比率。

#### `etl/extract_moe_udb.py`
- **職責**：讀取教育部 UDB 原始檔，聚合台中 14 所大專校院系所在學學生數、新生註冊率歷程（Section 4.1, 14）。
- **核心函式**：
  - `clean_registration_rate(val) -> float`：清理隱匿值、負值與極端異常值。
  - `extract_moe_udb_data() -> pd.DataFrame`：產出 `department_indicators_mart`。

#### `etl/map_ucan.py`
- **職責**：建立教育部學門系所至 UCAN 職涯途徑與 7 大目標產業之多權重映射表（Section 15, 16, 18）。
- **核心函式**：
  - `build_dept_ucan_mapping() -> pd.DataFrame`：套用 Primary (1.0) 與 Secondary (0.5) 稀釋權重，產出 `dept_ucan_industry_mapping`。

---

### 2.4 確定性數理計算引擎 (Deterministic Engines)

#### `engine/industry_momentum.py`
- **職責**：計算產業需求擴張動能（Section 10, 11），產出新設率趨勢、增資擴張率趨勢與標準化 Z 分數。
- **核心函式**：
  - `calculate_industry_momentum(target_year=113) -> pd.DataFrame`：
    - 計算 $Z_{entry}$ 與 $Z_{capital}$。
    - 計算 $\text{DemandMomentum} = 0.5 \times Z_{entry} + 0.5 \times Z_{capital}$。
    - 寫入 `industry_momentum_mart`。

#### `engine/talent_supply.py`
- **職責**：高教人才供給推估引擎（Section 12, 13, 14, 17, 18）。
- **核心函式**：
  - `project_department_supply_117() -> pd.DataFrame`：獨立計算每個系所的市占率趨勢與註冊率外推，乘上 117 年人口海嘯係數。
  - `calculate_industry_talent_supply() -> pd.DataFrame`：加權匯總至 7 大目標產業人才供給池，計算供給動能標準化值 $Z_{supply}$，寫入 `industry_supply_mart`。

#### `engine/mismatch_engine.py`
- **職責**：供需錯配預警引擎（Section 19, 20）。
- **核心函式**：
  - `calculate_mismatch_signals() -> pd.DataFrame`：
    - 計算 $\text{Mismatch} = \text{DemandMomentum} - \text{SupplyMomentum}$。
    - 判定象限（Q1–Q4）與警示等級（High / Medium / Low Warning）。
    - 寫入 `mismatch_signal_mart`。

#### `engine/evidence_engine.py`
- **職責**：提供 5 級確定性佐證回溯鏈（Section 21: Traceability Engine）。
- **核心函式**：
  - `get_mismatch_evidence(industry_id: str) -> Dict`：回傳包含計算公式、中間指標數值、所屬系所名單、關聯商工登記樣本之完整確定性佐證 JSON。

---

### 2.5 守門型 AI 決策代理人管線 (Agent Pipeline)

#### `agent/scope_guard.py`
- **職責**：Agent 01 - Scope Guard（Jev 守門器）。
- **核心規則**：
  - 檢測問題是否落在台中市產業與高教範疇。
  - 依據 P5 原則拒絕回答「預測未來股價」、「保證就業率」、「非台中行政區」之提問。
  - 阻斷時回傳 HTTP 403 政策拒絕訊息與合規引用條款。

#### `agent/intent_router.py`
- **職責**：Agent 02 - Intent Router，將自然語言分流至 8 大確定性意圖：
  1. `GET_MISMATCH_SIGNALS`（錯配總覽或高警示產業查詢）
  2. `GET_INDUSTRY_DYNAMICS`（特定產業新設/增資歷程）
  3. `GET_SPATIAL_DEMAND`（行政區產業聚落查詢）
  4. `GET_TALENT_SUPPLY`（117 年高教生源推估與學門）
  5. `GET_EVIDENCE_CHAIN`（回溯佐證與計算明細）
  6. `VERIFY_COMPANY_GCIS`（統編或公司名稱驗證）
  7. `GET_METHODOLOGY`（系統規格、公式與原則說明）
  8. `OUT_OF_SCOPE`（超出範圍）

#### `agent/tool_router.py`
- **職責**：Agent 03 - 根據識別之意圖與槽位（Slot），自 SQLite 資料庫中擷取對應的確定性數據字典。

#### `agent/explanation_generator.py`
- **職責**：Agent 04 - 接收確定性數據字典，組織成嚴謹、結構化的政策解說與決策建議文本（嚴格禁止加入未在數據中出現的推論數字）。

#### `agent/numeric_verifier.py`
- **職責**：Agent 05 - Numeric Verifier（反向數值核驗器）。
- **核心機制**：
  - 透過正則表達式抽取文本中所有出現的數值（如 `1.2810`, `156,000`, `-17.02%`）。
  - 比對該數值是否存在於 Agent 03 提供的確定性數據字典中。
  - 若核驗 100% 通過，加蓋 `[數值核驗通過]` 合規認證標籤；若發現虛假數字，觸發阻斷重寫。

#### `agent/agent_pipeline.py`
- **職責**：串接 Agent 01 至 05，對外暴露 `pipeline.query(user_question)` 統一接口。

---

## 三、SQLite 資料庫資料字典 (Database Schema & Dictionary)

資料庫實體路徑：`database/mismatch_system.db`（共 8 張標準化核心表）

### 表 1：`companies_cleaned` (標準化商工登記歷程表)
| 欄位名稱 | 型態 | 鍵約束 | 說明 |
| :--- | :--- | :--- | :--- |
| `company_id` | TEXT | PRIMARY KEY | 8 位統一編號字串 |
| `company_name` | TEXT | NOT NULL | 公司正式名稱（已標準化排除分公司門市） |
| `registration_date` | TEXT | NOT NULL | 核准設立日期 (YYYY-MM-DD) |
| `status` | TEXT | NOT NULL | 登記狀態（核准設立、解散、廢止等） |
| `capital` | INTEGER | NOT NULL | 登記資本額（新台幣元） |
| `city` | TEXT | NOT NULL | 縣市（固定為「台中市」） |
| `district` | TEXT | NOT NULL | 萃取之 29 行政區（或 UNKNOWN） |
| `address` | TEXT | NOT NULL | 登記完整地址 |
| `business_item_code` | TEXT | NOT NULL | 主要營業項目代碼 (如 CA02010) |
| `industry_id` | TEXT | FOREIGN KEY | 映射之目標產業代碼 (如 IND_MFG) |
| `change_date` | TEXT | NULL | 最後資本變更或異動日期 |

### 表 2：`industry_mapping_rules` (固定產業映射規則表 - Section 8)
| 欄位名稱 | 型態 | 鍵約束 | 說明 |
| :--- | :--- | :--- | :--- |
| `business_code` | TEXT | PRIMARY KEY | 經濟部營業項目代碼 (如 I301010) |
| `business_name` | TEXT | NOT NULL | 營業項目官方名稱 |
| `industry_id` | TEXT | NOT NULL | 對應之 7 大目標產業代碼 |
| `industry_name` | TEXT | NOT NULL | 對應產業中文名稱 |
| `mapping_rule` | TEXT | NOT NULL | 規則說明 (EXACT_CODE / KEYWORD) |
| `version` | TEXT | NOT NULL | 規則版本號 (v1.0) |

### 表 3：`demographics_projection` (少子化人口推估表 - Section 4.3, 12)
| 欄位名稱 | 型態 | 鍵約束 | 說明 |
| :--- | :--- | :--- | :--- |
| `year` | INTEGER | PRIMARY KEY | 學年度 (109 至 117) |
| `birth_population` | INTEGER | NOT NULL | 對應出生世代人口數 |
| `projected_age18_pop` | INTEGER | NOT NULL | 全國大專 18 歲適齡生源推估人數 |
| `growth_vs_base` | REAL | NOT NULL | 較 113 基期之增減幅度 (117年為 -17.02%) |

### 表 4：`department_indicators_mart` (高教系所歷程指標集市 - Section 4.1, 14)
| 欄位名稱 | 型態 | 鍵約束 | 說明 |
| :--- | :--- | :--- | :--- |
| `academic_year` | INTEGER | PK (組合) | 學年度 (109-113) |
| `institution_id` | TEXT | PK (組合) | 學校統計代碼 (如 0005) |
| `institution_name` | TEXT | NOT NULL | 學校名稱 (台中市轄內 14 所大專) |
| `department_id` | TEXT | PK (組合) | 系所代碼 (如 520101) |
| `department_name` | TEXT | NOT NULL | 系所完整名稱 |
| `field_code` | TEXT | NOT NULL | 教育部學類代碼 (如 0612 軟體開發) |
| `enrolled_students` | INTEGER | NOT NULL | 在學學生總數 |
| `registration_rate` | REAL | NOT NULL | 新生註冊率 (%) |
| `dept_share` | REAL | NOT NULL | 該年度在台中大專生源之占比 |

### 表 5：`dept_ucan_industry_mapping` (UCAN 職涯多權重映射集市 - Section 16, 18)
| 欄位名稱 | 型態 | 鍵約束 | 說明 |
| :--- | :--- | :--- | :--- |
| `department_id` | TEXT | PK (組合) | 系所代碼 |
| `ucan_cluster_id` | TEXT | PK (組合) | UCAN 職涯學群代碼 (如 UC_IT) |
| `ucan_cluster_name` | TEXT | NOT NULL | UCAN 職涯學群名稱 |
| `industry_id` | TEXT | PK (組合) | 對應之 7 大目標產業代碼 |
| `mapping_type` | TEXT | NOT NULL | 映射類型 (PRIMARY: 1.0, SECONDARY: 0.5) |
| `weight` | REAL | NOT NULL | 計算稀釋權重 (1.0 或 0.5) |
| `evidence` | TEXT | NOT NULL | 對應佐證條文與課綱依據 |

### 表 6：`industry_dynamics_mart` (產業動態集市 - Section 9)
| 欄位名稱 | 型態 | 鍵約束 | 說明 |
| :--- | :--- | :--- | :--- |
| `year` | INTEGER | PK (組合) | 年度 (109-113) |
| `district` | TEXT | PK (組合) | 行政區 (29 區或全體) |
| `industry_id` | TEXT | PK (組合) | 目標產業代碼 |
| `opening_count` | INTEGER | NOT NULL | 當期新設登記公司數 |
| `dissolution_count`| INTEGER | NOT NULL | 當期解散註銷公司數 |
| `capital_inc_count`| INTEGER | NOT NULL | 當期增資擴張公司數 |
| `beginning_stock` | INTEGER | NOT NULL | 期初現存公司存量 |
| `ending_stock` | INTEGER | NOT NULL | 期末登記公司存量 |
| `entry_rate` | REAL | NOT NULL | 新設公司率 (Opening / Stock) |
| `capital_exp_rate` | REAL | NOT NULL | 資本擴張率 (CapInc / Stock) |
| `exit_rate` | REAL | NOT NULL | 解散退場率 (Dissolution / Stock) |

### 表 7：`industry_momentum_mart` (產業擴張動能集市 - Section 11)
| 欄位名稱 | 型態 | 鍵約束 | 說明 |
| :--- | :--- | :--- | :--- |
| `industry_id` | TEXT | PRIMARY KEY | 目標產業代碼 |
| `industry_name` | TEXT | NOT NULL | 產業中文名稱 |
| `entry_rate` | REAL | NOT NULL | 113 年度新設率 |
| `entry_trend` | REAL | NOT NULL | 109-113 五年新設率趨勢斜率 |
| `capital_rate` | REAL | NOT NULL | 113 年度增資擴張率 |
| `capital_trend` | REAL | NOT NULL | 109-113 五年增資率趨勢斜率 |
| `exit_rate` | REAL | NOT NULL | 113 年度解散退場率 (風險參考) |
| `z_entry` | REAL | NOT NULL | 新設動能 Z-score |
| `z_capital` | REAL | NOT NULL | 資本擴張動能 Z-score |
| `demand_momentum` | REAL | NOT NULL | 需求擴張動能主分數 (0.5×Z_ent + 0.5×Z_cap) |

### 表 8：`mismatch_signal_mart` (供需錯配預警訊號集市 - Section 19, 20)
| 欄位名稱 | 型態 | 鍵約束 | 說明 |
| :--- | :--- | :--- | :--- |
| `industry_id` | TEXT | PRIMARY KEY | 目標產業代碼 |
| `industry_name` | TEXT | NOT NULL | 產業中文名稱 |
| `demand_momentum` | REAL | NOT NULL | 產業需求擴張動能 (Z_demand) |
| `supply_momentum` | REAL | NOT NULL | 高教人才供給動能 (Z_supply) |
| `mismatch` | REAL | NOT NULL | 錯配向量差值 (Demand - Supply) |
| `quadrant` | INTEGER | NOT NULL | 象限歸屬 (1:雙重擴張, 2:嚴重短缺, 3:雙重收縮, 4:相對過剩) |
| `quadrant_label` | TEXT | NOT NULL | 象限中文名稱 |
| `warning_level` | TEXT | NOT NULL | 預警等級 (High Warning, Medium Warning, Low Warning) |
| `evidence_summary` | TEXT | NOT NULL | 確定性佐證摘要 |

---

## 四、RESTful API 端點規格書 (API Specification)

基礎 URL：`http://127.0.0.1:8888`

### 1. 系統總覽與 KPI 指標
- **URL**：`GET /api/overview`
- **說明**：取得儀表板置頂核心數據（總存量、受監測系所、高警示產業數、雙軸動能氣壓計數據與錯配清單）。
- **Response 範例**：
  ```json
  {
    "total_companies_registered": 154284,
    "monitored_departments_count": 878,
    "high_warning_count": 2,
    "tiger_year_national_cliff": 156000,
    "tiger_year_cliff_drop_pct": -17.02,
    "mismatch_signals": [
      {
        "industry_id": "IND_MFG",
        "industry_name": "智慧製造與精密機械",
        "demand_momentum": -0.9466,
        "supply_momentum": 0.7801,
        "mismatch": -1.7267,
        "quadrant": 4,
        "quadrant_label": "第四象限：相對過剩壓力",
        "warning_level": "High Warning"
      }
    ]
  }
  ```

### 2. 產業動態觀測數據
- **URL**：`GET /api/industry-dynamics`
- **Query Parameters**：
  - `industry_id`（選填，預設空字串代表全部產業）
  - `district`（選填，預設空字串代表台中市全區）
- **Response 欄位**：`records`（歷年新設與增資統計）、`momentum_summary`（7大產業 113 年基準與 Z 分數）。

### 3. 台中空間需求分布
- **URL**：`GET /api/spatial-demand`
- **說明**：取得 29 行政區企業存量與產業聚落分布。
- **Response 欄位**：`allowed_districts`（29區清單）、`district_rankings`（存量遞減排行）、`industry_breakdown`（各區 7 大產業存量）。

### 4. 高教生源推估與學門
- **URL**：`GET /api/talent-supply`
- **說明**：取得 113 現況 vs 117 推估人才供給池對比、系所數與供給動能 Z 分數。

### 5. 供需錯配四象限監控
- **URL**：`GET /api/mismatch-signals`
- **說明**：取得供需錯配四象限散佈點、象限定義與 7 大目標產業完整預警資訊。

### 6. 確定性佐證回溯鏈
- **URL**：`GET /api/evidence?industry_id={IND_ID}`
- **說明**：傳入產業代碼，取得該產業完整的 5 級確定性佐證鏈（公式、中間值、培育系所名單、關聯商工登記樣本）。

### 7. AI 決策代理人智慧問答 (Jev 守門)
- **URL**：`POST /api/agent/query`
- **Request Body**：
  ```json
  {
    "question": "西屯區企業存量與新設動能如何？"
  }
  ```
- **Response 欄位**：`success`、`passed_guard`、`intent`、`answer`（包含政策建議與引用來源）、`verified_data`（底層確定性依據字典）。

### 8. 單一公司統編 GCIS 驗證 (Section 5.1)
- **URL**：`GET /api/gcis/verify-company?company_id={8碼統編}`
- **說明**：單一統編即時驗證登記現況與所屬目標產業。
