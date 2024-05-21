@app.route('/create_class', methods=['POST', 'GET'])
def create_class():
    if request.method == 'POST':
        global class_name
        class_name = request.form.get('class_name')
        classes.insert_one({"class_name": class_name, "students": []})
        return redirect(url_for('listen_class', class_name=class_name))

    return render_template('create_class.html')

@app.route("/listen/<class_name>", methods=['POST', 'GET'])
def listen_class(class_name):
    class_ = classes.find_one({"class_name": class_name})
    return render_template('listen.html', messages = class_)

@app.route('/listen', methods=['POST', 'GET'])
def listen():
    if request.method == 'POST':
        roll_no = request.json.get('data')
        print(roll_no)
        if roll_no:
            classes.update_one({"class_name": class_name}, {"$push": {"students": roll_no}})
            students.insert_one({roll_no: class_name})
            return jsonify({"status": "success"})
        return jsonify({"status": "failed","message":f"{roll_no}"})
    
@app.route('/listen/stop', methods=['POST', 'GET'])
def stop_classes():
    session.pop('class_name', None)
    return redirect(url_for('home'))
