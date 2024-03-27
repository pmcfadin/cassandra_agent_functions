"""Tools for interacting with an Apache Cassandra database."""

QUERY_CHECKER = """
{query}
Double check the CQL query above for common mistakes, including:
- Using incorrect keyspace or table names
- Using incorrect data types in the query
- Using the wrong column names
- Improper use of CQL statements like SELECT, INSERT, UPDATE, DELETE
- Incorrect use of filtering and ordering

If there are any of the above mistakes, rewrite the query. If there are no mistakes, just reproduce the original query.

Output the final CQL query only.

CQL Query: """
