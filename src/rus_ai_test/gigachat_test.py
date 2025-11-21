import json

import requests

#client_id = '019960b5-968f-7216-b7be-d9f6981c25fe'
#scope ='GIGACHAT_API_PERS'
#client_secret ='MDE5OTYwYjUtOTY4Zi03MjE2LWI3YmUtZDlmNjk4MWMyNWZlOjViYjY1Y2UyLTRjYTYtNDQwYS1hMzY5LTUxN2IzN2ExMmIzZg=='
#access_token = 'eyJjdHkiOiJqd3QiLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwiYWxnIjoiUlNBLU9BRVAtMjU2In0.o833sDZMsRAl8DpBYE5LuHXewVq735OCKkyk3H5vJ2STSXY2Q8YEKEmyPq2buA2PqgDcr-UoBpqmoDLizYSEQCdb-c3KlXLvZxF0CNIyN0d6hDDGqUs3y3f12Eoxy-Wtu3JDAbYQQSyQvdTFS2cvejucLldwjkbLdWfsFSf9biyjduFrtKB_JkZbjf6D64pRuI0ONTg_3dL86hOEgeLF7tmOVZ0_YaeyR9lKAKMe8VAw62cj64nHV1Q8Gs6auCGW6z1EK5zfDoHnsnsmZdDw9y3X87oqabkLxcQXkX7NrIL9XNF5gK_0Zu0lLymZQnfkrSo2s3dsqaZUhIdcrkttbQ.CpUvsDdeIJsiw05ooXEU0g.BFidcJrixlqA9mUxyzMGP2c1QOO4rPPTCJoNGybJ3mG9NKpuqUOK8a6tCSOCLmssAS2afOS4xpBfyzniYlFufcufh8Ol5x5b_u_UFOVkiMUU_E2YChBS6iKdnMf5PvyvT0R1zaBPiXTfxGagTBlBBEAjjy3NejF9Auxdy_WFB8FxyXG1Kbk5Ur0JIgX1r5V7Biel1m0UIYGbX4omiAD2ARNsoNHID3y94eRfcqA0vxK1A6I7dhcsM4gU7a4RC0J7oTt3VKUu5mX9gvt0VijkVjrdNlgNkDOHtPbOOubPUj7piYCx7hso1KjUNAHK7Ar9SPnpYHuE08rU4SSgr5hZ9fUGLYEYQCVfq5pulr_Fh4tYuTTsJ3keAfZGwNlfsI7HX0D5_PnoQm-tPYj_VdLmpAqdNJG5atCVgwirfXzzxzUUooBNsf9rqWS6hmdQdNtT4LkLfYz7ZgmEBowqJgYM5bC4Nnf4msOUbzHdYSPpcBYPqTqf1m6SEBVIAIBRT1Y06r73173cpyqhyw_hIvkokFDfywGedPyAjX8IPN1c49-Kuim5-z1n92ILHRwgykR_vZr1OgZTJ2cE51_ueCY2uzpVgf2laJ-Xgc85geqMaN7vlEMCvCpL_3guvpvx3mTC2--8UXm8RlwwPyKhmrqAP4MjE6JQDSeQz8vvIU0D4MAUS0jN0SvggxyamrZFVO1Rr3d_VgINlQs5Z2zKkfH3PGnGA2pYnlK7Z5743cEWIzE.bpryf9OmtJ496uYlY6k_7OilmY_nNEoYsSJ_UwD47xk'

#сработал
import requests

url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

