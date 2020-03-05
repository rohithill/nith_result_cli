class ROLL_NUMBER_NOT_FOUND(Exception): 
  
    # Constructor or Initializer 
    def __init__(self,roll_number): 
        self.value = f'Roll No. {roll_number} is invalid.'
  
    # __str__ is to print() the value 
    def __str__(self): 
        return (self.value) 


class Student:
    def __init__(self, roll_number,url=None):
        self.roll_number = roll_number.lower()
        self.url = url or self.get_result_url()
        self.data = {'RollNumber': roll_number}
        
    def get_result_url(self):
        url = "http://14.139.56.15/{}{}/studentResult/details.asp"

        if self.roll_number.startswith('iiitu'):
            year = self.roll_number[5:7]
            college_code = 'IIITUNA'
        else:
            year = self.roll_number[:2]
            college_code = 'scheme'
        return url.format(college_code,year)

    def __str__(self):  
        return f"Roll_number: {self.roll_number}"