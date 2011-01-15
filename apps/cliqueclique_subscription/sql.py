class CompiledStatement(object):
    def __init__(self, sql, vars):
        self.sql = sql
        self.vars = vars

    def __repr__(self):
        return "%s %% %s" % (repr(self.sql), repr(self.vars))

    def __str__(self):
        return self.sql % tuple("'%s'" % (var,) for var in self.vars)


def sql_from_compiled_statements(stmtdict):
    return dict((name, stmt.sql)
                for name, stmt
                in stmtdict.iteritems())

def vars_from_compiled_statements(stmtdict):
    return dict((name, stmt.vars)
                for name, stmt
                in stmtdict.iteritems())

def join_vars(partlist, vardict):
    res = []
    for name in partlist:
        if name in vardict:
            res.extend(vardict[name])
    return res



class Statement(object):
    def __init__(self, **parts):
        self.parts = parts

    def compile_parts(self, ind, tab, ln):
        return dict((name, part.compile(ind+tab, tab, ln))
                    for name, part
                    in self.parts.iteritems()
                    if part is not None)

    def compile(self, ind='', tab='  ', ln='\n'):
        raise NotImplementedError

    def __repr__(self):
        return repr(self.compile('', '  ', '\n'))

    def __str__(self):
        return str(self.compile('', '  ', '\n'))

class List(Statement):
    ln = False
    sep = ", "
    def __init__(self, *parts):
        self.parts = parts

    def compile_parts(self, ind, tab, ln):
        return [part.compile(ind+tab, tab, ln)
                for part
                in self.parts]

    def compile(self, ind='', tab='  ', ln='\n'):
        vars = []
        sqls = []
        for part in self.parts:
            compiled_part = part.compile(ind, tab, ln)
            template = "%s"
            if isinstance(part, List):
                template = "(%s)"
            sqls.append(template % (compiled_part.sql,))
            vars.extend(compiled_part.vars)
        sep = self.sep
        if self.ln:
            sep = ln+ind+sep
        return CompiledStatement(sep.join(sqls), vars)

    def __str__(self):
        return self.compile()

class And(List):
    sep = " and "

class Or(List):
    sep = " or "

class Join(List):
    sep = "join "
    ln = True

class OuterJoin(Join):
    sep = "left outer join "

class On(Statement):
    def __init__(self, table, on=None):
        Statement.__init__(self, table=table, on=on)

    def compile(self, ind='', tab='  ', ln='\n'):
        parts = self.compile_parts(ind, tab, ln)
        return CompiledStatement(
            ("%(table)s on %(on)s") % sql_from_compiled_statements(parts),
            join_vars(['table', 'on'], vars_from_compiled_statements(parts)))

class Select(Statement):
    def __init__(self, columns, froms=None, wheres=None):
        Statement.__init__(self, columns=columns, froms=froms, wheres=wheres)

    def compile(self, ind='', tab='  ', ln='\n'):
        parts = self.compile_parts(ind, tab, ln)
        template = ln+ind+"select %(columns)s"
        if 'froms' in parts:
            template += ln+ind+"from %(froms)s"
        if 'wheres' in parts:
            template += ln+ind+"where %(wheres)s"
        return CompiledStatement(
            template % sql_from_compiled_statements(parts),
            join_vars(['columns', 'froms', 'wheres'], vars_from_compiled_statements(parts)))

class Table(Statement):
    def __init__(self, name):
        Statement.__init__(self)
        self.name = name

    def get_original_name(self):
        return self.name

    def get_name(self):
        return self.name

    def compile(self, ind, tab, l):
        return CompiledStatement(self.name, [])

class Column(Statement):
    def __init__(self, table, name):
        Statement.__init__(self)
        self.table = table
        self.name = name

    def get_name(self):
        return "%(table)s.%(name)s" % {
            'table': self.table.get_name(),
            'name': self.name}

    def compile(self, ind='', tab='  ', ln='\n'):        
        return CompiledStatement(self.get_name(), [])

class Alias(Statement):
    def __init__(self, primary):
        Statement.__init__(self, primary=primary)

    def get_original_name(self):
        return self.parts['primary'].get_original_name()

    def get_name(self):
        return 'a%s' % (id(self),)

    def compile(self, ind, tab, l):
        parts = self.compile_parts(ind, tab, l)
        sql = sql_from_compiled_statements(parts)
        sql['name'] = self.get_name()

        template = "%(primary)s as %(name)s"
        if isinstance(self.parts['primary'], Select):
            template = "(%(primary)s) as %(name)s"

        return CompiledStatement(
            template % sql,
            join_vars(['primary'], vars_from_compiled_statements(parts)))

class Const(Statement):
    def __init__(self, value):
        Statement.__init__(self)
        self.value = value

    def compile(self, ind, tab, l):
        if self.value is None:
            return CompiledStatement("null", [])
        elif self.value is True: 
            return CompiledStatement("true", [])
        elif self.value is False:
            return CompiledStatement("false", [])
        else:
            return CompiledStatement("%s", [self.value])

class Comp(Statement):
    def __init__(self, val1, val2, comp='='):
        Statement.__init__(self, val1=val1, val2=val2)
        self.comp = comp

    def compile(self, ind='', tab='  ', ln='\n'):
        parts = self.compile_parts(ind, tab, ln)
        sql = sql_from_compiled_statements(parts)
        sql['comp'] = self.comp
        return CompiledStatement(
            ln+ind+"%(val1)s %(comp)s %(val2)s" % sql,
            join_vars(['val1', 'val2'], vars_from_compiled_statements(parts)))
