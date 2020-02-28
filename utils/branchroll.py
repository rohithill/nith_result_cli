# This acts like a dictionary

class BranchRoll(dict):
    '''
    This class provides dictionary like access to the roll numbers of various
    branches. For eg:
    
    >>> b = BranchRoll()
    >>> b.keys()  # list all the branches
    >>> b['CSE'].keys()     # list all the years in CSE branch
    >>> b['CSE']['2017']    # this will give a tuple with roll no of CSE branch of year 2017.

    Note that keys are strings.
    '''
    # This is read only
    def __init__(self):
        BRANCHES = ("CIVIL","ELECTRICAL","MECHANICAL","ECE","CSE","ARCHITECTURE",
                "CHEMICAL","MATERIAL","ECE_DUAL","CSE_DUAL")
        
        # Rollno format = YEAR + MI + BRANCH_CODE + class roll
        for code,branch in enumerate(BRANCHES,1):
            start_year = 2015 # starting batch year
            end_year = 2019 # current batch year
            roll_start = 1
            roll_end = 100
            
            if branch == "MATERIAL": # Material science started in year 2017
                start_year = 2017
            if branch == "ECE_DUAL":
                code = 4
            if branch == "CSE_DUAL":
                code = 5

            temp_dict = {}
            for year in range(start_year,end_year+1):
                MI = ''
                if year >= 2018:
                    roll_end = 150
                if branch in ("ECE_DUAL","CSE_DUAL"):
                    if year <= 2017:
                        MI = 'mi'
                    else:
                        roll_start = 501
                        roll_end = 600

                roll_list = [str(year)[-2:]+MI+str(code)+str(i).zfill(len(str(roll_end-1))) for i in range(roll_start,roll_end)]
                temp_dict[str(year)] = tuple(roll_list) # Making read only
            
            dict.__setitem__(self,branch,temp_dict)
    