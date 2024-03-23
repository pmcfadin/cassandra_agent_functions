from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

class CassandraConnection:
    def __init__(self, hosts=None, port=None, username=None, password=None, keyspace=None, client_id=None, client_secret=None, secure_connect_bundle_path=None):
        self.hosts = hosts
        self.port = port
        self.username = username
        self.password = password
        self.keyspace = keyspace
        self.client_id = client_id
        self.client_secret = client_secret
        self.secure_connect_bundle_path = secure_connect_bundle_path
        self.session = None

    def connect(self):
        """
        Establishes a connection to the Cassandra database.
        """

        if(self.secure_connect_bundle_path is not None):
            self.session = self._connect_to_astra()
        elif self.username and self.password:
            auth_provider = PlainTextAuthProvider(username=self.username, password=self.password)
            cluster = Cluster(self.hosts, port=self.port, auth_provider=auth_provider)
            self.session = cluster.connect(self.keyspace)
        else:
            cluster = Cluster(self.hosts, port=self.port)
            self.session = cluster.connect(self.keyspace)

        return self.session
    
    def _connect_to_astra(self):
        auth_provider = PlainTextAuthProvider(self.client_id, self.client_secret)
        cloud_config= {
                'secure_connect_bundle': self.secure_connect_bundle_path
        }
        
        cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
        session = cluster.connect()

        return session
    
    def disconnect(self):
        """
        Closes the connection to the Cassandra database.
        """
        if self.session:
            self.session.cluster.shutdown()
            self.session.shutdown()
            self.session = None

    def execute(self, query, parameters=None):
        """
        Executes a given CQL query.
        """
        if not self.session:
            raise Exception("Not connected to Cassandra database.")
        return self.session.execute(query, parameters or {})
