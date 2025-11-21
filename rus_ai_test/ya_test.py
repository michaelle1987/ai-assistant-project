import requests

from ai_api.api.get_bearer_token import create_iam_token

url="https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
token=create_iam_token()
headers ={
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

data = {
  "modelUri": "gpt://b1goe0ht2mcgvsi5hgfd/yandexgpt/latest",
  "completionOptions": {
    "stream": False,
    "temperature": 0.3,
    "maxTokens": "2000"
  },
  "messages": [
    {
      "role": "system",
      "text": "Исправь грамматические, орфографические и пунктуационные ошибки в тексте. Сохраняй исходный порядок слов."
    },
    {
      "role": "user",
      "text": "Нейросети помогают человеку работать быстрее и эффективнее но опосения что искуственный интелек заменит человека - пока преждевремены"
    }
  ]
}
#IDE тебе говорит: «Используй headers=..., data=..., json=...»,
# потому что иначе Python неправильно распределит твои аргументы по позициям.
response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    print(response.json()['result']['alternatives'][0]['message']['text'])
else:print(response.status_code,response.text,sep="\n")
