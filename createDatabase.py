import sqlite3
import json
import os
# Missing columns : 15120, 16517,15mi529
# Roll no's with no result: 16287, 17825, iiitu18149

DB_NAME = 'test1.db'

def init_db():
    print('Initialiazing ----->>>>>>')
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = 1")
    cur = conn.cursor()

    cur.execute('''CREATE TABLE student(
        rollno text PRIMARY KEY,
        name text not null,
        father_name text not null)''')

    cur.execute('''CREATE TABLE course(
        code TEXT PRIMARY KEY,
        title TEXT not null,
        credits INTEGER NOT NULL)''')

    cur.execute('''CREATE TABLE result(
        rollno TEXT,
        code TEXT,
        grade INTEGER,
        semester INTEGER NOT NULL,
        FOREIGN KEY (rollno)  REFERENCES student (rollno),
        FOREIGN KEY (code)  REFERENCES course (code),
        UNIQUE (rollno,code));''')
    
    cur.execute('''CREATE VIEW sgpi AS
        SELECT result.rollno,
        result.semester,
        round(CAST(sum(result.grade) as REAL)/sum(course.credits),2) AS sgpi
        FROM result
        JOIN course USING (code)
        GROUP BY result.rollno, result.semester;''')

    cur.execute('''CREATE VIEW cgpi AS
        SELECT result.rollno,
        round(CAST(sum(result.grade) as REAL)/sum(course.credits),2) AS CGPI
        FROM result
        JOIN course USING (code)
        GROUP BY result.rollno;''')

    conn.commit()
    
def main():
    # os.remove(DB_NAME)
    if not os.path.exists(DB_NAME):
        init_db()

    db = sqlite3.connect(DB_NAME)
    cursor = db.cursor()
    total_students = 0
    for path,_,files in os.walk('results'):
        for file in files:
            file_path = os.path.join(path,file)
            if file_path.endswith('mtech.json'):
                continue
            with open(file_path,'r') as f:
                results = json.load(f)
            for r in results:
                try:
                    student_name,father_name = [i.strip().title() for i in r[0][0][1].split('S/D of')]
                    rollno = r[0][1][1]
                    cursor.execute('''INSERT INTO student VALUES (?,?,?)''',(rollno,student_name,father_name))
                    for i in range(1,len(r),3):
                        sem = int(r[i][0][1:])
                        for subres in r[i+1][1:]:
                            _,sub_name,sub_code,credit,_,grade = [i.strip() for i in subres]
                            credit = int(credit)
                            grade = int(grade)
                            try:
                                cursor.execute('''INSERT INTO course VALUES (?,?,?)''',(sub_code,sub_name,credit))
                            except sqlite3.IntegrityError:
                                pass
                            cursor.execute('''INSERT INTO result VALUES (?,?,?,?)''',(rollno,sub_code,grade,sem))
                except Exception as e:
                    print(rollno,e)
                total_students += 1
    db.commit()
    print(total_students)

if __name__ == '__main__':
    main()
    #ABCD
