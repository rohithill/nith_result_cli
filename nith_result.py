import aiohttp
import lxml.html

import os, time, json, csv, functools, re
import asyncio
import argparse
from pathlib import Path
from typing import List

BASE_DIR = f'{os.path.abspath("./result")}'
RESULT_HTML_DIR = f'{BASE_DIR}/html'
RESULT_CSV_DIR = f'{BASE_DIR}/csv'
RESULT_JSON_DIR = f'{BASE_DIR}/json'
RESULT_JSON_RANKS_DIR = f'{BASE_DIR}/json_with_ranks'

if not os.path.exists(RESULT_HTML_DIR):
    os.makedirs(RESULT_HTML_DIR)

if not os.path.exists(RESULT_CSV_DIR):
    os.makedirs(RESULT_CSV_DIR)

SESSION: aiohttp.ClientSession

CONCURRENCY_LIMIT: int = 100
assert CONCURRENCY_LIMIT > 0

USE_CACHE: bool = True

parser = argparse.ArgumentParser()
# parser.add_argument("roll_number",help="download this roll_number's result")
# parser.add_argument("--url",help="specify url for the result")
parser.add_argument("--check-for-updates",action='store_true',help="Check if there are any changes between the result on website and html files stored locally")
parser.add_argument("--no-html",dest="html",action='store_false',help='Do not fetch result from website for storing in html dir')
parser.add_argument("--no-csv",dest="csv",action='store_false',help='Do not fetch result from website for storing in csv dir')
parser.add_argument("--no-json",dest="json",action='store_false',help='Do not fetch result from website for storing in json dir')
parser.add_argument("--no-ranks",dest="ranks",action='store_false',help='Do not calculate ranks')
parser.add_argument("--roll-pattern",dest="pattern",help='Filter rolls with this regex')
# parser.add_argument('rol')
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

def get_all_students() -> List[Student]:
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

async def get_result(student,check_for_updates=False):
    if check_for_updates:
        try:
            data = read_from_cache(student)
        except FileNotFoundError:
            print('no local file')
            return
        data2 = await fetch(student)
        if data != data2:
            print('result is outdated')
        else:
            print('result is same')
        return
    try:
        data = read_from_cache(student)
        return data
    except FileNotFoundError:
        pass
    data = await fetch(student)
    write_to_cache(student,data)
    return data

def html_to_csv(result):
    doc = lxml.html.fromstring(result)
    semesters = [i.text_content()[-3:] for i in doc.xpath('.//div[starts-with(text(),"Semester")]')]
    final_table = []
    tables = doc.xpath('//table[@class="ewTable"]')
    ft = tables[0]
    tc = []
    for r in ft:
        tc.extend([i.strip() for i in r.text_content().split('\n') if i.strip()])
    final_table.append([])
    final_table[0] = [tc[i:i+2] for i in range(0,len(tc),2)]
    sidx = 0
    for i,t in enumerate(tables[1:]):
        rs = t.xpath('.//tr')
        if i%2==0:
            final_table.append([semesters[sidx]])
        # print(semesters[sidx])
        final_table.append([])
        for j,r in enumerate(rs):
            res2 = r.xpath('.//td')
            res = [i.text_content().strip() for i in res2]
            final_table[-1].append(res)
        sidx += i%2
    # if student.roll_number == '196047':
    #     final_table[2][1].remove('')
    res = []
    s_details = final_table[0]
    s_roll = s_details[0][1]
    s_name = s_details[1][1]
    f_name = s_details[2][1]
    res.append(f'{s_roll}\t{s_name}\t{f_name}')
    for row in range(1,len(final_table),3):
        sem = final_table[row][0]
        data = final_table[row+1]
        footer = final_table[row+2]
        res.append(sem)
        for row in data:
            res.append('\t'.join(row))

        # two rows in footer
        res.append('\t'.join(footer[0]))
        res.append('\t'.join(i.split('=')[-1] for i in footer[1]))
    assert len(res) > 10, f'Result too short {len(res)} <= 10'
    return '\n'.join(res)

