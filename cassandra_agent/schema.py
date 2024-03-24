from pydantic.v1 import BaseModel, Field
from cassandra.cluster import Session
from langchain.tools import BaseTool, StructuredTool, tool
import json

class GetCassandraSchema(BaseModel):
    keyspace_name: str = Field(..., title="The keyspace to query")

class CassandraSchemaTool():
    
    def __init__(self, session: Session):

        self.session = session

    # def _get_session(self):
    #     load_dotenv()

    #     client_id = os.environ["ASTRA_CLIENT_ID"]
    #     client_secret = os.environ["ASTRA_CLIENT_SECRET"]
    #     secure_connect_bundle_path = os.environ["SECURE_CONNECT_BUNDLE_PATH"]

    #     session = CassandraConnection(    client_id=client_id,
    #         client_secret=client_secret,
    #         secure_connect_bundle_path=secure_connect_bundle_path,)
        
    #     return session.connect()

    def get_schema(self, keyspace_name: str) -> dict:
        """
        Get the schema of a keyspace in Cassandra.

        :param keyspace_name: The name of the keyspace.
        """
        schema = []
        try:
            keyspace_dict = {'keyspace': keyspace_name, 'tables': []}

            tables = self.session.execute(f"SELECT table_name FROM system_schema.tables WHERE keyspace_name = '{keyspace_name}';")

            for table_row in tables:
                table_name = table_row.table_name
                table_info = {'table_name': table_name, 'columns': [], 'indexes': []}

                # Fetch columns
                columns = self.session.execute(f"SELECT column_name, type FROM system_schema.columns WHERE keyspace_name = '{keyspace_name}' AND table_name = '{table_name}';")
                for column_row in columns:
                    table_info['columns'].append({'column_name': column_row.column_name, 'type': column_row.type})

                # Fetch indexes
                indexes = self.session.execute(f"SELECT index_name, kind FROM system_schema.indexes WHERE keyspace_name = '{keyspace_name}' AND table_name = '{table_name}';")
                for index_row in indexes:
                    table_info['indexes'].append({'index_name': index_row.index_name, 'type': index_row.kind})

                keyspace_dict['tables'].append(table_info)

                schema.append(keyspace_dict)

            return json.dumps(schema, indent=4)

        except Exception as e:
            print(f"Failed to get schema: {e}")

    def create_table(self, create_table_statement: str):
        """
        Create a table in Cassandra.

        :param create_table_statement: The CQL statement to create a table.
        """
        try:
            self.session.execute(create_table_statement)
            print("Table created successfully.")
        except Exception as e:
            print(f"Failed to create table: {e}")
