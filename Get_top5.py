from math import radians, cos, sin, asin, sqrt
import json
from mongoengine import connect,StringField,Document, EmbeddedDocument,ListField, EmbeddedDocumentField,IntField

class Crime_info(EmbeddedDocument):
    year = IntField()
    total = StringField()
    rate = StringField()
    rank = StringField()

    def __init__(self,year = None, total = None,rate = None, rank = None,  *args, **values):
        super().__init__(*args, **values)
        self.year = year
        self.total = total
        self.rate = rate
        self.rank = rank

class Details(EmbeddedDocument):
    average_score = StringField()
    average_crime = StringField()
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
    crime_info = ListField(EmbeddedDocumentField(Crime_info))

    def __init__(self,fax = None,phone = None, average_crime = None,average_score = None, postcode = None, surb_name = None, longitude = None, latitude = None, email = None, LGA = None, popu_density = None, score = [], crime_info = None,*args, **values):
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
        self.score = score
        self.average_crime = average_crime
        self.average_score = average_score


class Selective(Document):
    school_name = StringField()
    school_info = ListField(EmbeddedDocumentField(Details))

    def __init__(self, school_type = None, school_info = None, *args, **values):
        super().__init__(*args, **values)
        self.school_type = school_type
        self.school_info = school_info

connect(host='mongodb://Nina_z:z931022@ds241039.mlab.com:41039/school_recommendation')

def geodistance(lat1,lng1,lat2,lng2):
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
    dlon=lng2-lng1
    dlat=lat2-lat1
    a=sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    dis=2*asin(sqrt(a))*6371*1000
    return dis



def get_info(location):
    all_distance = []
    all_score = []
    all_crime = []
    for i in Selective.objects:
        for j in i.school_info:
            distance = geodistance(location[0], location[1], float(j.latitude), float(j.longitude))
            all_distance.append(distance)
            all_score.append(float(j.average_score))
            all_crime.append(float(j.average_crime))
    return all_distance,all_crime,all_score

def change_rate(a,b,c):
    total = a + b + c
    a = a / total * 10
    b = b / total * 10
    c = c / total * 10
    return [a, b, c]

#p1 is for distance_weight, p2 is for crime_weight, p3 is for score_weight.
def get_rank(location,p1,p2,p3):
    changed = change_rate(p1,p2,p3)
    p1 = changed[0]
    p2 = changed[1]
    p3 = changed[2]
    need = get_info(location)
    all_distance = need[0]
    all_crime = need[1]
    all_score = need[2]
    res = []
    second = []
    average = dict()
    distance_avg = 0
    score_avg = 0
    crime_avg = 0
    for i in Selective.objects:
        school_info = dict()
        school_info['school_name'] = i.school_name
        for j in i.school_info:
            distance = geodistance(location[0], location[1], float(j.latitude), float(j.longitude))
            distance_weight = (max(all_distance) - distance) / max(all_distance) * p1
            crime_weight = (max(all_crime) - float(j.average_crime)) / max(all_crime) * p2
            score_weight = float(j.average_score) / max(all_score) * p3
            school_info['longitude'] = j.longitude
            school_info['latitude'] = j.latitude
            school_info['distance_rate'] = (max(all_distance) - distance) / max(all_distance) * 10
            distance_avg += school_info['distance_rate']
            school_info['score_rate'] = float(j.average_score) / max(all_score) * 10
            score_avg += school_info['score_rate']
            school_info['crime_rate'] = (max(all_crime) - float(j.average_crime)) / max(all_crime) * 10
            crime_avg += school_info['crime_rate']
            school_info['total_rate'] = distance_weight + crime_weight + score_weight
        res.append(school_info)
    distance_avg = distance_avg / 40
    score_avg = score_avg / 40
    crime_avg = crime_avg / 40
    average['distance_average'] = distance_avg
    average['score_average'] = score_avg
    average['crime_average'] = crime_avg
    second.append(average)
    return [res, second]


def get_top5(location,p1,p2,p3):
    result = get_rank(location,p1,p2,p3)
    sort_all = sorted(result[0], key = lambda x : x['total_rate'], reverse = True)
    sort_all = sort_all[:5]
    sort_all = json.dumps(sort_all, indent=4)
    return [sort_all, result[1]]


def get_school_dict(name):
    need = dict()
    for i in Selective.objects:
        if i.school_name == name:
            for j in i.school_info:
                need['fax'] = j.fax
                need['phone'] = j.phone
                need['email'] = j.email
                need['LGA'] = j.LGA
                need['suburb_name'] = j.surb_name
                need['postcode'] = j.postcode
                need['longitude'] = j.longitude
                need['latitude'] = j.latitude
                need['population_density'] = j.popu_density
                need['average_score'] = j.average_score
                need['average_crime'] = j.average_crime
                need['score'] = j.score
                for k in j.crime_info:
                    need['crime_information'] = dict()
                    need['crime_information']['year'] = k.year
                    need['crime_information']['total'] = k.total
                    need['crime_information']['rate'] = k.rate
                    need['crime_information']['rank'] = k.rank
    return need

