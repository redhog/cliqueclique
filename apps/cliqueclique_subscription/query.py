import sql
import simplejson

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

    def new(self, start = None, joins = [], end = None):
        return Context(start or self.start, self.joins + joins, end or self.end)

class AnyContext(Context):
    def __init__(self):
        self.start = self.end = sql.Alias(sql.Table('cliqueclique_subscription_documentsubscription'))
        self.joins = [self.end]

class Query(object):
    symbol = 'query'
    class __metaclass__(type):
        def __init__(self, *arg, **kw):
            type.__init__(self, *arg, **kw)
            if self.__name__ != 'Query':
                Query.expr_registry[self.symbol] = self
    expr_registry = {}

    def __new__(cls, *arg, **kw):
        if cls is Query:
            return cls._any_from_expr(simplejson.loads(*arg, **kw))
        else:
            return object.__new__(cls)

    @classmethod
    def _from_expr(cls):
        return cls()

    @classmethod
    def _any_from_expr(cls, expr):
        if isinstance(expr, (list, tuple)):
            return cls.expr_registry[expr[0]]._from_expr(expr[1:])
        else:
            return cls.expr_registry[expr]._from_expr()

    def _to_expr(cls):
        return self.symbol

    def compile(self, context = AnyContext()):
        return context

    def __repr__(self):
        return simplejson.dumps(self._to_expr())

    def __str__(self):
        return str(self.compile())

class Pipe(Query):
    symbol = "|"

    def __new__(cls, *subs):
        self = super(Pipe, cls).__new__(cls)
        self.subs = subs
        return self

    @classmethod
    def _from_expr(cls, expr):
        return cls(*[Query._any_from_expr(e) for e in expr])

    def _to_expr(cls):
        return [self.symbol] + [sub._to_expr() for sub in self.subs]

    def compile(self, context = AnyContext()):
        next_context = context
        for sub in self.subs:
            next_context = sub.compile(next_context)
        return next_context.new(start=context.start, end=context.end)

    def __repr__(self):
        return " ".join(repr(sub) for sub in self.subs)

class Follow(Query):
    symbol = "Follow"

    def __new__(cls, *subs):
        self = super(Follow, cls).__new__(cls)
        self.subs = subs
        return self

    @classmethod
    def _from_expr(cls, expr):
        return cls(*[Query._any_from_expr(e) for e in expr])

    def _to_expr(cls):
        return [self.symbol] + [sub._to_expr() for sub in self.subs]

    def compile(self, context = AnyContext()):
        for sub in self.subs:
            context = sub.compile(context)
        return context

    def __repr__(self):
        return " ".join(repr(sub) for sub in self.subs)

class And(Query):
    symbol = "&"

    def __new__(cls, *subs):
        self = super(And, cls).__new__(cls)
        self.subs = subs
        return self

    @classmethod
    def _from_expr(cls, expr):
        return cls(*[Query._any_from_expr(e) for e in expr])

    def _to_expr(cls):
        return [self.symbol] + [sub._to_expr() for sub in self.subs]

    def compile(self, context = AnyContext()):
        for sub in self.subs:
            next_context = sub.compile(context)
            context = next_context.new(start=context.start, end=context.end)
        return context

    def __repr__(self):
        return " & ".join(repr(sub) for sub in self.subs)

class Child(Query):
    symbol = '>'
    prev_col = 'from_documentsubscription_id'
    next_col = 'to_documentsubscription_id'

    def compile(self, context = AnyContext()):
        assert context.end.get_original_name() == 'cliqueclique_subscription_documentsubscription'
        join = sql.Alias(sql.Table('cliqueclique_subscription_documentsubscription_parents'))
        next = sql.Alias(sql.Table('cliqueclique_subscription_documentsubscription'))
        joins = [sql.On(join,
                        on=sql.Comp(sql.Column(context.end, 'id'),
                                    sql.Column(join, self.prev_col))),
                 sql.On(next,
                        on=sql.Comp(sql.Column(join, self.next_col),
                                    sql.Column(next, 'id')))]
        return context.new(joins=joins, end=next)

    def __repr__(self):
        return self.symbol

class Parent(Child):
    prev_col = 'to_documentsubscription_id'
    next_col = 'from_documentsubscription_id'

class Owner(Query):
    symbol = "owner"
    def __new__(cls, owner):
        self = super(Owner, cls).__new__(cls)
        self.owner = owner
        return self

    @classmethod
    def _from_expr(cls, expr):
        return cls(*expr)

    def _to_expr(cls):
        return [self.symbol, self.owner]

    def compile(self, context = AnyContext()):
        assert context.end.get_original_name() == 'cliqueclique_subscription_documentsubscription'
        sub = sql.Alias(sql.Table('cliqueclique_subscription_documentsubscription'))
        joins = [sql.On(sub,
                        on=sql.And(sql.Comp(sql.Column(context.end, 'id'),
                                            sql.Column(sub, 'id')),
                                   sql.Comp(sql.Column(sub, 'node_id'),
                                            sql.Const(self.owner))))]
        return context.start.new(joins=joins, end=sub)

    def __repr__(self):
        return ":"

class Parts(Query):
    symbol = ":"
    def compile(self, context = AnyContext()):
        assert context.end.get_original_name() == 'cliqueclique_subscription_documentsubscription'
        part = sql.Alias(sql.Table('cliqueclique_document_documentpart'))
        joins = [sql.On(part,
                        on=sql.And(sql.Comp(sql.Column(context.end, 'document_id'),
                                            sql.Column(part, 'document_id')),
                                   sql.Comp(sql.Column(part, 'parent_id'),
                                            sql.Const(None))))]
        return context.new(joins=joins, end=part)

    def __repr__(self):
        return ":"

class Part(Query):
    symbol = "::"
    def compile(self, context = AnyContext()):
        assert context.end.get_original_name() == 'cliqueclique_document_documentpart'
        part = sql.Alias(sql.Table('cliqueclique_document_documentpart'))
        joins = [sql.On(part,
                        on=sql.And(sql.Comp(sql.Column(context.end, 'id'),
                                            sql.Column(part, 'parent_id'))))]
        return context.new(joins=joins, end=part)

    def __repr__(self):
        return "::"

class Property(Query):
    symbol="="
    def __new__(cls, key, value):
        self = super(Property, cls).__new__(cls)
        self.key = key
        self.value = value
        return self

    @classmethod
    def _from_expr(cls, expr):
        return cls(*expr)
    
    def _to_expr(cls):
        return [self.symbol, self.key, self.value]

    def compile(self, context = AnyContext()):
        assert context.end.get_original_name() == 'cliqueclique_document_documentpart'
        prop = sql.Alias(sql.Table('cliqueclique_document_documentproperty'))
        joins = [sql.On(prop,
                        on=sql.And(sql.Comp(sql.Column(context.end, 'id'),
                                            sql.Column(prop, 'part_id')),
                                   sql.Comp(sql.Column(prop, 'key'),
                                            sql.Const(self.key)),
                                   sql.Comp(sql.Column(prop, 'value'),
                                            sql.Const(self.value))))]
        return context.new(joins=joins)

    def __repr__(self):
        return "%s=%s" % (self.key, self.value)
