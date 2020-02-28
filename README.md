# NITH Result CLI
 
This is a cli application to download result of a student from the official NIT Hamirpur result website.


This project uses python3.7+, aiohttp, tqdm.

This project is used by https://nithp.herokuapp.com/result/
## Get this on your computer
Open the terminal and run the following commands:

1. Clone the repository
```bash
$ git clone https://github.com/rohithill/nith_result_cli.git
$ cd nith_result_cli
```
2. Create the virtual environment and install dependencies
```bash
$ python3 -m venv venv
$ ./venv/Scripts/activate
$ pip install -r requirements.txt
```

## Usage
For help, type:
```bash
$ python3 nith_result --help
```
To get result of roll number *17mi526* (output is in JSON format):
```bash
$ python3 nith_result 17mi526
```
To download the result of all students:
```bash
$ python3 download.py
```
Results are stored in **results** directory.


### Todo
- [x] Implement downloads using asyncio
- [x] Use tqdm to provide visualization of downloading
- [ ] Implement ranking mechanism
- [ ] Show success vs failure rate of result being downloaded
  

# Documentation
```
nith_result_cli
│   config.py
|   download.py
│   nith_result.py    
│   README.md
|   requirements.txt
└── utils
    |   __init__.py
    │   branchroll.py
    │   parser.py
    │   student.ppy
```

**nith_result.py** contains `get_result` function which is responsible for fetching the result from the website.

**config.py** contains various configuration variables which do things like in which to store the downloaded result, limit on number of concurrent connections.

**download.py** is responsible for downloading the result of all the students. It uses *aiohttp* and *asyncio* for fast downloading.

**utils** is a package which provides classes viz. `BranchRoll`,`ResultParser` and `Student`. Also includes `ROLL_NUMBER_NOT_FOUND` exception. See below for more details.

**utils/branchroll.py** defines `BranchRoll` class which provides roll numbers for all branches and all batches. A batch is identified by its joining year.

**utils/parser.py** defines `ResultParser` class which is responsible for parsing the result from the downloaded html from the official website. 

**utils/student.py** defines a `Student` class and `ROLL_NUMBER_NOT_FOUND` exception. An object of `Student` class will automatically have result URL. `ROLL_NUMBER_NOT_FOUND` exception is raised whenever a rollnumber is suspected to be not present. 
