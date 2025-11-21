from typing import List, Dict
from my_langchain.text.vector.base_embeddings import BaseEmbeddings
import numpy as np

class Chroma:
    def __init__(self, embedding_function: BaseEmbeddings = None,collection_name: str = "default"):
        self.embedding_function = embedding_function
        self.documents = []
        self.embeddings = []
        self.collection_name = collection_name

    @classmethod
    def from_texts(cls, texts: List[str], embedding: BaseEmbeddings, collection_name: str = "default", **kwargs):
        """Создать базу из текстов"""
        chroma = cls(embedding_function=embedding, collection_name=collection_name)
        chroma.add_texts(texts)
        return chroma

    def add_texts(self, texts: List[str]):
        """Добавить тексты в базу (только если их еще нет)"""
        for text in texts:
            if text not in self.documents:  # Проверка на дубликаты
                embedding = self.embedding_function.embed_documents([text])[0]
                self.documents.append(text)
                self.embeddings.append(embedding)
                # print(f"Добавлен чанк: {text[:50]}...")
            # else:
            #     print(f"Чанк уже существует: {text[:50]}...")

    def count(self) -> int:
        """Количество записанных чанков (аналог _collection.count())"""
        return len(self.documents)

    def delete_collection(self) -> bool:
        """Полное удаление векторных данных"""
        self.documents.clear()
        self.embeddings.clear()
        # print(f"Коллекция '{self.collection_name}' полностью очищена")
        return True

    def similarity_search(self, query: str, k: int = 4):
        """Поиск похожих документов"""
        query_embedding = self.embedding_function.embed_query(query)

        # Вычисляем косинусное сходство
        similarities = []
        for doc_embedding in self.embeddings:
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            similarities.append(similarity)

        # Сортируем по убыванию сходства
        sorted_indices = np.argsort(similarities)[::-1]

        # Возвращаем топ-K документов
        results = []
        for i in range(min(k, len(self.documents))):
            idx = sorted_indices[i]
            results.append({
                "page_content": self.documents[idx],
                "metadata": {"similarity": similarities[idx]}
            })

        return results

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Вычисление косинусного сходства"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def max_marginal_relevance_search(
            self,
            query: str,
            k: int = 4,
            fetch_k: int = 20,
            lambda_mult: float = 0.5
    ) -> List[Dict]:
        """
        Max Marginal Relevance Search

        Args:
            query: поисковый запрос
            k: количество возвращаемых документов
            fetch_k: количество документов для первоначального отбора
            lambda_mult: баланс между релевантностью и разнообразием (0-1)
                        0 = только разнообразие, 1 = только релевантность
        """
        # 1. Получаем эмбеддинг запроса
        query_embedding = self.embedding_function.embed_query(query)

        # 2. Находим первоначальные fetch_k самых релевантных документов
        initial_docs = self.similarity_search(query, k=fetch_k)

        if not initial_docs:
            return []

        # 3. Преобразуем в удобный формат
        docs = [doc["page_content"] for doc in initial_docs]
        doc_embeddings = []
        for doc in initial_docs:
            # Находим соответствующий эмбеддинг документа
            for i, text in enumerate(self.documents):
                if text == doc["page_content"]:
                    doc_embeddings.append(self.embeddings[i])
                    break

        # 4. Применяем алгоритм MMR
        selected_indices = self._mmr(
            query_embedding,
            doc_embeddings,
            k,
            lambda_mult
        )

        # 5. Возвращаем выбранные документы
        results = []
        for idx in selected_indices:
            original_idx = self.documents.index(docs[idx])
            results.append({
                "page_content": docs[idx],
                "metadata": {
                    "similarity": self._cosine_similarity(query_embedding, doc_embeddings[idx]),
                    "mmr_selected": True
                }
            })

        return results

    def _mmr(
            self,
            query_embedding: List[float],
            doc_embeddings: List[List[float]],
            k: int,
            lambda_mult: float
    ) -> List[int]:
        """Алгоритм Max Marginal Relevance"""
        selected_indices = []

        # Вычисляем сходство каждого документа с запросом
        query_similarities = [
            self._cosine_similarity(query_embedding, doc_emb)
            for doc_emb in doc_embeddings
        ]

        # Выбираем самый релевантный документ первым
        best_index = np.argmax(query_similarities)
        selected_indices.append(best_index)

        # Выбираем остальные k-1 документов
        while len(selected_indices) < min(k, len(doc_embeddings)):
            best_score = -float('inf')
            best_index = -1

            for i in range(len(doc_embeddings)):
                if i in selected_indices:
                    continue

                # Релевантность запросу
                relevance = query_similarities[i]

                # Максимальное сходство с уже выбранными документами
                max_similarity_to_selected = 0.0
                for j in selected_indices:
                    similarity = self._cosine_similarity(doc_embeddings[i], doc_embeddings[j])
                    max_similarity_to_selected = max(max_similarity_to_selected, similarity)

                # MMR score
                mmr_score = lambda_mult * relevance - (1 - lambda_mult) * max_similarity_to_selected

                if mmr_score > best_score:
                    best_score = mmr_score
                    best_index = i

            if best_index != -1:
                selected_indices.append(best_index)

        return selected_indices