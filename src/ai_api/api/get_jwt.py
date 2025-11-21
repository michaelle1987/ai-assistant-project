import time
import jwt
import json
import os


def create_jwt():
    service_account_id = os.environ.get('YANDEX_SERVICE_ACCOUNT_ID')
    key_id = os.environ.get('YANDEX_KEY_ID')
    private_key = os.environ.get('YANDEX_PRIVATE_KEY')

    # Если переменные окружения не найдены, пробуем прочитать из файла
    if not all([service_account_id, key_id, private_key]):
        try:
            # Локальный путь к файлу (для разработки)
            key_path = r'C:\Users\mnigh\PycharmProjects\PythonProject\ai_api\api\authorized_key.json'
            # ОТЛАДКА: покажем текущую директорию и существующие файлы
            with open(key_path, 'r') as f:
                obj = json.load(f)
                service_account_id = obj['service_account_id']
                key_id = obj['id']
                private_key = obj['private_key']
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            raise Exception("Yandex Cloud credentials not found in environment variables or key file")

    if not all([service_account_id, key_id, private_key]):
        raise Exception("Yandex Cloud credentials not found")

    now = int(time.time())
    payload = {
        'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
        'iss': service_account_id,
        'iat': now,
        'exp': now + 3600
    }

    encoded_token = jwt.encode(
        payload,
        private_key,
        algorithm='PS256',
        headers={'kid': key_id}
    )

    return encoded_token