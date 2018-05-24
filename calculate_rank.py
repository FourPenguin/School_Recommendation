from math import radians, cos, sin, asin, sqrt

from mongoengine import connect,StringField,Document, EmbeddedDocument,ListField, EmbeddedDocumentField,IntField

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

    def __init__(self,fax = None,phone = None, average_crime = None,average_score = None, postcode = None, surb_name = None, longitude = None, latitude = None, email = None, LGA = None, popu_density = None, crime_info = None,*args, **values):
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

def geodistance(lng1,lat1,lng2,lat2):
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
    dlon=lng2-lng1
    dlat=lat2-lat1
    a=sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    dis=2*asin(sqrt(a))*6371*1000
    return dis

a = [151.236751,-33.917952]

def get_info(location):
    all_distance = []
    all_score = []
    all_crime = []
    for i in Selective.objects:
        for j in i.school_info:
            distance = geodistance(location[0], location[1], float(j.longitude), float(j.latitude))
            all_distance.append(distance)
            all_score.append(float(j.average_score))
            all_crime.append(float(j.average_crime))
    return all_distance,all_crime,all_score

def get_rank(location):
    need = get_info(location)
    all_distance = need[0]
    all_crime = need[1]
    all_score = need[2]
    rank_school = dict()
    for i in Selective.objects:
        for j in i.school_info:
            distance = geodistance(a[0], a[1], float(j.longitude), float(j.latitude))
            distance_weight = (max(all_distance) - distance) / max(all_distance) * 4
            crime_weight = (max(all_crime) - float(j.average_crime)) / max(all_crime) * 3
            score_weight = float(j.average_score) / max(all_score) * 3
            value = []
            value.append(distance_weight + crime_weight + score_weight)
            value.append(j.longitude)
            value.append(j.latitude)
            rank_school[i.school_name] = value
    return rank_school

c = get_rank(a)
c = sorted(c.items(), key = lambda x : x[1], reverse = True)
print(c)