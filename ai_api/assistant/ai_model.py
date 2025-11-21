from enum import Enum
from typing import Dict, Type, Optional, Any


class AIModel(Enum):
    YANDEX_GPT = "YandexGPT"
    DEEP_SEEK = "DeepSeek"
    GIGA_CHAT = "GigaChat"


class RAGModel(Enum):
    CHROMA_DB = "ChromaDB"
    FLAT_INDEX = "FlatIndex"
    INVERTED_FILE_INDEX = "InvertedFileIndex"


# Динамически загружаем все API классы
_API_MAP: Dict[AIModel, Type] = {}
_EMBEDDINGS_MAP: Dict[AIModel, Type] = {}
_RAG_MAP: Dict[RAGModel, Type] = {}

# Пробуем загрузить Яндекс GPT
try:
    from ai_api.api.yandexgpt_api import YandexGPT_APIWithTokenRefresh
    _API_MAP[AIModel.YANDEX_GPT] = YandexGPT_APIWithTokenRefresh
    # print("✅ YandexGPT loaded")
except ImportError as e:
    print(f"❌ YandexGPT not available: {e}")

# Пробуем загрузить DeepSeek
try:
    from ai_api.api.deepseek_api import DeepSeekAPI
    _API_MAP[AIModel.DEEP_SEEK] = DeepSeekAPI
    # print("✅ DeepSeek loaded")
except ImportError as e:
    print(f"❌ DeepSeek not available: {e}")

# Пробуем загрузить GigaChat
try:
    from ai_api.api.gigachat_api import GigaChatAPI
    _API_MAP[AIModel.GIGA_CHAT] = GigaChatAPI
    # print("✅ GigaChat loaded")
except ImportError as e:
    print(f"❌ GigaChat not available: {e}")

# Пробуем загрузить эмбеддинги
try:
    from my_langchain.text.vector.yandex_embeddings import YandexEmbeddings
    if AIModel.YANDEX_GPT in _API_MAP:
        _EMBEDDINGS_MAP[AIModel.YANDEX_GPT] = YandexEmbeddings
    # print("✅ YandexEmbeddings loaded")
except ImportError as e:
    print(f"❌ YandexEmbeddings not available: {e}")

try:
    from my_langchain.text.vector.sber_embeddings import SberEmbeddings
    if AIModel.GIGA_CHAT in _API_MAP:
        _EMBEDDINGS_MAP[AIModel.GIGA_CHAT] = SberEmbeddings
    # print("✅ SberEmbeddings loaded")
except ImportError as e:
    print(f"❌ SberEmbeddings not available: {e}")

# Пробуем загрузить RAG базы данных
try:
    from ai_api.assistant.rag_db.chroma_db import ChromaDB_RAG
    _RAG_MAP[RAGModel.CHROMA_DB] = ChromaDB_RAG
    # print("✅ ChromaDB_RAG loaded")
except ImportError as e:
    print(f"❌ ChromaDB_RAG not available: {e}")

try:
    from ai_api.assistant.rag_db.flat_index import FlatIndex_RAG
    _RAG_MAP[RAGModel.FLAT_INDEX] = FlatIndex_RAG
    # print("✅ FlatIndex_RAG loaded")
except ImportError as e:
    print(f"❌ FlatIndex_RAG not available: {e}")

try:
    from ai_api.assistant.rag_db.inverted_file_index import InvertedFileIndex_RAG
    _RAG_MAP[RAGModel.INVERTED_FILE_INDEX] = InvertedFileIndex_RAG
    # print("✅ InvertedFileIndex_RAG loaded")
except ImportError as e:
    print(f"❌ InvertedFileIndex_RAG not available: {e}")


def get_api_class(model: AIModel) -> Type:
    """Безопасное получение класса API"""
    if model not in _API_MAP:
        available = list(_API_MAP.keys())
        raise ValueError(f"Unsupported model: {model}. Available: {available}")
    return _API_MAP[model]


def get_available_models() -> list[AIModel]:
    """Список доступных моделей"""
    return list(_API_MAP.keys())


def get_embeddings_class(model: AIModel) -> Optional[Type]:
    """Безопасное получение класса эмбеддингов"""
    return _EMBEDDINGS_MAP.get(model)


def get_available_embeddings() -> list[AIModel]:
    """Список доступных эмбеддингов"""
    return list(_EMBEDDINGS_MAP.keys())


def get_rag_class(model: RAGModel) -> Type:
    """Безопасное получение класса RAG базы данных"""
    if model not in _RAG_MAP:
        available = list(_RAG_MAP.keys())
        raise ValueError(f"Unsupported RAG model: {model}. Available: {available}")
    return _RAG_MAP[model]


def get_available_rag_models() -> list[RAGModel]:
    """Список доступных RAG моделей"""
    return list(_RAG_MAP.keys())


def create_rag_instance(model: RAGModel, file_paths: list, **kwargs) -> Any:
    """Создание экземпляра RAG базы данных"""
    rag_class = get_rag_class(model)
    return rag_class(file_paths, **kwargs)


# Проверяем что хотя бы одна модель доступна
if not _API_MAP:
    raise ImportError("No AI models available! Check your dependencies.")

if not _RAG_MAP:
    print("⚠️ No RAG models available! RAG functionality will be limited.")
