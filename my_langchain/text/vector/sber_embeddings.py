from typing import List
from my_langchain.text.vector.base_embeddings import BaseEmbeddings
from ai_api.api.abstract_api import API

# Заглушка для Sber (можно реализовать аналогично)
class SberEmbeddings(BaseEmbeddings):
    def __init__(self, api: API):
        self.api_key = api.credentials

    def name(self):
        return "gigachat-embeddings"

    def repr(self):
        return "GigaChatEmbeddingFunction()"

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # Реализация для Sber AI
        return [[0.1] * 384 for _ in texts]  # заглушка

    def embed_query(self, text: str) -> List[float]:
        return [0.1] * 384  # заглушка