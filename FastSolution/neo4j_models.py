# __author__ = 'Hochikong'
# Test Models
QUERY_FOR_FRIENDS = "MATCH (n1:Person)-[f:Friend]->(n2:Person) RETURN n1,f,n2"

# Fix Models
# Example:CREATE (:STOCK {Company:'京东方',StockNumber:'000725',BasicInfo:'xxx'})
CREATE_CORE_NODE = "CREATE (:STOCK {Company:{%s},StockNumber:{%s},BasicInfo:{%s}})"

# Example:MATCH (s:STOCK) WHERE s.StockNumber = '000725' CREATE (n:Related {Company:'某公司'})-[r:竞争对手]->(s)
CREATE_BASIC_STRUCTURE_FROM = "MATCH (s:STOCK) WHERE s.StockNumber = {%s} " \
                      "CREATE (n:Related {Company:{%s}})-[r:%s]->(s)"

# Example:MATCH (s:STOCK) WHERE s.StockNumber = '000725' CREATE (s)-[r:供应商]->(n:Related {Company:'某公司'})
CREATE_BASIC_STRUCTURE_TO = "MATCH (s:STOCK) WHERE s.StockNumber = {%s} " \
                      "CREATE (s)-[r:%s]->(n:Related {Company:{%s}})"

# Example:MATCH (s:STOCK) WHERE s.StockNumber = '000725' CREATE (n:EVENT {TEXT:'内容',KEYWORD:['关键词','实体']})-[f:利好]->(s)
CREATE_FACTOR = "MATCH (s:STOCK) WHERE s.StockNumber = {%s} " \
                "CREATE (n:EVENT {TEXT:{%s},KEYWORD:[{%s},{%s}]})-[f:%s]->(s)"

# Example:MATCH (s:STOCK) WHERE s.StockNumber = '000725' CREATE (:TIME {TIME:'2017-06-15,01:41'})-[t:时间]->(s)
CREATE_TIME = "MATCH (s:STOCK) WHERE s.StockNumber = {%s} CREATE (:TIME {TIME:{%s}})-[t:%s]->(s)"

# Example:MATCH (n)-[f:利好]->(s:STOCK {StockNumber:'000725'})<-[t:时间]-(tn) RETURN n,f,s,t,tn
QUERY_FOR_FACTORS = "MATCH (n)-[f:%s]->(s:STOCK {StockNumber:'xxx'})<-[t:%s]-(tn) RETURN n,f,s,t,tn"

# Example:MATCH (n)-[r:竞争对手]->(s:STOCK {StockNumber:'000725'}) RETURN n,r,s
QUERY_FOR_TYPE_STRUCTURE = "MATCH (n)-[r:%]->(s:STOCK {StockNumber:'xxx'}) RETURN n,r,s"

# Example:MATCH (n)-[r]->(s:STOCK {StockNumber:'000725'})-[rx]->(nx) RETURN n,r,s,rx,nx
QUERY_FOR_STRUCTURE = "MATCH (n)-[r]->(s:STOCK {StockNumber:'xxx'})-[rx]->(nx) RETURN n,r,s,rx,nx"

