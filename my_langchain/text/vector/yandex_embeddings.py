import requests
import numpy as np
from typing import List
import time
from my_langchain.text.vector.base_embeddings import BaseEmbeddings
from ai_api.api.abstract_api import API

class YandexEmbeddings(BaseEmbeddings):
    """Эмбеддинги через Yandex Embeddings API с поддержкой doc/query типов"""

    def __init__(self, api: API):
        self.folder_id = 'b1goe0ht2mcgvsi5hgfd'
        self._api = api
        self.embed_url = "https://llm.api.cloud.yandex.net:443/foundationModels/v1/textEmbedding"

        # URI для разных типов эмбеддингов
        self.doc_uri = f"emb://{self.folder_id}/text-search-doc/latest"
        self.query_uri = f"emb://{self.folder_id}/text-search-query/latest"

        self._setup_headers()

    def name(self):
        return "yandex-embeddings"

    def repr(self):
        return "YandexEmbeddingFunction()"

    def _setup_headers(self):
        """Настройка заголовков для аутентификации"""
        if self._api.credentials:
            self.headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._api.credentials}",
                "x-folder-id": self.folder_id
            }
        else:
            raise ValueError("Необходим IAM-токен")

    def _get_embedding(self, text: str, text_type: str = "doc") -> List[float]:
        """Получить эмбеддинг для текста"""
        model_uri = self.doc_uri if text_type == "doc" else self.query_uri

        data = {
            "modelUri": model_uri,
            "text": text,
        }

        try:
            self._setup_headers()
            response = self._api.embedding_post(self.embed_url, data, self.headers, 30)
            response.raise_for_status()

            embedding_data = response.json()
            return embedding_data["embedding"]

        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса к Yandex Embeddings: {e}")
            raise
        except KeyError:
            print(f"Неверный ответ от API: {response.text}")
            raise
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            raise

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Создать эмбеддинги для документов (text-search-doc)"""
        embeddings = []

        for i, text in enumerate(texts):
            try:
                embedding = self._get_embedding(text, text_type="doc")
                embeddings.append(embedding)

                # Небольшая задержка чтобы не превысить лимиты API
                if i < len(texts) - 1:
                    time.sleep(0.1)

            except Exception as e:
                print(f"Ошибка при обработке документа {i}: {e}")
                # Добавляем нулевой эмбеддинг в случае ошибки
                embeddings.append([0.0] * 256)  # предположительная размерность

        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """Создать эмбеддинг для запроса (text-search-query)"""
        return self._get_embedding(text, text_type="query")


class YandexEmbeddingsSimple(BaseEmbeddings):
    """Упрощенная версия Yandex Embeddings (без разделения doc/query)"""

    def __init__(self, iam_token: str = None):
        self.folder_id = 'b1goe0ht2mcgvsi5hgfd'
        self.iam_token = iam_token
        self.embed_url = "https://llm.api.cloud.yandex.net:443/foundationModels/v1/textEmbedding"
        self.model_uri = f"emb://{self.folder_id}/text-search-doc/latest"  # используем doc для всего

        self._setup_headers()

    def _setup_headers(self):
        if self.iam_token:
            self.headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.iam_token}",
                "x-folder-id": self.folder_id
            }
        else:
            raise ValueError("Необходим IAM-токен")

    def _get_embedding(self, text: str) -> List[float]:
        data = {
            "modelUri": self.model_uri,
            "text": text,
        }

        response = requests.post(self.embed_url, json=data, headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.json()["embedding"]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            embedding = self._get_embedding(text)
            embeddings.append(embedding)
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        return self._get_embedding(text)