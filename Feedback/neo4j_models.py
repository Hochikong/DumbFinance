# __author__ = 'Hochikong'
QUERY_FOR_FRIENDS = "MATCH (n1:Person)-[f:Friend]->(n2:Person) RETURN n1,f,n2"
