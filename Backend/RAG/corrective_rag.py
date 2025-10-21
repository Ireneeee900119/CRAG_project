from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document
from ddgs import DDGS

def detect_domain(llm, query):
    """
    檢查使用者問題是否屬於「內部文件」主題，例如緯創、ESG、報告書等。
    回傳值: "internal" 或 "external"
    """
    prompt = f"""
    你是一個分類器，負責判斷問題是否屬於企業永續報告書或公司內容相關主題。
    問題若與企業、報告書、ESG、環保、永續、公司治理、緯創有關，
    回答 "internal"；否則回答 "external"。

    問題：{query}
    """
    result = llm.invoke(prompt)
    decision = result.content.strip().lower()

    if "external" in decision:
        print("🌐 此問題不屬於文件範圍 → 將改用外部搜尋")
        return "external"
    else:
        print("📄 此問題屬於文件範圍 → 使用內部檢索")
        return "internal"

# ============ 1️⃣ Retrieval：文件檢索 ============
def retrieve_documents(query):
    embeddings = OpenAIEmbeddings()
    db = FAISS.load_local("vector_store", embeddings, allow_dangerous_deserialization=True)
    retriever = db.as_retriever(search_kwargs={"k": 4})
    docs = retriever.get_relevant_documents(query)
    print(f"📚 Retrieved {len(docs)} candidate documents.")
    return docs, embeddings


# ============ 2️⃣ Evaluation：文件正確性評估 ============
def evaluate_retrieval_quality(llm, query, docs):
    """
    請 LLM 判斷文件是否「正確」「模糊」「錯誤」
    """
    joined_docs = "\n\n".join([d.page_content for d in docs[:3]])
    eval_prompt = f"""
    你是一位資料品質檢查員，任務是評估以下文件是否能回答使用者的問題。
    Question: {query}
    Documents: {joined_docs}

    請回答三擇一：
    - "Correct" ：文件內容完整且明確回答問題
    - "Ambiguous" ：文件內容部分相關或資訊不足
    - "Incorrect" ：文件與問題無關或誤導

    只輸出其中一個字詞。
    """
    response = llm.invoke(eval_prompt)
    decision = response.content.strip()
    print(f"🔎 Evaluation result → {decision}")
    return decision


# ============ 3️⃣ Knowledge Correction：知識修正 ============
def refine_internal_knowledge(docs):
    """模擬內部精煉：整合並過濾 PDF 內容"""
    combined_text = "\n".join([d.page_content for d in docs])
    return Document(page_content=combined_text, metadata={"source": "internal"})


def search_external_knowledge(query, max_results=5):
    """外部搜尋補強"""
    print("🌐 Searching external sources...")
    try:
        with DDGS() as ddgs:
            results = [
                f"{r.get('title', '')}: {r.get('body', '')}"
                for r in ddgs.text(query, max_results=max_results)
            ]
        if not results:
            print("⚠️ No external results found.")
            return []
        else:
            print(f"🔍 Found {len(results)} external results.")
            combined_text = "\n".join(results)
            return [Document(page_content=combined_text, metadata={"source": "external"})]
    except Exception as e:
        print("❌ Search failed:", e)
        return []


def combine_knowledge(k_in, k_ex):
    """將內部與外部知識整合"""
    combined = k_in.page_content + "\n\n" + k_ex[0].page_content
    return Document(page_content=combined, metadata={"source": "hybrid"})


# ============ 4️⃣ Generation：最終答案生成 ============
def generate_answer(llm, query, context_doc):
    qa_prompt = f"""
    根據以下內容回答使用者的問題。
    若內容無法提供答案，請誠實回答「文件中無相關資訊」。

    Context:
    {context_doc.page_content}

    Question:
    {query}
    """
    response = llm.invoke(qa_prompt)
    return response.content.strip()


# ============ 主流程整合 ============
def run_corrective_rag_v8(query):
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    # Step 0: Domain Detection
    domain = detect_domain(llm, query)

    if domain == "external":
    # 不用檢索，直接用外部搜尋
        k_ex = search_external_knowledge(query)
        if k_ex:
            print("\n💬 正在生成最終回答（外部資料）...")
            final_answer = generate_answer(llm, query, k_ex[0])
            print("\n🟩 Final Answer:")
            print(final_answer)
            return final_answer
        else:
            return "無法在外部資料中找到答案。"

    # Step 1: Retrieval
    docs, embeddings = retrieve_documents(query)

    # Step 2: Evaluation
    eval_result = evaluate_retrieval_quality(llm, query, docs)

    # Step 3: Knowledge Correction
    if eval_result == "Correct":
        print("✅ 使用內部知識 (k_in)")
        k_in = refine_internal_knowledge(docs)
        context = k_in

    elif eval_result == "Ambiguous":
        print("⚠️ 文件資訊模糊，執行內部精煉 + 外部補強 (k_in + k_ex)")
        k_in = refine_internal_knowledge(docs)
        k_ex = search_external_knowledge(query)
        if k_ex:
            context = combine_knowledge(k_in, k_ex)
        else:
            context = k_in  # 若搜尋失敗，僅使用內部知識

    elif eval_result == "Incorrect":
        print("🚫 文件錯誤，改用外部搜尋 (k_ex)")
        k_ex = search_external_knowledge(query)
        if k_ex:
            context = k_ex[0]
        else:
            return "抱歉，無法從內部或外部找到相關資訊。"

    else:
        print("⚠️ 評估結果不明，預設使用內部知識。")
        k_in = refine_internal_knowledge(docs)
        context = k_in

    # Step 4: Generation
    print("\n💬 正在生成最終回答...")
    final_answer = generate_answer(llm, query, context)

    print("\n🟩 Final Answer:")
    print(final_answer)
    return final_answer

