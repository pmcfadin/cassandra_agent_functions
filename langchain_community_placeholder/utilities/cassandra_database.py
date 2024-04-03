"""Apache Cassandra database wrapper."""
from __future__ import annotations

from typing import Any, Dict, List, Tuple, Optional, Sequence, Union

import cassio
from cassandra.cluster import Session, ResultSet
import re

IGNORED_KEYSPACES = ['system', 'system_auth', 'system_distributed', 'system_schema', 'system_traces', 'system_views', 'datastax_sla', 'data_endpoint_auth']

class CassandraDatabase:
    """Apache Cassandra database wrapper."""

    def __init__(
        self,
        session: Optional[Session] = None,
        keyspace_list: Optional[List[str]] = None,
        exclude_tables: Optional[List[str]] = None,
        include_tables: Optional[List[str]] = None,
        cassio_init_kwargs: Optional[Dict[str, Any]] = None,
    ):
        self._session = self._resolve_session(session, cassio_init_kwargs)
        if not self._session:
            raise ValueError("Session not provided and cannot be resolved")

        self._exclude_keyspaces = IGNORED_KEYSPACES
        self._ignore_tables = exclude_tables or []
        self._include_tables = include_tables or []
        self._keyspaces = self._resolve_keyspaces(keyspace_list)

    def run(
        self,
        query: str,
        fetch: str = "all",
        include_columns: bool = False,
        **kwargs: Any,
    ) -> Union[str, Sequence[Dict[str, Any]], ResultSet]:
        """Execute a CQL query and return the results."""
        clean_query = self._validate_cql(query, 'SELECT')
        result = self._session.execute(clean_query, **kwargs)
        if fetch == "all":
            return list(result)
        elif fetch == "one":
            return result.one()._asdict() if result else {}
        elif fetch == "cursor":
            return result
        else:
            raise ValueError("Fetch parameter must be either 'one', 'all', or 'cursor'")

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

    def get_keyspace_schema(self, keyspace: str) -> List[Table]:
        """Get the schema for the specified keyspace."""
        if keyspace in self._keyspaces:
            return self._keyspaces[keyspace]
        else:
            return []
 
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
        return {"keyspaces": ", ".join(self._keyspaces.keys())}
    
    def format_keyspace_to_markdown(self, keyspace: str) -> str:
        """
        Generates a markdown representation of the schema for a specific keyspace by iterating
        over all tables within that keyspace and calling their as_markdown method.

        Parameters:
        - keyspace (str): The name of the keyspace to generate markdown documentation for.

        Returns:
        A string containing the markdown representation of the specified keyspace schema.
        """
        if keyspace in self._keyspaces:
            output = f"## Keyspace: {keyspace}\n\n"
            for table in self._keyspaces[keyspace]:
                output += table.as_markdown(include_keyspace=False, header_level=3) + "\n\n"
            return output
        else:
            return ""

    def format_schema_to_markdown(self) -> str:
        """
        Generates a markdown representation of the schema for all keyspaces and tables
        within the CassandraDatabase instance. This method utilizes the
        format_keyspace_to_markdown method to create markdown sections for each keyspace,
        assembling them into a comprehensive schema document.

        Iterates through each keyspace in the database, utilizing format_keyspace_to_markdown
        to generate markdown for each keyspace's schema, including details of its tables. These
        sections are concatenated to form a single markdown document that represents the schema
        of the entire database or the subset of keyspaces that have been resolved in this instance.

        Returns:
        A markdown string that documents the schema of all resolved keyspaces and their tables
        within this CassandraDatabase instance. This includes keyspace names, table names,
        comments, columns, partition keys, clustering keys, and indexes for each table.
        """
        output = "# Cassandra Database Schema\n\n"
        for keyspace in self._keyspaces.keys():
            output += f"{self.format_keyspace_to_markdown(keyspace)}\n\n"
  
    def _validate_cql(self, cql: str, type: str = 'SELECT') -> str:
        """
        Validates a CQL query string for basic formatting and safety checks.
        Ensures that `cql` starts with the specified type (e.g., SELECT) and does not contain
        content that could indicate CQL injection vulnerabilities.

        Parameters:
        - cql (str): The CQL query string to be validated.
        - type (str): The expected starting keyword of the query, used to verify that the query
        begins with the correct operation type (e.g., "SELECT", "UPDATE"). Defaults to "SELECT".

        Returns:
        - str: The trimmed and validated CQL query string without a trailing semicolon.

        Raises:
        - ValueError: If the value of `type` is not supported
        - DatabaseError: If `cql` is considered unsafe
        """
        SUPPORTED_TYPES = ['SELECT']
        if type and type.upper() not in SUPPORTED_TYPES:
            raise ValueError(f"Unsupported CQL type: {type}. Supported types: {SUPPORTED_TYPES}")

        # Basic sanity checks
        cql_trimmed = cql.strip()
        if not cql_trimmed.upper().startswith(type.upper()):
            raise DatabaseError(f"CQL must start with {type.upper()}.")

        # Allow a trailing semicolon, but remove (it is optional with the Python driver)
        cql_trimmed = cql_trimmed.rstrip(';')

        # Consider content within matching quotes to be "safe"
        cql_sanitized = re.sub(r"'.*?'", '', cql_trimmed)    # Remove single-quoted strings
        cql_sanitized = re.sub(r'".*?"', '', cql_sanitized)  # Remove double-quoted strings

        # Find unsafe content in the remaining CQL
        if ";" in cql_sanitized:
            raise DatabaseError("Potentially unsafe CQL, as it contains a ; at a place other than the end or within quotation marks.")
        
        # The trimmed query, before modifications
        return cql_trimmed

    def _fetch_keyspaces(self, keyspace_list : Optional[List[str]] = None):
        """
        Fetches a list of keyspace names from the Cassandra database. The list can be filtered by
        a provided list of keyspace names or by excluding predefined keyspaces.

        Parameters:
        - keyspace_list (Optional[List[str]]): A list of keyspace names to specifically include.
          If provided and not empty, the method returns only the keyspaces present in this list.
          If not provided or empty, the method returns all keyspaces except those specified in
          the _exclude_keyspaces attribute.

        Returns:
        - List[str]: A list of keyspace names according to the filtering criteria. This includes
          either the explicitly requested keyspaces (if keyspace_list is provided and contains
          valid keyspace names) or all keyspaces minus those intended to be excluded by default
          (specified in _exclude_keyspaces).
        """        
        all_keyspaces = self.run("SELECT keyspace_name FROM system_schema.keyspaces", fetch="all")
        if keyspace_list and len(keyspace_list) > 0:
            return [ks['keyspace_name'] for ks in all_keyspaces if ks['keyspace_name'] in keyspace_list]
        else:
            return [ks['keyspace_name'] for ks in all_keyspaces if ks['keyspace_name'] not in self._exclude_keyspaces]

    def _fetch_filtered_schema_data(self, keyspace_list):
        """
        Fetches schema data, including tables, columns, and indexes, filtered by a list of keyspaces.
        This method constructs CQL queries to retrieve detailed schema information from the specified
        keyspaces and executes them to gather data about tables, columns, and indexes within those keyspaces.

        Parameters:
        - keyspace_list (List[str]): A list of keyspace names from which to fetch schema data.

        Returns:
        - Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]: A tuple containing three lists:
        - The first list contains dictionaries of table details (keyspace name, table name, and comment).
        - The second list contains dictionaries of column details (keyspace name, table name, column name, type, kind, and position).
        - The third list contains dictionaries of index details (keyspace name, table name, index name, kind, and options).

        This method allows for efficiently fetching schema information for multiple keyspaces in a single operation,
        enabling applications to programmatically analyze or document the database schema.
        """
        # Construct IN clause for CQL query
        keyspace_in_clause = ', '.join([f"'{ks}'" for ks in keyspace_list])

        # Fetch filtered table details
        tables_query = f"SELECT keyspace_name, table_name, comment FROM system_schema.tables WHERE keyspace_name IN ({keyspace_in_clause})"
        tables_data = self.run(tables_query, fetch="all")

        # Fetch filtered column details
        columns_query = f"SELECT keyspace_name, table_name, column_name, type, kind, clustering_order, position FROM system_schema.columns WHERE keyspace_name IN ({keyspace_in_clause})"
        columns_data = self.run(columns_query, fetch="all")

        # Fetch filtered index details
        indexes_query = f"SELECT keyspace_name, table_name, index_name, kind, options FROM system_schema.indexes WHERE keyspace_name IN ({keyspace_in_clause})"
        indexes_data = self.run(indexes_query, fetch="all")

        return tables_data, columns_data, indexes_data

    def _resolve_keyspaces(self, keyspace_list : Optional[List[str]] = None) -> Dict[str, List[Table]]:
        """
        Efficiently fetches and organizes Cassandra table schema information, such as comments,
        columns, and indexes, into a dictionary mapping keyspace names to lists of Table objects.
        
        Returns:
        A dictionary with keyspace names as keys and lists of Table objects as values, where each
        Table object is populated with schema details appropriate for its keyspace and table name.
        """
        keyspaces = self._fetch_keyspaces(keyspace_list)
        tables_data, columns_data, indexes_data = self._fetch_filtered_schema_data(keyspaces)
              
        keyspace_dict = {}
        for table_data in tables_data:
            keyspace, table_name = table_data['keyspace_name'], table_data['table_name']
            comment = table_data.get('comment', '')
            
            # Filter columns and indexes for this table
            table_columns = [(c['column_name'], c['type']) for c in columns_data if c['keyspace_name'] == keyspace and c['table_name'] == table_name]
            partition_keys = [c['column_name'] for c in columns_data if c['kind'] == 'partition_key' and c['keyspace_name'] == keyspace and c['table_name'] == table_name]
            clustering_keys = [(c['column_name'], c['clustering_order']) for c in columns_data if c['kind'] == 'clustering' and c['keyspace_name'] == keyspace and c['table_name'] == table_name]
            table_indexes = [(c['index_name'], c['kind'], c['options']) for c in indexes_data if c['keyspace_name'] == keyspace and c['table_name'] == table_name]
            
            table_obj = Table(
                keyspace=keyspace,
                table_name=table_name,
                comment=comment,
                columns=table_columns,
                partition=partition_keys,
                clustering=clustering_keys,
                indexes=table_indexes
            )
            
            if keyspace not in keyspace_dict:
                keyspace_dict[keyspace] = []
            keyspace_dict[keyspace].append(table_obj)
        
        return keyspace_dict

    def _resolve_session(
        self,
        session: Optional[Session] = None, 
        cassio_init_kwargs: Optional[Dict[str, Any]] = None
    ) -> Session:
        """
        Attempts to resolve and return a Session object for use in database operations.
        
        This function follows a specific order of precedence to determine the appropriate session to use:
        1. `session` parameter if given,
        2. Existing `cassio` session,
        3. A new `cassio` session derived from `cassio_init_kwargs`, 
        4. `None`

        Parameters:
        - session (Optional[Session]): An optional session to use directly.
        - cassio_init_kwargs (Optional[Dict[str, Any]]): An optional dictionary of keyword arguments to `cassio`.

        Returns:
        - Session: The resolved session object if successful, or `None` if the session cannot be resolved.

        Raises:
        - ValueError: If `cassio_init_kwargs` is provided but is not a dictionary of keyword arguments.
        """
        # Prefer given session 
        if session:
            return session
        
        # Use pre-existing session on cassio
        try:
            s = cassio.check_resolve_session()
            return s
        except ValueError:
            # check_resolve_session throws a value error if session is not set
            pass

        # Try to init and return cassio session
        if cassio_init_kwargs:
            if isinstance(cassio_init_kwargs, dict):
                cassio.init(**cassio_init_kwargs)
                s = cassio.check_resolve_session()
                return s
            else:
                raise ValueError("cassio_init_kwargs must be a keyword dictionary")
            
        # return None if we're not able to resolve
        return None

