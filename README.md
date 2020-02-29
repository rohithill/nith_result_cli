# NITH Result CLI
 
This is a cli application to download result of a student from the official NIT Hamirpur result website.

This project uses python3.7+, aiohttp, tqdm.

If you just want the downladed results, see https://github.com/rohithill/nithp/tree/master/result.

This project is used by https://nithp.herokuapp.com/result/.

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

Please make sure that python version >= 3.7.

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
$ python3 download.py 2> errors.log # stderr is redirected to errors.log
```
Results are stored in **results** directory.


### Todo
- [x] Implement downloads using asyncio
- [x] Use tqdm to provide visualization of downloading
- [x] Implement ranking mechanism
- [ ] Show success vs failure rate of result being downloaded
- [ ] Make CLI better in terms of user experience per batch

# FAQ
### Why did you create this?
For learning and fun. As everything should be.

### Why did you not use threads?
I used threads initially, but I wanted to experiment with the async programming model. So I used asyncio and aiohttp.

### Why didn't you use requests/beautifulsoup?
The result html page is not so complex. And HTMLParser is already in python. 

### I see that batch results are downloaded one at a time. Isn't concurrency reduced?
Yes, you are right. The reason for this is tqdm. If all the batches are downloaded at same time, which was the case before, multiple tqdm progressbars appear on the terminal. As number of batches are quite large, all progressbars doesn't fit on screen. And that causes hell as they try to overwrite each other. Moreover, the loss in concurrency is not very much as the result of a batch is downloaded concurrently.

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
    |   calculateRank.py
    │   parser.py
    │   student.ppy
```

- **nith_result.py** contains `get_result` function which is responsible for fetching the result from the website.

- **config.py** contains various configuration variables which do things like in which to store the downloaded result, limit on number of concurrent connections.

- **download.py** is responsible for downloading the result of all the students. It uses *aiohttp* and *asyncio* for fast downloading.

- **utils** is a package which provides classes viz. `BranchRoll`,`ResultParser` and `Student`. Also includes `ROLL_NUMBER_NOT_FOUND` exception. See below for more details.

- **utils/branchroll.py** defines `BranchRoll` class which provides roll numbers for all branches and all batches. A batch is identified by its joining year.

- **utils/parser.py** defines `ResultParser` class which is responsible for parsing the result from the downloaded html from the official website. 

- **utils/student.py** defines a `Student` class and `ROLL_NUMBER_NOT_FOUND` exception. An object of `Student` class will automatically have result URL. `ROLL_NUMBER_NOT_FOUND` exception is raised whenever a rollnumber is suspected to be not present. 

- **utils/calculateRank.py** adds the rank,cgpi and sgpi fields to the downloaded result and stores the output in `DEST_DIR` declared in `config.py`.

