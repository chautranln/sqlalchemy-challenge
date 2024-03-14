# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
measurement = Base.classes.measurement
station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
# List all the available routes on homepage.
@app.route("/")
def home():
    return  (
        f"Available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (Input start date) <br/>"
        f"/api/v1.0/start/end (Input start and end date)"
    )

#Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.

#Return the JSON representation of your dictionary
@app.route("/api/v1.0/precipitation")
def precipitation():

    substract = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    prev_date = dt.date(substract.year, substract.month, substract.day)
    # Perform a query to retrieve the data and precipitation scores
    data = session.query(measurement.date, measurement.prcp).filter(measurement.date >= prev_date).order_by(measurement.date).all()
    dictionary = dict(data)
    return jsonify(dictionary)

#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations_func():
    columns = [station.station, station.name, station.latitude, station.longitude, station.elevation]
    query = session.query(*columns).all()

    stations=[]
    for id, name, latitude, longitude, elevation in query:
        dictionary={}
        dictionary["Station"] = id
        dictionary["Name"] = name
        dictionary["Latitude"] = latitude
        dictionary["Longitude"] = longitude
        dictionary["Elevation"] = elevation
        stations.append(dictionary)

    return jsonify(stations)

#Query the dates and temperature observations of the most-active station for the previous year of data.
#Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    substract = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    prev_date = dt.date(substract.year, substract.month, substract.day)
    most_active = session.query(measurement.date, measurement.tobs).filter(measurement.station == "USC00519281").filter(measurement.date >= prev_date).all()

    tobs_list=[]
    for date, value in most_active:
        dictionary={}
        dictionary["Date"] = date
        dictionary["Tobs"] = value
        tobs_list.append(dictionary)

    return jsonify(tobs_list)

#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
#For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
#For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route("/api/v1.0/<start>")
def beginning(start):
    query = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= start).all()
 
    start_temps=[]
    for min_temp, max_temp, avg_temp in query:
        dictionary={}
        dictionary["Minimum Temp"] = min_temp
        dictionary["Maximum Temp"] = max_temp
        dictionary["Average Temp"] = avg_temp
        start_temps.append(dictionary)
    print(f"Results: {start_temps}")
    return jsonify(start_temps)
    
@app.route("/api/v1.0/<start>/<end>")
def both(start, end):
    start_end = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
 
    start_end_temps=[]
    for min_temp, max_temp, avg_temp in start_end:
        dictionary={}
        dictionary["Minimum Temp"] = min_temp
        dictionary["Maximum Temp"] = max_temp
        dictionary["Average Temp"] = avg_temp
        start_end_temps.append(dictionary)
    print(f"Results: {start_end_temps}")
    return jsonify(start_end_temps)
    
if __name__ == '__main__':
    app.run(debug=True)