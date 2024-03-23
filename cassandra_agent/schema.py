from cassandra.cluster import Session

class CassandraSchema:
    def __init__(self, session: Session):
        self.session = session

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
