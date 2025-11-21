import yandexcloud
from yandex.cloud.iam.v1.iam_token_service_pb2 import CreateIamTokenRequest
from yandex.cloud.iam.v1.iam_token_service_pb2_grpc import IamTokenServiceStub

from ai_api.api.get_jwt import create_jwt
import os
import json


def create_iam_token():
    service_account_id = os.environ.get('YANDEX_SERVICE_ACCOUNT_ID')
    key_id = os.environ.get('YANDEX_KEY_ID')
    private_key = os.environ.get('YANDEX_PRIVATE_KEY')

    # Fallback: если нет переменных окружения, читаем из файла
    if not all([service_account_id, key_id, private_key]):
        try:
            key_path = r'C:\Users\mnigh\PycharmProjects\PythonProject\ai_api\api\authorized_key.json'
            with open(key_path, 'r') as f:
                obj = json.load(f)
                service_account_id = obj['service_account_id']
                key_id = obj['id']
                private_key = obj['private_key']
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            raise Exception("Yandex Cloud credentials not found in environment variables or key file")

    sa_key = {
        "id": key_id,
        "service_account_id": service_account_id,
        "private_key": private_key
    }

    jwt_token = create_jwt()

    sdk = yandexcloud.SDK(service_account_key=sa_key)
    iam_service = sdk.client(IamTokenServiceStub)
    iam_token = iam_service.Create(
        CreateIamTokenRequest(jwt=jwt_token)
    )

    return iam_token.iam_token