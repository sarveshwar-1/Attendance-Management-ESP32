import requests

base_url = 'http://127.0.0.1:2000'
root = "/root"
url = f"{base_url}{root}"
empid = "ElonMusk"

res = requests.post(url, json={"data": f"{empid}"})
if res.json().get("mode")  == "CREATE_SESSION":
    url = f"{base_url}{res.json().get('endpoint')}"



for i in range(1, 74):
    stdid = f"CB.SC.U4AIE23{i:03}"
    res = requests.post(url, json={"data": f"{stdid}"})
    print(res.json())
    print(res)
    print(res.text)

res = requests.post(url, json={"data": f"{empid}"})
print(res)
print(res.text)