class DatabaseError(Exception):
    """Exception raised for errors in the database schema.

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
    
class Table:
    def __init__(
        self,
        keyspace: str,
        table_name: str,
        db: Optional[CassandraDatabase] = None,
        comment: Optional[str] = None,
        columns: Optional[Tuple[str, str]] = None,
        partition: Optional[List[str]] = None,
        clustering: Optional[List[Tuple[str,str]]] = None,
        indexes: Optional[List[Tuple[str, str, str]]] = None
    ):
        """
        Initializes a representation of a Cassandra table, either by resolving its schema from the database
        or by directly using the provided schema details.

        Parameters:
        - keyspace (str): The keyspace in which the table exists.
        - table_name (str): The name of the table.
        - db (Optional[CassandraDatabase]): An optional database connection to resolve table schema.
        - comment (Optional[str]): An optional comment describing the table, used if `db` is not provided.
        - columns (Optional[Dict[str, str]]): A dictionary mapping column names to types, used if `db` is not provided.
        - partition (Optional[List[str]]): A list of partition key column names, used if `db` is not provided.
        - clustering (Optional[List[str]]): A list of clustering key column names, used if `db` is not provided.
        - indexes (Optional[List[Tuple[str, str, str]]]): A list of tuples describing indexes, used if `db` is not provided.

        Raises:
        - ValueError: If `keyspace` or `table_name` is not provided, or if `columns` or `partition` is not provided when `db` is None.
        """
        if keyspace is None or table_name is None:
            raise ValueError("keyspace and table_name are required")
        
        self._table_name = table_name
        self._keyspace = keyspace

        if db:
            self._comment = self._resolve_comment(db)
            self._columns, self._partition, self._clustering = self._resolve_columns(db)
            self._indexes = self._resolve_indexes(db)
        else:
            if not columns or len(columns) == 0:
                raise ValueError("non-empty column list must be provided")
            if not partition or len(partition) == 0:
                raise ValueError("non-empty partition list must be provided")
            self._comment = comment
            self._columns = columns
            self._partition = partition
            self._clustering = clustering or []
            self._indexes = indexes or []
    
    def as_markdown(self, include_keyspace: bool = True, header_level: Optional[int] = None):
        """
        Generates a Markdown representation of the Cassandra table schema, allowing for
        customizable header levels for the table name section.

        Parameters:
        - include_keyspace (bool): If True, includes the keyspace in the output. Defaults to True.
        - header_level (Optional[int]): Specifies the markdown header level for the table name.
          If None, the table name is included without a header. Defaults to None (no header level).

        Returns:
        - str: A string in Markdown format detailing the table name (with optional header level),
          keyspace (optional), comment, columns, partition keys, clustering keys (with optional clustering order),
          and indexes.
        """
        output = ""
        if header_level is not None:
            output += f"{'#' * header_level} "
        output += f"Table Name: {self._table_name}\n"

        if include_keyspace:
            output += f"- Keyspace: {self._keyspace}\n"
        if self._comment:
            output += f"- Comment: {self._comment}\n"

        output += f"- Columns\n"
        for column,type in self._columns:
            output += f"  - {column} ({type})\n"

        output += f"- Partition ({', '.join(self._partition)})\n"
        if self._clustering:
            cluster_list = []
            for column, clustering_order in self._clustering:
                if clustering_order.lower() == 'none':
                    cluster_list.append(column)
                else:
                    cluster_list.append(f"{column} {clustering_order}")
            output += f"- Clustering: ({', '.join(cluster_list)})\n"

        if self._indexes:                    
            output += f"- Indexes\n"
            for name, kind, options in self._indexes:
                output += f"  - {name} : kind={kind}, options={options}\n"

        return output

    @property 
    def table_name(self) -> str:
        return self._table_name

    @property
    def comment(self) -> str:
        return self._comment

    @property
    def keyspace(self) -> str:
        return self._keyspace
    
    @property
    def columns(self) -> Tuple[str,str]:
        return self._columns
    
    @property
    def partition(self) -> List[str]:
        return self._partition
    
    @property
    def cluster(self) -> List[Tuple[str,str]]:
        return self._clustering
    
    @property
    def indexes(self) -> List[Tuple[str,str,str]]:
        return self._indexes
    
    def _resolve_comment(self, db) -> str:
        results = db.run(f"SELECT comment FROM system_schema.tables WHERE keyspace_name = '{self._keyspace}' AND table_name = '{self._table_name}';")
        row = next(results, None)
        if row is not None:
            return row['comment']
        else:
            raise DatabaseError(f"Table not found: {self._keyspace}.{self._table_name}")

    def _resolve_columns(self, db) -> Tuple[List[Tuple[str, str]], List[str], List[Tuple[str,str]]]:
        columns = []
        partition_info = []
        cluster_info = []
        results = db.run(f"SELECT column_name, type, kind, clustering_order, position FROM system_schema.columns WHERE keyspace_name = '{self._keyspace}' AND table_name = '{self._table_name}';")
        for row in results:
            columns.append((row['column_name'], row['type']))
            if row['kind'] == 'partition_key':
                partition_info.append((row['column_name'], row['position']))
            elif row['kind'] == 'clustering':
                cluster_info.append((row['column_name'], row['clustering_order'], row['position']))

        partition = [column_name for column_name, _ in sorted(partition_info, key=lambda x: x[1])]
        cluster = [(column_name, clustering_order) for column_name, clustering_order, _ in sorted(cluster_info, key=lambda x: x[2])]

        return columns, partition, cluster
    
    def _resolve_indexes(self, db) -> List[Tuple[str, str, str]]:
        indexes = []
        results = db.run(f"SELECT index_name, kind, options FROM system_schema.indexes WHERE keyspace_name = '{self._keyspace}' AND table_name = '{self._table_name}';")
        for row in results:
            indexes.append((row['index_name'], row['kind'], row['options'])) 
        return indexes
    