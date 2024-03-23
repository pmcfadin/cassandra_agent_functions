# Importing core functionalities from the modules
from .connection import CassandraConnection
from .query import CassandraQuery, GetData
from .transform import transform_data_after_retrieval, transform_data_before_insert
from .schema import CassandraSchema
from .data_operations import insert_data_into_table, select_data_from_table, get_schema_from_database


tools = [
    {
        "type": "function",
        "function": {
            "name": "insert_data_into_table",
            "description": "Insert data into a Cassandra table. Requires the table name and the data to insert. Data should at least contain the primary key.",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "The name of the table",
                    },
                    "data": {
                        "type": "object",
                        "additionalProperties": True,
                        "description": "The data to insert, as a dictionary",
                    },
                },
                "required": ["table_name", "data"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "select_data_from_table",
            "description": "Select data from a Cassandra table with a limit",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "The name of the table",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of rows to return",
                    },
                },
                "required": ["table_name", "limit"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_schema_from_database",
            "description": "Get the schema from the Cassandra database",
            "parameters": {},
        },
    }
]