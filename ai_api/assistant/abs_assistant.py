from abc import ABC, abstractmethod
from ai_api.api.abstract_api import VoiceAPI, ImageAPI
from ai_api.assistant.ai_model import AIModel, get_api_class
from ai_api.assistant.ai_response import AIResponse


class AbsAssistant(ABC):
    def __init__(self,model_name: AIModel,**kwargs):
        self._model_name = model_name
        api_class = get_api_class(model_name)  # метод get не выдает ошибку на неизвестный ключ, но возвращает None

        if api_class is None:
            raise ValueError(f"Unsupported model: {model_name}")

        if kwargs.get('json_schema') is not None:
            self._api = api_class(kwargs.get('json_schema')+"\r\n" +kwargs.get('system_prompt'), kwargs.get('json_schema'))
        else:
            self._api = api_class(kwargs.get('system_prompt'))
        self._has_voice = isinstance(self._api, VoiceAPI)
        self._has_image_generation = isinstance(self._api, ImageAPI)
        self._history_messages = ''

    @property
    def model_name(self):
        return self._model_name.value

    @model_name.setter
    def model_name(self, value):
        if not value:
            raise ValueError("Model name cannot be empty")
        self._model_name = value

    @property
    def system_prompt(self):
        return "Системный промпт (инструкция):" + self._api._system_prompt

    @system_prompt.setter
    def system_prompt(self, value):
        self._api._system_prompt = value

    @property
    def json_schema(self):
        return self._api.json_schema

    @json_schema.setter
    def json_schema(self, value):
        self._api.json_schema = value

    @property
    def history_messages(self):
        if self._history_messages is None:
            return ''
        return self._history_messages

    def clearHistoryMessages(self):
        self._history_messages=''

    def has_voice_support(self) -> bool:
        return self._has_voice

    def has_image_generation(self) -> bool:
        return self._has_image_generation

    @abstractmethod
    def appendChatMessage(self, message):
        pass

    @abstractmethod
    def sendChatMessage(self, message):
        pass

    @abstractmethod
    def sendVoiceMessage(self, audio_data):
        pass

    @abstractmethod
    def appendVoiceMessage(self, audio_data):
        pass

    @abstractmethod
    def synthesize_speech(self, text: str):
        pass

    @abstractmethod
    def recognize_speech_from_file(self, audio_file_path: str):
        pass

    @abstractmethod
    def recognize_speech(self, audio_data: bytes):
        pass

    @property
    @abstractmethod
    def embeddings(self):
        pass

    @abstractmethod
    def generate_image(self, prompt: str, **kwargs) -> AIResponse:
        """Генерация изображения, возвращает ID операции или путь к файлу"""
        pass

    @abstractmethod
    def get_image_result(self, operation_id: str) -> AIResponse:
        """Получение результата генерации по ID операции"""
        pass

    @abstractmethod
    def generate_image_sync(self, prompt: str, **kwargs) -> AIResponse:
        """Синхронная генерация изображения (ожидание результата)"""
        pass

    @abstractmethod
    def generate_and_save_image(self, prompt: str, output_path: str, **kwargs) -> AIResponse:
        """Генерация и сохранение изображения в файл"""
        pass

