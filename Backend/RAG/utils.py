from langchain.chains import RetrievalQA

def evaluate_confidence(result):
    """根據來源數量簡單判斷信心程度"""
    num_sources = len(result.get("source_documents", []))
    return "high" if num_sources >= 2 else "low"

def rebuild_with_new_docs(db, new_texts, retriever, llm):
    """更新向量庫並重新查詢"""
    if not new_texts:
        print("⚠️ No new documents to add — skipping FAISS update.")
        return retriever

    db.add_texts(new_texts)
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True)
    return qa