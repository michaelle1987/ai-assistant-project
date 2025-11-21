import requests
from requests import Response

from ai_api.api.abstract_api import API, VoiceAPI, ImageAPI
from ai_api.api.get_bearer_token import create_iam_token

import time
import base64

class YandexGPT_API(API,VoiceAPI,ImageAPI):

    folder_id = 'b1goe0ht2mcgvsi5hgfd'
    max_file_duration_seconds=29

    def __init__(self,system_prompt=None,json_schema=None):
        super().__init__(system_prompt,json_schema)
        self.url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        self.createToken()

    def _get_chat_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def _get_speech_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            # Content-Type не нужен для STT
        }

    def createToken(self):
        self.token = create_iam_token()
        # print("token:", self.token, sep="\n")

    @property
    def credentials(self):
        return self.token

    def sendChatMessage(self,message):

        data = {
            "modelUri": "gpt://"+self.folder_id+"/yandexgpt/latest",
            "completionOptions": {
                "stream": False,
                "temperature": 0.3,
            },
            "messages": [
                {
                    "role": "system",
                    "text": self._system_prompt
                },
                {
                    "role": "user",
                    "text": message
                }
            ]
        }

        # IDE тебе говорит: «Используй headers=..., data=..., json=...»,
        # потому что иначе Python неправильно распределит твои аргументы по позициям.
        response = requests.post(self.url, headers=self._get_chat_headers(), json=data)

        if response.status_code == 200:
            self._tokens_input = int(response.json()['result']['usage']['inputTextTokens'])
            self._tokens_output = int(response.json()['result']['usage']['completionTokens'])
            return response.json()['result']['alternatives'][0]['message']['text']
        elif response.status_code == 401:
            # Просто бросаем исключение, обертка поймает
            error_msg = "Token expired"  # упрощенная логика
            raise Exception(f"Auth error: {error_msg}")
        else:
            return str(response.status_code) + " " + response.text

    # Работа со звуком
    def synthesize_speech(self, text: str) -> bytes:
        url = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
        params = {
            'text': text,
            'voice': 'oksana',  # alena, filipp, ermil
            'lang': 'ru-RU',
            'format': 'oggopus',
            'folderId': self.folder_id,
            # 'sampleRateHertz': 48000,
        }
        response = requests.post(url, headers=self._get_speech_headers(), params=params)

        if response.status_code == 200:
            return response.content
        elif response.status_code == 401:
            raise Exception("Token expired")  # ⬅️ бросаем исключение для обертки
        else:
            response.raise_for_status()  # ⬅️ для других ошибок

    def recognize_speech_from_file(self, audio_file_path: str) -> str:
        file_extension = audio_file_path.split('.')[-1].lower()
        bytes_per_second = self.AUDIO_FORMATS.get(file_extension)

        if(bytes_per_second is None):
            return 'Мы пока не умеем работать с форматом '+file_extension

        with open(audio_file_path, 'rb') as f:
            audio_data = f.read()

        max_size = self.max_file_duration_seconds * bytes_per_second
        if len(audio_data) > max_size:
            print(f"Обрезаем аудио с {len(audio_data)} до {max_size} байт")
            audio_data = audio_data[:max_size]

            # Распознаем
        return self.recognize_speech(audio_data)

    def recognize_speech(self, audio_data: bytes) -> str:
        """Распознает речь из аудио-данных"""
        url = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"

        params = {
            'folderId': self.folder_id,
            'lang': 'ru-RU',
            'profanityFilter': 'true'
        }

        response = requests.post(url, headers=self._get_speech_headers(), params=params, data=audio_data)

        if response.status_code == 200:
            return response.json().get('result', '')
        elif response.status_code == 401:
            raise Exception("Token expired")  # ⬅️ бросаем исключение для обертки
        else:
            return response.text  # ⬅️ другие ошибки возвращаем как есть

    # метод для эмбединга
    def embedding_post(self,embed_url,data,headers,timeout) -> Response:
        return requests.post(embed_url, json=data, headers=headers, timeout=timeout)

    # Генерация изображений
    def generate_image(self, prompt: str, **kwargs) -> str:
        """
        Асинхронная генерация изображения
        Возвращает ID операции
        """
        url = "https://llm.api.cloud.yandex.net:443/foundationModels/v1/imageGenerationAsync"

        # Параметры по умолчанию
        generation_options = {
            "seed": kwargs.get("seed", 10),
            "aspectRatio": {
                "widthRatio": str(kwargs.get("width_ratio", 4)),
                "heightRatio": str(kwargs.get("height_ratio", 3))
            }
        }

        data = {
            "modelUri": f"art://{self.folder_id}/yandex-art/latest",
            "generationOptions": generation_options,
            "messages": [{"text": prompt}]
        }

        response = requests.post(url, headers=self._get_chat_headers(), json=data)
        response.raise_for_status()

        result = response.json()
        return result['id']  # ID операции

    def get_image_result(self, operation_id: str) -> dict:
        """
        Получение результата генерации по ID операции
        """
        url = f"https://llm.api.cloud.yandex.net:443/operations/{operation_id}"

        response = requests.get(url, headers=self._get_chat_headers())
        response.raise_for_status()

        return response.json()

    def generate_image_sync(self, prompt: str, **kwargs) -> bytes:
        """
        Синхронная генерация изображения с ожиданием результата
        Возвращает bytes изображения
        """
        # Запускаем генерацию
        operation_id = self.generate_image(prompt, **kwargs)

        # Ожидаем завершения (макс 60 секунд)
        max_wait = 60
        wait_time = 0

        while wait_time < max_wait:
            try:
                result = self.get_image_result(operation_id)

                if result.get('done'):
                    if 'response' in result and 'image' in result['response']:
                        # Декодируем base64 в bytes
                        image_data = base64.b64decode(result['response']['image'])
                        return image_data
                    else:
                        # Если операция завершена, но нет изображения - это ошибка
                        error_msg = result.get('error', 'Неизвестная ошибка')
                        raise Exception(f"Ошибка генерации: {error_msg}")

                # Если операция еще не завершена, продолжаем ждать
                print(f"⏳ Ожидаем завершения генерации... ({wait_time}/60 сек)")

            except Exception as e:
                # Если получили 404, возможно операция уже завершена и удалена
                if "404" in str(e) and wait_time > 10:  # Ждем хотя бы 10 секунд
                    raise Exception("Операция генерации не найдена. Возможно, сервер удалил операцию слишком быстро")
                elif "404" in str(e):
                    # Продолжаем ждать, возможно операция еще обрабатывается
                    print(f"⚠️ Операция {operation_id} еще не доступна, продолжаем ожидание...")
                else:
                    # Другие ошибки прокидываем выше
                    raise e

            # Ждем 2 секунды перед следующей проверкой
            time.sleep(2)
            wait_time += 2

        raise Exception("Таймаут ожидания генерации изображения")

    def generate_and_save_image(self, prompt: str, output_path: str, **kwargs) -> str:
        """
        Генерация и сохранение изображения в файл
        """
        image_data = self.generate_image_sync(prompt, **kwargs)

        with open(output_path, 'wb') as f:
            f.write(image_data)

        return output_path


