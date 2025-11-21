import requests

from ai_api.assistant.test_assistant import getPostText, getImagePath

BOT_TOKEN = "8262729679:AAGqrX0EUlm6jvfCnKsoUOrd9rdmeOCR7zU"  # замените на ваш токен

def sendPostToTelegram(post_text, image_path, topic):
    """Отправляет пост с изображением в Telegram"""

    # Токен бота и список подписчиков
    # subscribers = [5695368714, 812311489, 726433126]
    subscribers = [-4280604102] #id приватной группы

    successful_sends = []
    failed_sends = []

    for chat_id in subscribers:
        try:
            # Сначала отправляем изображение
            with open(image_path, 'rb') as photo:
                files = {'photo': photo}
                data = {
                    'chat_id': chat_id,
                    'caption': post_text,
                    'parse_mode': 'HTML'
                }

                response = requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                    files=files,
                    data=data
                )

            result = response.json()

            if result.get('ok'):
                successful_sends.append(chat_id)
                print(f"✅ Сообщение отправлено пользователю {chat_id}")
            else:
                failed_sends.append(chat_id)
                error_msg = result.get('description', 'Неизвестная ошибка')
                print(f"❌ Ошибка отправки пользователю {chat_id}: {error_msg}")

        except Exception as e:
            failed_sends.append(chat_id)
            print(f"❌ Исключение при отправке пользователю {chat_id}: {e}")

    # Вывод итогов
    print(f"\n📊 ИТОГИ ОТПРАВКИ:")
    print(f"✅ Успешно отправлено: {len(successful_sends)}")
    print(f"❌ Не отправлено: {len(failed_sends)}")

    if successful_sends:
        print(f"📩 Получили: {successful_sends}")
    if failed_sends:
        print(f"📭 Не получили: {failed_sends}")

# Получить id приватной группы
def get_chat_id():

    # 1. Добавьте бота в группу
    # 2. Напишите любое сообщение в группе
    # 3. Выполните:

    response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates")
    updates = response.json()

    for update in updates['result']:
        if 'message' in update:
            chat = update['message']['chat']
            if chat['type'] in ['group', 'supergroup']:
                print(f"ID группы: {chat['id']}")
                print(f"Название: {chat.get('title')}")

#  Отправить сообщение в группу
def send_to_group(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': chat_id,  # тот самый отрицательный ID
        'text': text
    }
    response = requests.post(url, data=data)
    return response.json()

if __name__ == "__main__":
    topic = "Преимущества языка программирвоания Python для задач,связанных с искуственным интеллектом"
    postText=getPostText(topic,"Дружелюбный креативный")
    print(postText)
    image_path=getImagePath(topic)
    if image_path:
        print("🚀 Отправляем пост в Telegram...")
        sendPostToTelegram(postText, image_path, topic)