### Structure of a student's result:
`head` field provides corresponding headers.
```json
{
    "name": "ROHIT HILL",
    "roll": "17mi526",
    "result": {
        "head": [
            "Subject",
            "Subject Code",
            "Sub Point",
            "Grade",
            "Sub GP"
        ],
        "s01": [
            [
                "PHYSICS LAB",
                "CSS-117",
                "1",
                "A",
                "10"
            ],
            [
                "COMPUTER WORKSHOP",
                "CSD-114",
                "2",
                "A",
                "20"
            ],
            [
                "BASIC ELECTRONICS ENGINEERING",
                "CSD-115",
                "3",
                "A",
                "30"
            ],
            [
                "BASIC ELECTRONICS ENGINEERING LAB",
                "CSD-119",
                "1",
                "A",
                "10"
            ],
            [
                "ENGINEERING MATHEMATICS-I",
                "CSS-111",
                "3",
                "A",
                "30"
            ],
            [
                "COMPUTER FUNDAMENTALS & PROGRAMMING LAB",
                "CSD-118",
                "1",
                "AB",
                "9"
            ],
            [
                "COMPUTER FUNDAMENTALS & PROGRAMMING",
                "CSD-113",
                "3",
                "AB",
                "27"
            ],
            [
                "ENGINEERING ECONOMICS AND MANAGEMENT",
                "CSH-116",
                "3",
                "B",
                "24"
            ],
            [
                "PHYSICS FOR COMPUTER ENGINEERING",
                "CSS-112",
                "3",
                "A",
                "30"
            ]
        ],
        "s02": [
            [
                "CHEMISTRY FOR COMPUTER ENGINEERS",
                "CSS-122",
                "3",
                "A",
                "30"
            ],
            [
                "COMMUNICATION SKILLS",
                "CSH-123",
                "3",
                "AB",
                "27"
            ],
            [
                "COMMUNICATION SKILLS LAB.",
                "CSH-126",
                "1",
                "A",
                "10"
            ],
            [
                "ENGINEERING MATHEMATICS-II",
                "CSS-121",
                "3",
                "A",
                "30"
            ],
            [
                "ENGINEERING GRAPHICS",
                "CSD-127",
                "3",
                "B",
                "24"
            ],
            [
                "BASIC ELECTRICAL ENGINEERING",
                "CSD-124",
                "3",
                "AB",
                "27"
            ],
            [
                "CHEMISTRY LAB.",
                "CSS-125",
                "1",
                "AB",
                "9"
            ]
        ],
        "s03": [
            [
                "OBJECT ORIENTED PARADIGM LAB",
                "CSD-216",
                "1",
                "AB",
                "9"
            ],
            [
                "PROBABILITY & QUEUING MODELS",
                "CSS-210",
                "3",
                "B",
                "24"
            ],
            [
                "DIGITAL ELECTRONICS & LOGIC DESIGN LAB",
                "CSD-219",
                "1",
                "AB",
                "9"
            ],
            [
                "MICROPROCESSOR AND INTERFACING",
                "CSD-214",
                "3",
                "AB",
                "27"
            ],
            [
                "COMPUTER GRAPHICS LAB",
                "CSD-217",
                "1",
                "AB",
                "9"
            ],
            [
                "MICROPROCESSOR AND INTERFACING LAB",
                "CSD-218",
                "1",
                "AB",
                "9"
            ],
            [
                "OBJECT ORIENTED PARADIGM",
                "CSD-212",
                "3",
                "A",
                "30"
            ],
            [
                "COMPUTER GRAPHICS",
                "CSD-213",
                "3",
                "B",
                "24"
            ],
            [
                "DIGITAL ELECTRONICS AND LOGIC DESIGN",
                "CSD-215",
                "3",
                "A",
                "30"
            ],
            [
                "DISCRETE STRUCTURE",
                "CSD-211",
                "3",
                "AB",
                "27"
            ]
        ],
        "s04": [
            [
                "OPERATING SYSTEM",
                "CSD-222",
                "3",
                "A",
                "30"
            ],
            [
                "OPERATING SYSTEM LAB",
                "CSD-228",
                "1",
                "A",
                "10"
            ],
            [
                "DATA STRUCTURE",
                "CSD-223",
                "3",
                "A",
                "30"
            ],
            [
                "DATA STRUCTURE LAB",
                "CSD-229",
                "2",
                "A",
                "20"
            ],
            [
                "COMPUTER ORGANIZATION",
                "CSD-221",
                "3",
                "A",
                "30"
            ],
            [
                "COMPUTER ORGANIZATION LAB",
                "CSD-227",
                "1",
                "A",
                "10"
            ],
            [
                "SYSTEM SOFTWARE",
                "CSD-224",
                "3",
                "AB",
                "27"
            ],
            [
                "THEORY OF COMPUTATION",
                "CSD-225",
                "3",
                "AB",
                "27"
            ],
            [
                "BASIC ENVIRONMENTAL SCIENCE AND ENGINEERING",
                "CSS-226",
                "3",
                "B",
                "24"
            ]
        ],
        "s05": [
            [
                "ANALYSIS & DESIGN OF ALGORITHMS",
                "CSD-312",
                "3",
                "A",
                "30"
            ],
            [
                "COMMUNICATION ENGINEERING",
                "CSD-315",
                "3",
                "A",
                "30"
            ],
            [
                "COMPILER DESIGN",
                "CSD-314",
                "3",
                "A",
                "30"
            ],
            [
                "COMPILER DESIGN LAB",
                "CSD-319",
                "2",
                "B",
                "16"
            ],
            [
                "DATA BASE MANAGEMENT SYSTEMS",
                "CSD-313",
                "3",
                "A",
                "30"
            ],
            [
                "DATA BASE MANAGEMENT SYSTEMS LAB",
                "CSD-318",
                "2",
                "A",
                "20"
            ],
            [
                "MODELLING AND SIMULATION LAB",
                "CSD-317",
                "2",
                "A",
                "20"
            ],
            [
                "MODELLING AND SIMULATION",
                "CSD-311",
                "3",
                "A",
                "30"
            ],
            [
                "NEURAL NETWORKS AND FUZZY LOGIC",
                "EEO-316(a)",
                "3",
                "AB",
                "27"
            ]
        ]
    },
    "summary": {
        "head": [
            "SGPI",
            "SGPI Total",
            "CGPI",
            "CGPI Total"
        ],
        "s01": [
            "9.5",
            "190",
            "9.5",
            "190"
        ],
        "s02": [
            "9.24",
            "157",
            "9.38",
            "347"
        ],
        "s03": [
            "9.0",
            "198",
            "9.24",
            "545"
        ],
        "s04": [
            "9.45",
            "208",
            "9.3",
            "753"
        ],
        "s05": [
            "9.71",
            "233",
            "9.39",
            "986"
        ]
    },
    "cgpi": "9.39",
    "sgpi": "9.71",
    "rank": {
        "class": {
            "cgpi": 5,
            "sgpi": 5
        },
        "year": {
            "cgpi": 14,
            "sgpi": 32
        },
        "college": {
            "cgpi": 114,
            "sgpi": 113
        }
    }
}
```