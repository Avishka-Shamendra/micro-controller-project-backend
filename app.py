from flask import Flask, request, render_template
from xml.etree import ElementTree
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from capparselib.parsers import CAPParser
from flask_migrate import Migrate

app = Flask(__name__)

DEBUG = True
DB_URL = 'postgresql://postgres:postgreslaa@localhost:5432/micro-project'
sqlAlchemyconfigure = 'SQLALCHEMY_TRACK_MODIFICATIONS'

PARAM_TEMP_MEAN_NAME="TEMP_MEAN"
PARAM_TEMP_STD_DEV_NAME="TEMP_STD"
PARAM_HUMIDITY_MEAN_NAME="HUMIDITY_MEAN"
PARAM_HUMIDITY_STD_DEV_NAME="HUMIDITY_STD"
PARAM_PRESSURE_MEAN_NAME="PRESSURE_MEAN"
PARAM_PRESSURE_STD_DEV_NAME="PRESSURE_STD"
PARAM_LIGHT_MEAN_NAME="LIGHT_MEAN"
PARAM_LIGHT_STD_DEV_NAME="LIGHTSTD"

app.debug = DEBUG
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config[sqlAlchemyconfigure] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class SensorData(db.Model):
    __tablename__ = 'sensor_data'

    id = db.Column(db.Integer, primary_key=True)
    temperature_mean = db.Column(db.Float)
    temperature_std_dev = db.Column(db.Float)
    humidity_mean = db.Column(db.Float)
    humidity_std_dev = db.Column(db.Float)
    pressure_mean = db.Column(db.Float)
    pressure_std_dev = db.Column(db.Float)
    light_mean = db.Column(db.Float)
    light_std_dev = db.Column(db.Float)
    timestamp = db.Column(db.String(255))


    def __init__(self, timestamp,
     temperature_mean,temperature_std_dev, 
     humidity_mean,humidity_std_dev,
     pressure_mean,  pressure_std_dev, 
     light_mean,  light_std_dev):

        self.temperature_mean  = temperature_mean 
        self.temperature_std_dev = temperature_std_dev

        self.humidity_mean = humidity_mean
        self.humidity_std_dev = humidity_std_dev

        self.pressure_mean = pressure_mean
        self.pressure_std_dev = pressure_std_dev

        self.light_mean = light_mean
        self.light_std_dev = light_std_dev

        self.timestamp = timestamp

    @staticmethod
    def addNewRow(timestamp,params):
        
        timestamp = timestamp

        temperature_mean = float(params[PARAM_TEMP_MEAN_NAME])
        temperature_std_dev = float(params[PARAM_TEMP_STD_DEV_NAME])
        humidity_mean = float(params[PARAM_HUMIDITY_MEAN_NAME])
        humidity_std_dev = float(params[PARAM_HUMIDITY_STD_DEV_NAME])
        pressure_mean = float(params[PARAM_PRESSURE_MEAN_NAME])
        pressure_std_dev = float(params[PARAM_PRESSURE_STD_DEV_NAME])
        light_mean = float(params[PARAM_LIGHT_MEAN_NAME])
        light_std_dev = float(params[PARAM_LIGHT_STD_DEV_NAME])

        try:
            obj = SensorData(timestamp, 
            temperature_mean, temperature_std_dev, 
            humidity_mean, humidity_std_dev, 
            pressure_mean,pressure_std_dev,
            light_mean, light_std_dev)
            db.session.add(obj)
            db.session.commit()
            return True
        except:
            return False

@app.route('/')
def index():
    records = SensorData.query.order_by(desc(SensorData.timestamp)).limit(5).all()
    return render_template("home.html", records=records)

@app.route('/upload', methods=['POST'])
def post():
    alert_list = CAPParser(request.data.decode('utf-8')).as_dict()
    alert = alert_list[0]
    timestamp = alert['cap_sent']
    params = {}
    for param in alert['cap_info'][0]['cap_parameter']:
        params[param['valueName']] = param['value']
    SensorData.addNewRow(timestamp, params)
    return "200 OK"

if __name__ == '__main__':
    app.run()