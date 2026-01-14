from langchain_community.vectorstores import FAISS
from ingest import load_and_chunk_documents
from langchain.embeddings.base import Embeddings
from sentence_transformers import SentenceTransformer

class LocalHuggingFaceEmbeddings(Embeddings):
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        return self.model.encode(texts, convert_to_numpy=True).tolist()

    def embed_query(self, text):
        return self.model.encode([text], convert_to_numpy=True)[0].tolist()

def build_index():
    chunks = load_and_chunk_documents()

    embeddings = LocalHuggingFaceEmbeddings()

    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local("faiss_index")

    print("FAISS index saved.")

if __name__ == "__main__":
    build_index()
