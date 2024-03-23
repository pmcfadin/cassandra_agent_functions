from cassandra.cluster import Cluster, Session
from typing import List, Any
from pydantic.v1 import BaseModel, Field

class GetData(BaseModel):
    keyspace: str = Field(..., title="The keyspace to query")
    table: str = Field(..., title="The table to query")
    limit: int = Field(..., title="The limit of rows to return")
    

class CassandraQuery:
    def __init__(self, session: Session):
        self.session = session

    def get_data(self, keyspace: str, table: str, limit: int) -> List[Any]:
        ''' Get data from a table in a keyspace with a limit
        :param keyspace: The keyspace to query
        :param table: The table to query
        :param limit: The limit of rows to return
        :return: The list of results
        '''
        query = f"SELECT * FROM {keyspace}.{table} LIMIT {limit}"

        try:
            return self.session.execute(query)
        except Exception as e:
            print(f"Error executing query: {e}")
            return []
        
    def put_data(self, keyspace: str, table: str, data: dict) -> None:
        query = f"INSERT INTO {keyspace}.{table} ({', '.join(data.keys())}) VALUES ({', '.join(data.values())})"

        try:
            self.session.execute(query)
        except Exception as e:
            print(f"Error executing query: {e}")

    def update_data(self, keyspace: str, table: str, data: dict) -> None:
        query = f"UPDATE {keyspace}.{table} SET {', '.join([f'{k}={v}' for k, v in data.items()])}"
        

    def execute_query(self, keyspace: str, table: str, parameters: tuple = (), limit = None) -> List[Any]:
        """
        Execute a CQL query and return the results.

        :param query: The CQL query string.
        :param parameters: The parameters for the query, if any.
        :return: The list of results.
        """
        query = f"SELECT * FROM {keyspace}.{table} LIMIT {limit}"

        try:
            return self.session.execute(query, parameters)
        except Exception as e:
            print(f"Error executing query: {e}")
            return []
