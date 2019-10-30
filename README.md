# nith result cli
 
This is a cli application to download result of a student from the official NIT Hamirpur result website.

It can be used as a standalone program through command line.
Try to run it as command line program to see more options.

`$ python3 nith_result <RollNumber>`


### To use in a project:
Exports a single function **get_result** which is used to get result of a roll number
and an Exception **ROLL_NUMBER_NOT_FOUND**

```python
>>> from nith_result import get_result, ROLL_NUMBER_NOT_FOUND
```

[download.py](download.py) downloads result of all students concurrently and stores in the **results** directory. This also serves as a demo on how to use [nith_result.py](nith_result.py) in a project.

[createDatabase.py](createDatabase.py) creates a sqlite3 database from the **results** directory.

This project is used by [nithp.herokuapp.com/result/](https://nithp.herokuapp.com/result/)