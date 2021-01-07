import sqlite3
import json
import os

# Missing columns : 15120, 16517,15mi529
# Roll no's with no result: 16287, 17825, iiitu18149
# from config import DB_NAME, DEST_DIR
DB_NAME='mydb.db'
DEST_DIR = 'result/json_with_ranks'

def init_db():
    # There are four tables
    # student, result, summary

    print('Initialiazing .....')
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = 1")
    cur = conn.cursor()
    # print('hefe')
    cur.execute('''CREATE TABLE student(
        roll text PRIMARY KEY,
        name text not null,
        branch text not null,
        cgpi REAL not null,
        sgpi REAL not null,
        rank_college_cgpi INTEGER not null,
        rank_college_sgpi INTEGER not null,
        rank_year_cgpi INTEGER not null,
        rank_year_sgpi INTEGER not null,
        rank_class_cgpi INTEGER not null,
        rank_class_sgpi INTEGER not null
        );''')

    cur.execute('''CREATE TABLE result(
        roll TEXT,
        grade TEXT NOT NULL,
        sem INTEGER NOT NULL,
        sub_gp INTEGER NOT NULL,
        sub_point INTEGER NOT NULL,
        subject TEXT NOT NULL,
        subject_code TEXT NOT NULL,
        FOREIGN KEY (roll)  REFERENCES student (roll),
        UNIQUE (roll,subject_code));''')

    # cur.execute('''CREATE TABLE result_pg(
    #     rollno TEXT,
    #     code TEXT,
    #     grade INTEGER,
    #     semester INTEGER NOT NULL,
    #     FOREIGN KEY (rollno)  REFERENCES student (rollno),
    #     FOREIGN KEY (code)  REFERENCES course (code),
    #     UNIQUE (rollno,code));''')

    # cur.execute('''CREATE VIEW sgpi AS
    #     SELECT result.rollno,
    #     result.semester,
    #     round(CAST(sum(result.grade) as REAL)/sum(course.credits),2) AS sgpi
    #     FROM result
    #     JOIN course USING (code)
    #     GROUP BY result.rollno, result.semester;''')

    # cur.execute('''CREATE VIEW sgpi_pg AS
    #     SELECT result_pg.rollno,
    #     result_pg.semester,
    #     round(CAST(sum(result_pg.grade) as REAL)/sum(course.credits),2) AS sgpi
    #     FROM result_pg
    #     JOIN course USING (code)
    #     GROUP BY result_pg.rollno, result_pg.semester;''')

    # cur.execute('''CREATE VIEW cgpi AS
    #     SELECT result.rollno,
    #     round(CAST(sum(result.grade) as REAL)/sum(course.credits),2) AS CGPI
    #     FROM result
    #     JOIN course USING (code)
    #     GROUP BY result.rollno;''')

    # cur.execute('''CREATE VIEW cgpi_pg AS
    #     SELECT result_pg.rollno,
    #     round(CAST(sum(result_pg.grade) as REAL)/sum(course.credits),2) AS CGPI
    #     FROM result_pg
    #     JOIN course USING (code)
    #     GROUP BY result_pg.rollno;''')
    cur.execute('''CREATE TABLE summary(
        roll TEXT,
        sem INTEGER,
        cgpi REAL,
        sgpi REAL,
        cgpi_total INTEGER,
        sgpi_total INTEGER,
        UNIQUE(roll,sem)
        );''')
    conn.commit()

def insert_subjects(result):
    for i in range(1,len(result),3):
        sem = int(result[i][0][1:])
        for subres in result[i+1][1:]:
            _,sub_name,sub_code,credit,*_ = [i.strip() for i in subres]
            credit = int(credit)
            try:
                cursor.execute('''INSERT INTO course VALUES (?,?,?)''',(sub_code,sub_name,credit))
            except sqlite3.IntegrityError:
                pass

