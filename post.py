import requests


url = "http://127.0.0.1:2000/listen"

for i in range(10):
    requests.post(url, data={"data": f"{i}"})