from typing import List
from my_langchain.text.vector.base_embeddings import BaseEmbeddings

class LocalEmbeddings(BaseEmbeddings):
    """Локальные эмбеддинги через sentence-transformers"""

    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
        except ImportError:
            raise ImportError("Установите sentence-transformers: pip install sentence-transformers")

    def name(self):
        return "local-embeddings"

    def repr(self):
        return "LocalEmbeddingFunction()"

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        embedding = self.model.encode([text])
        return embedding[0].tolist()