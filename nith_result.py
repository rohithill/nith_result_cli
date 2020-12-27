import sys
import aiohttp
import lxml.html

import asyncio
import functools
import json
import os, csv
from pathlib import Path
from typing import List
import argparse
import queue

BASE_DIR = f'{os.path.abspath("./result")}'
RESULT_HTML_DIR = f'{BASE_DIR}/html'
RESULT_CSV_DIR = f'{BASE_DIR}/csv'
RESULT_JSON_DIR = f'{BASE_DIR}/json'
RESULT_JSON_RANKS_DIR = f'{BASE_DIR}/json_with_ranks'

if not os.path.exists(RESULT_HTML_DIR):
    os.makedirs(RESULT_HTML_DIR)

if not os.path.exists(RESULT_CSV_DIR):
    os.makedirs(RESULT_CSV_DIR)

SERVER_IP = '59.144.74.15'
SESSION: aiohttp.ClientSession

CONCURRENCY_LIMIT: int = 100
assert CONCURRENCY_LIMIT > 0

USE_CACHE: bool = True

# parser = argparse.ArgumentParser()
# parser.add_argument("roll_number",help="download this roll_number's result")
# parser.add_argument("--url",help="specify url for the result")
# args = parser.parse_args()

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
        self.roll = roll.upper()
        self.branch = branch
        self.year = get_year(roll)

    def __str__(self):
        return f"<{self.roll} ({self.branch})>"


def get_result_url(student):
    year = str(student.year)[2:]
    code = 'scheme'
    URL = f'http://{SERVER_IP}/{code}{year}/studentResult/details.asp'
    return URL

def get_branch(roll):
    ...

def get_year(roll):
    return int('20' + roll[:2])

def student_path(student: Student):
    return f'{student.branch}/{student.year}/{student.roll}'

def read_from_cache(student: Student):
    with open(f'{RESULT_HTML_DIR}/{student_path(student)}.html') as f:
        return f.read()

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

def write_to_cache(student,result):
    fp = get_html_path(student)
    with open(fp,'w') as f:
        f.write(result)

async def fetch(student):
    URL = get_result_url(student)
    async with SESSION.post(URL,data={'RollNumber': student.roll}) as response:
        result = await response.text()
    return result

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
    # if len(res) < 10:

    #     raise
    assert len(res) > 10, f'Result too short {len(res)} < 10'
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

def calculateRank():
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
                    print(e,file=sys.stderr)

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


    # missing entry in official website
    # for sub in modified_result['196047']['result']:
    #     if sub['subject code'] == 'AR-111':
    #         sub['grade'] = 'F'
    #         sub['sub gp'] = '0'


    # redundant entry of subjects in official website
    # for roll in ('184552','17582'):
    #     result = modified_result[roll]['result']
    #     new_result = list(dict((i['Subject Code'],i) for i in result).values())
    #     modified_result[roll]['result'] = new_result

    for branch in branches.keys():
        if not os.path.exists(f'{RESULT_JSON_RANKS_DIR}/{branch}'):
            os.makedirs(f'{RESULT_JSON_RANKS_DIR}/{branch}')
        year_to_roll = branches.get(branch)
        for year in year_to_roll.keys():
            file_name = f'{RESULT_JSON_RANKS_DIR}/{branch}/{year}.json'
            result = []
            for roll in year_to_roll[year]:
                res = modified_result.get(roll)
                if res:
                    result.append(res)
            with open(file_name,'w') as f:
                print("Writing", file_name, len(result))
                f.write(json.dumps(result))

async def get_result(student,use_cache=True):
    if use_cache:
        try:
            data = read_from_cache(student)
            return data
        except FileNotFoundError:
            data = await fetch(student)
    else:
        data = await fetch(student)
    write_to_cache(student,data)
    return data

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
cnt = 0
gpt = 0
async def worker(in_q,out_q,use_cache=True):
    while True:
        s = await in_q.get()
        data = await get_result(s,use_cache=use_cache)
        out_q.put((s,data))
        in_q.task_done()
        global cnt,gpt
        cnt += 1
        if cnt % 100 == 0:
            new_gpt = time.perf_counter()
            print(f'Completed {cnt} {new_gpt - gpt}')
            gpt = new_gpt

async def main():

    students = get_all_students()
    print(f'Total # of Students: {len(students)}')
    # Fetch result
    if False:
        global SESSION
        SESSION = aiohttp.ClientSession()
        workers = []
        fetch_queue = asyncio.Queue()
        res_queue = queue.Queue()
        for i in range(CONCURRENCY_LIMIT):
            w = asyncio.create_task(worker(fetch_queue,res_queue,use_cache=USE_CACHE))
            workers.append(w)

        for s in students:
            await fetch_queue.put(s)
        await fetch_queue.join()
        for w in workers:
            w.cancel()
        await asyncio.gather(*workers, return_exceptions=True)
        await SESSION.close()


    # HTML -> CSV
    # If HTML is malformed, then correct it here
    if False:
        for s in students:
            with open(get_html_path(s)) as f:
                data = f.read()
                if 'Check the Roll Number' in data:
                    continue
                if 'server error' in data:
                    continue
                if 'File or directory not found' in data:
                    continue
                try:
                    data = html_to_csv(data)
                except AssertionError as e:
                    # print(e)
                    print('HTML->CSV',s,s.branch,e)
                else:
                    with open(get_csv_path(s),'w') as g:
                        g.write(data)

    # CSV -> JSON
    if False:
        for s in students:
            fn = get_csv_path(s)
            if not os.path.exists(fn):
                # some rollnos are invalid therefore file doesn't exist
                continue
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

    print('Calculating ranks')
    # JSON -> JSON_WITH_RANKS
    calculateRank()
    # if True:
    #     for s in students:
    #         fn = get_json_path(s)
    #         if not os.path.exists(fn):
    #             continue
    #         with open(fn) as f:
    #             data = json.loads(f.read())
    # JSON -> Database

if __name__ == '__main__':
    import time
    st = time.perf_counter()

    asyncio.run(main())

    et = time.perf_counter()
    print('Time Taken: ',et - st)