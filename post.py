import requests

base_url = 'http://127.0.0.1:2000'
root = "/root"
url = f"{base_url}{root}"

empid = "1234"

res = requests.post(url, json={"data": f"{empid}"})
if res.json().get("mode")  == "CREATE_SESSION":
    url = f"{base_url}{res.json().get('endpoint')}"
# print(res.json())


for i in range(10):
    res = requests.post(url, json={"data": f"CB.SC.U4AIE230{i}"})
    # print(res.json())

res = requests.post(url, json={"data": f"{empid}"})
if res.json().get("mode")  == "END_SESSION":
    url = f"{base_url}{root}"