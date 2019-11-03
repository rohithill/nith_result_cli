'''
Exports a single function get_result which is used to get result of a roll number
and an Exception ROLL_NUMBER_NOT_FOUND

>>> from nith_result import get_result

It can be used as a standalone program through command line.
Try to run it as command line program to see more options.
'''

import json
import hashlib
import urllib.error
from urllib import parse, request
from html.parser import HTMLParser

class ROLL_NUMBER_NOT_FOUND(Exception): 
  
    # Constructor or Initializer 
    def __init__(self): 
        self.value = 'Error: Roll No. is invalid.'
  
    # __str__ is to print() the value 
    def __str__(self): 
        return(self.value) 

class ResultParser(HTMLParser):
    def custom_init(self):
        self.inside = False
        self.tr = False
        self.td = False
        self.divt = False
        self.tables = []

    def handle_starttag(self, tag, attrs):
        if tag == 'table' and not self.inside:
            self.tables.append([])
            self.inside = True
        if self.inside and tag=='tr':
            self.tr = True
            self.tables[-1].append([])
        if self.tr and tag=='td':
            self.td = True
        if not self.inside and tag == 'div':
            self.divt = True

    def handle_data(self,data):
        if self.td:
            data = data.strip()
            if data:
                self.tables[-1][-1].append(data)
        if self.divt and not self.inside:
            data = data.strip()
            if data:
                data = [i.strip() for i in data.split(':')]
                if data[0] == 'Semester':
                    self.tables.append([data[1]])

    def handle_endtag(self, tag):
        if tag=='td':
            self.td = False
        elif tag=='tr':
            self.tr = False
        elif tag == 'table':
            self.inside = False
        if tag == 'div' and self.divt:
            self.divt = False

class Student:
    def __init__(self, roll_number,url=None):
        self.roll_number = roll_number
        self.url = url or self.get_result_url()
        # print(self.url)
    def get_result_student(self):
        data = parse.urlencode({'RollNumber':self.roll_number}).encode()

        # print(self.url)
        req = request.Request(self.url,data)
        the_page = b''
        error = False
        # try:
        with request.urlopen(req,timeout=15) as response:
            the_page = response.read()
        # print('---------------------\n',the_page)
        # except urllib.error.HTTPError as e:
            # error = e
        # if error:
        #     import sys
        #     print(error,file=sys.stderr)
        if 'redirect_dict' in dir(req):
            # print("redirected")
            raise ROLL_NUMBER_NOT_FOUND
        # return page content with error (which is roll no. not found). Magic number is hash of error page
        return the_page

    def get_result_url(self):
        url = "http://59.144.74.15/{}{}/studentResult/details.asp"
        if self.roll_number.startswith('iiitu'):
            year = self.roll_number[5:7]
            college_code = 'IIITUNA'
        else:
            year = self.roll_number[:2]
            college_code = 'scheme'
        return url.format(college_code,year)

    def __str__(self):  
        return f"Roll_number: {self.roll_number}"

def get_result(roll_number: str,url=None):
    '''
    Accepts a roll_number and optionally a url to fetch result from.
    May raise an exception.
    Returns a json string of result if successful.

    JSON Format : 
    [[['Name','<Name>'],['Roll Number','<Roll Number>']],
    ...Below three rows will occur for each semester...
    [<Semester>],
    [<Table of result for <Semester>],
    [<Summary of result for <Semester>]]
    '''
    stud = Student(roll_number,url)
    result = stud.get_result_student()
    result = result.decode()
    # print(result)
    r = ResultParser()
    r.custom_init()
    r.feed(result)
    r.tables[0][0][1] = r.tables[0][0][1].replace('\xa0','')
    return json.dumps(r.tables)

def main():
    import sys
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("roll_number",help="download this roll_number's result")
    parser.add_argument("--html",action="store_true",help="Generates html output of the result")
    parser.add_argument("--url",help="specify url for the result")
    args = parser.parse_args()
    try:
        result = get_result(args.roll_number,args.url)
        result = json.loads(result)
        if args.html:
            table_number = 0
            name_table = result[0]
            for table in result:
                print('<table>')
                if table_number % 3 == 1:
                    print('<tr><td>Semester</td>')
                    print(f'<td>{table[0]}</td><tr>')
                else:
                    for row in table:
                        print('<tr>')
                        for cell in row:
                            print(f'<td>{cell}</td>')
                        print('</tr>')
                print('</table>')
                table_number += 1
        else:
            print(result)
    except Exception as e:
        print('--->',e)
        # sys.exit(0)

if __name__ == '__main__':
    main()
