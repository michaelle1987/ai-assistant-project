from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat.chat_models import GigaChat

giga = GigaChat(
    # Для авторизации запросов используйте ключ, полученный в проекте GigaChat API
    credentials="MDE5OTYwYjUtOTY4Zi03MjE2LWI3YmUtZDlmNjk4MWMyNWZlOjViYjY1Y2UyLTRjYTYtNDQwYS1hMzY5LTUxN2IzN2ExMmIzZg==",
    ca_bundle_file="russian_trusted_root_ca.cer",
)

messages = [
    SystemMessage(
        content="Роль. Ты специалист по составлению презентаций. Ты пишешь тезисы для слайдов. Инструкции. Презентация должна быть емкой, содержательной по смыслу и убедительной. Помни, что презентация используется для привлечения клиентов. Клиента нужно убедить воспользоваться услугой. Презентация должна отвечать в первую очередь на вопросы \"Зачем это нужно клиенту? Какую проблему это решает\". И только далее презентация содержит в себе информацию \"как это можно реализовать\". Когда тебя просят составить презентацию, в ответе пиши заголовок слайда и тезисы к нему. Тезисы должны быть емкими, содержательными по смыслу и убедительными."
    )
]

while(True):
    user_input = input("Пользователь: ")
    if user_input == "пока":
      break
    messages.append(HumanMessage(content=user_input))
    res = giga.invoke(messages)
    messages.append(res)
    print("GigaChat: ", res.content)