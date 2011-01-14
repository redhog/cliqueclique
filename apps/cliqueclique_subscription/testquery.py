from query import *
#print Expression(And(Pipe(Parts(), Part(), Property("subject", "Root document")),
#                     Owner(4711)))
print Expression(Pipe(Parts(), Part(), And(Property("subject", "Root document"), Property("foo", "bar"))))
