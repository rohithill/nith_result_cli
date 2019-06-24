import json
from urllib import parse, request
import argparse
import hashlib
from html.parser import HTMLParser

class ResultParser(HTMLParser):
    # def __init__(self, strict, convert_charrefs):
    #     self.inside = False
    #     return super().__init__(strict, convert_charrefs)
    def custom(self):
        self.inside = False
        self.state = 0
        self.final = []
        self.tr = False
        self.td = False

    def handle_starttag(self, tag, attrs):
        if tag == 'table' and not self.inside:
            # print('start tag',tag,attrs)
            self.final.append([])
            self.inside = True
        if self.inside and tag=='tr':
            self.tr = True
            self.final[-1].append([])
        if self.tr and tag=='td':
            self.td = True


    def handle_data(self,data):
        # if self.inside and self.tr:
        #     data = data.strip()
        #     if data:
        #         print('handle_data: ',repr(data))
        #         return data
        if self.td:
            data = data.strip()
            if data:
                self.final[-1][-1].append(data)
            # print(data)
            # print(self.final)
        # elif self.tr:
        #     self.final.append([])
        
    def handle_endtag(self, tag):
        # if tag == 'table':
        #     print('handle end tag: ',tag)
        #     self.inside = False
        #     self.state = 1 + (self.state)%2
        if self.inside:
            # print('handle end tag: ',tag)
            pass
        if self.td and tag=='td':
            self.td = False
        elif self.tr and tag=='tr':
            self.tr = False
        elif self.inside and tag == 'table':
            self.inside = False

class Student:
    def __init__(self, roll_number):
        self.roll_number = roll_number
        self.name = None

    def get_result(self):
        url = self.get_result_url()
        data = parse.urlencode({'RollNumber':self.roll_number}).encode()
        req = request.Request(url,data)
        with request.urlopen(req) as response:
            the_page = response.read()
        # return page content with error (which is roll no. not found). Magic number is hash of error page
        return the_page.decode(), hashlib.md5(the_page).hexdigest() == '2d1aad8069f3b88c1150dcd92a3cb9de'

    def get_result_url(self):
        year = self.roll_number[:2]
        return f'http://59.144.74.15/scheme{year}/studentResult/details.asp'
    
    def __str__(self):
        return f"Name: {self.name}, Roll_number: {self.roll_number}"

def process(roll_number):
    stud = Student(roll_number)
    result, error = stud.get_result()
    if error:
        print("roll no not found")
    else:
        # print(result)
        r = ResultParser()
        r.custom()
        r.feed(result)
        # jathura.append(r.final)
        import pprint
        print(json.dumps(r.final))
        # print(json.dumps(r.final))

    # if args.o:
    #     with open(args.o,'w') as f:
    #         json.dump(args.roll_number,f)
    # print(args.o)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("roll_number",help="download this roll_number's result")
    parser.add_argument("-o",metavar='<file>',help="Places the output into <file>")
    args = parser.parse_args()
    process(args.roll_number)
    # print(args.roll_number)

if __name__ == '__main__':
    # jathura = {}
    main()
    # print(jathura)
