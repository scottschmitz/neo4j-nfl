from neo4j import GraphDatabase

# Define a Neo4j helper class
class Neo4jHelper:
  def __init__(self, uri, user, password):
    self.driver = GraphDatabase.driver(uri, auth=(user, password))

  def close(self):
    """Close the database connection."""
    self.driver.close()

  def run_query(self, query, parameters=None):
    """Execute a Cypher query and return results."""
    with self.driver.session() as session:
      return session.run(query, parameters or {})
