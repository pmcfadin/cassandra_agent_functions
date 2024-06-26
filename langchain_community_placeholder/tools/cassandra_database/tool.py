"""Tools for interacting with an Apache Cassandra database."""
from typing import Any, Dict, Optional, Sequence, Type, Union

from cassandra.cluster import Cluster, ResultSet
from cassandra.query import dict_factory

from langchain_core.pydantic_v1 import BaseModel, Field, root_validator

from langchain_core.language_models import BaseLanguageModel
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.prompts import PromptTemplate
from langchain_community_placeholder.utilities.cassandra_database import CassandraDatabase
from langchain_core.tools import BaseTool
from langchain_community_placeholder.tools.cassandra_database.prompt import QUERY_CHECKER

class BaseCassandraDatabaseTool(BaseModel):
    """Base tool for interacting with an Apache Cassandra database."""

    db: CassandraDatabase = Field(exclude=True)

    class Config(BaseTool.Config):
        pass

class _QueryCassandraDatabaseToolInput(BaseModel):
    query: str = Field(..., description="A detailed and correct CQL query.")

class QueryCassandraDatabaseTool(BaseCassandraDatabaseTool, BaseTool):
    """Tool for querying an Apache Cassandra database with provided CQL."""

    name: str = "cassandra_db_query"
    description: str = """
    Execute a CQL query against the database and get back the result.
    If the query is not correct, an error message will be returned.
    If an error is returned, rewrite the query, check the query, and try again.
    """
    args_schema: Type[BaseModel] = _QueryCassandraDatabaseToolInput

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Union[str, Sequence[Dict[str, Any]], ResultSet]:
        """Execute the query, return the results or an error message."""
        return self.db.run_no_throw(query)

class _GetSchemaCassandraDatabaseToolInput(BaseModel):
    keyspace: str = Field(
        ...,
        description=(
            "The name of the keyspace for which to return the schema."
        ),
    )

class GetSchemaCassandraDatabaseTool(BaseCassandraDatabaseTool, BaseTool):
    """Tool for getting the schema of a keyspace in an Apache Cassandra database."""

    name: str = "cassandra_db_schema"
    description: str = """
    Input to this tool is a keyspace name, output is a table description of Apache Cassandra tables.
    If the query is not correct, an error message will be returned.
    If an error is returned, report back to the user that the keyspace doesn't exist and stop.
    """
    
    args_schema: Type[BaseModel] = _GetSchemaCassandraDatabaseToolInput
  
    def _run(
        self,
        keyspace: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Get the schema for a keyspace."""
        return self.db.get_keyspace_schema_no_throw(keyspace)

class _GetTableDataCassandraDatabaseToolInput(BaseModel):
    keyspace: str = Field(
        ...,
        description=(
            "The name of the keyspace containing the table."
        ),
    )
    table: str = Field(
        ...,
        description=(
            "The name of the table for which to return data."
        ),
    )
    predicate: str = Field(
        ...,
        description=(
            "The predicate for the query that uses the primary key."
        ),
    )
    limit: int = Field(
        ...,
        description=(
            "The maximum number of rows to return."
        ),
    )

class GetTableDataCassandraDatabaseTool(BaseCassandraDatabaseTool, BaseTool):
    """
    Tool for getting data from a table in an Apache Cassandra database. 
    Use the WHERE clause to specify the predicate for the query that uses the primary key. A blank predicate will return all rows. Avoid this if possible. 
    Use the limit to specify the number of rows to return. A blank limit will return all rows.
    """

    name: str = "cassandra_db_select_table_data"
    description: str = """
    Tool for getting data from a table in an Apache Cassandra database. 
    Use the WHERE clause to specify the predicate for the query that uses the primary key. A blank predicate will return all rows. Avoid this if possible. 
    Use the limit to specify the number of rows to return. A blank limit will return all rows.
    """
    args_schema: Type[BaseModel] = _GetTableDataCassandraDatabaseToolInput

    def _run(
        self,
        keyspace: str,
        table: str,
        predicate: str,
        limit: int,    
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Get data from a table in a keyspace."""
        return self.db.get_table_data_no_throw(keyspace, table, predicate, limit)
