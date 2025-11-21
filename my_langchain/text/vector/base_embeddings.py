from abc import ABC, abstractmethod
from typing import List

class BaseEmbeddings(ABC):
    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Создать эмбеддинги для документов"""
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Создать эмбеддинг для запроса"""
        pass

    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def repr(self):
        pass
