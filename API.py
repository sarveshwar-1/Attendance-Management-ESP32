from flask import Flask, request,render_template
import db
app = Flask(__name__)

@app.route('/', methods=['POST','GET'])
def index():
    if request.method == 'POST':
        data = request.json
        db.add_student(data)
        render_template('index.html')
        
        return 'data entered successfully'
    y = db.get_students()
    return render_template('index.html',messages = y)

if __name__ == '__main__':
    app.run(debug=True, port=2000)