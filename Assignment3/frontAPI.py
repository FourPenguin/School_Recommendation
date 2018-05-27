from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map, icons
from flask_googlemaps import GoogleMaps
from flask import Flask,render_template,abort,request,url_for,json
import calculate_rank
from mongoengine import connect,StringField,Document, EmbeddedDocument,ListField, EmbeddedDocumentField,IntField
api_key = "AIzaSyDXTdv6iq0Vd7NntXWnTf1nTIZoGBMjNOY"
app = Flask(__name__)
app.config["GOOGLEMAPS_KEY"] = "AIzaSyDXTdv6iq0Vd7NntXWnTf1nTIZoGBMjNOY"
GoogleMaps(app,key = api_key)

@app.route("/", methods= ['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template("index.html")
    else:
        return url_for("recommendation")

@app.route("/recommendation",methods = ['GET', 'POST'])
def recom():
    if request.method == "GET":
        return render_template("index.html")
    else:
        input_lantitude = request.values.get("Latitude")
        input_longtitude = request.values.get("Longitude")

        input_location = request.values.get("Location")
        a = float(request.values.get("Distance"))
        b = float(request.values.get("Crime"))
        c = float(request.values.get("Score"))
    # print(a,b,c)
        if input_lantitude == '' or input_longtitude == '':
            return render_template("index.html")
        else:
            af = [float(input_lantitude),float(input_longtitude)]
            result = calculate_rank.get_top5(af,a,b,c)
            print(af,result[0],result[1])
            return render_template("recom.html", schools=json.dumps(result[0]), avr_rate =json.dumps(result[1])
                                   ,result = result[0])

@app.route("/<schoolname>",methods = ['GET'])
def details(schoolname):
    details_info= calculate_rank.get_school_dict(schoolname)
    #print(details_info)
    return render_template("details.html", detail_school=details_info, detail_school_name = schoolname, json_school = json.dumps(details_info))
if __name__ == "__main__":
    app.run()