from aiohttp import ClientSession,TCPConnector
from tqdm import tqdm

import asyncio
import sys
import json

from utils import BranchRoll, Student, ROLL_NUMBER_NOT_FOUND
from nith_result import get_result
from config import RESULT_DIR, CONCURRENCY_LIMIT

EXT = 'json' # file extension to store data

# This function adds semaphore support to func, 
# useful for limiting the concurrent calls when func doesn't support it natively
def limiter(func,semaphore):
    async def wrapper(*args,**kwargs):
        async with semaphore:
            res = await func(*args,**kwargs)
            return res
    return wrapper

async def download_many(students,file_name,session,*,pbar=None,debug=False,connector=None):
    pbar = tqdm(desc=file_name,total=len(students),file=sys.stdout)
    tasks = []
    for student in students:
        # print(student.roll_number,file=sys.stderr)
        tasks.append(asyncio.create_task(get_result(student,session=session,pbar=pbar)))
    await asyncio.gather(*tasks,return_exceptions=True)
    # a list of tasks is returned (due to exceptions)
    # otherwise how to handle exceptions?
    return tasks
    
async def download_and_store(students,file_name,session):
    results = await download_many(students,file_name,session)

    complete_result = [i.result() for i in filter(lambda x: not x.exception(),results)]
    
    # log exceptions
    for result in filter(lambda x: x.exception(),results):
        if not isinstance(result.exception(),ROLL_NUMBER_NOT_FOUND):
            print(result.exception(),file=sys.stderr)
    
    if complete_result:
        with open(file_name,'w') as f:
            f.write(json.dumps(complete_result))
        
    return len(complete_result)

async def main():
    import os
    global get_result
    
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

    # This will limit the no of concurrent calls to get_result
    get_result = limiter(get_result,semaphore)

    branches = BranchRoll()
    total_students = 0
    tasks = []

    # should i create a global session like this one 
    # or should download_many create a session for itself?

    async with ClientSession() as session:
        if not os.path.exists(RESULT_DIR):
            os.mkdir(RESULT_DIR)

        for branch in branches.keys():
            if not os.path.exists(f'{RESULT_DIR}/{branch}'):
                os.mkdir(f'{RESULT_DIR}/{branch}')

            year_to_roll = branches.get(branch)
            
            for year in year_to_roll.keys():
                file_name = f'{RESULT_DIR}/{branch}/{year}.{EXT}'
                if os.path.exists(file_name):
                    print('Already Exists, Skipping... ' + file_name)
                    continue
                rolls = [Student(roll) for roll in year_to_roll.get(year)]
                result = asyncio.create_task(download_and_store(rolls,file_name,session))
                await result

if __name__ == '__main__':
    asyncio.run(main())
    from nith_result import get_download_volume
    print(f'Total bytes downloaded : {get_download_volume()}')
