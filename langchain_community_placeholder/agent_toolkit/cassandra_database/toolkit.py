"""Apache Cassandra Toolkit."""
from typing import List

from langchain_core.pydantic_v1 import Field
from langchain_core.language_models import BaseLanguageModel
from langchain_community.agent_toolkits.base import BaseToolkit
from langchain_community.tools import BaseTool

from langchain_community_placeholder.utilities.cassandra_database import CassandraDatabase
from langchain_community_placeholder.tools.cassandra_database.tool import (
    GetSchemaCassandraDatabaseTool,
    QueryCassandraDatabaseTool,
    GetTableDataCassandraDatabaseTool,
    )

class CassandraDatabaseToolkit(BaseToolkit):
    """Toolkit for interacting with an Apache Cassandra database."""

    db: CassandraDatabase = Field(exclude=True)

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the toolkit."""
        return [
            GetSchemaCassandraDatabaseTool(db=self.db),
            QueryCassandraDatabaseTool(db=self.db),
            GetTableDataCassandraDatabaseTool(db=self.db),
        ]
