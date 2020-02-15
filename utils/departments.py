# Contains department as dictionaries returning generators
departments = {
"CIVIL" : {
    '2015': ('151' + str(x).zfill(2) for x in range(1,100)),
    '2016': ('161' + str(x).zfill(2) for x in range(1,100)),
    '2017': ('171' + str(x).zfill(2) for x in range(1,100)),
    '2018': ('181' + str(x).zfill(3) for x in range(1,150)),
    '2019': ('191' + str(x).zfill(3) for x in range(1,150)),    
},

"ELECTRICAL" : {
    '2015': ('152' + str(x).zfill(2) for x in range(1,100)),
    '2016': ('162' + str(x).zfill(2) for x in range(1,100)),
    '2017': ('172' + str(x).zfill(2) for x in range(1,100)),
    '2018': ('182' + str(x).zfill(3) for x in range(1,150)),
    '2019': ('192' + str(x).zfill(3) for x in range(1,150)),
},

"MECHANICAL" : {
    '2015': ('153' + str(x).zfill(2) for x in range(1,100)),
    '2016': ('163' + str(x).zfill(2) for x in range(1,100)),
    '2017': ('173' + str(x).zfill(2) for x in range(1,100)),
    '2018': ('183' + str(x).zfill(3) for x in range(1,150)),
    '2019': ('193' + str(x).zfill(3) for x in range(1,150)),
},

"ECE" : {
    '2015': ('154' + str(x).zfill(2) for x in range(1,100)),
    '2016': ('164' + str(x).zfill(2) for x in range(1,100)),
    '2017': ('174' + str(x).zfill(2) for x in range(1,100)),
    '2018': ('184' + str(x).zfill(3) for x in range(1,150)),
    '2019': ('194' + str(x).zfill(3) for x in range(1,150)),
},

"ECE_DUAL" : {
    '2015': ('15mi4' + str(x).zfill(2) for x in range(1,100)),
    '2016': ('16mi4' + str(x).zfill(2) for x in range(1,100)),
    '2017': ('17mi4' + str(x).zfill(2) for x in range(1,100)),
    '2018': ('1845' + str(x).zfill(2) for x in range(1,100)),
    '2019': ('1945' + str(x).zfill(2) for x in range(1,100)),
},

"CSE" : {
    '2015': ('155' + str(x).zfill(2) for x in range(1,100)),
    '2016': ('165' + str(x).zfill(2) for x in range(1,100)),
    '2017': ('175' + str(x).zfill(2) for x in range(1,100)),
    '2018': ('185' + str(x).zfill(3) for x in range(1,150)),
    '2019': ('195' + str(x).zfill(3) for x in range(1,150)),
},

"CSE_DUAL" : {
    '2015': ('15mi5' + str(x).zfill(2) for x in range(1,100)),
    '2016': ('16mi5' + str(x).zfill(2) for x in range(1,100)),
    '2017': ('17mi5' + str(x).zfill(2) for x in range(1,100)),
    '2018': ('1855' + str(x).zfill(2) for x in range(1,100)),
    '2019': ('1955' + str(x).zfill(2) for x in range(1,100)),
},

"ARCHITECTURE" : {
    '2015': ('156' + str(x).zfill(2) for x in range(1,100)),
    '2016': ('166' + str(x).zfill(2) for x in range(1,100)),
    '2017': ('176' + str(x).zfill(2) for x in range(1,100)),
    '2018': ('186' + str(x).zfill(3) for x in range(1,150)),
    '2019': ('196' + str(x).zfill(3) for x in range(1,150)),
},

"CHEMICAL" : {
    '2015': ('157' + str(x).zfill(2) for x in range(1,99)),
    '2016': ('167' + str(x).zfill(2) for x in range(1,99)),
    '2017': ('177' + str(x).zfill(2) for x in range(1,99)),
    '2018': ('187' + str(x).zfill(3) for x in range(1,150)),
    '2019': ('197' + str(x).zfill(3) for x in range(1,150)),
},

"MATERIAL" : {
    '2017': ('178' + str(x).zfill(2) for x in range(1,99)),
    '2018': ('188' + str(x).zfill(3) for x in range(1,150)),
    '2019': ('198' + str(x).zfill(3) for x in range(1,150)),
},

"IIITU_CSE" : {
    '2015': ('IIITU151' + str(x).zfill(2) for x in range(1,99)),
    '2016': ('IIITU161' + str(x).zfill(2) for x in range(1,99)),
    '2017': ('IIITU171' + str(x).zfill(2) for x in range(1,99)),
    '2018': ('IIITU181' + str(x).zfill(2) for x in range(1,99)),
},

"IIITU_ECE": {
    '2015': ('IIITU152' + str(x).zfill(2) for x in range(1,99)),
    '2016': ('IIITU162' + str(x).zfill(2) for x in range(1,99)),
    '2017': ('IIITU172' + str(x).zfill(2) for x in range(1,99)),
    '2018': ('IIITU182' + str(x).zfill(2) for x in range(1,99)),
},

"IIITU_IT": {
    '2017': ('IIITU173' + str(x).zfill(2) for x in range(1,99)),
    '2018': ('IIITU183' + str(x).zfill(2) for x in range(1,99)),
}
}