 執好的，以下是移除所有表情符號後、正式版本的 README.md。
內容保持專業、條列清晰，適合放在 GitHub 或專案報告中。

⸻

Corrective RAG System — 緯創永續報告書智慧問答系統

專案簡介

本專案實作一個具備自我評估與主題適應能力的 RAG 系統（Corrective RAG），
結合 PDF 文件知識與即時外部搜尋，
可針對「緯創資通 2024 永續報告書」進行問答與分析，
並在無法由文件回答時，自動啟用網路補強。

系統核心邏輯源於 Corrective RAG (CRAG) 架構，
具備以下能力：
	1.	文件檢索 (Retrieval)：從本地向量資料庫中擷取最相關內容
	2.	文件評估 (Evaluation)：判斷文件是否足以回答問題（Correct / Ambiguous / Incorrect）
	3.	知識修正 (Correction)：
	•	正確 → 使用內部文件
	•	模糊 → 結合內外知識
	•	錯誤 → 改用外部搜尋
	4.	生成回覆 (Generation)：根據最終知識生成回答
	5.	主題偵測 (Domain Detection)：若問題與文件主題無關（如天氣、餐廳推薦），直接走外部搜尋。

⸻

系統架構流程

User Query (X)
   ↓
Domain Detection → 判斷是否屬於文件範圍
   ↓
[In-domain] → Retrieval → 評估文件正確性
      ├── Correct → 精煉內部知識 (k_in)
      ├── Ambiguous → 內部精煉 + 外部補強 (k_in + k_ex)
      └── Incorrect → 外部搜尋 (k_ex)
[Out-of-domain] → 直接外部搜尋 (k_ex)
   ↓
Generation → 輸出最終回答


⸻

專案結構

project/
│
├── Backend/
│   ├── data/
│   │   ├── 2024SustainabilityReportCH.pdf   # 緯創永續報告書
│   │   └── build_data.py                    # 建立向量資料庫
│   │
│   ├── RAG/
│   │   ├── corrective_rag_v9.py             # 主程式（CRAG + Domain Detection）
│   │   └── utils.py                         # 相關工具（可選）
│   │
│   └── main.py                              # 問答入口點
│
├── .venv/                                   # 虛擬環境
└── README.md


⸻

安裝與環境設定

1. 建立虛擬環境

python3 -m venv .venv
source .venv/bin/activate

2. 安裝依賴套件

pip install -r requirements.txt

若沒有 requirements.txt，可直接執行：

pip install langchain langchain-openai langchain-community faiss-cpu ddgs pypdf

3. 設定 OpenAI API Key

export OPENAI_API_KEY="你的_API_KEY"


⸻

建立文件向量資料庫

python Backend/data/build_data.py

此腳本會：
	•	讀取 2024SustainabilityReportCH.pdf
	•	切割為小段落（chunk）
	•	嵌入為向量
	•	儲存為 vector_store/

執行後可看到：

Loading PDF...
Split into 413 chunks.
Embedded batch 9/9
Vector DB saved to vector_store


⸻

啟動問答系統

python Backend/main.py

輸入你的問題，例如：

請輸入你的問題：緯創的永續報告書有什麼重點？

系統輸出：

此問題屬於文件範圍 → 使用內部檢索
Retrieved 4 candidate documents.
Evaluation result → Correct
使用內部知識 (k_in)

Final Answer:
緯創永續報告書重點包括資料透明化、ESG 準則對應、重大議題鑑別、內部治理與外部確信等。


⸻

外部搜尋範例

若問題與文件無關（例如「今天天氣如何？」），
系統會自動偵測並使用網路搜尋：

此問題不屬於文件範圍 → 將改用外部搜尋
Found 5 external results.

Final Answer:
根據中央氣象局資料，今日台北地區多雲時晴，氣溫約 27°C。


⸻

Corrective RAG 評估邏輯

狀態	判定邏輯	採用策略
Correct	文件主題一致且能回答	內部知識 (k_in)
Ambiguous	文件部分相關、資訊不足	內外混合 (k_in + k_ex)
Incorrect	文件與問題無關	外部搜尋 (k_ex)
Out-of-domain	問題不屬於文件範圍	直接外部搜尋


⸻

技術棧

類別	使用技術
向量資料庫	FAISS
語言模型	OpenAI GPT-4o
文件切割	RecursiveCharacterTextSplitter
文件處理	PyPDFLoader
外部搜尋	DDGS (DuckDuckGo Search)
自動評估	ChatOpenAI 自我評分
架構	Corrective RAG + Domain Detection


⸻

開發重點
	1.	模糊補強 (Ambiguous)：自動結合內外資料來源，避免「不確定回答」。
	2.	主題偵測 (Domain Detection)：篩選與報告書相關問題，避免浪費內部檢索資源。
	3.	可擴充性強：模組化設計，可輕鬆接入其他企業報告或新聞文件。
	4.	全中文互動：Prompt 與輸出皆為台灣中文語境，適用本地問答場景。

⸻

未來方向
	•	加入 Self-Reflective RAG（自我反思式生成）
	•	增加 Web 資料重排名（Reranking）
	•	整合多文件主題（多報告書支援）
	•	加入 Query Log 分析與問答信心統計

⸻

授權與使用

本專案為研究與教育用途。
如需應用於商業環境，請自行設定 API Key 並遵守 OpenAI 使用條款。

⸻

作者

Minrou Lin (林旻柔)
AI 專題開發者 | Corrective RAG 研究實作

⸻

是否希望我幫你補一份 requirements.txt（列出正確的套件與版本）一起附在這個 README？
這樣就能直接讓別人一鍵安裝並執行整個系統。
