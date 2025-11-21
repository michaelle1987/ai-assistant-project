import requests
from ai_api.api.get_bearer_token import create_iam_token

AUDIO_FILE_PATH = 'D:/yandex_speechkit_test.ogg'

# Читаем файл
with open(AUDIO_FILE_PATH, 'rb') as f:
    audio_data = f.read()

file_size = len(audio_data)
print(f"Размер файла: {file_size} байт ({file_size / 1024:.1f} KB)")
print(f"Примерная длительность: {file_size / 3800:.1f} секунд")

# ОБРЕЗАЕМ до 29 секунд (29 сек * 1500 байт/сек = 43500 байт)
max_size = 29 * 3800  # 29 секунд максимум для SpeechKit
if len(audio_data) > max_size:
    print(f"Обрезаем файл с {len(audio_data)} до {max_size} байт")
    audio_data = audio_data[:max_size]

# Распознаем
url = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
token = create_iam_token()

headers = {
    "Authorization": f"Bearer {token}"
}

params = {
    'folderId': 'b1goe0ht2mcgvsi5hgfd',
    'lang': 'ru-RU',
    'profanityFilter': 'false'
}

print("Отправляем запрос к SpeechKit...")
response = requests.post(url, headers=headers, params=params, data=audio_data)

print(f"Status: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    recognized_text = result.get('result', '')
    print("✅ УСПЕХ!")
    print("Распознанный текст:", recognized_text)

    # Сохраняем результат в файл
    with open('D:/recognized_text.txt', 'w', encoding='utf-8') as f:
        f.write(recognized_text)
    print("Текст сохранен в D:/recognized_text.txt")

else:
    print("❌ Ошибка:", response.text)

    # Попробуем альтернативный вариант с multipart
    print("\nПробуем альтернативный способ...")
    files = {
        'audio': ('audio.ogg', audio_data, 'audio/ogg')
    }

    response2 = requests.post(url, headers=headers, files=files, data=params)
    print(f"Альтернативный способ - Status: {response2.status_code}")

    if response2.status_code == 200:
        result = response2.json()
        print("✅ УСПЕХ (альтернативный способ):")
        print("Текст:", result.get('result', ''))
    else:
        print("❌ Ошибка и в альтернативном способе:", response2.text)