from abc import ABC, abstractmethod

from my_langchain.text.vector.base_embeddings import BaseEmbeddings


class AbsRAG_DB(ABC):
    def __init__(self, file_paths):
        self._initialized = False
        self._file_paths = file_paths
        self._splited_data = []

    @abstractmethod
    def init_rag_instance(self, embeddings: BaseEmbeddings = None):
        """Инициализация RAG инстанса (предварительная сборка/загрузка)"""
        pass

    @abstractmethod
    def split_into_chunks(self):
        pass

    @abstractmethod
    def get_relevant_text(self, question: str, embedding: BaseEmbeddings) -> str:
        pass

