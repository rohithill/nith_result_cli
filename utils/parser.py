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
