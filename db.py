import mysql.connector

db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='12345678',
    database = 'attendance'
)

mycursor = db.cursor()
# mycursor.execute("INSERT INTO students (rollno, time) VALUES (123,123)")
# db.commit()

mycursor.execute("SELECT * FROM students")
for i in mycursor:
    print(i)

# mycursor.execute("DELETE from students")
# db.commit()

def add_student(x):
    data = x['data']
    time = x['time']
    sql = "INSERT INTO students (rollno, time) VALUES (%s, %s)"
    val = (data,time)
    mycursor.execute(sql, val)
    db.commit()
    return "success"

def get_students():
    mycursor.execute("SELECT * FROM students")
    return mycursor.fetchall()
def delete_students():
    mycursor.execute("DELETE from students")
    db.commit()
    return "success"
