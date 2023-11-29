"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""

import os
import flask
from flask import request
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import config

import logging
from pymongo import MongoClient

import requests

API_URL = "http://API:PORT/api/brevets"

###
# Globals
###
app = flask.Flask(__name__)
CONFIG = config.configuration()

# set up mongo client
#client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
# Use database "idk"
#db = client.control_sets
# Using collection "lists" in database
#collection = db.lists
###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('404.html'), 404


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")
    
    km = request.args.get('km', 999, type=float)
    start_time = request.args.get("start_time")
    brevet_dist_km = request.args.get("brevet_dist_km")

    app.logger.debug("request.args: {}".format(request.args))

    open_time = acp_times.open_time(km, brevet_dist_km, arrow.get(start_time, 'YYYY-MM-DDTHH:mm'))
    close_time = acp_times.close_time(km, brevet_dist_km, arrow.get(start_time, 'YYYY-MM-DDTHH:mm'))
   
    open_time_str = open_time.format('YYYY-MM-DDTHH:mm')
    close_time_str = close_time.format('YYYY-MM-DDTHH:mm')
    result = {"open": open_time_str, "close": close_time_str}
    return flask.jsonify(result=result)


def get_rows():
    """ 
    Obtains the newest document in the "lists" (control_sets) collection in database "idk"

    Returns begin_time, brevet_dist, and rows in a tuple
    """
    try:
        response = requests.get(f"{API_URL}/brevets")
        response.raise_for_status()
        data = response.json()
        latest_brevet = data['brevets'][-1] if data['brevets'] else None

        if latest_brevet:
            return latest_brevet['start_time'], latest_brevet['length'], latest_brevet['checkpoints']
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching controls: {e}")
        return None


def insert_rows(begin_time, brevet_dist, rows):
    '''
    inserts a new list of rows into database "control_sets", stores into the collection "lists" (probably going to change this to control_sets)

    Inputs the begin_time (string), brevet_dist (string), rows(list of dictionaries)

    Returns the unique ID assigned to the document by mongo (primary key)
    '''

    try:
        distances = [cp['distance'] for cp in rows]
        locations = [cp['location'] for cp in rows]

        payload = {
            "start_time": begin_time,
            "length": brevet_dist,
            "distances": distances,
            "locations": locations,
        }

        response = requests.post(f"{API_URL}/brevets", json=payload)
        response.raise_for_status()
        data = response.json()
        
        return data.get('brevet_id')
    except requests.exceptions.RequestException as e:
        print(f"Error inserting rows: {e}")
        return None


@app.route("/_submit", methods=["POST"])
def _submit():
    '''
    Will deal with collaboration with MongoDB to store the values from each row 
    on webpage.
    '''
    try: 
        # Read the entire body of request as JSON
        # This will fail if the request body is not a JSON
        input_json = flask.request.json
        # If successful, this is now in dictionary format 
        begin_time = input_json["begin_time"]
        brevet_dist = input_json["brevet_dist"]
        rows = input_json["rows"]
        
        insert_id = insert_rows(begin_time, brevet_dist, rows)

        return flask.jsonify( result = {},
                            message = "Inserted!",
                            status = 1,
                            mongo_id=insert_id)
    except:
        return flask.jsonify( result = {},
                            message = "Oh no! Server Error",
                            status = 0,
                            mongo_id='None')

    return

@app.route("/_display")
def _display():
    '''
    Will retrieve most recent save from submit and display it back into webpage. 
    This save will contain previous values put into the rows on webpage

    Accepts GET requests only

    JSON interface: gets json, responds with json
    '''
    try:
        begin_time, brevet_dist, rows = get_rows()
        return flask.jsonify(
                result = { "begin_time": begin_time, "brevet_dist": brevet_dist, "rows": rows },
                status = 1,
                message = "Successfully fetched controls!"
                )
    except:
        return flask.jsonify(
                result = {},
                status = 0,
                message = "Something went wrong, couldnt fetch controls"
                )

    return
#############

if __name__ == "__main__":
    app.debug = os.environ.get('DEBUG')
    if app.debug:
        app.logger.setLevel(logging.DEBUG)

    port = os.environ.get('PORT')
    print("Opening for global access on port {}".format(port))
    app.run(port=port, host="0.0.0.0")
