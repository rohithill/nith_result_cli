import sqlite3
import json
import os

db = sqlite3.connect('mydb.db')
cursor = db.cursor()
cursor.execute('''DROP TABLE IF EXISTS students''')
db.commit()
cursor.execute('''CREATE TABLE students(rollno TEXT PRIMARY KEY,result TEXT)''')
total_students = 0
for path,_,files in os.walk('results'):
    # rfile = 'result_cse_dual_17mi5.json'
    for file in files:
        file_path = os.path.join(path,file)
        if file_path.endswith('mtech.json'):
            continue
        # print(file_path)
        with open(file_path,'r') as f:
            results = json.load(f)
        for r in results:
            rollno = r[0][1][1]
            # print(rollno)
            cursor.execute('''INSERT INTO students VALUES(?,?)''',(rollno,json.dumps(r)))
            total_students += 1
            print(rollno ,end = ' ')
        print()
        print()
db.commit()
print(total_students)