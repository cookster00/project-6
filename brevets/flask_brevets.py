"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)
"""

import flask
from flask import request
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations

import logging
import os
import requests  # The library we use to send requests to the API

# Set up Flask app
app = flask.Flask(__name__)
app.debug = True if "DEBUG" not in os.environ else os.environ["DEBUG"]
port_num = True if "PORT" not in os.environ else os.environ["PORT"]
app.logger.setLevel(logging.DEBUG)

##################################################
################### API Callers ##################
##################################################

API_ADDR = os.environ["API_ADDR"]
API_PORT = os.environ["API_PORT"]
API_URL = f"http://{API_ADDR}:{API_PORT}/api/"


def get_brevet():
    """
    Obtains the newest document in the "lists" collection in the database
    by calling the RESTful API.

    Returns title (string) and items (list of dictionaries) as a tuple.
    """
    # Get documents (rows) in our collection (table),
    # Sort by primary key in descending order and limit to 1 document (row)
    # This will translate into finding the newest inserted document.

    lists = requests.get(f"{API_URL}brevets").json()

    # lists should be a list of dictionaries.
    # we just need the last one:
    brevet = lists[-1]
    return brevet["items"], brevet["start_time"], brevet["brevet_dist_km"]


def insert_brevet(items, start_time, brevet_dist_km):
    """
    Inserts a new brevet into the database by calling the API.

    Inputs a title (string) and items (list of dictionaries)
    """
    _id = requests.post(f"{API_URL}brevets", json={"items": items, "start_time": start_time, "brevet_dist_km": brevet_dist_km}).json()
    return _id

##################################################
################## Flask routes ##################
##################################################


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
    """
    app.logger.debug("Got a JSON request")
    km = request.args.get('km', None, type=float)
    brevet_dist_km = request.args.get('brevet_dist_km', None, type=float)
    start_time = request.args.get('start_time', arrow.now().isoformat)

    open_time = acp_times.open_time(km, brevet_dist_km, start_time).format('YYYY-MM-DDTHH:mm')
    close_time = acp_times.close_time(km, brevet_dist_km, start_time).format('YYYY-MM-DDTHH:mm')
    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)


@app.route("/insert", methods=["POST"])
def insert():
    """
    /insert : inserts a brevet into the database.

    Accepts POST requests ONLY!

    JSON interface: gets JSON, responds with JSON
    """
    try:
        # Read the entire request body as a JSON
        # This will fail if the request body is NOT a JSON.
        input_json = request.json
        # if successful, input_json is automatically parsed into a python dictionary
        items = input_json["items"]
        start_time = input_json["start_time"]
        brevet_dist_km = input_json["brevet_dist_km"]

        brevet_id = insert_brevet(items, start_time, brevet_dist_km)
        app.logger.debug(brevet_id)

        return flask.jsonify(result={},
                             message="Inserted!",
                             status=1,  # This is defined by you. You just read this value in your javascript.
                             mongo_id=brevet_id)
    except:
        # Ensure Flask responds with a JSON.
        return flask.jsonify(result={},
                             message="Oh no! Server error!",
                             status=0,
                             mongo_id='None')


@app.route("/fetch")
def fetch():
    """
    /fetch : fetches the newest to-do list from the database.

    Accepts GET requests ONLY!

    JSON interface: gets JSON, responds with JSON
    """
    try:
        items, start_time, brevet_dist_km = get_brevet()
        return flask.jsonify(
            result={"items": items, "start_time": start_time, "brevet_dist_km": brevet_dist_km},
            status=1,
            message="Successfully fetched brevet!")
    except:
        return flask.jsonify(
            result={},
            status=0,
            message="Something went wrong, couldn't fetch any brevets!")


##################################################
################# Start Flask App ################
##################################################

if __name__ == "__main__":
    app.run(port=port_num, host="0.0.0.0")





