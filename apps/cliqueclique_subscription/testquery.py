from query import *
s = '["Follow", ["|", ":", "::", ["&", ["=", "subject", "Root document"], ["=", "foo", "bar"]]]]'
print s
query = Query(s)
print repr(query)
assert s == repr(query)
statement = query.compile()
sql = statement.compile()
print "SQL:", sql.sql
print "VARS:", sql.vars