class YandexGPT_APIWithTokenRefresh(API, VoiceAPI, ImageAPI):
    """
    Декоратор/обертка для YandexGPT_API с автоматическим обновлением токена
    и защитой от бесконечных попыток
    """

    def __init__(self, system_prompt=None, json_schema=None):
        super().__init__(system_prompt, json_schema)
        self._wrapped_api = YandexGPT_API(system_prompt, json_schema)
        self._retry_count = 0
        self._max_retries = 2

    def _refresh_token_if_expired(self, method, *args, **kwargs):
        """
        Вызывает метод с обновлением токена при ошибке авторизации
        с ограничением количества попыток
        """
        if self._retry_count > self._max_retries:
            return "Ошибка: не удалось обновить токен после нескольких попыток"

        try:
            result = method(*args, **kwargs)
            self._retry_count = 0  # сбрасываем при успехе
            return result
        except Exception as e:
            error_msg = str(e)
            if 'token has expired' in error_msg.lower() or 'expired' in error_msg.lower():
                print('Обнаружена просрочка токена, обновляем...')
                self._retry_count += 1
                self._wrapped_api.createToken()
                return self._refresh_token_if_expired(method, *args, **kwargs)
            else:
                raise e

    # Методы API с автоматическим обновлением токена
    def sendChatMessage(self, message):
        return self._refresh_token_if_expired(self._wrapped_api.sendChatMessage, message)

    def synthesize_speech(self, text: str) -> bytes:
        return self._refresh_token_if_expired(self._wrapped_api.synthesize_speech, text)

    def recognize_speech(self, audio_data: bytes) -> str:
        return self._refresh_token_if_expired(self._wrapped_api.recognize_speech, audio_data)

    def recognize_speech_from_file(self, audio_file_path: str) -> str:
        return self._refresh_token_if_expired(self._wrapped_api.recognize_speech_from_file, audio_file_path)

    def embedding_post(self,embed_url,data,headers,timeout) -> Response:
        return self._refresh_token_if_expired(self._wrapped_api.embedding_post, embed_url, data, headers, timeout)

    # Методы генерации изображений (делают HTTP запросы)

    def generate_image(self, prompt: str, **kwargs) -> str:
        return self._refresh_token_if_expired(self._wrapped_api.generate_image, prompt, **kwargs)

    def get_image_result(self, operation_id: str) -> dict:
        return self._refresh_token_if_expired(self._wrapped_api.get_image_result, operation_id)

    def generate_image_sync(self, prompt: str, **kwargs) -> bytes:
        return self._refresh_token_if_expired(self._wrapped_api.generate_image_sync, prompt, **kwargs)

    def generate_and_save_image(self, prompt: str, output_path: str, **kwargs) -> str:
        return self._refresh_token_if_expired(self._wrapped_api.generate_and_save_image, prompt, output_path, **kwargs)

    # Методы без проверки токена (простая делегация)
    def createToken(self):
        return self._wrapped_api.createToken()

    def _get_chat_headers(self):
        return self._wrapped_api._get_chat_headers()

    def _get_speech_headers(self):
        return self._wrapped_api._get_speech_headers()

    def add_input_tokens(self, count: int):
        self._wrapped_api.add_input_tokens(count)

    def add_output_tokens(self, count: int):
        self._wrapped_api.add_output_tokens(count)

    def reset_counters(self):
        self._wrapped_api.reset_counters()

    # Делегирование свойств
    @property
    def folder_id(self):
        return self._wrapped_api.folder_id

    @property
    def max_file_duration_seconds(self):
        return self._wrapped_api.max_file_duration_seconds

    @property
    def credentials(self):
        return self._wrapped_api.credentials

    @property
    def tokens_input(self) -> int:
        return self._wrapped_api._tokens_input

    @property
    def tokens_output(self) -> int:
        return self._wrapped_api._tokens_output

    @property
    def total_tokens(self) -> int:
        return self._wrapped_api.total_tokens

    # Свои свойства
    @property
    def retry_count(self):
        return self._retry_count