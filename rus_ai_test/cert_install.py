from gigachat import GigaChat

# Используйте ключ авторизации, полученный в личном кабинете, в проекте GigaChat API.
with GigaChat(credentials="MDE5OTYwYjUtOTY4Zi03MjE2LWI3YmUtZDlmNjk4MWMyNWZlOjViYjY1Y2UyLTRjYTYtNDQwYS1hMzY5LTUxN2IzN2ExMmIzZg==", ca_bundle_file="russian_trusted_root_ca.cer") as giga:
    response = giga.chat("Какие факторы влияют на стоимость страховки на дом?")
    print(response.choices[0].message.content)