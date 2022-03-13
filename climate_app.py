import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)
measurement = Base.classes.measurement
station = Base.classes.station

session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
last_twelve_months = '2016-08-23'
first_date = session.query(measurement.date).order_by(measurement.date).first()
recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
session.close()

@app.route("/")
def welcome():
    return (
        f"<p>Welcome to the Hawaii's Weather API!</p>"
        f"<p>Available Routes:</p>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/station<br/>"
        f"/api/v1.0/start_date/<start_date><br/>"       
        f"/api/v1.0/start_end_date/<start>/<end><br/>"
    )

# Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def Precipitation():
    prcp_results = session.query(measurement.date, func.avg(measurement.prcp)).\
        filter(measurement.date >= last_twelve_months).\
            group_by(measurement.date).all()
    session.close()
    return jsonify(predictions=list(np.ravel(prcp_results)))

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/station")
def Stations():
    station_list = session.query(station.station, station.name).all()
    session.close()
    return jsonify(predictions=list(np.ravel(station_list)))

# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def Temperature():
    tobs_prev_year = session.query(measurement.date, measurement.station, measurement.tobs).\
        filter(measurement.date >= last_twelve_months).all()
    session.close()
    return jsonify(predictions=list(np.ravel(tobs_prev_year)))

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date.
# When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
@app.route("/api/v1.0/start_date/<start_date>")
def StartDate(start_date):
    start_date_only = session.query(measurement.date, func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
        filter(measurement.date == start_date).all()
    session.close()
    return jsonify(predictions=list(np.ravel(start_date_only)))


# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range.
# When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
@app.route("/api/v1.0/start_end_date/<start>/<end>")
def StartEnd(start,end):
    start_end_date = session.query(measurement.date, func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= end).all()
    session.close()
    return jsonify(predictions=list(np.ravel(start_end_date)))

if __name__ == '__main__':
    app.run(debug=True)


