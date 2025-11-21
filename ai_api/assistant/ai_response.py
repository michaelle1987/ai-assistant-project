class AIResponse:
    def __init__(self, **kwargs):
        self._text = kwargs.get('text')
        self._audio_data = kwargs.get('audio_data')
        self._json = kwargs.get('json')
        self._tokens_input = kwargs.get('tokens_input',0)
        self._tokens_output = kwargs.get('tokens_output',0)
        self._images = []  # список для хранения GeneratedImage

        # Если передан image, добавляем его в список
        image = kwargs.get('image')
        if image:
            self._images.append(image)

    @property
    def text(self)->str:
        return self._text
    @property
    def audio_data(self)->bytes:
        return self._audio_data
    @property
    def json(self)->dict:
        return self._json
    @property
    def images(self) -> list:
        # Возвращаем копию для защиты от внешних изменений
        return self._images.copy()
    @property
    def tokens_input(self)->int:
        return self._tokens_input
    @property
    def tokens_output(self)->int:
        return self._tokens_output

    @text.setter
    def text(self, value: str):
        self._text = value
    @audio_data.setter
    def audio_data(self, value: bytes):
         self._audio_data = value
    @json.setter
    def json(self, value: dict):
        self._json = value
    @tokens_input.setter
    def tokens_input(self, value: int):
        if not isinstance(value, int) or value < 0:
            raise ValueError("tokens_input must be a non-negative integer")
        self._tokens_input = value
    @tokens_output.setter
    def tokens_output(self, value: int):
        if not isinstance(value, int) or value < 0:
            raise ValueError("tokens_output must be a non-negative integer")
        self._tokens_output = value
    def add_image(self, image):
        """Добавить изображение в список"""
        if not isinstance(image, GeneratedImage):
            raise TypeError("Можно добавлять только GeneratedImage")
        self._images.append(image)

    def __add__(self, other):
        """Перегрузка оператора + для конкатенации AIResponse"""
        if not isinstance(other, AIResponse):
            raise TypeError("Можно складывать только AIResponse с AIResponse")

        # Конкатенация текстов
        new_text = None
        if self._text and other._text:
            new_text = self._text + "\r\n" + other._text
        elif self._text:
            new_text = self._text
        elif other._text:
            new_text = other._text

        # Аудио: объединяем если оба не None
        new_audio = None
        if self._audio_data and other._audio_data:
            new_audio = self._audio_data + other._audio_data  # конкатенация байтов
        elif self._audio_data:
            new_audio = self._audio_data
        elif other._audio_data:
            new_audio = other._audio_data

        # JSON: мерджим словари если оба не None
        new_json = None
        if self._json and other._json:
            new_json = {**self._json, **other._json}  # объединение словарей
        elif self._json:
            new_json = self._json
        elif other._json:
            new_json = other._json

        # Суммируем токены
        new_tokens_input = self._tokens_input + other._tokens_input
        new_tokens_output = self._tokens_output + other._tokens_output

        # Объединяем изображения
        new_images = self._images + other._images

        # Создаем новый AIResponse с объединенными данными
        new_response = AIResponse(
            text=new_text,
            audio_data=new_audio,
            json=new_json,
            tokens_input=new_tokens_input,
            tokens_output=new_tokens_output
        )
        new_response._images = new_images  # напрямую устанавливаем объединенный список

        return new_response

    def __str__(self):
        images_info = f", images_count={len(self._images)}" if self._images else ""
        return f"AIResponse(text={self._text}, audio_len={len(self._audio_data) if self._audio_data else 0}, json={self._json}{images_info})"

class GeneratedImage:
    def __init__(self, **kwargs):
        self.image_bytes = kwargs.get('image_bytes')  # bytes - сырые байты изображения
        self.format = kwargs.get('format', 'jpeg')    # str - формат ('jpg', 'png', etc.)
        self.size = kwargs.get('size', (1024, 1024))  # tuple - размеры (width, height)
        self.prompt = kwargs.get('prompt', '')        # str - промпт, который сгенерировал это изображение
        self.generation_params = kwargs.get('generation_params', {})  # dict - параметры (seed, aspect_ratio, model)
        self.operation_id = kwargs.get('operation_id')  # str - ID асинхронной операции
        self.generated_at = kwargs.get('generated_at')  # datetime - время генерации
        self.filename = kwargs.get('filename', '')    # str - предлагаемое имя файла
        self.file_size = kwargs.get('file_size', 0)   # int - размер в байтах
        self.telegram_ready = kwargs.get('telegram_ready', False)  # bool - оптимизировано ли для Telegram
