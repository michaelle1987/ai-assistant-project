
import telebot
from ai_api.assistant.ai_assistant import AIAssistant
from ai_api.assistant.ai_model import AIModel

bot = telebot.TeleBot("8262729679:AAGqrX0EUlm6jvfCnKsoUOrd9rdmeOCR7zU")
assistant = AIAssistant(AIModel.YANDEX_GPT, system_prompt="Ты специалист по школьной программе, отвечай на вопросы научно-популярным языком, говори емко, но содержательно")

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Бот запущен! 🐍")

@bot.message_handler(func=lambda message: message.chat.type == "private")
def handle_message(message):
    response = assistant.sendChatMessage(message.text)
    bot.reply_to(message, response.text)


@bot.message_handler(content_types=['voice'], func=lambda message: message.chat.type == "private")
def handle_voice(message):
    # Скачиваем голосовое сообщение
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    response = assistant.sendVoiceMessage(downloaded_file)
    bot.send_audio(message.chat.id, response.audio_data, title=assistant.model_name,performer="ИИ-ассистент")
    bot.reply_to(message, response.text)

# Запускаем бота
if __name__ == "__main__":
    print("Бот запущен...")
    bot.polling(none_stop=True)  # будет перезапускаться при ошибках
