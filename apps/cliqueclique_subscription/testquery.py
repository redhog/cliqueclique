from query import *

print repr(Query('["Follow", ["|", ":", "::", ["&", ["=", "subject", "Root document"], ["=", "foo", "bar"]]]]').compile())
