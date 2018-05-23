import csv
import xlrd
import json

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

# year
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
recommendation = dict()
for i in school_info:
    if 'score' in school_info[i]:
        school_info[i]['surb'] = school_info[i]['surb'].replace(" ", '_')
        recommendation[i.replace(' ', '_')] = school_info[i]

recommendation = json.dumps(recommendation, indent = 4)
print(recommendation)