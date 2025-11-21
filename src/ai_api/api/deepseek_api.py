import os
from dotenv import load_dotenv

from requests import Response

from ai_api.api.abstract_api import API
from openai import OpenAI

class DeepSeekAPI(API):
    def __init__(self,system_prompt=None,json_schema=None):
        super().__init__(system_prompt,json_schema)
        load_dotenv()
        self.key=os.environ.get('DEEPSEEK_API_KEY')
        self.client = OpenAI(
            api_key=self.key,
            base_url="https://api.deepseek.com"
        )

    def sendChatMessage(self,message):
        messages = []

        messages.append({"role": "system", "content": self._system_prompt})
        messages.append({"role": "user", "content": message})

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                stream=False, # ← обычный запрос (не потоковый) весь ответ сразу, не по частям
                temperature=0.7,
                # max_tokens=500  # 👈 ограничи длину ответа
            )

            self._tokens_input = response.usage.prompt_tokens
            self._tokens_output = response.usage.completion_tokens

            return response.choices[0].message.content

        except Exception as e:
            return f"Ошибка API: {e}"

    def credentials(self):
        return self.key

    def embedding_post(self,embed_url,data,headers,timeout) -> Response:
        pass