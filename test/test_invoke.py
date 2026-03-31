import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from langchain_classic.retrievers.ensemble import EnsembleRetriever
from langchain_community.retrievers.bm25 import BM25Retriever

from src.ingestion import load_all_documents, split_documents

load_dotenv()

# 1. Khởi tạo Embedding
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
    
# 2. Load FAISS
vectorstore = FAISS.load_local(
    "faiss_db", 
    embeddings, 
    allow_dangerous_deserialization=True
)
faiss_retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

documents = load_all_documents()
chunks = split_documents(documents)

bm25_retriever = BM25Retriever.from_documents(chunks)
bm25_retriever.k = 10



retriever = EnsembleRetriever(
    retrievers=[faiss_retriever, bm25_retriever],
    weights=[0.7, 0.3]
)

test_query = "Nghỉ phép"

try:
    # results sẽ là một danh sách các Document object
    results = retriever.invoke(test_query)
    
    print(f"✅ Tìm thấy tổng cộng: {len(results)} đoạn văn bản liên quan.")
    
    # 3. In thử 3 đoạn đầu tiên để kiểm tra nội dung
    for i, doc in enumerate(results[:3]):
        print(f"\n📍 Kết quả {i+1}:")
        print(f"Nội dung (trích đoạn): {doc.page_content[:200]}...")
        print(f"Nguồn: {doc.metadata.get('source', 'Không rõ')}")
            
except Exception as e:
    print(f"❌ Lỗi khi chạy Retriever: {e}")