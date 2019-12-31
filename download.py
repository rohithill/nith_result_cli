from utils.departments import departments as depts
from utils.student import Student, ROLL_NUMBER_NOT_FOUND
from nith_result import get_result

# modified fetch function with semaphore
import asyncio
from aiohttp import ClientSession

# no of results to fetch at the same time
MAX_CONCURRENT_DOWNLOADS = 1
ctf = None
async def download_many(session,students,*,debug=False):
    tasks = []
    for student in students:
        tasks.append(asyncio.create_task(get_result(session,student)))
    results = asyncio.gather(*tasks,return_exceptions=True)
    await results
    global ctf
    ctf = tasks
    # a list of tasks is returned (due to exceptions)
    # otherwise how to handle exceptions?
    return tasks

async def download_and_store(session,students,file_name):
    fp = open(file_name,'w')
    results = await download_many(session,students)
    no_of_students = 0
    idx = 0
    for result in results:
        # print(dir(result))
        print(students[idx].roll_number)
        idx+=1
        if isinstance(result.exception(),ROLL_NUMBER_NOT_FOUND):
            if result.exception() == ROLL_NUMBER_NOT_FOUND:
                print("hey there")
            print(result.exception(),repr(result.exception()),result)
            # logger.emit(result.exception())
        else:
            # print('Writing result')
            fp.write(str(result.result())+'\n')
            no_of_students += 1
    return no_of_students

async def main():
    total_students = 0
    FOLDER_PATH = 'result-async'
    import os
    tasks = []
    async with ClientSession() as session:
        if not os.path.exists(FOLDER_PATH):
            os.mkdir(FOLDER_PATH)
        for dept_name in depts.keys():
            dept = depts.get(dept_name)
            if not os.path.exists(f'{FOLDER_PATH}/{dept_name}'):
                os.mkdir(f'{FOLDER_PATH}/{dept_name}')
            for year in dept.keys():
                # print(dept_name,year)
                file_name = f'result-async/{dept_name}/{year}.txt'
                # print(file_name)
                if os.path.exists(file_name):
                    print(f'{file_name} : Already Exists, Skipping...')
                    continue
                roll_nos = [Student(i) for i in dept.get(year)]
                tasks.append(asyncio.create_task(download_and_store(session,roll_nos,file_name)))

        results = asyncio.gather(*tasks)
        await results
        for task in tasks:
            print(task.result())
            total_students += task.result()
        print(total_students)

if __name__ == '__main__':
    asyncio.run(main())

