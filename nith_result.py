import aiohttp

import os, time, json, functools, re, asyncio, argparse
from pathlib import Path
from collections import defaultdict

VERSION: str = "0.1.0"

BASE_DIR = f'{os.path.abspath("./result")}'
RESULT_HTML_DIR = f'{BASE_DIR}/html'
RESULT_CSV_DIR = f'{BASE_DIR}/csv'
RESULT_JSON_DIR = f'{BASE_DIR}/json'
RESULT_JSON_RANKS_DIR = f'{BASE_DIR}/json_with_ranks'

if not os.path.exists(RESULT_HTML_DIR):
    os.makedirs(RESULT_HTML_DIR)

if not os.path.exists(RESULT_CSV_DIR):
    os.makedirs(RESULT_CSV_DIR)

CONCURRENCY_LIMIT: int = 100
assert CONCURRENCY_LIMIT > 0

SESSION : aiohttp.ClientSession

#-------- CLI --------
parser = argparse.ArgumentParser()
# parser.add_argument("roll_number",help="download this roll_number's result")
# parser.add_argument("--url",help="specify url for the result")
parser.add_argument("--check-for-updates",action='store_true',help="Check if there are any changes between the result on website and html files stored locally")
parser.add_argument("--no-html",dest="html",action='store_false',help='Do not fetch result from website for storing in html dir')
parser.add_argument("--no-csv",dest="csv",action='store_false',help='Do not fetch result from website for storing in csv dir')
parser.add_argument("--no-json",dest="json",action='store_false',help='Do not fetch result from website for storing in json dir')
parser.add_argument("--no-ranks",dest="ranks",action='store_false',help='Do not calculate ranks')
parser.add_argument("--roll-pattern",dest="pattern",help='Filter rolls with this regex')
args = parser.parse_args()

class BranchRoll(dict):
    '''
    This class provides dictionary like access to the roll numbers of various
    branches. For eg:

    >>> b = BranchRoll()
    >>> b.keys()  # list all the branches
    >>> b['CSE'].keys()     # list all the years in CSE branch
    >>> b['CSE']['2017']    # this will give a tuple with roll no of CSE branch of year 2017.

    Note that keys are strings.
    '''
    # This is read only
    def __init__(self):
        BRANCHES = ("CIVIL","ELECTRICAL","MECHANICAL","ECE","CSE","ARCHITECTURE",
                "CHEMICAL","MATERIAL","ECE_DUAL","CSE_DUAL")

        # Rollno format = YEAR + MI + BRANCH_CODE + class roll
        for code,branch in enumerate(BRANCHES,1):
            start_year = 2015 # starting batch year
            end_year = 2019 # current batch year
            roll_start = 1
            roll_end = 100

            if branch == "MATERIAL": # Material science started in year 2017
                start_year = 2017
            if branch == "ECE_DUAL":
                code = 4
            if branch == "CSE_DUAL":
                code = 5

            temp_dict = {}
            for year in range(start_year,end_year+1):
                MI = ''
                if year >= 2018:
                    roll_end = 150
                if branch in ("ECE_DUAL","CSE_DUAL"):
                    if year <= 2017:
                        MI = 'MI'
                    else:
                        roll_start = 501
                        roll_end = 600

                roll_list = [str(year)[-2:]+MI+str(code)+str(i).zfill(len(str(roll_end-1))) for i in range(roll_start,roll_end)]
                temp_dict[str(year)] = tuple(roll_list) # Making read only
            super().__setitem__(branch,temp_dict)

class Student:
    def __init__(self, roll, branch, url=None):
        self.roll = roll
        self.branch = branch
        self.year = get_year(roll)

    def __str__(self):
        return f"<{self.roll} ({self.branch})>"
    __repr__ = __str__

def get_all_students():
    a = BranchRoll()
    students = []
    for branch in a:
        for year in a[branch]:
            for roll in a[branch][year]:
                s = Student(roll,branch)
                assert s.year == int(year)
                students.append(s)
    return students

def get_result_url(student):
    year = str(student.year)[2:]
    code = 'scheme'
    URL = f'http://59.144.74.15/{code}{year}/studentResult/details.asp'
    return URL

def get_year(roll):
    return int('20' + roll[:2])

def student_path(student: Student):
    return f'{student.branch}/{student.year}/{student.roll}'

def create_if_not_exist(func):
    '''Create parent directory path'''
    @functools.wraps(func)
    def inner(*args,**kwargs):
        fp = func(*args,**kwargs)
        pth = Path(fp)
        if not os.path.exists(pth.parent):
            os.makedirs(pth.parent)
        return fp
    return inner

@create_if_not_exist
def get_html_path(student):
    return f'{RESULT_HTML_DIR}/{student_path(student)}.html'

