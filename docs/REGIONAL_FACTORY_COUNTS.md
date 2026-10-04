# 區域同業工廠家數

`GET /api/regional-peer-density?district=大雅區&year=113&industry_code=29`
回傳已匯入的經濟部工廠校正及營運調查快照。既有 `DISTRICT_QUERY`
亦改用同一工具，無資料時不再讀取模擬產業資料。

資料來源：https://service.moea.gov.tw/EE520/investigate/InvestigateG.aspx

目前人工核對並轉錄的範圍：大雅區、行業中類29機械設備業。

| 年度 | 營運中工廠家數 |
| --- | ---: |
| 111 | 207 |
| 112 | 211 |
| 113 | 219 |

`data/raw/factory_counts.csv` 為可擴充的輸入；資料版本不是即時 API。
缺資料回傳 `no_data` 與 `factory_count: null`，保密符號 `*`、無值符號
`-` 回傳未知值；重複年度／行政區／行業紀錄會拒絕處理。
未指定行業時，只列出已匯入行業，不能視為全區總數。

本工具先提供同類營運中工廠家數，未使用面積計算地理密度。
工廠家數不等於公司家數、徵才需求、搶人壓力或缺工人數。
精密機械在問答原型暫對應29機械設備業，並非更細的精密機械子產業。

`ui/factory-assessment.html` 為離線評估原型，同業卡片嵌入同一官方
快照，其他指標仍清楚標示為示範。此頁尚未串接後端 API。
舊 `/api/spatial-demand`、原本首頁與靜態部署的問答備援尚未改接。
其他三個工具與教育部人才供給工具維持原有實作。

驗證：`python tests/test_factory_density.py`。此項測試不依賴 pandas
或完整後端環境；尚未驗證完整 API 啟動與部署。
