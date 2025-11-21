import telebot
from ai_api.assistant.ai_assistant import AIAssistant
from ai_api.assistant.tools_assistant import ToolsAssistant
from ai_api.assistant.ai_model import AIModel
import requests

bot = telebot.TeleBot("8262729679:AAGqrX0EUlm6jvfCnKsoUOrd9rdmeOCR7zU")
system_prompt=r"""
[Системная инструкция]
ТВОЯ ЗАДАЧА:
- Приветствуй клиента и предложи запись к врачу
- Собери 5 обязательных параметров:
  1. Имя пациента
  2. Телефон для связи
  3. Тип приема (первичный/вторичный)
  4. Желаемые дата и время приема
  5. Специализация врача
- Спроси о дополнительных пожеланиях (необязательно)

КАК РАБОТАТЬ:
- Веди естественный диалог, задавай вопросы 
- Не показывай технические детали пользователю
- Когда соберешь ВСЕ данные - сообщи "Вы записаны"
- Пока данные не собраны, не говори "Вы записаны"
Ты медицинский ассистент. НЕ представляйся именем пользователя. НЕ говори 'Меня зовут [имя пользователя]'. Используй нейтральные формулировки: 'Я ваш помощник', 'Я ассистент клиники' и т.д.
"""
json_schema=r"""{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "Имя пациента",
      "minLength": 2,
      "maxLength": 50
    },
    "phone": {
      "type": "string", 
      "description": "Телефон для связи",
      "pattern": "^[\\+\\d\\-\\(\\)\\s]+$",
      "minLength": 5
    },
    "service": {
      "type": "string",
      "description": "Тип приема",
      "enum": ["Первичный прием", "Вторичный прием", "Консультация", "Диагностика"]
    },
    "datetime": {
      "type": "string",
      "description": "Дата и время приема", 
      "format": "date-time"
    },
    "specialization": {
      "type": "string",
      "description": "Специализация врача",
      "enum": ["Терапевт", "Педиатр", "Кардиолог", "Невролог", "Гастроэнтеролог", "Гинеколог", "Уролог", "Дерматолог", "Офтальмолог", "Отоларинголог", "Хирург", "Ортопед"]
    },
    "comment": {
      "type": "string",
      "description": "Дополнительные пожелания или комментарии",
      "maxLength": 500
    }
  },
  "required": ["name", "phone", "service", "datetime", "specialization"],
  "additionalProperties": false
}
"""
assistant = AIAssistant(AIModel.DEEP_SEEK, system_prompt=system_prompt)
assistant.clearHistoryMessages()
json_assistant=ToolsAssistant(AIModel.DEEP_SEEK, system_prompt=r"""Прочитай историю диалога и в ответе выдай только json из данных, предоставленных клиентом
""",json_schema=json_schema)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Бот запущен! 🐍")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    print(message.text)
    response = assistant.appendChatMessage(message.text)
    print(response.text)
    if ("Вы записаны" or "вы записаны") in response.text:
        print("История сообщений")
        print(assistant.history_messages)
        json_response = json_assistant.sendChatMessage(assistant.history_messages)
        result = save_to_google_sheets(json_response.json)
        print(result)
        assistant.clearHistoryMessages()
    else:
        pass
    bot.send_message(message.chat.id, response.text)


def save_to_google_sheets(data):
    web_app_url = "https://script.google.com/macros/s/AKfycbxwz-bHqCyKE_dusnUKxfxFxpQucZn2qS6w0rViWOL6B1FKzzAgn-IJxaP9fQyLgQ70uw/exec"

    payload = {
        "name": data.get('name', ''),
        "phone": data.get('phone', ''),
        "service": data.get('service', ''),
        "datetime": data.get('datetime', ''),
        "specialization": data.get('specialization', ''),
        "comment": data.get('comment', '')
    }

    try:
        response = requests.post(web_app_url,
                                 json=payload,
                                 headers={'Content-Type': 'application/json'})

        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")  # Добавь это для дебага

        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Запускаем бота
if __name__ == "__main__":
    print("Бот запущен...")
    bot.polling(none_stop=True)  # будет перезапускаться при ошибках
    # data = {
    #     'name': 'Анна',  # Имя пациента
    #     'phone': '+79997654321',  # Телефон для связи
    #     'service': 'Первичный прием',  # Тип приема (первичный/вторичный)
    #     'datetime': '2024-01-20 15:00',  # Желаемые дата и время приема
    #     'specialization': 'Кардиолог',  # Специализация врача
    #     'comment': 'Боли в сердце'  # Необязательный параметр - пожелания/комментарии
    # }
    #
    # result = save_to_google_sheets(data)
    # print(result)

