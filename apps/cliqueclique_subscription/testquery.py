from query import *

query = Query('["Follow", ["|", ":", "::", ["&", ["=", "subject", "Root document"], ["=", "foo", "bar"]]]]')
context = query.compile()
statement = context.compile()
sql = statement.compile()
print "SQL:", sql.sql
print "VARS:", sql.vars
