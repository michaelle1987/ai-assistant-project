import faiss
import numpy as np
import os
from pathlib import Path
from typing import List
import pickle

from ai_api.assistant.rag_db.abs_db import AbsRAG_DB
from my_langchain.text.recursive_character_text_splitter import RecursiveCharacterTextSplitter
from my_langchain.text.vector.base_embeddings import BaseEmbeddings

class InvertedFileIndex_RAG(AbsRAG_DB):
    """FAISS RAG с инвертированным файловым индексом (ускоренный поиск для больших коллекций)"""

    def __init__(self, file_paths: List[str], persist_directory: str = None, index_name: str = None,
                 nlist: int = 100):
        super().__init__(file_paths)

        # Автоматически генерируем имя индекса на основе хеша файлов
        if index_name is None:
            files_hash = self._compute_files_hash()
            self._index_name = f"ivf_index_{files_hash}"
        else:
            self._index_name = index_name

        self._nlist = nlist  # Количество кластеров для IVF
        self._dimension = 256

        # Автоматически определяем persist_directory если не передан
        if persist_directory is None:
            self._persist_directory = self._find_project_faiss_db_path()
        else:
            self._persist_directory = persist_directory

        os.makedirs(self._persist_directory, exist_ok=True)

        self._index = None
        self._documents = []
        self._metadatas = []
        self._vector_store_built = False

        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", "(?<=\. )"]
        )

        print(f"FAISS IVFIndex будет сохранен в: {self._persist_directory}")
        print(f"Имя индекса: {self._index_name}")

    def init_rag_instance(self, embeddings: BaseEmbeddings = None):
        """Инициализация FAISS IVF - загрузка или предварительная сборка"""
        if not self._initialized:
            print("Инициализация FAISS IVFIndex...")
            if embeddings is None:
                raise ValueError("Для FAISS инициализации требуются эмбеддинги")

            # Пытаемся загрузить существующий индекс
            if not self.load_index():
                print("Индекс не найден, строим новый...")
                # Принудительно строим индекс
                self._build_vector_store(embeddings)
                self.save_index()  # сразу сохраняем
            else:
                print("Индекс успешно загружен")

            self._initialized = True

    def _find_project_faiss_db_path(self) -> str:
        """Автоматически находит путь к faiss_db в корне проекта"""
        current_file = Path(__file__)

        for parent in current_file.parents:
            if parent.name == "PythonProject":
                project_root = parent
                faiss_db_path = project_root / "faiss_db" / "ivf_index"
                return str(faiss_db_path)

        default_path = current_file.parent / "faiss_db" / "ivf_index"
        print(f"Корень проекта не найден, используем путь по умолчанию: {default_path}")
        return str(default_path)

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

    def _build_vector_store(self, embeddings: BaseEmbeddings):
        """Построение векторного хранилища с IVF индексом"""
        chunks = self.split_into_chunks()

        if not chunks:
            print("Нет чанков для индексации")
            return

        # Получаем эмбеддинги для всех чанков
        print("Создание эмбеддингов для чанков...")
        chunk_embeddings = embeddings.embed_documents(chunks)

        # Определяем размерность
        if chunk_embeddings:
            self._dimension = len(chunk_embeddings[0])

        # Создаем IVF индекс
        quantizer = faiss.IndexFlatIP(self._dimension)
        self._index = faiss.IndexIVFFlat(quantizer, self._dimension, min(self._nlist, len(chunks)))

        # Преобразуем в numpy array и нормализуем
        embeddings_array = np.array(chunk_embeddings).astype('float32')
        faiss.normalize_L2(embeddings_array)

        # Обучаем индекс если достаточно данных
        if len(embeddings_array) >= self._nlist:
            print("Обучение IVF индекса...")
            self._index.train(embeddings_array)

        # Добавляем данные
        self._index.add(embeddings_array)

        # Сохраняем документы и метаданные
        self._documents = chunks
        self._metadatas = [{"chunk_id": i, "source": "file"} for i in range(len(chunks))]

        self._vector_store_built = True
        print(f"Построен FAISS IVFIndex с {len(chunks)} документами, {self._nlist} кластерами")

    def get_relevant_text(self, question: str, embedding: BaseEmbeddings) -> str:
        """Получить релевантные тексты для вопроса"""
        if not self._vector_store_built:
            self._build_vector_store(embedding)

        if self._index is None or len(self._documents) == 0:
            return "Векторное хранилище не построено или пустое"

        # Получаем эмбеддинг запроса
        query_embedding = embedding.embed_query(question)
        query_array = np.array([query_embedding]).astype('float32')
        faiss.normalize_L2(query_array)

        # Определяем количество результатов
        k = min(4 if len(question) > 20 else 3, len(self._documents))

        # Устанавливаем количество проходов по кластерам (nprobe)
        self._index.nprobe = min(10, self._nlist // 10)  # Ищем в 10% кластеров

        # Ищем похожие документы
        similarities, indices = self._index.search(query_array, k)

        # Собираем релевантные документы
        relevant_docs = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self._documents) and idx >= 0:  # Проверяем границы
                relevant_docs.append(self._documents[idx])

        if relevant_docs:
            return "\n\nФрагмент текста\n\n".join(relevant_docs)
        else:
            return "Релевантные фрагменты не найдены."

    def save_index(self):
        """Сохранить индекс на диск с метаданными файлов"""
        if self._index is not None:
            index_path = os.path.join(self._persist_directory, f"{self._index_name}.faiss")
            meta_path = os.path.join(self._persist_directory, f"{self._index_name}.pkl")

            # Сохраняем FAISS индекс
            faiss.write_index(self._index, index_path)

            # Сохраняем хеш файлов в метаданные
            files_hash = self._compute_files_hash()

            with open(meta_path, 'wb') as f:
                pickle.dump({
                    'documents': self._documents,
                    'metadatas': self._metadatas,
                    'dimension': self._dimension,
                    'nlist': self._nlist,
                    'files_hash': files_hash,  # добавляем хеш
                    'file_paths': self._file_paths  # и пути для отладки
                }, f)

            print(f"IVF индекс сохранен: {index_path}")

    def load_index(self):
        """Загрузить индекс с диска, проверяя актуальность"""
        index_path = os.path.join(self._persist_directory, f"{self._index_name}.faiss")
        meta_path = os.path.join(self._persist_directory, f"{self._index_name}.pkl")

        if os.path.exists(index_path) and os.path.exists(meta_path):
            # Проверяем что метаданные соответствуют текущим файлам
            with open(meta_path, 'rb') as f:
                data = pickle.load(f)

            # Сравниваем хеш сохраненного индекса с текущим
            if data.get('files_hash') == self._compute_files_hash():
                self._index = faiss.read_index(index_path)
                self._documents = data['documents']
                self._metadatas = data['metadatas']
                self._dimension = data['dimension']
                self._nlist = data['nlist']
                self._vector_store_built = True
                print(f"IVF индекс загружен: {index_path}, документов: {len(self._documents)}")
                return True
            else:
                print("Файлы изменились, требуется пересборка индекса")
                return False
        return False

    @property
    def persist_directory(self):
        return self._persist_directory

    def get_index_info(self):
        """Получить информацию об индексе"""
        if self._index is None:
            return "Индекс не инициализирован"

        return f"FAISS IVFIndex: {self._index.ntotal} документов, {self._nlist} кластеров"

    def _compute_files_hash(self) -> str:
        """Вычислить хеш содержимого всех файлов"""
        import hashlib
        hash_obj = hashlib.md5()
        for file_path in sorted(self._file_paths):  # сортируем для стабильности
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    content = f.read()
                    hash_obj.update(content)
        return hash_obj.hexdigest()[:16]  # берем первые 16 символов