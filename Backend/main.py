from RAG.corrective_rag import run_corrective_rag_v8


# ============ 測試入口 ============
if __name__ == "__main__":
    query = input("請輸入你的問題：")
    run_corrective_rag_v8(query)


    """ 
    query = "緯創在2024年永續報告書中提到的淨零排放目標是什麼？"
    """

  