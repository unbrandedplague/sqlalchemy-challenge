# Import the dependencies.
from xml.dom.pulldom import START_ELEMENT
from flask import Flask, jsonify, render_template
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt
import os


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources\hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
#define a route for the root URL ("/") and return simple message
@app.route("/")
def landing_page():
    #provide information about routes
    routes = {
        "routes":[
            "/api/v1.0/precipitation",
            "/api/v1.0/stations",
            "/api/v1.0/tobs",
            "/api/v1.0/<start>",
            "/api/v1.0/<start>/<end>",
        ]
    }
    return jsonify(routes)

#define a route to retrieve and return precipitation data for the last year
@app.route("/api/v1.0/precipitation")
def precipitation():
    #calculate the date one year ago from the most recent date in the dataset
    recent_date = session.query(func.max(Measurement.date)).scalar()
    year_ago = dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    #query precipitation data for the last year
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >=year_ago).all()

    #create a dictionary with date as the key and precipitation as the balue
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

#define a rout to retrieve and return station data
@app.route("/api/v1.0/stations")
def stations():
    #query all stations in the database
    results = session.query(Station.station, Station.name).all()

    #create a list of dictionaries with station information
    station_data = [{"stations": stations, "name": name} for stations, name in results]

    return jsonify(station_data)

#Define a route to retrieve and retun temperature data for the most active station for the last year
@app.route("/api/v1.0/tobs")
def tobs():
    #calculate the date one year ago from the most recent date in dataset
    recent_date = session.query(func.max(Measurement.date)).scalar()
    year_ago = dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    #query temperature data (tobs) for the most active station for the last year
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= year_ago).all()
    
    # create a list of dictionaries with data and teperature data
    tobs_data = [{"date": date, "temperature": tobs} for date, tobs in results]

    return jsonify(tobs_data)

# define a rout to calculate min, max, and average temp from a start date to the end of dataset
@app.route("/api/v1.0/<start>")
def start(start):
    
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    start_date = dt.datetime.strptime(start,'%Y-%m-%d')
    

    temp_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start_date).all()
    
    #create a dictionary with temperature summary data
    temperature_summary = {
        "start_date": start_date.strftime('%Y-%m-%d'),
        "min_temperature": temp_stats[0][0],
        "max_temperature": temp_stats[0][1],
        "avg_temperature": temp_stats[0][2],
    }

    return jsonify(temperature_summary)
    

#define a route to calculate min, max, and average temperatures from a start date to an edn date
# @app.route("/api/v1.0/<start>/<end>")
# def start_end_summary(start_date, end_date):
    
    # most_recent_date = session.query(func.max(Measurement.date)).scalar()
    #end_date = dt.datetime.strptime(most_recent_Date, '%Y-%m-%d')

#     #query and calculate min, max, and average temperatures froms tart date to end date
#     results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
#         filter(Measurement.date > start_date).\
#         filter(Measurement.date < end_date).all()
    
#     #create a dictionary with temperature summary data
#     temperature_summary = {
#         "start_date": start_date,
#         "end_date": most_recent_date,
#         "min_temperature": results[0][0],
#         "max_temperature": results[0][1],
#         "avg_temperature": results[0][2],
#     }

#     return jsonify(temperature_summary)

if __name__=="__main__":
    app.run(debug=True)

#
