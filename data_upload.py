
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

    def __init__(self,fax = None,phone = None, postcode = None, surb_name = None, longitude = None, latitude = None, email = None, LGA = None, popu_density = None, crime_info = None,*args, **values):
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


class Selective(Document):
    school_name = StringField()
    school_info = ListField(EmbeddedDocumentField(Details))

    def __init__(self, school_type = None, school_info = None, *args, **values):
        super().__init__(*args, **values)
        self.school_type = school_type
        self.school_info = school_info


connect(host='mongodb://Nina_z:z931022@ds241039.mlab.com:41039/school_recommendation')


for i in recommendation:
    res = Selective()
    res.school_name = i
    temp_school = Details()
    temp_school.latitude = recommendation[i]['latitude']
    temp_school.phone = recommendation[i]['phone']
    temp_school.fax = recommendation[i]['fax']
    temp_school.surb_name = recommendation[i]['surb']
    temp_school.longitude = recommendation[i]['longitude']
    temp_school.LGA = recommendation[i]['LGA']
    temp_school.email = recommendation[i]['school-email']
    if 'popu_density' in recommendation[i]:
        temp_school.popu_density = recommendation[i]['popu_density']
    for z in recommendation[i]['score']:
        temp_school.score.append(z)
    Crime = Crime_info()
    cc = []
    for j in recommendation[i]['crime-rate']:
        Crime = Crime_info()
        Crime.rank = str(recommendation[i]['crime-rate'][j]['rank'])
        Crime.total = str(recommendation[i]['crime-rate'][j]['total'])
        Crime.rate = str(recommendation[i]['crime-rate'][j]['rate'])
        Crime.year = j
        cc.append(Crime)
    temp_school.crime_info = cc
    res.school_info = [temp_school]
    res.save()