def insert_result(result):
    result_insert_stmt = '''INSERT INTO result VALUES (?,?,?,?)'''
    r = result
    try:
        student_name = r[0][0][1]
        rollno = r[0][1][1]
        if (rollno == '184552'):
            print('here')
        try:
            cursor.execute('''INSERT INTO student VALUES (?,?)''',(rollno,student_name))
            # print('inserted')
        except Exception as e:
            print('here',e)
            # print(path)
            # if 'pg' in path:
                # pass
            # else:
                # raise e
        for i in range(1,len(r),3):
            sgpi,_,cgpi,*_ = result[i+2][1]
            sgpi = sgpi.split('=')[-1]
            cgpi = cgpi.split('=')[-1]

            sem = int(r[i][0][1:])
            for subres in r[i+1][1:]:
                _,sub_name,sub_code,credit,_,grade = [i.strip() for i in subres]
                credit = int(credit)
                grade = int(grade)
                # try:
                    # pass
                    # cursor.execute('''INSERT INTO course VALUES (?,?,?)''',(sub_code,sub_name,credit))
                # except sqlite3.IntegrityError:
                    # print('inte',end=' ')
                    # pass
                # print(result_insert_stmt)
                cursor.execute(result_insert_stmt,(rollno,sub_code,grade,sem))
            cursor.execute('INSERT INTO summary VALUES (?,?,?,?)',(rollno,sem,sgpi,cgpi))

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(tb)
        print(rollno,e)

def insert_student(s):
    data = (
        s['roll'],
        s['name'],
        s['branch'],
        s['cgpi'],
        s['sgpi'],
        s['rank']['college']['cgpi'],
        s['rank']['college']['sgpi'],
        s['rank']['year']['cgpi'],
        s['rank']['year']['sgpi'],
        s['rank']['class']['cgpi'],
        s['rank']['class']['sgpi'],
    )
    cursor.execute('INSERT INTO student values(?,?,?,?,?, ?,?,?,?,?, ?)',data)

def insert_result(s):
    # try:
    #     s['result'][1]
    # except:
    #     print(s['roll'],s)
    #     return
    # print(s['result'][1],s['result'][0].keys())
    for sub in s['result']:
        # print('here')
        # print('sub\n',sub,type(sub))
        # break
        try:
            data = (
                s['roll'],
                sub['grade'],
                sub['sem'],
                sub['sub gp'],
                sub['sub point'],
                sub['subject'],
                sub['subject code']
            )
        except Exception as e:
            print(sub,e)
            return
        cursor.execute('INSERT INTO result VALUES (?,?,?,?,?, ?,?)',data)

def insert_summary(s):
    for r in s['summary']:
        data = (
            s['roll'],
            r['sem'],
            r['cgpi'],
            r['sgpi'],
            r['cgpi total'],
            r['sgpi total'],
        )
        cursor.execute('INSERT INTO summary VALUES(?,?,?,?,? ,?)',data)
def get_files():
    for path,_,files in os.walk(DEST_DIR):
        for file in files:
            file_path = os.path.join(path,file)
            yield file_path

def main():
    total_students = 0
    for file_path in get_files():
        # if 'pg' in path:
            # print('skipping dualdegree')
            # result_insert_stmt = '''INSERT INTO result_pg VALUES (?,?,?,?)'''
            # continue
        # if file_path.endswith('mtech.json'):
        #     continue
        ans = 0
        print("Processing ",file_path)
        # continue
        with open(file_path,'r') as f:
            data = json.loads(f.read())
        for r in data:
            insert_student(r)
            try:
                insert_result(r)
            except:
                print(r)
            insert_summary(r)
            ans += 1
            # try:
            # except Exception as e:
            #     print(e,r)

        db.commit()
        total_students += ans
    print(total_students)

if __name__ == '__main__':
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    if not os.path.exists(DB_NAME):
        init_db()
    db = sqlite3.connect(DB_NAME)
    cursor = db.cursor()
    main()