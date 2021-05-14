import mongomock
import os
import json
from mock_lamb import MockContext
from pymongo import MongoClient

# TODO: This still needs access to the internet to run


@mongomock.patch(servers=(('localhost', 27017),))
def test_panvel_post(app, test_panvel_event):
    resp = app(test_panvel_event, MockContext)
    resp = json.loads(resp)
    assert resp['outputs'][0]['state'] == 'Maharashtra'
    assert resp['outputs'][0]['size'] == 44


def test_lucknow_post(app, test_lucknow_event):
    resp = app(test_lucknow_event, MockContext)
    resp = json.loads(resp)
    assert resp['outputs'][0]['state'] == 'Uttar Pradesh'
    assert resp['outputs'][0]['size'] == 73


def test_west_bengal_post(app, test_west_bengal_post):
    resp = app(test_west_bengal_post, MockContext)
    resp = json.loads(resp)


# TODO: Test the GETs back from the DB
