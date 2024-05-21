import requests

base_url = 'http://127.0.0.1:2000'
root = "/root"
url = f"{base_url}{root}"
create_class_url = f"{base_url}/listen"
empid = "1234"

res = requests.post(url)
if res.json().get("mode")  == "CREATE_CLASS":
    url = f"{base_url}{res.json().get('endpoint')}"


res = requests.post(url, json={"data": f"{empid}"})
if res.json().get("mode")  == "CREATE_SESSION":
    url = f"{base_url}{res.json().get('endpoint')}"
print(res.json())


# for i in range(1, 72):
#     empid = f"CB.SC.U4AIE23{i:03}"
res = requests.post(create_class_url, json={"data": 1})
print(res.text)
print(res.json)
print(res)

# res = requests.post(url, json={"data": f"{empid}"})
# if res.json().get("mode")  == "END_SESSION":
#     url = f"{base_url}{root}"