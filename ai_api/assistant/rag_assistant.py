from ai_api.assistant.ai_assistant import AIAssistant
from ai_api.assistant.ai_response import AIResponse
from ai_api.assistant.embeddings import AIEmbeddings
from ai_api.assistant.ai_model import create_rag_instance

class RAGAssistant(AIAssistant):
    def __init__(self, model_name, **kwargs):
        # Достаем RAG параметры ДО вызова super()
        file_paths = kwargs.get('file_paths', [])
        rag_model = kwargs.get('rag_model')

        if not file_paths:
            raise ValueError("RAGAssistant requires file_paths parameter")
        if not rag_model:
            raise ValueError("RAGAssistant requires rag_model parameter")

        # Убираем RAG параметры из kwargs чтобы super() их не получил
        rag_kwargs = {}
        for key in ['persist_directory', 'collection_name', 'index_name', 'nlist']:
            if key in kwargs:
                rag_kwargs[key] = kwargs.pop(key)

        # Теперь super() получит только AI-параметры
        super().__init__(model_name, **kwargs)

        self._closed = False
        self._file_paths = file_paths
        self._rag_model = rag_model
        self._embeddings = AIEmbeddings(model_name, self._api)

        # Создаем RAG instance
        self._rag_db = create_rag_instance(
            self._rag_model,
            self._file_paths,
            **rag_kwargs
        )

        self._rag_db.init_rag_instance(self._embeddings)

    def appendChatMessage(self, message):
        pass

    def sendChatMessage(self, message):
        context = self._rag_db.get_relevant_text(message,self._embeddings)
        prompt_template = f"""Используй следующий контекст чтобы ответить на вопрос:
        {context}
        Вопрос: {message}
        """
        return super().sendChatMessage(prompt_template)

    def sendVoiceMessage(self, audio_data):
        pass

    def appendVoiceMessage(self, audio_data):
        pass

    def synthesize_speech(self, text: str):
        pass

    def recognize_speech_from_file(self, audio_file_path: str):
        pass

    def recognize_speech(self, audio_data: bytes):
        pass

    @property
    def embeddings(self):
        return self._embeddings

    def generate_image(self, prompt: str, **kwargs) -> AIResponse:
        """Генерация изображения, возвращает ID операции или путь к файлу"""
        pass

    def get_image_result(self, operation_id: str) -> AIResponse:
        """Получение результата генерации по ID операции"""
        pass

    def generate_image_sync(self, prompt: str, **kwargs) -> AIResponse:
        """Синхронная генерация изображения (ожидание результата)"""
        pass

    def generate_and_save_image(self, prompt: str, output_path: str, **kwargs) -> AIResponse:
        """Генерация и сохранение изображения в файл"""
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Автоматическое сохранение при выходе из with"""
        self.save_rag_index()

    # def __del__(self):
    #     """Автоматическое сохранение при удалении объекта (fallback)"""
    #     if hasattr(self, '_closed') and not self._closed:
    #         self.save_rag_index()

    def save_rag_index(self):
        """Явное сохранение индекса"""
        if not self._closed and hasattr(self, '_rag_db') and self._rag_db is not None:
            # Проверяем является ли rag_db экземпляром FAISS
            if hasattr(self._rag_db, 'save_index'):
                print("Сохранение FAISS индекса...")
                self._rag_db.save_index()
            # Для ChromaDB сохранение не нужно - она persistent по умолчанию
            self._closed = True

