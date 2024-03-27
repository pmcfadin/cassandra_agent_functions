
"""Apache Cassandra database wrapper."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Union

from cassandra.cluster import Cluster, ResultSet
from cassandra.query import dict_factory

from langchain_core.utils import get_from_env

class CassandraDatabase:
    """Apache Cassandra database wrapper."""

    def __init__(
        self,
        contact_points: Optional[Sequence[str]] = None,
        port: int = 9042,
        keyspace: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs: Any,
    ):
        self._contact_points = contact_points.split(",") if isinstance(contact_points, str) else contact_points
        self._port = port
        self._keyspace = keyspace
        self._username = username
        self._password = password
        self._cluster = self._create_cluster()
        self._session = self._cluster.connect(self._keyspace)
        self._session.row_factory = dict_factory

    def _create_cluster(self) -> Cluster:
        return Cluster(
            contact_points=self._contact_points,
            port=self._port,
            auth_provider=self._get_auth_provider(),
            **self.get_extra_args()
        )

    def _get_auth_provider(self) -> Optional[Any]:
        if self._username and self._password:
            from cassandra.auth import PlainTextAuthProvider
            return PlainTextAuthProvider(username=self._username, password=self._password)
        return None

    def get_extra_args(self) -> Dict[str, Any]:
        return {}

    def run(
        self,
        query: str,
        fetch: str = "all",
        include_columns: bool = False,
        **kwargs: Any,
    ) -> Union[str, Sequence[Dict[str, Any]], ResultSet]:
        """Execute a CQL query and return the results."""
        try:
            result = self._session.execute(query, **kwargs)
            if fetch == "all":
                return list(result)
            elif fetch == "one":
                return result.one()._asdict() if result else {}
            elif fetch == "cursor":
                return result
            else:
                raise ValueError("Fetch parameter must be either 'one', 'all', or 'cursor'")
        except Exception as e:
            """Format the error message"""
            return f"Error: {e}"

    def run_no_throw(
        self,
        query: str,
        fetch: str = "all",
        include_columns: bool = False,
        **kwargs: Any,
    ) -> Union[str, Sequence[Dict[str, Any]], ResultSet]:
        """Execute a CQL query and return the results or an error message."""
        try:
            return self.run(query, fetch, include_columns, **kwargs)
        except Exception as e:
            """Format the error message"""
            return f"Error: {e}"

    def get_keyspace_schema_no_throw(self, keyspace: str) -> str:
        """Get the schema for the specified keyspace."""
        try:
            return self.get_keyspace_schema(keyspace)
        except Exception as e:
            """Format the error message"""
            return f"Error: {e}"

    def get_keyspace_schema(self, keyspace: str) -> str:
        """Get the schema for the specified keyspace."""
 
        schema = []

        keyspace_dict = {'keyspace': keyspace, 'tables': []}
        tables = self.run(f"SELECT table_name FROM system_schema.tables WHERE keyspace_name = '{keyspace}';")

        for table_row in tables:
            table_name = table_row['table_name']
            table_info = {'table_name': table_name, 'columns': [], 'indexes': []}

            # Fetch columns
            columns = self.run(f"SELECT column_name, type FROM system_schema.columns WHERE keyspace_name = '{keyspace}' AND table_name = '{table_name}';")
            for column_row in columns:
                table_info['columns'].append({'column_name': column_row['column_name'], 'type': column_row['type']})

            # Fetch indexes
            indexes = self.run(f"SELECT index_name, kind FROM system_schema.indexes WHERE keyspace_name = '{keyspace}' AND table_name = '{table_name}';")
            for index_row in indexes:
                table_info['indexes'].append({'index_name': index_row['index_name'], 'type': index_row['kind']})

            keyspace_dict['tables'].append(table_info)

        schema.append(keyspace_dict)

        return schema

    def get_table_data_no_throw(self, keyspace: str, table: str, limit: int) -> str:
        """Get data from the specified table in the specified keyspace."""
        try:
            return self.get_table_data(keyspace, table, limit)
        except Exception as e:
            """Format the error message"""
            return f"Error: {e}"

    def get_table_data(self, keyspace: str, table: str, limit: int) -> str:
        """Get data from the specified table in the specified keyspace."""
        if limit:
            query = f"SELECT * FROM {keyspace}.{table} LIMIT {limit};"
        else:        
            query = f"SELECT * FROM {keyspace}.{table};"
        result = self.run(query, fetch="all")
        data = "\n".join(str(row) for row in result)
        return data

    def get_context(self) -> Dict[str, Any]:
        """Return db context that you may want in agent prompt."""
        keyspaces = self._cluster.metadata.keyspaces.keys()
        return {"keyspaces": ", ".join(keyspaces)}