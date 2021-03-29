# NITH Result CLI

This is a cli application to download result of a student from the official NIT Hamirpur result website.
Results are downloaded quite fast. 🚀

This project uses python3.7+, aiohttp.

See your result at https://nithp.herokuapp.com/result/.

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
$ source ./venv/Scripts/activate
$ pip install -r requirements.txt
```

## Usage
For help, type:
```bash
$ python3 nith_result.py --help
```
To get result of roll number *17mi526* (written inside `result` directory):
```bash
$ python3 nith_result.py --roll-pattern=17mi526
```
`roll-pattern` is accepts regex, so to download result of 2017 batch:
```bash
$ python3 nith_result.py --roll-pattern=17(mi)?...
```
To download the result of all students:
```bash
$ python3 nith_result.py
```

### Todo
- [x] Implement downloads using asyncio
- [x] Implement ranking mechanism
- [ ] Make CLI better in terms of user experience
- [ ] Use a progress bar to provide visualization of downloading (eg https://github.com/rsalmei/alive-progress)
- [ ] Show success vs failure rate of result being downloaded

# FAQ
### Why did you create this?
For learning and fun. As everything should be.

### Why did you not use threads?
I used threads initially, but I wanted to experiment with the async programming model. So I used asyncio and aiohttp.

### Why didn't you use requests/beautifulsoup?
I used beautiful soup with lxml. It was slow. And The result html page is not so complex.

# Documentation
TODO