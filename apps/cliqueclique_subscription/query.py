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
            if isinstance(expr[0], (list, tuple)):
                return cls.expr_registry["&"]._from_expr(expr)
            else:
                return cls.expr_registry[expr[0]]._from_expr(expr[1:])
        else:
            return cls.expr_registry[expr]._from_expr()

    def _to_expr(self):
        return self.symbol

    def _compile(self, context):
        return context

    def compile(self):
        return self._compile(AnyContext()).compile()

    def __repr__(self):
        return simplejson.dumps(self._to_expr())

    def __str__(self):
        return simplejson.dumps(self._to_expr())

class Pipe(Query):
    symbol = "|"

    def __new__(cls, *subs):
        self = super(Pipe, cls).__new__(cls)
        self.subs = subs
        return self

    @classmethod
    def _from_expr(cls, expr):
        return cls(*[Query._any_from_expr(e) for e in expr])

    def _to_expr(self):
        return [self.symbol] + [sub._to_expr() for sub in self.subs]

    def _compile(self, context):
        for sub in self.subs:
            context = sub._compile(context)
        return context

class And(Query):
    symbol = "&"

    def __new__(cls, *subs):
        self = super(And, cls).__new__(cls)
        self.subs = subs
        return self

    @classmethod
    def _from_expr(cls, expr):
        return cls(*[Query._any_from_expr(e) for e in expr])

    def _to_expr(self):
        res = [sub._to_expr() for sub in self.subs]
        if isinstance(res[0], (str, unicode)):
            res = [self.symbol] + res
        return res

    def _compile(self, context):
        for sub in self.subs:
            next_context = sub._compile(context)
            context = next_context.new(start=context.start, end=context.end)
        return context

class Child(Query):
    symbol = '>'
    prev_col = 'from_documentsubscription_id'
    next_col = 'to_documentsubscription_id'

    def _compile(self, context):
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

    def _to_expr(self):
        return [self.symbol, self.owner]

    def _compile(self, context):
        assert context.end.get_original_name() == 'cliqueclique_subscription_documentsubscription'
        sub = sql.Alias(sql.Table('cliqueclique_subscription_documentsubscription'))
        joins = [sql.On(sub,
                        on=sql.And(sql.Comp(sql.Column(context.end, 'id'),
                                            sql.Column(sub, 'id')),
                                   sql.Comp(sql.Column(sub, 'node_id'),
                                            sql.Const(self.owner))))]
        return context.start.new(joins=joins, end=sub)

class Id(Query):
    symbol = "id"
    def __new__(cls, id):
        self = super(Id, cls).__new__(cls)
        self.id = id
        return self

    @classmethod
    def _from_expr(cls, expr):
        return cls(*expr)

    def _to_expr(self):
        return [self.symbol, self.id]

    def _compile(self, context):
        assert context.end.get_original_name() == 'cliqueclique_subscription_documentsubscription'
        sub = sql.Alias(sql.Table('cliqueclique_subscription_documentsubscription'))
        joins = [sql.On(sub,
                        on=sql.And(sql.Comp(sql.Column(context.end, 'id'),
                                            sql.Column(sub, 'id')),
                                   sql.Comp(sql.Column(sub, 'document_id'),
                                            sql.Const(self.id))))]
        return context.start.new(joins=joins, end=sub)

class Parts(Query):
    symbol = ":"
    def _compile(self, context):
        assert context.end.get_original_name() == 'cliqueclique_subscription_documentsubscription'
        part = sql.Alias(sql.Table('cliqueclique_document_documentpart'))
        joins = [sql.On(part,
                        on=sql.And(sql.Comp(sql.Column(context.end, 'document_id'),
                                            sql.Column(part, 'document_id')),
                                   sql.Comp(sql.Column(part, 'parent_id'),
                                            sql.Const(None),
                                            'is')))]
        return context.new(joins=joins, end=part)

    def __repr__(self):
        return ":"

class Part(Query):
    symbol = "::"
    def _compile(self, context):
        assert context.end.get_original_name() == 'cliqueclique_document_documentpart'
        part = sql.Alias(sql.Table('cliqueclique_document_documentpart'))
        joins = [sql.On(part,
                        on=sql.And(sql.Comp(sql.Column(context.end, 'id'),
                                            sql.Column(part, 'parent_id'))))]
        return context.new(joins=joins, end=part)

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
    
    def _to_expr(self):
        return [self.symbol, self.key, self.value]

    def _compile(self, context):
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
