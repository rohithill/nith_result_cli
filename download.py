import asyncio
from aiohttp import ClientSession
from tqdm import tqdm

from utils.departments import departments as depts
from utils.student import Student, ROLL_NUMBER_NOT_FOUND
from nith_result import get_result
from config import RESULT_DIR


async def download_many(session,students,*,pbar=None,debug=False):
    tasks = []
    for student in students:
        tasks.append(asyncio.create_task(get_result(session,student,pbar=pbar)))
    results = asyncio.gather(*tasks,return_exceptions=True)
    await results
    # a list of tasks is returned (due to exceptions)
    # otherwise how to handle exceptions?
    return tasks
    
async def download_and_store(session,students,file_name):
    import sys
    import json
    pbar = tqdm(desc=file_name,total=len(students),file=sys.stdout)
    results = await download_many(session,students,pbar=pbar)
    no_of_students = 0
    idx = 0
    fp = open(file_name,'w')
    for result in results:
        # print(dir(result))
        # print(students[idx].roll_number)
        if result.exception():
            if isinstance(result.exception(),ROLL_NUMBER_NOT_FOUND):
                # print(result.exception(),file=sys.stderr)
                pass
            else:
                pass
                # print(result.exception())
        else:
            # print('Writing result')
            fp.write(json.dumps(result.result())+'\n')
            no_of_students += 1
        idx+=1
    # print(students[0].roll_number,no_of_students)
    return no_of_students

async def main():
    import os
    total_students = 0
    tasks = []
    async with ClientSession() as session:
        if not os.path.exists(RESULT_DIR):
            os.mkdir(RESULT_DIR)

        for dept_name in depts.keys():
            dept = depts.get(dept_name)
            
            if not os.path.exists(f'{RESULT_DIR}/{dept_name}'):
                os.mkdir(f'{RESULT_DIR}/{dept_name}')
            
            for year in dept.keys():
                file_name = f'{RESULT_DIR}/{dept_name}/{year}.txt'
                message = f'{file_name}'
                if os.path.exists(file_name):
                    print('Already Exists, Skipping... ' + message )
                    continue
                else:
                    print('Downloading...' + message)
                roll_nos = [Student(i) for i in dept.get(year)]
                tasks.append(asyncio.create_task(download_and_store(session,roll_nos,file_name)))

        await asyncio.gather(*tasks)
        # print('done')
        for task in tasks:
            # print(task.result())
            total_students += task.result()
        # print(total_students)

if __name__ == '__main__':
    asyncio.run(main())
    # from nith_result import print_size
    # print_size()
