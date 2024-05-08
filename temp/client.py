import requests
import json

url = 'http://127.0.0.1:2000/'
headers = {'message':'your mom is hot'}
response = requests.post(url,headers=headers)
print(response.text)