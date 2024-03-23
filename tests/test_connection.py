import pytest
from cassandra_agent.connection import CassandraConnection

def test_connection_successful(mocker):
    # Mock the Cluster.connect method to simulate a successful connection
    mocker.patch('cassandra.cluster.Cluster.connect', return_value=True)

    connection = CassandraConnection(['127.0.0.1'], 9042)
    assert connection.connect() is True

def test_connection_failure(mocker):
    # Mock the Cluster.connect method to simulate a connection failure
    mocker.patch('cassandra.cluster.Cluster.connect', side_effect=Exception('Connection failed'))

    connection = CassandraConnection(['127.0.0.1'], 9042)
    with pytest.raises(Exception) as excinfo:
        connection.connect()
    assert 'Connection failed' in str(excinfo.value)
