from ai_api.assistant.ai_model import AIModel
from ai_api.assistant.ai_assistant import AIAssistant
import os
from datetime import datetime
import time
import requests


def save_audio_file(audio_data, file_name):
    with open(file_name, 'wb') as audio_file:
        audio_file.write(audio_data)
    print(f'Файл сохранен как {file_name}')

def test_simple_assistant():
    assistant = AIAssistant(AIModel.DEEP_SEEK,
                            system_prompt="""Ты - профессиональный копирайтер и специалист по созданию контента. Твоя задача - генерировать качественные, привлекательные посты для социальных сетей и блогов.

ТВОИ НАВЫКИ:
- Создание цепляющих заголовков
- Написание структурированного контента
- Адаптация стиля под разные платформы
- Использование призывов к действию
- Оптимизация для SEO

ФОРМАТ ОТВЕТА:
Всегда предоставляй готовый к публикации пост с заголовком и телом текста.
Начинай сообщение сразу же с заголовка поста.""")
    # print(assistant.model_name)
    # print(assistant.system_prompt)
    # print("Есть поддержка голосовых сообщений? " + str(assistant.has_voice_support()))
    response = assistant.sendChatMessage("В чем преимущества платформы nodul.ru?")
    print(response.text)
    print(response.tokens_input)
    print(response.tokens_output)
    # audio_content=assistant.synthesize_speech("Здравствуйте, как вас зовут?")
    # save_audio_file(audio_content, 'output.ogg')
    # print(assistant.recognize_speech_from_file('D:/yandex_speechkit_test.ogg'))
    sendTelegram(response.text)

def sendTelegram(text):
    import os
    import telebot

    # Ваши данные
    BOT_TOKEN = os.environ.get('BOT_TOKEN')  # Начинается с 'bot...'
    CHAT_ID = "5695368714"  # Числовой ID пользователя

    # Отправка сообщения
    bot = telebot.TeleBot(BOT_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=text)
    print("Сообщение отправлено!")


def testModels():
    assistant = AIAssistant(AIModel.DEEP_SEEK,
                             system_prompt="Твоя задача определить запрос \'простой\' или \'сложный\'. Если запрос относится к компьютерным наукам, значит \'сложный\'. Верни только в нижнем регистре только одно слово \'простой\' или \'сложный\'")
    assistant1 = AIAssistant(AIModel.YANDEX_GPT,
                            system_prompt="Ты ассистент-помощник. Отвечай коротко, емко, но содержательно")
    assistant2 = AIAssistant(AIModel.DEEP_SEEK,
                            system_prompt="Ты ассистент-помощник. Отвечай коротко, емко, но содержательно")

    prompt = "Особенности и преимущества применения каскада моделей ИИ"

    start_time = time.time()
    # if assistant.appendChatMessage(prompt).text == 'сложный':
    #     print(assistant2.appendChatMessage(prompt).text)
    # else:
    #     print(assistant1.appendChatMessage(prompt).text)
    #     pass
    print(assistant1.appendChatMessage(prompt).text)
    latency = time.time() - start_time
    print("общее время"+str(latency))

def getPostText(topic,tone):#тема и тон - аргументы
    assistant = AIAssistant(AIModel.YANDEX_GPT,
                            system_prompt="Ты высококвалифицированный SMM-специалист, который будет помогать в генерации текста для постов с заданной тематикой и заданным тоном. Только пиши краткие содержательные посты, строго не больше 1000 символов.")
    return assistant.sendChatMessage(
        f"Напиши пост для соц.сетей на тему - {topic}. Тон - {tone}").text

def getImagePath(topic):
    assistant = AIAssistant(AIModel.YANDEX_GPT,
                            system_prompt="Ты ассистент,который составит промпт для нейросети, которая будет генерировать изображения. Ты должен составлять промпт на заданную тематику.")
    test_prompt=assistant.sendChatMessage(
        f"Сгенерируй изображение для соц.сетей с темой - {topic}").text
    print('Промпт генерации:')
    print(test_prompt)

    if not assistant.has_image_generation():
        print("❌ Генерация изображений не поддерживается")
        return None

    try:
        response = assistant.generate_image_sync(test_prompt)

        if response.images:
            image = response.images[0]

            test_dir = "test_images"
            os.makedirs(test_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"simple_test_{timestamp}.jpg"
            filepath = os.path.join(test_dir, filename)

            with open(filepath, 'wb') as f:
                f.write(image.image_bytes)

            print(f"✅ Изображение сохранено: {filepath}")

            return filepath

    except Exception as e:
        print(f"❌ Ошибка: {e}")

    return None

def test_generate_image(test_prompt):
    assistant = AIAssistant(AIModel.YANDEX_GPT)
    response = assistant.generate_image_sync(test_prompt)
    image = response.images[0]

    test_dir = "test_images"
    os.makedirs(test_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"simple_test_{timestamp}.jpg"
    filepath = os.path.join(test_dir, filename)

    with open(filepath, 'wb') as f:
        f.write(image.image_bytes)

    print(f"✅ Изображение сохранено: {filepath}")

if __name__ == "__main__":
    test_simple_assistant()

