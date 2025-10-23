好的，這是一份經過重新編排，適合直接用於 GitHub 專案的 `README.md` 內容。我使用 Markdown 格式來強化結構和閱讀性。

````markdown
# Corrective RAG System — 緯創永續報告書智慧問答系統

## 專案簡介
本專案實作一個具備**自我評估與主題適應能力**的 RAG 系統（Corrective RAG, CRAG），旨在為「緯創資通 2024 永續報告書」提供精準、可靠的問答與分析服務。

系統核心邏輯源於 Corrective RAG (CRAG) 架構，結合本地 PDF 文件知識與即時外部搜尋，能在文件知識不足時自動進行網路補強，並具備以下核心能力：

1. **文件檢索 (Retrieval)**：從本地向量資料庫中擷取最相關內容。
2. **文件評估 (Evaluation)**：判斷文件是否足以回答問題（Correct / Ambiguous / Incorrect）。
3. **知識修正 (Correction)**：根據評估結果，決定只用內部文件、內外混合、或完全使用外部搜尋。
4. **主題偵測 (Domain Detection)**：若問題與文件主題無關（Out-of-domain），直接啟用外部搜尋，節省資源。
5. **生成回覆 (Generation)**：根據最終知識來源生成高品質回答。

---

## 系統架構流程
專案流程圖示如下：

```mermaid
graph TD
    A[User Query (X)] --> B{Domain Detection};
    B -- In-domain --> C[Retrieval];
    B -- Out-of-domain --> I[外部搜尋 (k_ex)];
    C --> D{Evaluation};
    D -- Correct --> E[精煉內部知識 (k_in)];
    D -- Ambiguous --> F[內部精煉 + 外部補強 (k_in + k_ex)];
    D -- Incorrect --> G[外部搜尋 (k_ex)];
    E --> H[Generation];
    F --> H;
    G --> H;
    I --> H;
    H --> J[輸出最終回答];
````

### Corrective RAG 評估邏輯

| 狀態 | 判定邏輯 | 採用策略 | 知識來源 |
| :--- | :--- | :--- | :--- |
| **Correct** | 文件主題一致且能回答 | 內部知識 | $k_{in}$ |
| **Ambiguous** | 文件部分相關、資訊不足 | 內外混合 | $k_{in} + k_{ex}$ |
| **Incorrect** | 文件與問題無關 | 外部搜尋 | $k_{ex}$ |
| **Out-of-domain** | 問題不屬於文件範圍 | 直接外部搜尋 | $k_{ex}$ |

-----

## 專案結構

```
project/
│
├── Backend/
│   ├── data/
│   │   ├── 2024SustainabilityReportCH.pdf   # 緯創永續報告書 (知識來源)
│   │   └── build_data.py                    # 建立向量資料庫腳本
│   │
│   ├── RAG/
│   │   ├── corrective_rag_v9.py             # 主程式（CRAG + Domain Detection 核心邏輯）
│   │   └── utils.py                         # 相關工具程式
│   │
│   └── main.py                              # 問答系統入口點
│
├── .venv/                                   # 虛擬環境目錄
└── README.md
```

-----

## 安裝與環境設定

### 1\. 建立與啟動虛擬環境

```bash
# 建立虛擬環境
python3 -m venv .venv

# 啟動虛擬環境
source .venv/bin/activate
```

### 2\. 安裝依賴套件

若專案根目錄下有 `requirements.txt`：

```bash
pip install -r requirements.txt
```

若沒有，可直接安裝必要套件：

```bash
pip install langchain langchain-openai langchain-community faiss-cpu pypdf duckduckgo-search
```

> **備註**: 這裡將 `ddgs` 替換為 `duckduckgo-search`，這是較常用的套件名稱。

### 3\. 設定 OpenAI API Key

請將您的 OpenAI API Key 設定為環境變數：

```bash
export OPENAI_API_KEY="你的_API_KEY"
```

-----

## 執行步驟

### 1\. 建立文件向量資料庫

執行腳本，將 PDF 文件轉換為可供檢索的向量資料庫（`vector_store/`）：

```bash
python Backend/data/build_data.py
```

**預期輸出範例:**

```
Loading PDF...
Split into 413 chunks.
Embedded batch 9/9
Vector DB saved to vector_store
```

### 2\. 啟動問答系統

執行 `main.py` 啟動互動式問答系統：

```bash
python Backend/main.py
```

**內部檢索範例 (Correct):**

```
請輸入你的問題：緯創的永續報告書有什麼重點？

系統輸出：
此問題屬於文件範圍 → 使用內部檢索
Retrieved 4 candidate documents.
Evaluation result → Correct
使用內部知識 (k_in)

Final Answer:
緯創永續報告書重點包括資料透明化、ESG 準則對應、重大議題鑑別、內部治理與外部確信等。
```

**外部搜尋範例 (Out-of-domain):**

```
請輸入你的問題：今天天氣如何？

系統輸出：
此問題不屬於文件範圍 → 將改用外部搜尋
Found 5 external results.

Final Answer:
根據中央氣象局資料，今日台北地區多雲時晴，氣溫約 27°C。
```

-----

## 技術棧

| 類別 | 使用技術 |
| :--- | :--- |
| **向量資料庫** | FAISS |
| **語言模型** | OpenAI GPT-4o (用於生成與自我評估) |
| **RAG 框架** | LangChain |
| **外部搜尋** | DDGS (DuckDuckGo Search) |
| **文件處理** | PyPDFLoader / RecursiveCharacterTextSplitter |
| **核心架構** | Corrective RAG (CRAG) + Domain Detection |

-----

## 開發重點

  * **模糊補強 (Ambiguous)**：自動結合內部報告書與外部網路資訊，避免因內部資訊不足而產生「不確定回答」。
  * **主題偵測 (Domain Detection)**：精準篩選與報告書相關問題，避免浪費內部檢索資源處理閒聊或無關主題。
  * **可擴充性強**：模組化設計，可輕鬆接入其他企業報告或新聞文件。
  * **全中文互動**：Prompt 與輸出皆為台灣中文語境，適用本地問答場景。

## 未來方向

  * 加入 **Self-Reflective RAG**（自我反思式生成）機制。
  * 增加 Web 資料重排名（Reranking）以優化外部搜尋結果。
  * 整合多文件主題（支援多份報告書或不同公司文件）。
  * 加入 Query Log 分析與問答信心統計。

## 授權與使用

本專案主要用於研究與教育用途。
如需應用於商業環境，請自行設定 API Key 並遵守 OpenAI 使用條款及其他相關服務的授權規定。

```
```
