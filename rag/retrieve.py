from langchain_community.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
from sentence_transformers import SentenceTransformer

# Local embeddings wrapper
class LocalHuggingFaceEmbeddings(Embeddings):
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        return self.model.encode(texts, convert_to_numpy=True).tolist()

    def embed_query(self, text):
        return self.model.encode([text], convert_to_numpy=True)[0].tolist()


def load_vectorstore():
    embeddings = LocalHuggingFaceEmbeddings()

    vectorstore = FAISS.load_local(
        "faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vectorstore
