import pytest


@pytest.fixture(scope="session")
def monkeysession(request):
    from _pytest.monkeypatch import MonkeyPatch
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope='session')
def app(monkeysession):
    monkeysession.setenv('INDIA_COVID_HOST', 'localhost:27017')
    monkeysession.setenv('INDIA_COVID_AUTH_HEADER', 'testAuth')
    monkeysession.setenv('INDIA_COVID_SKIP_UPLOADING', 'True')
    from lambda_function import lambda_handler
    yield lambda_handler


@pytest.fixture(scope='session')
def test_panvel_event():
    return {'state': 'Maharashtra', 'city': 'Panvel'}


@pytest.fixture(scope='session')
def test_lucknow_event():
    return {'state': 'Uttar Pradesh', 'city': 'Lucknow'}
