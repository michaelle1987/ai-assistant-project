from requests import Response

from ai_api.api.abstract_api import API
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat.chat_models import GigaChat

class GigaChatAPI(API):
    def __init__(self,system_prompt=None,json_schema=None):
        super().__init__(system_prompt,json_schema)
        self.key="MDE5OTYwYjUtOTY4Zi03MjE2LWI3YmUtZDlmNjk4MWMyNWZlOjViYjY1Y2UyLTRjYTYtNDQwYS1hMzY5LTUxN2IzN2ExMmIzZg=="
        self.giga = GigaChat(
            # Для авторизации запросов используйте ключ, полученный в проекте GigaChat API
            credentials=self.key,
            ca_bundle_file=r"C:\Users\mnigh\PycharmProjects\PythonProject\rus_ai_test\russian_trusted_root_ca.cer",
        )

    def sendChatMessage(self,message):
        # Каждый раз создаем новые сообщения без истории
        messages = [
            SystemMessage(content=self._system_prompt),
            HumanMessage(content=message)
        ]
        try:
            response = self.giga.invoke(messages)
            return response.content

        except Exception as e:
            return f"Ошибка GigaChat API: {e}"

    def credentials(self):
        return self.key

    def embedding_post(self,embed_url,data,headers,timeout) -> Response:
        pass