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
students_collection = mongo.db.students
staff = mongo.db.staff
session_collection = mongo.db.sessions
classes = mongo.db.classes
subjects = mongo.db.subjects
attendance = mongo.db.attendance
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
        if staff.find_one({"username": username}):
            return 'Username already exists'
        if password != request.form.get('repeatPassword'):
            return 'Passwords do not match'
        class_subjects = []
        for i in range(int(request.form.get('count'))):
            class_subjects.append({f"class{i}":request.form.get(f'class{i}'),f"subject{i}":request.form.get(f'subject{i}')})

        print(class_subjects)
        staff.insert_one({
            "name": request.form.get('name'),
            "employeeId": request.form.get('employeeId'),
            "username": username,
            "password": generate_password_hash(password),
            "class_subjects": class_subjects
        })
        return redirect(url_for('home'))
    else:
        return render_template('register.html',subjects=subjects.find(),classes=classes.find())

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
    session_collection.update_one({"session_id": _id}, {"$set": {"is_status": False}})
    student_ = session_collection.find_one()['students'][0]
    class_ = students_collection.find_one({"student_id": student_})['class_name']
    staff_id = session_collection.find_one()["staff"]
    staff_ = staff.find_one({"employeeId": staff_id})
    class_subjects= staff_.get('class_subjects')
    subject = ""
    for n,i in enumerate(class_subjects):
        if i.get(f'class{n}') == class_: 
            subject = i.get(f'subject{n}')
            break
    Attendance = []
    for i in session_collection.find_one()['students']:
        if classes.find_one({"class_name": class_, "students": i}):
            Attendance.append({"student_id": i, "status": "Present"})
        else:
            Attendance.append({"student_id": i, "status": "Absent"})
    attendance.insert_one({"class": class_, "subject": subject, "staff": staff_id,"timestamp":datetime.datetime.now() ,"Attendance": Attendance})

    
    



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
# ----------------- ROOT –---------------------------------
@app.route('/root', methods=['GET','POST'])
def root():
    staffid = request.json['data']
    print(staffid)
    print(type(staffid))
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
            print("Session already exists")
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
        for i in students:
            students_collection.insert_one({"student_id": i, "class_name": class_name})
        return redirect(url_for('create_class'))
    return 'Invalid request'

# ---------------------Attendance------------------------------------
@app.route('/attendance', methods=['POST','GET'])
def view_attendance():
    return render_template('view_attendance.html',attendance=attendance.find())
if __name__ == '__main__':
    app.run(debug=True, port=2000)