payload={
  "model": "GigaChat",
  "messages": [
    {
      "role": "user",
      "content": "Привет! Как дела?"
    }
  ],
  "stream": False,
  "repetition_penalty": 1,
}
headers = {
  'Accept': 'application/json',
  'Authorization': 'Bearer eyJjdHkiOiJqd3QiLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwiYWxnIjoiUlNBLU9BRVAtMjU2In0.oqchBWD1Ss0lYeuwQhHNCnH8p257x6xd207uvGCJbGfXECSWPg8yrDT1U7XoLSgrpZ9FtwEnyAR_0MyLyqD73riuQNfbifftY_O1c6No4N5VD7LI-tPccalw-7T0DlPD-slba2RxUtCIJK2-cib49OKdkYLl9wijJWC7cO_9j_m6svnBsY4IiqFspEwVC42ol89FAxhZWI0Rd6GgdV97M9sC5Hk9Y2biLYI6OP37BlZfNK8svtlCLKuni3zQw_9Xg5v_NnVd2E3aG-VdVs_WPrBihwk8bz9qLzyJXY4jbYVBL77omDz9xbmCFx5Wr7hiXG6n1d2YA4eIJeckUcGabg.vsVh0cSlQVFm550KOVeJSg.W-Xc0hYvyuWZhbhQ9gg8EMwgMm7kHTe_fEjI0lqU3Jq2xjfSOCmsW1cZUCIxsya-8mHS2pedXMxR3Vb0dpxiTNkaPFM0sZeuzSa928iAvkGnuYFahwEEx1uQLDDMf27lV5RMpMwkBogUoLUoy6LSdm-1YsWgaDnX0FrgWNhoNX2TI4uiZ13u2ZG9mk1nl8uoiRke8NpvQBf4Ro0xE6UxebF-DsGj64pS_YgC_4IhSVOC4NaFuDW4mvxctu8i4YqcmqnE714giZL3h7oy1705wD9uoH6TzlTVvNoTq5ygq098oUshn3rnW0txmmTbEg3ySr67lml5WCFlEQUawzKfc-wcZSZBgftcZ-ZEvPPxBKGbOWNneAJhtD1RAARECCCT8CaO-vgQecCSgAJDrauDXMME45oDSlJoavRQTecQDEsoVX4qBOrWgqEFQpwYGGig1ddQeLHS-NfmkM2OBIhTEiYCjFgT9HBybWFtuxL5m12Pa_tX6Xv8yr8oTGq9ZhPxJJzboyyrZp98O38qFvGaOKWSTIxkE6Jye2SJuy6J6ezXqxzm5oL4gQe8Jk5fcYiF35MfqSS_S_NvZaU4tWzY2tZseFnY0G2dae6BABl8PShIF4Td77Yrht6MOdEzguyR5pMLQ_syXEOyzxr9Y3PVcDSW6apU3XJ4okMsWXqRmYP_qW2PV1hpMXKmZstmNSXVmkGNFImmTggXjArQ9whSGFsuNJR2bGmsdvj1RdpEIy4.Mj67uHUAa-8BPpeQ273cVjHzApviveu_rRdPoKDXhAI'
}

response = requests.request("POST", url, headers=headers, json=payload, verify='russian_trusted_root_ca.cer')

print(response.json()['choices'][0]['message']['content'])

# from gigachat import GigaChat
# import os
# print("Текущая рабочая директория:", os.getcwd())
# print("Существует ли файл сертификата:", os.path.exists("russian_trusted_root_ca.cer"))
# # Устанавливаем переменную окружения для SSL сертификата (если требуется)
# os.environ["REQUESTS_CA_BUNDLE"] = r"C:Users\mnigh\PycharmProjects\PythonProject\rus_ai_test\russian_trusted_root_ca.cer"
# os.environ["SSL_CERT_FILE"] = r"C:Users\mnigh\PycharmProjects\PythonProject\rus_ai_test\russian_trusted_root_ca.cer"
# # Создаем кастомную сессию с вашим сертификатом
# session = requests.Session()
# session.verify = r"C:Users\mnigh\PycharmProjects\PythonProject\rus_ai_test"  # Путь к вашему сертификату
#
# giga = GigaChat(
#     credentials="MDE5OTYwYjUtOTY4Zi03MjE2LWI3YmUtZDlmNjk4MWMyNWZlOjViYjY1Y2UyLTRjYTYtNDQwYS1hMzY5LTUxN2IzN2ExMmIzZg==",
# )
#
# response = giga.chat("Привет! Как дела?")
#
# print(response.choices[0].message.content)
