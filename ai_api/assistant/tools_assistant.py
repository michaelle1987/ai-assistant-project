from ai_api.assistant.ai_assistant import AIAssistant
from ai_api.assistant.ai_response import AIResponse
import re
import json

class ToolsAssistant(AIAssistant):
    def __init__(self, model_name, **kwargs):
        super().__init__(model_name, **kwargs)

    def sendChatMessage(self, message):
        json_str = self._api.sendChatMessage(message)
        json_str = json_str.replace('```json', '').replace('```', '').strip()
        json_str = json_str.replace('```', '')  # на всякий случай еще раз
        json_str = re.sub(r'^json\s*', '', json_str, flags=re.IGNORECASE)  # убирает "json" в начале
        data = json.loads(json_str)
        return AIResponse(json=data)