import logging
logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.WARNING)
log = logging.getLogger(__name__)


from pymongo import MongoClient
import nose
from mongo import test_insert, test_fetch
import arrow

client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)

db = client.test_inputs
collection = db.test_lists

# Define a constant variable for time
TIME1 = "2023-07-01T00:00"

# Convert the time string to an Arrow object for easier manipulation
BEGIN_TIME = arrow.get(TIME1)

# Specify the brevet distance as a string
BREVET_DIST = "500"

# Define three rows of data, each containing information about a specific kilometer point
ROW1 = {'km': 100, 'open_time': begin_time.shift(minutes=+60), 'close_time': begin_time.shift(minutes=+65)}
ROW2 = {'km': 200, 'open_time': begin_time.shift(minutes=+120), 'close_time': begin_time.shift(minutes=+125)}
ROW3 = {'km': 300, 'open_time': begin_time.shift(minutes=+180), 'close_time': begin_time.shift(minutes=+185)}

# Combine the rows into a list
ROWS = [ROW1, ROW2, ROW3]

# Function to test the insertion of data into the collection
def insert_test():
    # Insert the test data and get the inserted document's ID
    _id = insert_attempt(BEGIN_TIME, BREVET_DIST, ROWS)
    # Assert that the returned ID is a string
    assert isinstance(_id, str)

# Function to test the fetching of data from the collection
def fetch_test():
    # Fetch the latest attempt data from the collection
    result = fetch_attempt()
    # Assert that the fetched data matches the expected values
    assert result[0] == BEGIN_TIME
    assert result[1] == BREVET_DIST
    assert result[2][0] == ROW1
    assert result[2][1] == ROW2
    assert result[2][2] == ROW3
