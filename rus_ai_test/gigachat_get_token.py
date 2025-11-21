import requests

url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

payload={
  'scope': 'GIGACHAT_API_PERS'
}
headers = {
  'Content-Type': 'application/x-www-form-urlencoded',
  'Accept': 'application/json',
  'RqUID': '5a9c6fe6-fc9e-4050-aed7-04db997d87ac',
  'Authorization': 'Basic MDE5OTYwYjUtOTY4Zi03MjE2LWI3YmUtZDlmNjk4MWMyNWZlOjViYjY1Y2UyLTRjYTYtNDQwYS1hMzY5LTUxN2IzN2ExMmIzZg=='
}

response = requests.request("POST", url, headers=headers, data=payload, verify='russian_trusted_root_ca.cer')

print(response.json()['access_token'])