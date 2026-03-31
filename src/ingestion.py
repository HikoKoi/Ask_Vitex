import os
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


def load_all_documents():
    path = 'data'

    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Thư mục '{path}' vừa được tạo. Hãy bỏ file quy chế vào đó rồi chạy lại!")
        return []

    loaders = {'.pdf': PyPDFLoader, '.docx': Docx2txtLoader}
    docs = []
    for file in os.listdir(path):
        ext = os.path.splitext(file)[1].lower()
        if ext in loaders:
            loader = loaders[ext](os.path.join(path, file))
            docs.extend(loader.load())
    return docs

def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500) #separators=["\n\n", "\n", ".", " "]
    chunks = splitter.split_documents(documents)
    return chunks

def run_ingestion():
    documents = load_all_documents()
    if not documents:
        print("Không tìm thấy file PDF hay DOCX nào trong thư mục data!")
        return

    # 2. Cắt nhỏ
    chunks = split_documents(documents)

    # 3. Embedding & Save
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    
    print("Đang xây dựng kho vector FAISS...")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    vectorstore.save_local("faiss_db")
    print("Đã tạo xong faiss_db! Giờ bạn có thể chạy rag_engine.py.")

if __name__ == "__main__":
    run_ingestion()