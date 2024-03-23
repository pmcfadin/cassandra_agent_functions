import pytest
from cassandra_agent.query import CassandraQuery
from cassandra_agent.connection import CassandraConnection

# Example test for a function that executes a CQL query
def test_execute_query_successful(mocker):
    mock_session = mocker.Mock()
    mock_session.execute.return_value = ['result1', 'result2']

    mock_connect = mocker.Mock()
    mock_connect.return_value = mock_session

    mocker.patch('cassandra_agent.connection.CassandraConnection.connect', new=mock_connect)

    cassandra_connection = CassandraConnection(['127.0.0.1'], 9042)
    cassandra_connection.connect()

    cassandra_query = CassandraQuery(cassandra_connection.session)
    results = cassandra_query.execute_query("SELECT * FROM mytable")
    assert len(results) == 2
    assert 'result1' in results
