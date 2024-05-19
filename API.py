from flask import Flask, request,render_template,redirect,url_for,session
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/Attendance"
mongo = PyMongo(app)
students = mongo.db.students
staff = mongo.db.staff
classes = mongo.db.classea
app.config['SECRET_KEY'] = 'secret'
# @app.before_request
# def require_login():
#     allowed_routes = ['login', 'register']  # routes that don't require login
#     if request.endpoint not in allowed_routes and 'username' not in session:
#         return redirect(url_for('login'))
@app.route('/post', methods=['POST','GET'])
def index():
    if request.method == 'POST':
        data = request.json
        students.insert_one(data)
        print('success')
        return 'success'
@app.route('/home', methods=['POST','GET'])
def home():
    return render_template('index.html')


@app.route('/deleteAll', methods=['POST','GET'])
def delete():
    students.delete_many({})
    return redirect(url_for('home'))

@app.route('/login', methods=['POST','GET'])
def login():
    print(request.method)
    if request.method == 'POST':
        print(request.form)
        username = request.form.get('username')
        password = request.form.get('password')
        user = staff.find_one({"username": username})
        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            session['logged_in'] = True
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
            print(request.form)
            staff.insert_one({
                "username": username,
                "password": generate_password_hash(password),
                "classes": request.form.getlist('classes[]'),
                "subjects": request.form.getlist('subjects[]')
            })
            session['username'] = username
            return redirect(url_for('home'))
    else:
        return render_template('register.html')
@app.route('/add_class', methods=['POST','GET'])
def add_class():
    if request.method == 'POST':
        class_name = request.form.get('class_name')
        staff.update_one({"username": session['username']}, {"$push": {"classes": class_name}})
        return 'Class added successfully'
    else:
        return 'Invalid request'

@app.route('/listen', methods=['POST','GET'])
def listen():

    # class_name = session.get('class_name')

    print(f"{class_name = }")
    
    if class_name is None:
        return redirect(url_for('create_class'))
    
    if request.method == 'POST':
        roll_no = request.form.get('data')
        print(roll_no)
        if roll_no:
            classes.update_one({"class_name": class_name}, {"$push": {"students": roll_no}})
            return redirect(f"/listen/{class_name}")
        return redirect(f"/listen/{class_name}")
    return render_template('listen.html')

@app.route("/listen/<class_name>", methods=['POST','GET'])
def listen_class(class_name):
    class_ = classes.find_one({"class_name": class_name})
    return render_template('listen.html',messages=class_)

@app.route('/listen/stop',methods=['POST','GET'])
def stop_classes():
    class_name = None
    if session['class_name']: del session['class_name']
    return redirect(url_for('home'))

@app.route('/create_class', methods=['POST','GET'])
def create_class():
    if request.method == 'POST':
        global class_name
        class_name = request.form.get('class_name')
        classes.insert_one({"class_name": class_name, "students": []})
        session['class_name'] = class_name
        return redirect(f'listen/{class_name}')
    else:
        return render_template('create_class.html')

@app.route('/view_profile', methods=['GET'])
def view_profile():
    if request.method == 'GET':
        user = staff.find_one({"username": session['username']})
        if user:
            return render_template('view_profile.html', user=user)
        else:
            return 'User not found'
    else:
        return 'Invalid request'

@app.route('/view_students', methods=['GET'])
def view_students():
    if request.method == 'GET':
        students_list = students.find()
        return render_template('view_students.html', students=students_list)
    else:
        return 'Invalid request'
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
if __name__ == '__main__':
    app.run(debug=True, port=2000)