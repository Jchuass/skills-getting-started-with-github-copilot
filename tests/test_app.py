import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    original = {k: v['participants'].copy() for k, v in activities.items()}
    yield
    for k in activities:
        activities[k]['participants'] = original[k].copy()

def test_get_activities():
    r = client.get('/activities')
    assert r.status_code == 200
    data = r.json()
    assert 'Chess Club' in data

def test_signup_success():
    email = 'test1@mergington.edu'
    r = client.post('/activities/Tennis Club/signup', params={'email': email})
    assert r.status_code == 200
    assert email in activities['Tennis Club']['participants']

def test_signup_same_activity_duplicate_blocked():
    email = 'michael@mergington.edu'  # already in Chess Club
    r = client.post('/activities/Chess Club/signup', params={'email': email})
    assert r.status_code == 400

def test_signup_cross_activity_blocked():
    email = 'emma@mergington.edu'  # in Programming Class
    r = client.post('/activities/Chess Club/signup', params={'email': email})
    assert r.status_code == 400
    assert 'already signed up for' in r.json().get('detail', '')

def test_remove_participant_success():
    email = 'michael@mergington.edu'
    r = client.delete('/activities/Chess Club/participants', params={'email': email})
    assert r.status_code == 200
    assert email not in activities['Chess Club']['participants']

def test_remove_nonexistent_participant():
    r = client.delete('/activities/Chess Club/participants', params={'email': 'noone@mergington.edu'})
    assert r.status_code == 404
