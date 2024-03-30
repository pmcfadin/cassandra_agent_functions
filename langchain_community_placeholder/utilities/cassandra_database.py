
"""Apache Cassandra database wrapper."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Union

from cassandra.cluster import Cluster, ResultSet
from cassandra.query import dict_factory
from cassandra.auth import PlainTextAuthProvider

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
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        secure_connect_bundle_path: Optional[str] = None,
        mode: str = "CASSANDRA",
        **kwargs: Any,
    ):
        self._contact_points = contact_points.split(",") if isinstance(contact_points, str) else contact_points
        self._port = port
        self._keyspace = keyspace
        self._username = username
        self._password = password
        self._client_id = client_id
        self._client_secret = client_secret
        self._secure_connect_bundle_path = secure_connect_bundle_path
        self._mode = mode
        self._cluster = self._create_cluster()
        self._session = self._cluster.connect()
        self._session.row_factory = dict_factory
        self.metadata = self._cluster.metadata
        self._keyspace_info = self._cluster.metadata.keyspaces[self._keyspace]
        self.tables = self._cluster.metadata.keyspaces[self._keyspace].tables

    def _create_cluster(self) -> Cluster:
        if self._mode == "CASSANDRA":
            return Cluster(
                contact_points=self._contact_points,
                port=self._port,
                auth_provider=PlainTextAuthProvider(username=self._username, password=self._password),
                **self.get_extra_args()
            )
        elif self._mode == "ASTRA":
        
            auth_provider = PlainTextAuthProvider(self._client_id, self._client_secret)
            cloud_config= {
                'secure_connect_bundle': self._secure_connect_bundle_path
            }
            cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
            return cluster
        else:
            raise ValueError("Mode must be either 'CASSANDRA' or 'ASTRA'")


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

    def get_table_data_no_throw(self, keyspace: str, table: str, predicate: str, limit: int) -> str:
        """Get data from the specified table in the specified keyspace. Optionally can take a predicate for the WHERE clause and a limit."""
        try:
            return self.get_table_data(keyspace, table, predicate, limit)
        except Exception as e:
            """Format the error message"""
            return f"Error: {e}"

    # This is a more basic string building function that doesn't use a query builder or prepared statements
    # TODO: Refactor to use a query builder or prepared statements
    def get_table_data(self, keyspace: str, table: str, predicate: str, limit: int) -> str:
        """Get data from the specified table in the specified keyspace."""

        query = f"SELECT * FROM {keyspace}.{table}"

        if predicate:
            query += f" WHERE {predicate}"
        if limit:
            query += f" LIMIT {limit}"
        
        query += ";"
        
        result = self.run(query, fetch="all")
        data = "\n".join(str(row) for row in result)
        return data

    def get_context(self) -> Dict[str, Any]:
        """Return db context that you may want in agent prompt."""
        keyspaces = self._cluster.metadata.keyspaces.keys()
        return {"keyspaces": ", ".join(keyspaces)}
    
    def format_schema_to_markdown(self) -> str:
        """
        Takes the Metadata object from a Cassandra cluster connection and formats the schema
        into a markdown representation.

        :param metadata: The Metadata object from a Cassandra cluster connection.
        :return: A string in markdown format representing the schema.
        """
        markdown_output = ""

        # Iterate through each keyspace
        for keyspace_name, keyspace_metadata in self.metadata.keyspaces.items():
            if keyspace_name.startswith('system'):
                continue # Skip system keyspaces

            if keyspace_name.startswith('data_endpoint_auth'):
                continue # Skip data_endpoint_auth keyspaces

            if keyspace_name.startswith('datastax_sla'):
                continue
            
            markdown_output += f"Keyspace Name: {keyspace_name}\n"

            # Iterate through each table in the keyspace
            for table_name, table_metadata in keyspace_metadata.tables.items():
                markdown_output += f" - Table Name: {table_name}\n"
                # List columns and their types
                for column_name, column_metadata in table_metadata.columns.items():
                    markdown_output += f"   - {column_name} ({column_metadata.cql_type})\n"

                # List primary key components
                primary_key_parts = [col.name for col in table_metadata.primary_key]
                markdown_output += f"   - Primary Key ({', '.join(primary_key_parts)})\n"

                # List indexes, if any
                if table_metadata.indexes:
                    markdown_output += "   - Indexes\n"
                    for index_name, index_metadata in table_metadata.indexes.items():
                        markdown_output += f"      - {index_name}: {index_metadata.kind}\n"

            markdown_output += "\n"  # Add some spacing between keyspaces

        return markdown_output