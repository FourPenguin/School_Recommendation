
import csv
import xlrd
from mongoengine import connect,StringField,Document, EmbeddedDocument,ListField, EmbeddedDocumentField,IntField,FloatField
# read the data of high school scores
score_file = csv.reader(open("2015-2018-selective-high-schools-minimum-entry-scores.csv", 'r'))

# record the each high school name and score from 2015 - 2018
school_name_score = dict()

# statistic the data from the file
for i in score_file:
    if i[0] != 'selective_high_school ':
        school_name_score[i[0].lower()] = [i[j] for j in range(1,5)]

# read the data of high school information
school_detail = csv.reader(open("masterdatasetnightlybatchcollections.csv", 'r'))

# record the school details
school_info = dict()

# statistic school details
for i in school_detail:
    if i[14] != "Not Selective" and i[2] != "School_name":
        kk = i[2].lower()
        school_info[kk] = dict()
        school_info[kk]['fax'] = i[8]
        school_info[kk]['phone'] = i[6]
        school_info[kk]['postcode'] = i[5]
        school_info[kk]['surb'] = i[4].rstrip().lower()
        school_info[kk]['longitude'] = i[35]
        school_info[kk]['latitude'] = i[34]
        school_info[kk]['school-email'] = i[7]
        school_info[kk]['LGA'] = i[25].lower()

# read data from offences table
crime_book = xlrd.open_workbook('LgaRankings_2013-2017_27_Offences.xlsx', "r")

# get first table
content = crime_book.sheet_by_index(0)

# year information
start_year = int(content.row_values(0)[0].split(" ")[-3])
end_year = int(content.row_values(0)[0].split(" ")[-1])

# record the crime rate in NSW from 2013 - 2017
crime_rate = dict()

# statistic data from the crime table
for i in range(7, 136):
    row = content.row_values(i)
    kkk = row[0].lower()
    crime_rate[kkk] = dict()
    index = 1
    for j in range(start_year, end_year + 1):
        crime_rate[kkk][j] = dict()
        crime_rate[kkk][j]['total'] = row[index]
        crime_rate[kkk][j]['rate'] = row[index + 1]
        crime_rate[kkk][j]['rank'] = row[index + 2]
        index += 3

# read the data from population density file
density_book = xlrd.open_workbook('australia_density.xls', "r")

# get second table
content2 = density_book.sheet_by_index(1)

# record the population density
population_density = dict()

# statistic data from the density table
for i in range(13, 951):
    if content2.row_values(i)[4] != '' and content2.row_values(i)[4].startswith("Total"):
        key = content2.row_values(i)[4].replace("Total", '').lstrip()
        population_density[key.lower()] = content2.row_values(i)[-1]
    if content2.row_values(i)[5] != '':
        population_density[content2.row_values(i)[5].lower().replace(" ", '')] = content2.row_values(i)[-1]

# gather all the information in the school info
for i in school_info:
    if school_info[i]['surb'] in population_density:
        school_info[i]['popu-density'] = population_density[school_info[i]['surb']]
    if school_info[i]['surb'] in crime_rate:
        school_info[i]['crime-rate'] = crime_rate[school_info[i]['surb']]
    if school_info[i]['LGA'] in crime_rate:
        school_info[i]['crime-rate'] = crime_rate[school_info[i]['LGA']]
    if i in school_name_score:
        school_info[i]['score'] = school_name_score[i]

# final recommendation school list


def get_recom_list():
    recommendation = dict()
    for i in school_info:
        if 'score' in school_info[i]:
            school_info[i]['surb'] = school_info[i]['surb'].replace(" ", '_')
            recommendation[i.replace(' ', '_')] = school_info[i]
    return recommendation

# recommendation = json.dumps(recommendation, indent = 4)


class Crime_info(EmbeddedDocument):
    year = IntField()
    total = StringField()
    rate = StringField()
    rank = StringField()
    score = IntField()

    def __init__(self,year = None, total = None,rate = None, rank = None, score = None , *args, **values):
        super().__init__(*args, **values)
        self.year = year
        self.total = total
        self.rate = rate
        self.rank = rank
        self.score = score


class Details(EmbeddedDocument):
    fax = StringField()
    phone = StringField()
    postcode = StringField()
    surb_name = StringField()
    longitude = StringField()
    latitude = StringField()
    email = StringField()
    LGA = StringField()
    popu_density = StringField()
    score = ListField()
    average_score = StringField()
    average_crime = StringField()
    crime_info = ListField(EmbeddedDocumentField(Crime_info))

    def __init__(self,fax = None,phone = None, postcode = None, surb_name = None, longitude = None,
                 average_score = None, latitude = None, email = None, LGA = None, popu_density = None,
                 average_crime = None, crime_info = None,*args, **values):
        super().__init__(*args, **values)
        self.fax = fax
        self.phone = phone
        self.postcode = postcode
        self.surb_name = surb_name
        self.longitude = longitude
        self.latitude = latitude
        self.email = email
        self.LGA = LGA
        self.popu_density = popu_density
        self.crime_info = crime_info
        self.average_score = average_score
        self.average_crime = average_crime


class Selective(Document):
    school_name = StringField()
    school_info = ListField(EmbeddedDocumentField(Details))

    def __init__(self, school_type = None, school_info = None, *args, **values):
        super().__init__(*args, **values)
        self.school_type = school_type
        self.school_info = school_info

connect(host='mongodb://Nina_z:z931022@ds241039.mlab.com:41039/school_recommendation')


def upload_to_db(recommendation):
    for i in recommendation:
        statistic = 0
        count = 0
        total = 0
        res = Selective()
        res.school_name = i
        temp_school = Details()
        temp_school.latitude = recommendation[i]['latitude']
        temp_school.postcode = recommendation[i]['postcode']
        temp_school.phone = recommendation[i]['phone']
        temp_school.fax = recommendation[i]['fax']
        temp_school.surb_name = recommendation[i]['surb']
        temp_school.longitude = recommendation[i]['longitude']
        temp_school.LGA = recommendation[i]['LGA']
        temp_school.email = recommendation[i]['school-email']
        if 'popu_density' in recommendation[i]:
            temp_school.popu_density = recommendation[i]['popu_density']
        for z in recommendation[i]['score']:
            total += int(z)
            count += 1
            temp_school.score.append(z)
        temp_school.average_score = str(round(total / count, 3))
        Crime = Crime_info()
        cc = []
        for j in recommendation[i]['crime-rate']:
            Crime = Crime_info()
            Crime.rank = str(recommendation[i]['crime-rate'][j]['rank'])
            Crime.total = str(recommendation[i]['crime-rate'][j]['total'])
            Crime.rate = str(recommendation[i]['crime-rate'][j]['rate'])
            Crime.year = j
            cc.append(Crime)
            if isinstance(recommendation[i]['crime-rate'][j]['rate'], float):
                statistic += recommendation[i]['crime-rate'][j]['rate']
        if isinstance(statistic, float):
            temp_school.average_crime = str(statistic / 5)
        else:
            temp_school.average_crime = 'None'
        temp_school.crime_info = cc
        res.school_info = [temp_school]
        res.save()