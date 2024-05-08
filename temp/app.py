from flask import Flask, render_template
import requests
app = Flask(__name__)
URL = 'http://127.0.0.1:5000'
response = requests.get(URL)
if response.status_code == 200:
    # Parse JSON response
    data = response.json()
    print(data)
else:
    print(f'Failed to retrieve data: {response.status_code}')
@app.route('/')
def index():
    return render_template("index.html")

if  __name__ == '__main__':
    app.run(debug= True)