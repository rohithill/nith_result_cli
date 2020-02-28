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

# custom imports
from utils import ResultParser, Student, ROLL_NUMBER_NOT_FOUND

async def get_result(student,*,session=None,pbar=None):
    '''
    Accepts a student object,optionally an aiohttp session and tqdm progressbar.
    May raise an exception.
    Returns a python dict of result if successful. 
    See convert_to_dict function below for format of returned dict.
    '''
    local_session = False
    if session is None:
        session = aiohttp.ClientSession()
        local_session = True
    async with session.post(student.url,data=student.data) as response:
        global net_size
        result = await response.text()

        net_size += len(result)
        if pbar:
            pbar.update(1)
        
        if student.roll_number not in result:
            raise ROLL_NUMBER_NOT_FOUND(student.roll_number)
        parser = ResultParser()
        parser.custom_init()
        try:
            parser.feed(result)
        except IndexError as e:
            # Assuming that IndexError is raised for invalid numbers
            raise ROLL_NUMBER_NOT_FOUND(student.roll_number)
        if local_session:
            await session.close()
        return convert_to_dict(parser.tables)

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
    # print(result)
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
