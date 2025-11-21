from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from ai_api.assistant.ai_assistant import AIAssistant
from ai_api.assistant.ai_model import AIModel
from ai_api.assistant.tools_assistant import ToolsAssistant

app = Flask(__name__)
CORS(app)

APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwtm9U8XOSyyuoR871U9E6yI2Mc3TmADwoO4LRheMM8CBnnGrCOXMe8tul_Zqbl7Gh3bQ/exec"

# Инициализация ассистентов
system_prompt = r"""
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

json_schema = r"""{
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
}"""

# Хранилище сессий для разных пользователей
user_sessions = {}


@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return '', 200

    data = request.json
    user_message = data['message']
    user_id = data.get('user_id', 'default')  # ID пользователя из фронтенда

    # Получаем или создаем сессию пользователя
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            'chat_assistant': AIAssistant(AIModel.DEEP_SEEK, system_prompt=system_prompt),
            'json_assistant': ToolsAssistant(AIModel.DEEP_SEEK,
                                          system_prompt=r"""Прочитай историю диалога и в ответе выдай только json из данных, предоставленных клиентом""",
                                          json_schema=json_schema)
        }
        user_sessions[user_id]['chat_assistant'].clearHistoryMessages()

    session = user_sessions[user_id]
    chat_assistant = session['chat_assistant']
    json_assistant = session['json_assistant']

    # Отправляем сообщение основному ассистенту
    response = chat_assistant.appendChatMessage(user_message)

    response_data = {
        'response': response.text,  # Берем только текст из AIResponse
        'history': chat_assistant.history_messages
    }

    # Проверяем, завершен ли диалог
    if response.text and ("Вы записаны" in response.text or "вы записаны" in response.text):
        try:
            # Извлекаем JSON из истории диалога используя sendJSONRequest
            json_response = json_assistant.sendChatMessage(chat_assistant.history_messages)

            # Сохраняем данные
            save_result = save_to_google_sheets(json_response.json)

            response_data['saved'] = True
            response_data['save_result'] = save_result

            # Очищаем историю для нового диалога
            chat_assistant.clearHistoryMessages()

        except Exception as e:
            response_data['save_error'] = str(e)
            print(f"Ошибка обработки JSON: {e}")

    return jsonify(response_data)


def save_to_google_sheets(data):
    payload = {
        "name": data.get('name', ''),
        "phone": data.get('phone', ''),
        "service": data.get('service', ''),
        "datetime": data.get('datetime', ''),
        "specialization": data.get('specialization', ''),
        "comment": data.get('comment', '')
    }

    try:
        response = requests.post(APPS_SCRIPT_URL,
                                 json=payload,
                                 headers={'Content-Type': 'application/json'})
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.route('/reset/<user_id>', methods=['POST'])
def reset_chat(user_id):
    """Сброс диалога для пользователя"""
    if user_id in user_sessions:
        user_sessions[user_id]['chat_assistant'].clearHistoryMessages()
    return jsonify({'status': 'success', 'message': 'Диалог сброшен'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)