@create_if_not_exist
def get_csv_path(student):
    return f'{RESULT_CSV_DIR}/{student_path(student)}.csv'

@create_if_not_exist
def get_json_path(student):
    return f'{RESULT_JSON_DIR}/{student_path(student)}.json'

@create_if_not_exist
def get_json_with_ranks_path(student):
    return f'{RESULT_JSON_RANKS_DIR}/{student_path(student)}.json'

def read_from_cache(student: Student):
    with open(f'{RESULT_HTML_DIR}/{student_path(student)}.html') as f:
        return f.read()

def write_to_cache(student,result):
    fp = get_html_path(student)
    with open(fp,'w') as f:
        f.write(result)

async def fetch(student):
    URL = get_result_url(student)
    async with SESSION.post(URL,data={'RollNumber': student.roll}) as response:
        result = await response.text()
        result = result.replace('\r\n','\n')
    return result

async def get_result_html(student,check_for_updates=False):
    if check_for_updates:
        try:
            data = read_from_cache(student)
        except FileNotFoundError:
            print('no local file')
            return
        data_new = await fetch(student)
        if data != data_new:
            print('result is outdated')
        else:
            print('result is same')
        return
    try:
        data = read_from_cache(student)
        return data
    except FileNotFoundError:
        data = await fetch(student)
        write_to_cache(student,data)
        return data

def strip_tags(html):
    '''
    Removes the markup tags(html) from the given html and
    returns only the text
    '''
    html = html[html.find('<body>'):html.find('Note')] # After body and before footer
    # html = re.sub('&nbsp;','',html)   # remove the trailing &nbsp from Sr. No
    return re.sub('<[^<]+?>', '', html) # See https://stackoverflow.com/a/4869782

def html_to_list(result):
    '''
    Returns a list with details and result
    List format:
    [
        [<rollnumber>,<name>,<father name>],
        [<semester result>],
        [<semester result>],
        ...
    ]

    Format of <semester result>:
    [
        [<sem>],
        [<result_header>],      # width 6
        [<subject_result>],
        [<subject_result>],
        ...
        [<subject_result>],
        [<summary_header>],     # width 4
        [<summary_result>]
    ]
    '''
    RESULT_TABLE_WIDTH = 6

    data = strip_tags(result)
    data = data.split('Semester : ')
    data = [i.split('\n') for i in data]
    for i in range(len(data)):
        data[i] = [x.strip() for x in data[i] if x.strip()]

    detail_row = data[0]
    for i in range(len(detail_row)):
        if detail_row[i].startswith('Roll Number'):
            details = detail_row[i+1:i+6:2]
            break

    assert len(details) == 3, 'Incomplete student details'

    result = []
    for row in data[1:]:
        # each row is a semester result
        # first element is semester
        # last eight elements are result summary (sgpi, cgpi)
        # rest elements (in between) are subject result
        sem = [row[0]]
        summary_head = row[-8:-4]
        summary_body = [i.split('=')[-1] for  i in row[-4:]]
        summary = [summary_head,summary_body]

        assert (len(row) - 9) % RESULT_TABLE_WIDTH == 0, 'Incorrect format of result'

        sem_result = [row[i:i+RESULT_TABLE_WIDTH] for i in range(1,len(row)-len(summary)-RESULT_TABLE_WIDTH,RESULT_TABLE_WIDTH)]
        assert len(sem_result) >= 2, 'Incomplete semester result'
        result.append([sem] + sem_result + summary)

    assert len(result) > 0, 'Empty result'
    res = [details] + result

    # print(*res,sep='\n')

    # TODO: Check for very short result,
    # possible result of left out student
    # assert
    return res

def list_to_dict(result):
    '''
    Stores result in a dict in the following format:
    {
        "name": <Name>,
        "roll": <Roll Number>,
        "fname": <Father Name>,
        "result": {
            "head": <head of the tables>,
            "S01": [<subject_result>,<subject_result>],
            "S02": [<subject_result>,<subject_result>]
        },
        "summary": {
            "head": <head of the tables>,
            "S01": <summary_result>,
            "S02": <summary_result>
        }
    }
    head : Stores the name of the columns
    subject_result : A list of values corresponding to headers in head of result.
    summary_result : A list of values corresponding to headers in head of summary.
    '''
    details = result[0]
    result_dict = {
        "roll" : details[0],
        "name" : details[1],
        "fname": details[2],
        "result" : {
            "head" : "Subject	Subject Code	Sub Point	Grade	Sub GP".split('\t'),
        },
        "summary" : {
            "head" : 'SGPI	SGPI Total	CGPI	CGPI Total'.split('\t')
        }
    }

    # Result of 2016 batch on official NITH result  website is bit different from others
    # Due to that roll and name are swapped
    if not '0' <= result_dict["roll"][0] <= '9':
        print('executed')
        result_dict["roll"],result_dict["name"] = result_dict["name"], result_dict["roll"]
        result_dict["name"] = result_dict["name"].split('\u00a0')[0]

    for sem_result in result[1:]:
        sem = sem_result[0][0]
        result_body = [i[1:] for i in sem_result[2:-2]]     # Drop the 'Sr. No' column
        summary_body = sem_result[-1]

        assert len(summary_body) == len(result_dict['summary']['head'])
        assert len(result_body[0]) == len(result_dict['result']['head'])

        result_dict['result'][sem] = result_body
        result_dict['summary'][sem] = summary_body

    return result_dict


