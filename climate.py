# import modules
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# start Flask
app = Flask(__name__)

# define routes
# /
    # List all available api routes.

@app.route("/")
def welcome():
    return (f'''
        Available Routes:<br/>
        <a href="/api/v1.0/precipitation">Precipitation</a><br/>
        <a href="/api/v1.0/stations">Stations</a><br/>
        <a href="/api/v1.0/tobs">TOBS</a><br/>
        <a href="/api/v1.0/start">Select a start date</a><br/>
        <a href="/api/v1.0/start/end">Select a start and end date</a><br/>
        ''')

# /api/v1.0/precipitation
    # Convert the query results to a Dictionary using date as the key and prcp as the value.
    # Return the JSON representation of your dictionary.
    # Perform a query to retrieve the data and precipitation scores

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    date_range = session.query(Measurement.date, func.sum(Measurement.prcp)).\
        group_by(Measurement.date).\
        order_by(Measurement.date.desc())
    date = []
    rain = []
    for row in date_range:        
        date.append(row[0])
        rain.append(row[1])
    prcp_dict = dict(zip(date, rain))
    
    return jsonify(prcp_dict)

# /api/v1.0/stations
    # Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_list = session.query(Station.station, Station.name)
    station = []
    name = []
    for row in station_list:        
        station.append(row[0])
        name.append(row[1])
    station_dict = dict(zip(station, name))
    
    return jsonify(station_dict)

# /api/v1.0/tobs
    # query for the dates and temperature observations from a year from the last data point.
    # Return a JSON list of Temperature Observations (tobs) for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date
    date_range = session.query(Measurement.date, func.sum(Measurement.prcp)).\
        group_by(Measurement.date).\
        order_by(Measurement.date.desc()).\
        filter(Measurement.date >= '2016-08-23')
    date = []
    rain = []
    for row in date_range:
        date.append(row[0])
        rain.append(row[1])
    rain_dict = dict(zip(date, rain))

    return jsonify(rain_dict)

# /api/v1.0/<start>
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date.
    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

@app.route("/api/v1.0/start")
def start():
    # date = input("Please enter a date in YYYY-mm-dd format.")
    session = Session(engine)
    date_query = session.query(
        func.min(Measurement.tobs), 
        func.avg(Measurement.tobs), 
        func.max(Measurement.tobs)).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= '2010-01-01').all()
    
    # Load the previous query results into a Pandas DataFrame and add the `trip_dates` range as the `date` index
    date_list = []
    for date in date_query:
        date_list.append(date)
    results_df = pd.DataFrame(date_list, columns=['min', 'avg', 'max'])
    start_dict = pd.DataFrame.to_dict(results_df, orient='index')

    return jsonify(start_dict)

# /api/v1.0/<start>/<end>
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range.
    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

@app.route("/api/v1.0/start/end")
def startend():
    # start_date = input("Please enter a start date in YYYY-mm-dd format.") 
    # end_date = input("Please enter an end date in YYYY-mm-dd format.") 
    session = Session(engine)
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    date_query = session.query(*sel).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= '2010-01-01').\
        filter(func.strftime("%Y-%m-%d", Measurement.date) <= '2017-08-23').all()

    # Load the previous query results into a Pandas DataFrame and add the `trip_dates` range as the `date` index
    date_list = []
    for date in date_query:
        date_list.append(date)
    results_df = pd.DataFrame(date_list, columns=['min', 'avg', 'max'])
    startend_dict = pd.DataFrame.to_dict(results_df, orient='index')

    return jsonify(startend_dict)

if __name__ == '__main__':
    app.run(debug=True)