from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import math

def build_vectorstore_from_pdf(pdf_path, save_path="vector_store", batch_size=50):
    """從 PDF 建立向量資料庫（分批嵌入，避免超出 token 限制）"""
    print(f"Loading PDF: {pdf_path}")
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    print(f"Loaded {len(pages)} pages from PDF.")

    # Step 1: 切割文字成小段
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", "。", "！", "？"]
    )
    split_docs = text_splitter.split_documents(pages)
    print(f"Split into {len(split_docs)} chunks.")

    # Step 2: 批次處理嵌入
    embeddings = OpenAIEmbeddings()
    db = None  # 初始化向量資料庫

    print(f"Starting batched embedding (batch size={batch_size})...")
    for i in range(0, len(split_docs), batch_size):
        batch_docs = split_docs[i:i+batch_size]
        batch_texts = [doc.page_content for doc in batch_docs]
        batch_metadatas = [doc.metadata for doc in batch_docs]

        # 嵌入這一批
        batch_vectors = embeddings.embed_documents(batch_texts)

        # 若第一次，建立新的 FAISS；否則加入現有資料庫
        if db is None:
            # FAISS 是由 Meta 開發的開源函式庫，用於高效能的相似度搜索和密集向量聚類庫
            db = FAISS.from_texts(batch_texts, embeddings, metadatas=batch_metadatas)
        else:
            db.add_texts(batch_texts, metadatas=batch_metadatas)

        print(f"Embedded batch {math.ceil(i/batch_size)+1}/{math.ceil(len(split_docs)/batch_size)}")

    # Step 3: 儲存資料庫
    db.save_local(save_path)
    print(f"Vector DB saved to {save_path}")

    return db


if __name__ == "__main__":
    pdf_file = "Backend/data/2024SustainabilityReportCH.pdf"
    build_vectorstore_from_pdf(pdf_file)