def csv_to_dict(result):
    '''
    Stores result in a dict in the following format:
    {
        "name": <Name>,
        "roll": <Roll Number>,
        "result": {
            "head": <head of the tables>,
            "S01": [<subject_result>,<subject_result>],
            "S02": [<subject_result>,<subject_result>]
        },
        "summary": {
            "head": <head of the tables>,
            "S02": <summary_result>
            "S01": <summary_result>,
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

    c_sem = None
    LOOK_SEMESTER = 1
    LOOK_RESULT_BODY = 2
    state = LOOK_SEMESTER
    # sem(1) means sem section has 1 row
    # body(n) means body section can have variable rows
    # csv_pattern: sem(1) -> res_header(1) -> body(n) -> summary_head(1) -> summary(1) -> sem
    ptr = 1
    while ptr < len(result):
        if state == LOOK_SEMESTER:
            assert len(result[ptr]) == 1
            c_sem = result[ptr][0]
            result_dict["result"][c_sem] = []
            state = LOOK_RESULT_BODY
            ptr += 2 # skip header
        elif state == LOOK_RESULT_BODY:
            if result[ptr] == result_dict['summary']['head']:
                result_dict["summary"][c_sem] = result[ptr+1]
                ptr += 2 # skip summary body
                state = LOOK_SEMESTER
                continue
            result_dict["result"][c_sem].append(result[ptr][1:])
            ptr += 1
    return result_dict

def calculate_rank():
    branches = BranchRoll()
    college_list = []
    year_list = {}
    modified_result = {}

    for branch in branches.keys():
        if not os.path.exists(f'{RESULT_JSON_DIR}/{branch}'):
            continue
        year_to_roll = branches.get(branch)
        for year in year_to_roll.keys():
            rolls = year_to_roll[year]
            class_result = []
            for roll in rolls:
                file_name = f'{RESULT_JSON_DIR}/{branch}/{year}/{roll.upper()}.json'

                if not os.path.exists(file_name):
                    continue

                with open(file_name,'r') as f:
                    class_result.append(json.loads(f.read()))
            latest_sem = lambda s: max(filter(lambda x: 'S' == x[0].upper(),s['summary'].keys()))
            # print(f'{len(class_result)}')
            # filtering students who may have left the college
            # class_result = filter(lambda s:not( int(s['roll'][:2]) + (int(latest_sem(s)[1:])+1)//2 != 20 and int(latest_sem(s)[1:]) <= 7),class_result)
            # class_result = list(class_result)

            # print(f'latest sem  {latest_sem(s)}')
            for s in class_result:
                try:
                    sgpi = s['summary'][latest_sem(s)][0]
                    cgpi = s['summary'][latest_sem(s)][2]

                    modified_result[s['roll']] = s
                    s['branch'] = branch

                    # adds the branch
                    # This also updates class_result
                    modified_result[s['roll']].update(
                    {
                        'cgpi': None,
                        'sgpi': None,
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

                    modified_result[s['roll']]['sgpi'] = sgpi
                    modified_result[s['roll']]['cgpi'] = cgpi

                except Exception as e:
                    print(e)

            # class rank calculation
            try:
                for field in ('cgpi','sgpi'):
                    # print(class_result[0])
                    class_result.sort(key=lambda x: float(x[field]),reverse=True)
                    for rank,s in enumerate(class_result,1):
                        modified_result[s['roll']]['rank']['class'][field] = str(rank)
            except KeyError as e:

                print(f'CalculateRank KeyError,')
            college_list.extend(class_result)
            if not year_list.get(year):
                year_list[year] = []
            year_list[year].extend(class_result)
    # year rank calculation
    for year in year_list:
        result = year_list[year]
        for field in ('cgpi','sgpi'):
            result.sort(key=lambda x: float(x[field]),reverse=True)
            for rank,s in enumerate(result,1):
                modified_result[s['roll']]['rank']['year'][field] = str(rank)

    # college rank calculation
    result = college_list
    for field in ('cgpi','sgpi'):
        result.sort(key=lambda x: float(x[field]),reverse=True)
        for rank,s in enumerate(result,1):
            modified_result[s['roll']]['rank']['college'][field] = str(rank)

    # converting to proper json
    for roll in modified_result:
                temp_list = []
                r = modified_result[roll]
                for sem in r['result']:
                    if sem == 'head':
                        continue
                    for sub in r['result'][sem]:
                        temp_dict = {}
                        for i,j in zip(r['result']['head'],sub):
                            temp_dict[i.lower()] = j
                        temp_dict['sem'] = str(int(sem[1:]))
                        temp_list.append(temp_dict)
                r['result'] = temp_list

                # change summary
                temp_list = []
                for sem in r['summary']:
                    if sem == 'head':
                        continue
                    temp_dict = {}
                    for i,j in zip(r['summary']['head'],r['summary'][sem]):
                        temp_dict[i.lower()] = j
                    temp_dict['sem'] = str(int(sem[1:]))
                    temp_list.append(temp_dict)
                r['summary'] = temp_list

    # missing entry in official website
    # for sub in modified_result['196047']['result']:
    #     if sub['subject code'] == 'AR-111':
    #         sub['grade'] = 'F'
    #         sub['sub gp'] = '0'


    # redundant entry of subjects in official website
    for roll in ('184552','17582'):
        result = modified_result[roll]['result']
        new_result = list(dict((i['subject code'],i) for i in result).values())
        modified_result[roll]['result'] = new_result

    for branch in branches.keys():
        if not os.path.exists(f'{RESULT_JSON_RANKS_DIR}/{branch}'):
            os.makedirs(f'{RESULT_JSON_RANKS_DIR}/{branch}')
        year_to_roll = branches.get(branch)
        for year in year_to_roll.keys():
            result = []
            cnt = 0
            for roll in year_to_roll[year]:
                res = modified_result.get(roll)
                if res:
                    cnt += 1
                    student = Student(roll,branch)
                    file_name = get_json_with_ranks_path(student)

                    with open(file_name,'w') as f:
                        f.write(json.dumps(res))
            print(f'{branch} {year} {cnt}')



cnt = 0
gpt = 0
async def process_student(queue):
    while True:
        s = await queue.get()
        while True:
            if args.html:
                # print('Downloading results from website to html dir')
                data = await get_result(s,check_for_updates=args.check_for_updates)
            if args.check_for_updates:
                break

            # HTML -> CSV
            # If HTML is malformed, then correct it here
            if args.csv:
                # print(f'Parsing html to csv {s}')
                with open(get_html_path(s)) as f:
                    data = f.read()
                    if 'Check the Roll Number' in data:
                        break
                    if 'server error' in data:
                        break
                    if 'File or directory not found' in data:
                        break
                    try:
                        data = html_to_csv(data)
                    except AssertionError as e:
                        print('HTML->CSV',s,s.branch,e)
                        break
                    else:
                        with open(get_csv_path(s),'w') as g:
                            g.write(data)

            # CSV -> JSON
            if args.json:
                # print('Parsing csv to json')
                fn = get_csv_path(s)
                # some rollnos are invalid therefore file doesn't exist
                # if not os.path.exists(fn):
                    # continue
                with open(fn) as f:
                    data = csv.reader(f,delimiter='\t')
                    data = list(data)
                try:
                    data = csv_to_dict(list(data))
                except Exception as e:
                    print('CSV->JSON',s,s.branch,e)
                else:
                    with open(get_json_path(s),'w') as g:
                        g.write(json.dumps(data))
            break
        global cnt,gpt
        cnt += 1
        if cnt % 100 == 0:
            new_gpt = time.perf_counter()
            print(f'Completed {cnt} {new_gpt - gpt}')
            gpt = new_gpt
        queue.task_done()

async def main():
    global SESSION

    students = get_all_students()
    print(args)
    if args.pattern:
        p = re.compile(args.pattern + '$', re.IGNORECASE)
        students = list(filter(lambda x: p.match(x.roll),students))
    print(students[:5])
    print(f'Total # of Students: {len(students)}')

    SESSION = aiohttp.ClientSession()
    workers = []
    q = asyncio.Queue()
    for s in students:
        await q.put(s)
    for i in range(CONCURRENCY_LIMIT):
        w = asyncio.create_task(process_student(q))
        workers.append(w)
    print('awaiting queue join')
    await q.join()
    print('queue join success')
    for w in workers:
        w.cancel()
    await asyncio.gather(*workers, return_exceptions=True)
    await SESSION.close()


    # print('Calculating ranks')
    # JSON -> JSON_WITH_RANKS
    if args.ranks:
        calculate_rank()
    # if True:
    #     for s in students:
    #         fn = get_json_path(s)
    #         if not os.path.exists(fn):
    #             continue
    #         with open(fn) as f:
    #             data = json.loads(f.read())


if __name__ == '__main__':
    import time
    st = time.perf_counter()

    asyncio.run(main())

    et = time.perf_counter()
    print('Program finish time: ',et - st)