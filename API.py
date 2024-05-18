from flask import Flask, request,render_template,redirect,url_for
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/Attendance"
mongo = PyMongo(app)
students = mongo.db.students
staff = mongo.db.staff
app.config['SECRET_KEY'] = 'secret'
@app.route('/post', methods=['POST','GET'])
def index():
    if request.method == 'POST':
        data = request.json
        students.insert_one(data)
        print('success')
        return 'success'
@app.route('/home', methods=['POST','GET'])
def home():
    y = students.find()
    y = list(y)
    print(y)
    return render_template('index.html', messages=y)
@app.route('/deleteAll', methods=['POST','GET'])
def delete():
    students.delete_many({})
    return redirect(url_for('home'))
@app.route('/main', methods=['POST','GET'])
def main():
    return render_template('main.html')
from flask import session

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = staff.find_one({"username": username})
        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            return redirect(url_for('home'))
        else:
            return 'Invalid username or password'
    else:
        return render_template('login.html')

@app.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if students.find_one({"username": username}):
            return 'Username already exists'
        if password != request.form.get('repeatPassword'):
            return 'Passwords do not match'
        else:
            staff.insert_one({
                "username": username,
                "password": generate_password_hash(password),
                "classes": request.form.get('classes[]'),
                "subjects": request.form.get('subjects[]')
            })
            session['username'] = username
            return redirect(url_for('home'))
    else:
        return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))
if __name__ == '__main__':
    app.run(debug=True, port=2000)