'''
Exports a single function get_result which is used to get result of a roll number
and an Exception ROLL_NUMBER_NOT_FOUND

>>> from nith_result import get_result

It can be used as a standalone program through command line.
Try to run it as command line program to see more options.
'''
# 3rd party imports
import aiohttp

# inbuilt imports
import json
import sys
import os
# custom imports
from utils import ResultParser, Student, ROLL_NUMBER_NOT_FOUND
from config import HTML_CACHE_DIR

if not os.path.exists(HTML_CACHE_DIR):
    os.mkdir(HTML_CACHE_DIR)

async def get_result(student,*,session=None,pbar=None):
    '''
    Accepts a student object,optionally an aiohttp session and tqdm progressbar.
    May raise an exception.
    Returns a python dict of result if successful. 
    See convert_to_dict function below for format of returned dict.
    '''
    global net_size
    RESULT_FILE = f'{HTML_CACHE_DIR}/{student.roll_number}.html'
    if not os.path.isfile(RESULT_FILE):
        local_session = False
        if session is None:
            session = aiohttp.ClientSession()
            local_session = True
        async with session.post(student.url,data=student.data) as response:
            result = await response.text()
        with open(RESULT_FILE,'w') as f:
            f.write(result)
        if local_session:
            await session.close()
    else:
        with open(RESULT_FILE,'r') as f:
            result = f.read()
    

    net_size += len(result)
    if pbar:
        pbar.update(1)
    
    if student.roll_number not in result:
        raise ROLL_NUMBER_NOT_FOUND(student.roll_number)
    # parser = ResultParser()
    # parser.custom_init()
    import lxml.html
    doc = lxml.html.fromstring(result)
    semesters = [i.text_content()[-3:] for i in doc.xpath('.//div[starts-with(text(),"Semester")]')]
    # print(semesters)
    # for sem in semesters:
    #     print(sem.text_content())
    # print(doc)
    final_table = []
    tables = doc.xpath('//table[@class="ewTable"]')
    ft = tables[0]
    # print(dir(ft),ft.getchildren(),ft.text_content())
    # print(ft.getchildren())
    tc = []
    for r in ft:
        tc.extend([i.strip() for i in r.text_content().split('\n') if i.strip()])
    final_table.append([])
    final_table[0] = [tc[i:i+2] for i in range(0,len(tc),2)]
        # print(tc,'here')
    # print(tc)
    # data = ft.xpath('.//td/text()')
    # print(data)
    sidx = 0
    for i,t in enumerate(tables[1:]):
        rs = t.xpath('.//tr')
        if i%2==0:
            final_table.append([semesters[sidx]])
        # print(semesters[sidx])
        final_table.append([])
        for j,r in enumerate(rs):
            # print(len(r))
            # xx = r.xpath('.//td')
            # print(dir(xx[0]))
            
            res2 = r.xpath('.//td')
            res = [i.text_content().strip() for i in res2]
            final_table[-1].append(res)
            # res = r.xpath('.//td/text()')
            
            # if j==0 and i%2==0:
            #     res = ['Sr. No'] + res
            # print(res)
            # res = r.xpath('.//td/text()')
            # print()
        # print('---------------------------')
        
        sidx += i%2
        # print(rs[0].getchildren())

    # print(tables)
    # print(final_table)
    # <table class="ewTable">
    # print(student.roll_number)
    if student.roll_number == '196047':
        final_table[2][1].remove('')
        # print(final_table[2][1])
    # try:
        # print(final_table)
        # print(final_table)
        # parser.feed(result)
        # print(parser.tables)
        # print('here')
        # if student.roll_number == 196047:
            # final_table[]
        # try:
        #     assert final_table == parser.tables
        # except Exception as e:
            # with open('asfroll.txt','a') as f:
            #     f.write(student.roll_number + '\n')
                # print('*'*200,student.roll_number)
        # print(parser.tables)
    # except IndexError as e:
        # Assuming that IndexError is raised for invalid numbers
        # raise ROLL_NUMBER_NOT_FOUND(student.roll_number)
    return convert_to_dict(final_table)
    # return convert_to_dict(parser.tables)

def convert_to_dict(result):
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

    result_dict = {
        "name" : result[0][1][1],
        "roll" : result[0][0][1],
        "result" : {
            "head" : result[2][0][1:]
        },
        "summary" : {
            "head" : result[3][0]
        }
    }

    for i in range(1,len(result),3):
        sem = result[i][0].lower()
        result_dict["result"][sem] = [j[1:] for j in result[i+1][1:]]
        summary = result_dict["summary"][sem] = result[i+2][1]

        # validate and store only the sgpi,cgpi
        # eg: "178/22=8.09" -> "8.09"
        for j in (0,2):
            summary[j] = summary[j].replace('=','/')
            
            #  a/b=c
            a,b,c = map(float,summary[j].split('/'))
            summary[j] = str(c)

            from math import ceil
            # validate calculation
            if round(a/b,2) != c:
                print(f'Validation Error : {j}, {a}/{b} = {c} , {ceil(a/b*1000)} {result_dict["roll"]}, {sem}',file=sys.stderr)
    return result_dict

async def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("roll_number",help="download this roll_number's result")
    parser.add_argument("--url",help="specify url for the result")
    args = parser.parse_args()

    try:
        student = Student(args.roll_number.lower(),args.url)
        result = await get_result(student)

        print(json.dumps(result))
    except Exception as e:
        print(e,file=sys.stderr)

# total bytes downloaded
net_size = 0
def get_download_volume():
    return net_size

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
