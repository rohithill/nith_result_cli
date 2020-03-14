# Calculate ranks of the students
# Global ranks, year ranks, class ranks
# Also adds branch.
import os
import json
import sys

from utils import BranchRoll
from config import RESULT_DIR, DEST_DIR

PROPER_JSON = True     # This will decide if processed output is more 
                        # conformant to json, Increases output size on True

def calculateRank():
    branches = BranchRoll()
    college_list = []
    year_list = {}
    modified_result = {}

    for branch in branches.keys():
        if not os.path.exists(f'{RESULT_DIR}/{branch}'):
            continue
        year_to_roll = branches.get(branch)
        for year in year_to_roll.keys():
            file_name = f'{RESULT_DIR}/{branch}/{year}.{EXT}'
            if not os.path.exists(file_name):
                continue
            with open(file_name,'r') as f:
                class_result = json.loads(f.read())
            latest_sem = lambda s: max(s['summary'].keys())

            # filtering students who may have left the college
            # class_result = filter(lambda s:not( int(s['roll'][:2]) + (int(latest_sem(s)[1:])+1)//2 != 20 and int(latest_sem(s)[1:]) <= 7),class_result)
            # class_result = list(class_result)
            
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
            for field in ('cgpi','sgpi'):
                class_result.sort(key=lambda x: float(x[field]),reverse=True)
                for rank,s in enumerate(class_result,1):
                    modified_result[s['roll']]['rank']['class'][field] = str(rank)

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

    if not os.path.exists(DEST_DIR):
        os.mkdir(DEST_DIR)

    if PROPER_JSON:
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
    for sub in modified_result['196047']['result']:
        if sub['subject code'] == 'AR-111':
            sub['grade'] = 'F'
            sub['sub gp'] = '0'

    # redundant entry in official website
    modified_result['184552']['result'].remove({
        'subject': 'ENGINEERING MATHEMATICS-II', 
        'subject code': 'ECS-121', 'sub point': '3', 
        'grade': 'F', 'sub gp': '0', 'sem': '2'})
    # print(to_remove)
    # modified_result['184552']['result'].remove(modified_result['184552']['result'].)
    # print(modified_result['196047'])
    # modified_result['196047']
    for branch in branches.keys():
        if not os.path.exists(f'{DEST_DIR}/{branch}'):
            os.mkdir(f'{DEST_DIR}/{branch}')
        year_to_roll = branches.get(branch)
        for year in year_to_roll.keys():
            file_name = f'{DEST_DIR}/{branch}/{year}.{EXT}'
            result = []
            for roll in year_to_roll[year]:
                res = modified_result.get(roll)
                if res:
                    result.append(res)
            with open(file_name,'w') as f:
                f.write(json.dumps(result))

from download import EXT