"""
Nose tests for acp_times.py

Write your tests HERE AND ONLY HERE.
"""

import nose    # Testing framework
from nose.tools import assert_raises
import logging

from acp_times import open_time, close_time
import arrow

logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.WARNING)
log = logging.getLogger(__name__)

TIME1 = '2023-07-01T00:00'
TIME2 = '2025-12-17T14:23'


def test_zero():
    start_time = arrow.get(TIME1)
    close = close_time(0, 200, start_time)
    open = open_time(0, 200, start_time)
    assert open ==  start_time
    assert close == start_time.shift(minutes=60)

def test_negatives():
    start_time = arrow.get(TIME1)
    assert_raises(ValueError, open_time, -1, 200, start_time)
    assert_raises(ValueError, close_time, -1, 200, start_time)

def test1():
    start_time = arrow.get(TIME1)
    t2 = open_time(300, 300, start_time)
    t3 = open_time(500, 600, start_time)
    t4 = open_time(700, 1000, start_time)
    assert t2 == start_time.shift(minutes=+540)
    assert t3 == start_time.shift(minutes=+928)
    assert t4 == start_time.shift(minutes=+1342)
              
def test2():
    start_time = arrow.get(TIME2)
    t1 = close_time(150, 200, start_time)
    t2 = close_time(300, 300, start_time)
    t3 = close_time(500, 600, start_time)
    t4 = close_time(700, 1000, start_time) 
    assert t1 == start_time.shift(minutes=+600)
    assert t2 == start_time.shift(minutes=+1200)
    assert t3 == start_time.shift(minutes=+2000)
    assert t4 == start_time.shift(minutes=+2925)

def test3():
    start_time = arrow.get(TIME1)
    cont_open = close_time(0, 200, start_time)
    cont_close = close_time(205, 200, start_time)
    assert cont_open == start_time.shift(minutes=+60)
    assert cont_close == start_time.shift(minutes=+800)


