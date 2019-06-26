import json
import hashlib
import urllib.error
from urllib import parse, request
from html.parser import HTMLParser

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
        self.url = url

    def get_result(self):
        url = self.url or self.get_result_url()
        data = parse.urlencode({'RollNumber':self.roll_number}).encode()
        req = request.Request(url,data)
        the_page = b''
        error = False
        try:
            with request.urlopen(req) as response:
                the_page = response.read()
        except urllib.error.HTTPError as e:
            error = 404
        # return page content with error (which is roll no. not found). Magic number is hash of error page
        return the_page, hashlib.md5(the_page).hexdigest() == '2d1aad8069f3b88c1150dcd92a3cb9de' or error

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
        return f"Name: {self.name}, Roll_number: {self.roll_number}"

def process(roll_number,url=None):
    stud = Student(roll_number,url)
    result, error = stud.get_result()
    if error:
        return result,error
    else:
        result = result.decode()
        r = ResultParser()
        r.custom_init()
        r.feed(result)
        r.tables[0][0][1] = r.tables[0][0][1].replace('\xa0','')
        return r.tables, None

def main():
    import sys
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("roll_number",help="download this roll_number's result")
    parser.add_argument("--html",action="store_true",help="Generates html output of the result")
    parser.add_argument("--url",help="specify url for the result")
    args = parser.parse_args()
    result,error = process(args.roll_number,args.url)
    if error:
        print("Error: Roll number not found",file=sys.stderr)
    else:
        if args.html:
            table_number = 0
            name_table = result[0]
            for table in result:
                print('<table>')
                if table_number %3 == 1:
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

if __name__ == '__main__':
    main()
