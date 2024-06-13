from neo4j import GraphDatabase

class Neo4j:
    def __init__(self, uri="neo4j://localhost", auth=("neo4j", "password")):
        with GraphDatabase.driver(uri=uri, auth=auth) as driver:
            driver.verify_connectivity()
        
        self.uri=uri
        self.auth = auth
        
        self.driver = GraphDatabase.driver(self.uri, auth=self.auth)
    
    def close(self):
        self.driver.close()