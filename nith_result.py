'''
Exports a single function get_result which is used to get result of a roll number
and an Exception ROLL_NUMBER_NOT_FOUND

>>> from nith_result import get_result

It can be used as a standalone program through command line.
Try to run it as command line program to see more options.
'''

import json
from utils.parser import ResultParser
from utils.student import Student, ROLL_NUMBER_NOT_FOUND

async def get_result(session,student):
    '''
    Accepts a roll_number and optionally a url to fetch result from.
    May raise an exception.
    Returns a json string of result if successful.

    [[['Name','<Name>'],['Roll Number','<Roll Number>']],
    ...Below three rows will occur for each semester...
    [<Semester>],
    [<Table of result for <Semester>],
    [<Summary of result for <Semester>]]
    '''
    async with session.post(student.url,data=student.data) as response:
        result = await response.text()
        # print(result)
        parser = ResultParser()
        parser.custom_init()
        try:
            parser.feed(result)
            parser.tables[0][0][1] = parser.tables[0][0][1].replace('\xa0','')
        except IndexError as e:
            # Assuming that IndexError is raised for invalid numbers
            raise ROLL_NUMBER_NOT_FOUND
            # return
        # Remove '\xa0' from the name of the student
        return parser.tables

async def main():
    import sys
    import argparse
    import aiohttp
    parser = argparse.ArgumentParser()
    parser.add_argument("roll_number",help="download this roll_number's result")
    parser.add_argument("--html",action="store_true",help="Generates html output of the result")
    parser.add_argument("--url",help="specify url for the result")
    args = parser.parse_args()
    try:
        async with aiohttp.ClientSession() as session:
            student = Student(args.roll_number.lower(),args.url)
            # print(student)
            result = await get_result(session,student)
        # print(result)
        if args.html:
            table_number = 0
            name_table = result[0]
            for table in result:
                print('<table>')
                if table_number % 3 == 1:
                    print('<tr><td>Semester</td>')
                    print(f'<td>{table[0]}</td><tr>')
                else:
                    for row in table:
                        print('<tr>')
                        for cell in row:
                            print(f'<td>{cell}</td>')
                        print('</tr>')
                print('</table>')
                table_number += 1
        else:
            for r in result:
                print(*r,sep='\n')
    except Exception as e:
        print('--->',e)
        raise e
        # sys.exit(0)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
