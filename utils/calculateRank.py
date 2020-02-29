# Calculate ranks of the students
# Global ranks, year ranks, class ranks
import os
import json
import sys

from utils import BranchRoll
from config import RESULT_DIR, DEST_DIR
from download import EXT


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