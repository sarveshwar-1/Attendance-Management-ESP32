from flask import Flask, request,render_template,redirect,url_for,session,jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'


# --------- DATABASE CONNECTION ------------
app.config["MONGO_URI"] = "mongodb://localhost:27017/Attendance"
mongo = PyMongo(app)
students = mongo.db.students
staff = mongo.db.staff
session_collection = mongo.db.sessions
classes = mongo.db.classes
# ------------------------------------------

# @app.before_request
# def require_login():
#     allowed_routes = ['login', 'register']  # routes that don't require login
#     if request.endpoint not in allowed_routes and 'username' not in session:
#         return redirect(url_for('login'))

# ------------ AUTHENTICATION ----------------

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = staff.find_one({"username": username})
        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            session['logged_in'] = True
            return redirect(url_for('home'))
        return 'Invalid username or password'
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
        
        staff.insert_one({
            "name": request.form.get('name'),
            "employeeId": request.form.get('employeeId'),
            "username": username,
            "password": generate_password_hash(password),
            "classes": request.form.getlist('classes[]'),
            "subjects": request.form.getlist('subjects[]')
        })
        session['username'] = username
        return redirect(url_for('home'))
    else:
        return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/home', methods=['POST','GET'])
def home():
    return render_template('index.html')

# --------------- SESSION MANAGEMENT UTILS ----------------

def get_session(_id):
    return session_collection.find_one({"session_id": _id, "is_status": True})

def end_session(_id):
    return session_collection.find_one_and_update({"session_id": _id}, {"$set": {"is_status": False}})

def create_session(staffid):
    session_id = uuid.uuid4().hex
    
    session_collection.insert_one(
        {
            "session_id": session_id,
            "class_name": "",
            "students": [],
            "staff": staffid,
            "is_status": True,
            "timestamp": f"{datetime.datetime.now()}",
        })
    return session_id

# ---------------------------------------------------------
global class_started
class_started = {"status" : False, "endpoint": ""}

# ----------------- ROOT –---------------------------------
@app.route('/root', methods=['GET','POST'])
def root():
    staffid = request.json['data']
    print(staffid)
    if request.method == 'POST':
        if staff.find_one({"employeeId": staffid}):
            return jsonify({'mode': 'CREATE_SESSION','endpoint': f"/session/{create_session(staffid)}", "status": "success"})
        return jsonify({"status":"staff not found"}) 
    return jsonify({"status":"failed"})

@app.route('/session/<_id>', methods=['GET','POST'])
def managesession(_id):
    response = request.json
    print(response)
    if request.method == 'POST':
        if session_collection.find_one({"session_id": _id , "staff": response['data'], "is_status": True}):
            end_session(_id)
            return jsonify({'mode': 'END_SESSION','endpoint': ""})
        session_collection.update_one({"session_id": _id}, {"$push": {"students": request.json['data']}})
        return jsonify({"status": "success"})
    return jsonify({"mes":"hello"})

@app.route('/add_class', methods=['POST','GET'])
def add_class():
    if request.method == 'POST':
        class_name = request.form.get('class_name')
        staff.update_one({"username": session['username']}, {"$push": {"classes": class_name}})
        return 'Class added successfully'
    return render_template('add_class.html')    

@app.route('/view_profile', methods=['GET'])
def view_profile():
    if request.method == 'GET':
        user = staff.find_one({"username": session['username']})
        if user:
            return render_template('view_profile.html', user=user)
        
        return 'User not found'
    return 'Invalid request'

# ---------------------Create Class------------------------------------
@app.route('/create_class', methods=['POST','GET'])
def create_class():
    sessions = session_collection.find()
    print(sessions)
    return render_template('create_class.html',sessions=sessions)
@app.route("/create_class/session", methods=['POST'])
def create_class_session():
    if request.method == 'POST':
        class_name = request.form.get('class_name')
        session_id = request.form.get('session_id')
        students = session_collection.find_one({"session_id": session_id})['students']
        classes.insert_one({"class_name": class_name, "students": students})
        return redirect(url_for('createclass'))
    return 'Invalid request'


# @app.route('/view_class/<class_id>', methods=['GET'])
# def view_class(class_id):
#     _class = classes.find_one({"_id": class_id})
#     return render_template('view_class.html', messages= _class)
# @app.route('/create_class', methods=['POST','GET'])
# def create_class():
#     if request.method == 'POST':
#         class_name = request.form.get('class_name')
#         _class = {
#             "_id": uuid.uuid4().hex, 
#             "class_name": class_name,
#             "students": []
#         }
#         classes.insert_one(_class)
        
#         global class_started
#         class_started = {"status":True, "endpoint": f"/add_students/{_class['_id']}", "class_id": f"{_class['_id']}"}
        
#         return redirect(f"/view_class/{_class['_id']}")

#     return render_template('create_class.html')

# @app.route('/add_students/<class_id>', methods=['GET'])
# def add_students(class_id):
#     if request.method == 'POST':
#         student = request.form.get('student')
#         classes.update_one({"_id": class_id}, {"$push": {"students": student}})
#         return {"status": "success"}
#     return {'mes':'hello'}




if __name__ == '__main__':
    app.run(debug=True, port=2000)