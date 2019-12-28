from utils.departments import departments as dept
from utils.student import Student
from nith_result import get_result

# modified fetch function with semaphore
import asyncio
from aiohttp import ClientSession

# no of results to fetch at the same time
MAX_CONCURRENT_DOWNLOADS = 1

async def bound_fetch(sem, url, session,rollno):
    # Getter function with semaphore.
    async with sem:
        await fetch(url, session,rollno)


async def run(roll_number_generator):
    url = "http://localhost:8080/{}"
    tasks = []
    # create instance of Semaphore
    sem = asyncio.Semaphore(1000)

    # Create client session that will ensure we dont open new connection
    # per each request.
    async with ClientSession() as session:
        for rollno in roll_number_generator:
            # pass Semaphore and session to every GET request
            task = asyncio.ensure_future(bound_fetch(sem, 'http://59.144.74.15/scheme17/studentResult/details.asp', session,rollno))
            tasks.append(task)

        responses = asyncio.gather(*tasks)
        await responses
    return tasks
        # print(responses,tasks)
        # print(tasks[0].result(),dir(tasks[0]))

async def get_batch_result(roll_number_generator,url=None):
    batch_result = []

  
    return batch_result

async def download_result_and_store(roll_number_generator, file_path, url=None):
    batch_result = await run(roll_number_generator)
    return len(batch_result)
# sys.exit()

async def download_many(session,students):
    tasks = []
    for student in students:
        tasks.append(asyncio.create_task(get_result(session,student)))
    results = asyncio.gather(*tasks)
    await results
    # print(results,tasks,sep='\n')
    return (task.result() for task in tasks)
async def download_and_store(session,students,file_name):
    fp = open(file_name,'w')
    results = await download_many(session,students)
    for result in results:
        fp.write(str(result)+'\n')

async def main():
    myclass = dept.get('CSE_DUAL').get('2017')
    lt = 100
    ff = []
    # for rollno in myclass:
    #     if not lt:
    #         break
    #     lt -= 1
    #     print(rollno)
    #     ff.append(Student(rollno))
    ff.append(Student('17mi562'))
    async with ClientSession() as session:
        await download_and_store(session,ff,'./results.txt')

if __name__ == '__main__':
    asyncio.run(main())

