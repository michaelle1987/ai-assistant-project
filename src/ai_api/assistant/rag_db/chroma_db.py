import chromadb
import os
from pathlib import Path
from typing import List
from chromadb.config import Settings
import uuid

from ai_api.assistant.rag_db.abs_db import AbsRAG_DB
from my_langchain.text.recursive_character_text_splitter import RecursiveCharacterTextSplitter
from my_langchain.text.vector.base_embeddings import BaseEmbeddings


class ChromaDB_RAG(AbsRAG_DB):
    def __init__(self, file_paths: List[str], persist_directory: str = None, collection_name: str = "rag_documents"):
        super().__init__(file_paths)
        self._collection_name = collection_name

        # Автоматически определяем persist_directory если не передан
        if persist_directory is None:
            self._persist_directory = self._find_project_chroma_db_path()
        else:
            self._persist_directory = persist_directory

        # Создаем директорию, если не существует
        os.makedirs(self._persist_directory, exist_ok=True)

        self._client = None
        self._collection = None
        self._vector_store_built = False
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", "(?<=\. )"]
        )

        print(f"ChromaDB будет сохранена в: {self._persist_directory}")

    def init_rag_instance(self, embeddings: BaseEmbeddings = None):
        """Инициализация ChromaDB - сразу разделяем на чанки"""
        if not self._initialized:
            print("Инициализация ChromaDB...")
            self._splited_data =self.split_into_chunks()  # ChromaDB требует предварительного разделения
            self._initialized = True

    def _find_project_chroma_db_path(self) -> str:
        """Автоматически находит путь к chroma_db в корне проекта"""
        current_file = Path(__file__)

        # Ищем корень проекта (PythonProject)
        for parent in current_file.parents:
            if parent.name == "PythonProject":
                project_root = parent
                chroma_db_path = project_root / "chroma_db"
                return str(chroma_db_path)

        # Если не нашли PythonProject, создаем chroma_db рядом с текущим файлом
        default_path = current_file.parent / "chroma_db"
        print(f"Корень проекта не найден, используем путь по умолчанию: {default_path}")
        return str(default_path)

    def _initialize_client(self):
        """Инициализация клиента ChromaDB"""
        if self._client is None:
            self._client = chromadb.PersistentClient(
                path=self._persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )

    def _get_or_create_collection(self, embedding_function=None):
        """Получить или создать коллекцию"""
        self._initialize_client()

        try:
            if embedding_function:
                self._collection = self._client.get_collection(
                    name=self._collection_name,
                    embedding_function=embedding_function
                )
            else:
                self._collection = self._client.get_collection(name=self._collection_name)
            print(f"Коллекция '{self._collection_name}' загружена")
        except Exception as e:
            print(f"Коллекция не найдена, создаем новую: {e}")
            if embedding_function:
                self._collection = self._client.create_collection(
                    name=self._collection_name,
                    embedding_function=embedding_function,
                    metadata={"hnsw:space": "cosine"}
                )
            else:
                self._collection = self._client.create_collection(
                    name=self._collection_name,
                    metadata={"hnsw:space": "cosine"}
                )

    def split_into_chunks(self):
        """Разделить документы на чанки"""
        all_chunks = []

        for file_path in self._file_paths:
            if not os.path.exists(file_path):
                print(f"Файл не найден: {file_path}")
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    doc_text = file.read()

                chunks = self._splitter.split_text(doc_text)
                all_chunks.extend(chunks)
                print(f"Файл {file_path} разделен на {len(chunks)} чанков")

            except Exception as e:
                print(f"Ошибка при обработке файла {file_path}: {e}")

        return all_chunks

    def _build_vector_store(self, embeddings):
        # chunks = self.split_into_chunks()

        class ConsistentEmbeddingFunction:
            def __init__(self, embeddings_model):
                self.embeddings_model = embeddings_model

            def __call__(self, input):
                """Используем embed_query для всего, как в SimpleChroma"""
                if isinstance(input, list):
                    texts = input
                else:
                    texts = input

                # ВАЖНО: используем embed_query для консистентности!
                results = []
                for text in texts:
                    embedding = self.embeddings_model.embed_query(text)
                    results.append(embedding)
                return results

            def name(self) -> str:
                return "consistent-yandex-embeddings"

        embedding_function = ConsistentEmbeddingFunction(embeddings)
        self._get_or_create_collection(embedding_function)

        # ChromaDB сама вычислит эмбеддинги через нашу function
        documents = []
        metadatas = []
        ids = []

        for i, chunk in enumerate(self._splited_data ):
            documents.append(chunk)
            metadatas.append({"chunk_id": i, "source": "file"})
            ids.append(str(uuid.uuid4()))

        self._collection.add(
            documents=documents,  # эмбеддинги вычисляются автоматически
            metadatas=metadatas,
            ids=ids
        )

    def get_relevant_text(self, question: str, embedding: BaseEmbeddings) -> str:
        """Получить релевантные тексты для вопроса"""
        if not self._vector_store_built:
            self._build_vector_store(embedding)

        # Для запроса используем embed_query
        query_embedding = embedding.embed_query(question)

        # Ищем похожие документы
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=4 if len(question) > 20 else 3, # 3 для простых вопросов, 4 для сложных многословных
            include=["documents", "metadatas", "distances"]
        )

        if results['documents'] and results['documents'][0]:
            relevant_docs = results['documents'][0]
            return "\n\nФрагмент текста\n\n".join(relevant_docs)
        else:
            return "Релевантные фрагменты не найдены."

    @property
    def persist_directory(self):
        """Свойство для доступа к пути базы данных извне"""
        return self._persist_directory

    def get_collection_info(self):
        """Получить информацию о коллекции"""
        if self._collection is None:
            return "Коллекция не инициализирована"

        count = self._collection.count()
        return f"Коллекция '{self._collection_name}': {count} документов"

    def delete_collection(self):
        """Удалить коллекцию"""
        if self._client and self._collection:
            self._client.delete_collection(self._collection_name)
            self._collection = None
            self._vector_store_built = False
            print(f"Коллекция '{self._collection_name}' удалена")