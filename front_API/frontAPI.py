from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map, icons
from flask_googlemaps import GoogleMaps
from flask import Flask,render_template,abort

class school:
    def __init__(self,name,long,lan):
        self.name = name
        self.long = long
        self.lan = lan

data = [{"name":"Alexandria_Park_Community_School",
         "long":"-33.900941",
         "lan": "151.195844",
         },
        {"name":"Armidale_High_School",
         "long": "-32.166098",
         "lan": "150.888095",}]

schools = [school(item["name"],item["long"],item["lan"]) for item in data]
api_key = "AIzaSyDXTdv6iq0Vd7NntXWnTf1nTIZoGBMjNOY"
app = Flask(__name__)
app.config["GOOGLEMAPS_KEY"] = "AIzaSyDXTdv6iq0Vd7NntXWnTf1nTIZoGBMjNOY"
GoogleMaps(app,key = api_key)

@app.route("/", methods= ['GET'])
def index():
    item_location = [(item.long,item.lan) for item in schools]

    return render_template("index.html", schools = schools)

if __name__ == "__main__":
    app.run()