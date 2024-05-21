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


# ----------------- ROOT –---------------------------------
@app.route('/root', methods=['GET','POST'])
def root():
    staffid = request.json['data']
    if request.method == 'POST':
        if staff.find_one({"employeeId": staffid}):
            return jsonify({'mode': 'CREATE_SESSION','endpoint': f"/session/{create_session(staffid)}"}) 
    return jsonify({"mes":"hello"})

@app.route('/session/<_id>', methods=['GET','POST'])
def managesession(_id):
    response = request.json
    print(response)
    if request.method == 'POST':
        if session_collection.find_one({"session_id": _id , "staff": response['data'], "is_status": True}):
            end_session(_id)
            return jsonify({'mode': 'END_SESSION','endpoint': ""})
        session_collection.update_one({"session_id": _id}, {"$push": {"students": request.json['data']}})
        return {"status": "success"}
    return jsonify({"mes":"hello"})


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
    if class_name is None:
        return redirect(url_for('create_class'))

    if request.method == 'POST':
        roll_no = request.json.get('data')
        if roll_no:
            classes.update_one({"class_name": class_name}, {"$push": {"students": roll_no}})
            students.insert_one({roll_no: class_name})
            return redirect(f"/listen/{class_name}")
        return redirect(f"/listen/{class_name}")

    return render_template('listen.html')


@app.route("/listen/<class_name>", methods=['POST','GET'])
def listen_class(class_name):
    class_ = classes.find_one({"class_name": class_name})
    if request.method == 'POST':
        print(request.json)
        print(request)
        roll_no = request.json.get('data')
        print(roll_no)
        if roll_no:
            classes.update_one({"class_name": class_name}, {"$push": {"students": roll_no}})
            students.insert_one({roll_no: class_name})
            return redirect(f"/listen/{class_name}")
        return redirect(f"/listen/{class_name}")
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

        return redirect(f'listen/{class_name}')

    return render_template('create_class.html')


@app.route('/view_profile', methods=['GET'])
def view_profile():
    if request.method == 'GET':
        user = staff.find_one({"username": session['username']})
        if user:
            return render_template('view_profile.html', user=user)
        
        return 'User not found'
    return 'Invalid request'




if __name__ == '__main__':
    app.run(debug=True, port=2000)