async def process_student(student):
    data = await get_result_html(student,check_for_updates=args.check_for_updates)

    # HTML -> CSV
    # If HTML is malformed, then correct it manually
    if 'Check the Roll Number' in data:
        return
    if 'server error' in data:
        return
    if 'File or directory not found' in data:
        return
    try:
        data = html_to_list(data)
    except Exception as e:
        print('Exception HTML->CSV',student,student.branch,e)
        return

    # CSV->JSON
    try:
        data = list_to_dict(data)
    except Exception as e:
        print('Exception CSV->JSON',student,student.branch,e)
    else:
        return data

async def worker(queue,out):
    while True:
        s = await queue.get()
        result = await process_student(s)
        out.append((s,result))
        queue.task_done()

async def stage1(students):
    # downloads and return result of students
    # students: a list of students
    # return a list with (student,result) as elements
    global SESSION

    SESSION = aiohttp.ClientSession()
    workers = []
    q = asyncio.Queue()
    out = []
    for s in students:
        await q.put(s)
    for i in range(CONCURRENCY_LIMIT):
        w = asyncio.create_task(worker(q,out))
        workers.append(w)

    print('awaiting queue join')
    await q.join()
    print('queue join success')

    for w in workers:
        w.cancel()
    await asyncio.gather(*workers, return_exceptions=True)

    await SESSION.close()

    assert len(out) == len(students), 'Failed to fetch result of all students'
    return out

def calculate_rank(result):
    # Elements are (student, result_dict) pair
    latest_sem = lambda x: max(filter(lambda x: x != 'head',x['summary'].keys()))
    SGPI_IDX = result[0][1]['summary']['head'].index('SGPI')
    CGPI_IDX = result[0][1]['summary']['head'].index('CGPI')
    for s,r in result:
        sgpi = float(r['summary'][latest_sem(r)][SGPI_IDX])
        cgpi = float(r['summary'][latest_sem(r)][CGPI_IDX])
        r.update({
                    'cgpi': cgpi,
                    'sgpi': sgpi,
                    'rank': {
                        'class': {
                            'cgpi' : None,
                            'sgpi' : None,
                        },
                        'year': {
                            'cgpi' : None,
                            'sgpi' : None,
                        },
                        'college' : {
                            'cgpi' : None,
                            'sgpi' : None,
                        }
                    }
               })

    for key in ('cgpi','sgpi'):
        result.sort(key=lambda x: x[1][key],reverse=True)

        rank_store = defaultdict(int)
        for s,r in result:
            s_rank = r['rank']

            class_key = str(s.year) + s.branch
            year_key = s.year

            rank_store['college'] += 1
            rank_store[year_key] += 1
            rank_store[class_key] += 1

            s_rank['college'][key] = rank_store['college']
            s_rank['year'][key] = rank_store[year_key]
            s_rank['class'][key] = rank_store[class_key]
        print(key)
        print(*[(i[0],i[1][key]) for i in result[:40]],sep='\n')
    return result

def stage2(res):
    # Calculate rankings
    print('Calculating ranks')
    return calculate_rank(res)

def stage3():
    # Result (with ranks) to SQLite db
    pass

async def main():
    students = get_all_students()

    if args.pattern:
        p = re.compile(args.pattern + '$', re.IGNORECASE)
        students = list(filter(lambda x: p.match(x.roll),students))

    print(f'Total # of Students: {len(students)}')

    res = await stage1(students)

    res = filter(lambda x: x[1], res) # remove students with None as result
    res = list(res)
    print('Total downloaded:',len(res))

    res = stage2(res)
    for e in res:
        s,r = e
        with open(get_json_with_ranks_path(s),'w') as f:
            f.write(json.dumps(r))

    #TODO: Add stage 3

if __name__ == '__main__':
    import time
    st = time.perf_counter()

    asyncio.run(main())

    et = time.perf_counter()
    print('Program finish time:',et - st)