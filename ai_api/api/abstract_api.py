from abc import ABC, abstractmethod
from typing import Dict

from requests import Response

class CommonAPI(ABC):
    def __init__(self):
        self._tokens_input=0
        self._tokens_output = 0

    @property
    def tokens_input(self) -> int:
        return self._tokens_input

    @property
    def tokens_output(self) -> int:
        return self._tokens_output

    def add_input_tokens(self, count: int):
        self._tokens_input += count

    def add_output_tokens(self, count: int):
        self._tokens_output += count

    def reset_counters(self):
        self._tokens_input = 0
        self._tokens_output = 0

    @property
    def total_tokens(self) -> int:
        return self._tokens_input + self._tokens_output

class API(CommonAPI, ABC):
    def __init__(self,system_prompt=None,json_schema=None):
        super().__init__()
        if (system_prompt is None or
                not isinstance(system_prompt, str) or
                system_prompt.strip() == ''):

            self._system_prompt = "Ты ассистент-помощник"
        else:
            self._system_prompt = system_prompt.strip()

        self._json_schema = json_schema

            # # Для точных задач (программирование, факты)
            # temperature = 0.1 - 0.3
            #
            # # Для общения, творчества (рекомендуемый диапазон)
            # temperature = 0.7 - 0.9
            #
            # # Для очень креативных задач (поэзия, истории)
            # temperature = 1.0 - 1.5

    @property
    def system_prompt(self):
        return self._system_prompt

    @system_prompt.setter
    def system_prompt(self, value):
        self._system_prompt = value

    @property
    def json_schema(self):
        return self._json_schema

    @json_schema.setter
    def json_schema(self, value):
        self._json_schema = value

    @abstractmethod
    def sendChatMessage(self,message):
        pass

    @property
    @abstractmethod
    def credentials(self):
        pass

    @abstractmethod
    def embedding_post(self,embed_url,data,headers,timeout) -> Response:
        pass

    # @abstractmethod
    # def _get_chat_headers(self):
    #     pass


class VoiceAPI(CommonAPI, ABC):
    AUDIO_FORMATS: Dict[str, int] = {
        'ogg': 3800,  # подобран экспериментально
        'wav': 32000,  # 16 kHz, 16-bit
        'mp3': 16000,  # 128 kbps
        'flac': 12000,  # ~96 kbps
    }

    def __init__(self):
        super().__init__()  # ← обязательно вызываем

    @abstractmethod
    def synthesize_speech(self, text: str) -> bytes:
        pass

    @abstractmethod
    def recognize_speech_from_file(self, audio_file_path: str) -> str:
        pass

    @abstractmethod
    def recognize_speech(self, audio_data: bytes) -> str:
        pass


class ImageAPI(CommonAPI, ABC):
    def __init__(self):
        super().__init__()  # ← обязательно вызываем

    @abstractmethod
    def generate_image(self, prompt: str, **kwargs) -> str:
        """Генерация изображения, возвращает ID операции или путь к файлу"""
        pass

    @abstractmethod
    def get_image_result(self, operation_id: str) -> dict:
        """Получение результата генерации по ID операции"""
        pass

    @abstractmethod
    def generate_image_sync(self, prompt: str, **kwargs) -> bytes:
        """Синхронная генерация изображения (ожидание результата)"""
        pass
