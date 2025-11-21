from typing import List

from ai_api.assistant.ai_model import AIModel, get_embeddings_class
from my_langchain.text.vector.base_embeddings import BaseEmbeddings
from my_langchain.text.vector.yandex_embeddings import YandexEmbeddings
from my_langchain.text.vector.local_embeddings import LocalEmbeddings
from my_langchain.text.vector.sber_embeddings import SberEmbeddings
from ai_api.api.abstract_api import API

class AIEmbeddings(BaseEmbeddings):
    """Универсальный адаптер для эмбеддингов"""

    def __init__(self, model_name: AIModel, api: API):
        # self.model_name = model_name
        # self.credentials = credentials
        # self._setup_embedding_model()
        self._embedder = get_embeddings_class(model_name)(api=api)

    def name(self):
        return self._embedder.name()

    def repr(self):
        return self._embedder.repr()

    # def _setup_embedding_model(self):
    #     """Настройка конкретной модели эмбеддингов"""
    #     if self.model_name == "yandex":
    #         self._embedder = YandexEmbeddings(credentials=self.credentials)
    #     elif self.model_name == "sber":
    #         self._embedder = SberEmbeddings(credentials=self.credentials)
    #     elif self.model_name == "local":
    #         self._embedder = LocalEmbeddings()
    #     else:
    #         raise ValueError(f"Неизвестная модель: {self.model_name}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._embedder.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._embedder.embed_query(text)