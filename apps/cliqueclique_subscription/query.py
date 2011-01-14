import sql

class Context(object):
    def __init__(self, start, joins, end):
        self.start = start
        self.joins = joins
        self.end = end

    def compile(self):
        return sql.Select(
            columns = sql.Column(self.end, '*'),
            froms = sql.Join(*self.joins))

    def __repr__(self):
        return "%s..%s (%s)" % (self.start.get_name(), self.end.get_name(), str(self.joins))

    def __str__(self):
        return str(self.compile())

class AnyContext(Context):
    def __init__(self):
        self.start = self.end = sql.Alias(sql.Table('cliqueclique_subscription_documentsubscription'))
        self.joins = [self.end]

class Query(object):
    def compile(self, context):
        return context

    def __repr__(self):
        return repr(self.compile(AnyContext()))

    def __str__(self):
        return str(self.compile(AnyContext()))

class Pipe(Query):
    def __init__(self, *subs):
        self.subs = subs

    def compile(self, context):
        next_context = context
        for sub in self.subs:
            next_context = sub.compile(next_context)
        return Context(context.start, next_context.joins, context.end)

    def __repr__(self):
        return " ".join(repr(sub) for sub in self.subs)

class Expression(Query):
    def __init__(self, *subs):
        self.subs = subs

    def compile(self, context):
        for sub in self.subs:
            context = sub.compile(context)
        return context

    def __repr__(self):
        return " ".join(repr(sub) for sub in self.subs)

class And(Query):
    def __init__(self, *subs):
        self.subs = subs

    def compile(self, context):
        for sub in self.subs:
            next_context = sub.compile(context)
            context = Context(context.start, next_context.joins, context.end)
        return context

    def __repr__(self):
        return " & ".join(repr(sub) for sub in self.subs)

class Child(Query):
    symbol = '>'
    prev_col = 'from_documentsubscription_id'
    next_col = 'to_documentsubscription_id'

    def compile(self, context):
        join = sql.Alias(sql.Table('cliqueclique_subscription_documentsubscription_parents'))
        next = sql.Alias(sql.Table('cliqueclique_subscription_documentsubscription'))
        joins = [sql.On(join,
                        on=sql.Comp(sql.Column(context.end, 'id'),
                                    sql.Column(join, self.prev_col))),
                 sql.On(next,
                        on=sql.Comp(sql.Column(join, self.next_col),
                                    sql.Column(next, 'id')))]
        return Context(context.start, context.joins + joins, next)

    def __repr__(self):
        return self.symbol

class Parent(Child):
    prev_col = 'to_documentsubscription_id'
    next_col = 'from_documentsubscription_id'

class Owner(Query):
    def __init__(self, owner):
        self.owner = owner

    def compile(self, context):
        sub = sql.Alias(sql.Table('cliqueclique_subscription_documentsubscription'))
        joins = [sql.On(sub,
                        on=sql.And(sql.Comp(sql.Column(context.end, 'id'),
                                            sql.Column(sub, 'id')),
                                   sql.Comp(sql.Column(sub, 'node_id'),
                                            sql.Const(self.owner))))]
        return Context(context.start, context.joins + joins, sub)

    def __repr__(self):
        return ":"

class Parts(Query):
    def compile(self, context):
        part = sql.Alias(sql.Table('cliqueclique_document_documentpart'))
        joins = [sql.On(part,
                        on=sql.And(sql.Comp(sql.Column(context.end, 'document_id'),
                                            sql.Column(part, 'document_id')),
                                   sql.Comp(sql.Column(part, 'parent_id'),
                                            sql.Const(None))))]
        return Context(context.start, context.joins + joins, part)

    def __repr__(self):
        return ":"

class Part(Query):
    def compile(self, context):
        part = sql.Alias(sql.Table('cliqueclique_document_documentpart'))
        joins = [sql.On(part,
                        on=sql.And(sql.Comp(sql.Column(context.end, 'id'),
                                            sql.Column(part, 'parent_id'))))]
        return Context(context.start, context.joins + joins, part)

    def __repr__(self):
        return "::"

class Property(Query):
    def __init__(self, key, value):
        self.key = key
        self.value = value
    
    def compile(self, context):
        prop = sql.Alias(sql.Table('cliqueclique_document_documentproperty'))
        joins = [sql.On(prop,
                        on=sql.And(sql.Comp(sql.Column(context.end, 'id'),
                                            sql.Column(prop, 'part_id')),
                                   sql.Comp(sql.Column(prop, 'key'),
                                            sql.Const(self.key)),
                                   sql.Comp(sql.Column(prop, 'value'),
                                            sql.Const(self.value))))]
        return Context(context.start, context.joins + joins, context.end)


    def __repr__(self):
        return "%s=%s" % (self.key, self.value)
