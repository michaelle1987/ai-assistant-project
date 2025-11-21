import re
import json

from ai_api.assistant.abs_assistant import AbsAssistant
from ai_api.assistant.ai_response import AIResponse, GeneratedImage
from ai_api.help_functions import _clean_text_for_speech

class AIAssistant(AbsAssistant):
    def __init__(self,model_name,**kwargs):
        super().__init__(model_name,**kwargs)

    def appendChatMessage(self, message):
        self._history_messages +="\r\n"+ message
        response_text= self._api.sendChatMessage(self._history_messages)
        self._history_messages +=response_text
        return AIResponse(text=response_text)

    def sendChatMessage(self, message):
        # return '\nОтвет от '+self._model_name.value+':\n\n'+self._api.sendChatMessage(message)
        return AIResponse(text=self._api.sendChatMessage(message),tokens_input=self._api.tokens_input,tokens_output=self._api.tokens_output)

    def sendVoiceMessage(self, audio_data):
        if self._has_voice:
            # Распознаем речь из аудио данных
            recognize_response = self.recognize_speech(audio_data)

            # отправляем запрос текстом
            response= self.sendChatMessage(recognize_response.text)

            response+= self.synthesize_speech(response.text)
            return recognize_response+response
        else:
            raise NotImplementedError(f"Модель {self._model_name} не поддерживает озвучку")

    def appendVoiceMessage(self, audio_data):
        if self._has_voice:
            # Распознаем речь из аудио данных
            recognize_response = self.recognize_speech(audio_data)

            # отправляем запрос текстом
            response = self.appendChatMessage(recognize_response.text)

            response+=  self.synthesize_speech(response.text)
            return recognize_response+response
        else:
            raise NotImplementedError(f"Модель {self._model_name} не поддерживает озвучку")

    def synthesize_speech(self, text: str):
        """Озвучить текст, если модель поддерживает"""
        if self._has_voice:
            cleaned_text = _clean_text_for_speech(text)
            # print(cleaned_text)
            audio_data = self._api.synthesize_speech(cleaned_text)
            return AIResponse(audio_data=audio_data)
        else:
            raise NotImplementedError(f"Модель {self._model_name} не поддерживает озвучку")

    def recognize_speech_from_file(self, audio_file_path: str):
        """Распознать речь, если модель поддерживает"""
        if self._has_voice:
            return AIResponse(text=self._api.recognize_speech_from_file(audio_file_path))
        else:
            raise NotImplementedError(f"Модель {self._model_name} не поддерживает распознавание речи")

    def recognize_speech(self, audio_data: bytes):
        """Распознать речь, если модель поддерживает"""
        if self._has_voice:
            return AIResponse(text=self._api.recognize_speech(audio_data))
        else:
            raise NotImplementedError(f"Модель {self._model_name} не поддерживает распознавание речи")

    @property
    def embeddings(self):
        raise NotImplementedError(f"Асссистент не поддерживает эмбеддинг")

    # Методы генерации изображений
    def generate_image(self, prompt: str, **kwargs) -> AIResponse:
        """Асинхронная генерация изображения, возвращает ID операции"""
        if self._has_image_generation:
            operation_id = self._api.generate_image(prompt, **kwargs)
            # Создаем GeneratedImage с operation_id для отслеживания
            image = GeneratedImage(
                prompt=prompt,
                operation_id=operation_id,
                generation_params=kwargs
            )
            return AIResponse(text=f"Запущена генерация изображения. ID: {operation_id}", image=image)
        else:
            raise NotImplementedError(f"Модель {self._model_name} не поддерживает генерацию изображений")

    def get_image_result(self, operation_id: str) -> AIResponse:
        """Получение результата генерации по ID операции"""
        if self._has_image_generation:
            result = self._api.get_image_result(operation_id)
            return AIResponse(json=result)  # Возвращаем сырой результат для анализа
        else:
            raise NotImplementedError(f"Модель {self._model_name} не поддерживает генерацию изображений")

    def generate_image_sync(self, prompt: str, **kwargs) -> AIResponse:
        """Синхронная генерация изображения с ожиданием результата"""
        if self._has_image_generation:
            image_bytes = self._api.generate_image_sync(prompt, **kwargs)

            # Создаем полноценный GeneratedImage
            image = GeneratedImage(
                image_bytes=image_bytes,
                prompt=prompt,
                format='jpeg',  # Яндекс возвращает JPEG
                size=(1024, 1024),  # Можно вычислить реальный размер из метаданных
                generation_params=kwargs,
                file_size=len(image_bytes),
                telegram_ready=True  # Яндекс изображения обычно готовы для Telegram
            )

            return AIResponse(text=f"Изображение сгенерировано: {prompt}", image=image)
        else:
            raise NotImplementedError(f"Модель {self._model_name} не поддерживает генерацию изображений")

    def generate_and_save_image(self, prompt: str, output_path: str, **kwargs) -> AIResponse:
        """Генерация и сохранение изображения в файл"""
        if self._has_image_generation:
            saved_path = self._api.generate_and_save_image(prompt, output_path, **kwargs)

            # Читаем сохраненный файл для создания GeneratedImage
            with open(saved_path, 'rb') as f:
                image_bytes = f.read()

            image = GeneratedImage(
                image_bytes=image_bytes,
                prompt=prompt,
                format=output_path.split('.')[-1],
                filename=output_path.split('/')[-1],
                file_size=len(image_bytes),
                generation_params=kwargs
            )

            return AIResponse(text=f"Изображение сохранено: {saved_path}", image=image)
        else:
            raise NotImplementedError(f"Модель {self._model_name} не поддерживает генерацию изображений")