# Import the dependencies.
from xml.dom.pulldom import START_ELEMENT
from flask import Flask, jsonify, render_template
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import datetime as dt
import os
import numpy as np


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

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
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        f"<p>'start' and 'end' date should be in the format MMDDYYYY.</p>"
    )
    

#define a route to retrieve and return precipitation data for the last year
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    #calculate the date one year ago from the most recent date in the dataset
    recent_date = session.query(func.max(Measurement.date)).scalar()
    year_ago = dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    #query precipitation data for the last year
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >=year_ago).all()

    #create a dictionary with date as the key and precipitation as the value
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

#define a rout to retrieve and return station data
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    #query all stations in the database
    results = session.query(Station.station).all()
    
    stations = list(np.ravel(results))

    #create a list of dictionaries with station information
    
    
    return jsonify(stations = stations)

#Define a route to retrieve and retun temperature data for the most active station for the last year
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
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
    session = Session(engine)
    
    
    start_date = dt.datetime.strptime(start,'%m-%d-%Y')
    
    temp_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start_date).all()

    if temp_stats[0][0] is not None:    
    #create a dictionary with temperature summary data
        temperature_summary = {
            "start_date": start_date.strftime('%m-%d-%Y'),
             "min_temperature": temp_stats[0][0],
             "max_temperature": temp_stats[0][1],
             "avg_temperature": temp_stats[0][2],
        }

        return jsonify(temperature_summary)

    else:

        return jsonify({"error": "No teperature data found for the provided start date."}), 404

#define a route to calculate min, max, and average temperatures from a start date to an edn date
@app.route("/api/v1.0/<start>/<end>")
def start_end_summary(start, end):

    session = Session(engine)
    
    start_date = dt.datetime.strptime(start,'%m-%d-%Y')
    end_date = dt.datetime.strptime(end, '%m-%d-%Y')

# #     #query and calculate min, max, and average temperatures froms tart date to end date
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date > start_date).\
        filter(Measurement.date < end_date).all()
    
#     #create a dictionary with temperature summary data
    temperature_summary = {
            "start_date": start_date.strftime('%m-%d-%Y'),
            "end_date": end_date.strftime('%m-%d-%Y'),
            "min_temperature": results[0][0],
            "max_temperature": results[0][1],
            "avg_temperature": results[0][2],
        }

    return jsonify(temperature_summary)
session.close()
if __name__=="__main__":
    app.run(debug=True)

