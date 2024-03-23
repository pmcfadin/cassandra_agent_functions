import pytest
from unittest.mock import Mock, patch
from cassandra.cluster import Session


@pytest.fixture(scope="module")
def cassandra_session():
    """
    Mock Cassandra session for use in tests.
    This uses the built-in `unittest.mock` library to create a mock session.
    """
    # Mocking the Session object from the cassandra-driver library
    with patch.object(Session, 'execute', return_value=True) as mock_session:
        # Create a session instance which could be a mock or real, depending on your test setup
        session = create_session()
        yield session  # Provide the session to the test case
        # Teardown logic could go here (e.g., closing the session)

@pytest.fixture(scope="function")
def mock_execute_success():
    """
    Mock successful execution of a Cassandra query.
    """
    with patch('cassandra.cluster.Session.execute', return_value=True) as mock_method:
        yield mock_method

@pytest.fixture(scope="function")
def mock_execute_failure():
    """
    Mock failed execution of a Cassandra query.
    """
    with patch('cassandra.cluster.Session.execute', side_effect=Exception("Query failed")) as mock_method:
        yield mock_method
