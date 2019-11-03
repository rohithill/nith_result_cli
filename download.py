import time
import concurrent.futures
import sys
import json
import os
from queue import deque
import urllib.error
import socket
from nith_result import get_result,ROLL_NUMBER_NOT_FOUND

# consts contains info related to rollno and branches specific to nith
# format is starting rollno prefix, total  studetns , width, branch)
RESULT_DIR = 'result'

constants = [('civil','1'),('electrical','2'),('mechanical','3'),('ece','4'),
            ('cse','5'),('architecture','6'),('chemical','7')]

# Each batch is a 4 tuple entry,
# prefix,number of students, rollno width, branch name

batches = []
for branch,c in constants:
    for y in map(str,range(12,19)): # rollno's from 2012 to 2018
        if y < '18':
            batches.append((y+c,99,2,branch))
        else:
            # with new batches 3 digits ending is in use. 
            # Starting from 18 series of roll nos.
            batches.append((y+c,150,3,branch))

batches.extend([
    ('15mi4', 70, 2, 'ece_dual'),
    ('16mi4', 70, 2, 'ece_dual'),
    ('17mi4', 70 ,2, 'ece_dual'),
    ('1845', 99 , 2 , 'ece_dual'),

    ('14mi5', 70, 2, 'cse_dual'),
    ('15mi5', 70, 2, 'cse_dual'),
    ('16mi5', 70, 2, 'cse_dual'),
    ('17mi5', 70, 2, 'cse_dual'),
    ('1855' , 99, 2, 'cse_dual'),

    ('15mi4', 70, 2, 'pg_ece_dual'),

    ('14mi5', 70, 2, 'pg_cse_dual'),
    ('15mi5', 70, 2, 'pg_cse_dual'),

    ('178' , 99, 2, 'material'),
    ('188', 150 , 3, 'material'),
    ])

# IIIT Una
batches.extend((f'iiitu{y}1',99,2,'cse_una') for y in ('15','16','17','18'))
batches.extend((f'iiitu{y}2',99,2,'ece_una') for y in ('15','16','17','18'))
batches.extend((f'iiitu{y}3',99,2,'it_una') for y in ('17','18'))

# print(batches)

if not os.path.exists(RESULT_DIR):
    os.mkdir(RESULT_DIR)

def get_batch_result(roll_number_generator,url=None):
    batch_result = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_list = deque()
        for roll_number in roll_number_generator:
            future = executor.submit(get_result,roll_number,url)
            future_list.append((future,roll_number))
        while future_list:
            future, roll_number = future_list.popleft()
        # for future, roll_number in future_list:
            try:
                data = json.loads(future.result())
                batch_result.append(data)
                print('rollnumber: ' , roll_number)
            except ROLL_NUMBER_NOT_FOUND as e:
                pass
            # except urllib.error.URLError as e:
            except socket.timeout as e:
            #     # if socket.timeout == e:
                # print('socket timeout')
                print(roll_number,e)
                future_list.append((executor.submit(get_result,roll_number,url),roll_number))
            except urllib.error.HTTPError as e:
                print('yaha',roll_number,e)
            except urllib.error.URLError as e:
                print('here',roll_number,e)
                future_list.append((executor.submit(get_result,roll_number,url),roll_number))
            except Exception as e:
                print(roll_number,e)

            #     if urllib.error.URLError == e:
            #         print("Possible timeout error")
            #     print(f"{roll_number}",e,file=sys.stderr)
            # else:
        print('batch_complete')
    return batch_result

def download_result_and_store(roll_number_generator, file_path, url=None):
    batch_result = get_batch_result(roll_number_generator,url)
    if (len(batch_result)):
        with open(file_path,'w') as f:
            json.dump(batch_result,f)
    return len(batch_result)

# sys.exit()
st = time.time()

for batch in batches:
    prefix, ending, width, branch = batch
    print("Processing batch:",prefix,branch)

    if not os.path.exists(f'{RESULT_DIR}/{branch}'):
        os.mkdir(f'{RESULT_DIR}/{branch}')

    file_path = f'{RESULT_DIR}/{branch}/batch_{prefix}.json'
    roll_pattern = prefix + '%s'
    roll_number_generator = (roll_pattern % str(i).zfill(width) for i in range(1,ending+1))

    if os.path.isfile(file_path):
        print(f'File path {file_path} already exists --- Skipping')
    else:
        url = None
        if (branch.startswith('pg')):
            url = f'http://59.144.74.15/dualdegree{prefix[:2]}/studentResult/details.asp'
            print(url, ' for pg')
        no_of_studs = download_result_and_store(roll_number_generator,file_path,url)
        et = time.time()

        print('Time taken: ',et-st)
        print(f'Total Students found for {prefix} {branch}:',no_of_studs)
        print()

    # mtech result of dual degree
    # if batch[0].startswith('15mi'):
    #     file_path = f'results/{branch}/batch_{prefix}_mtech.json'
    #     if os.path.isfile(file_path):
    #         print(f'File path {file_path} already exists --- Skipping')
    #     else:
    #         no_of_studs = download_result_and_store(roll_number_generator,file_path,'http://59.144.74.15/dualdegree15/studentResult/details.asp')
    #         et = time.time()

    #         print('Time taken: ',et-st)
    #         print(f'Total Students found for {prefix} {branch}:',no_of_studs)
    #         print()