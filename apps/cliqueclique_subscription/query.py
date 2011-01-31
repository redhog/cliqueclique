import sql
import simplejson

PartTable = sql.Table('cliqueclique_document_documentpart')
SubscriptionTable = sql.Table('cliqueclique_subscription_documentsubscription')
ParentsTable = sql.Table('cliqueclique_subscription_documentsubscription_parents')
NodeTable = sql.Table('cliqueclique_node_localnode')
DocumentTable = sql.Table('cliqueclique_document_document')
PropertyTable = sql.Table('cliqueclique_document_documentproperty')

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

    def assert_start(self, name):
        if self.start.get_original_name() != name:
            raise AssertionError("Context expected to start with %s but it starts with %s" % (name, self.start.get_original_name()))

    def assert_end(self, name):
        if self.end.get_original_name() != name:
            raise AssertionError("Context expected to end in %s but it ends in %s" % (name, self.end.get_original_name()))

class AnyContext(Context):
    def __init__(self):
        self.start = self.end = sql.Alias(SubscriptionTable)
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
    def _from_expr(cls, expr):
        assert len(expr) == 0
        return cls()

    @classmethod
    def _any_from_expr(cls, expr):
        if isinstance(expr, (list, tuple)):
            if not expr or isinstance(expr[0], (list, tuple)):
                return cls.expr_registry["&"]._from_expr(expr)
            else:
                return cls.expr_registry[expr[0]]._from_expr(expr[1:])
        else:
            return cls.expr_registry[expr]._from_expr([])

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

class ListQuery(Query):
    def __new__(cls, *subs):
        self = super(ListQuery, cls).__new__(cls)
        self.subs = subs
        return self

    @classmethod
    def _from_expr(cls, expr):
        return cls(*[Query._any_from_expr(e) for e in expr])

    def _to_expr(self):
        return [self.symbol] + [sub._to_expr() for sub in self.subs]

class Pipe(ListQuery):
    symbol = "/"

    def _compile(self, context):
        for sub in self.subs:
            context = sub._compile(context)
        return context

class And(ListQuery):
    symbol = "&"

    def _to_expr(self):
        res = [sub._to_expr() for sub in self.subs]
        if res and isinstance(res[0], (str, unicode)):
            res = [self.symbol] + res
        return res

    def _compile(self, context):
        for sub in self.subs:
            next_context = sub._compile(context)
            context = next_context.new(start=context.start, end=context.end)
        return context

class OrPipe(ListQuery):
    symbol = "|/"

    def _compile(self, context):
        ends = []
        starts = []
        for sub in self.subs:
            new_start = sql.Alias(context.end)
            new_context = sub._compile(context.new(joins=[new_start], end = new_start))
            context = new_context.new(start=context.start, end=context.end)
            if new_context.end is not new_start:
                starts.append(new_start)
                ends.append(new_context.end)

        old_start = context.end
        new_end = sql.Alias(ends[0])

        start_ors = [sql.Comp(sql.Column(old_start, 'id'),
                              sql.Column(start, 'id'))
                     for start in starts]
        if ends:
            for end in ends[1:]:
                if ends[0].get_original_name() != end.get_original_name():
                    raise AssertionError("OrPipe arguments must all end in the same table (%s != %s)" % (ends[0].get_original_name(), end.get_original_name()))
        end_ors = [sql.Comp(sql.Column(new_end, 'id'),
                            sql.Column(end, 'id'))
                   for end in ends]
        joins = [sql.On(new_end, sql.And(sql.Or(*start_ors), sql.Or(*end_ors)))]
        return context.new(joins = joins, end=new_end)

class Or(OrPipe):
    symbol = "|"
    def _compile(self, context):
        new_context = OrPipe._compile(self, context)
        return new_context.new(end = context.end)

class Child(Query):
    symbol = '>'
    prev_col = 'to_documentsubscription_id'
    next_col = 'from_documentsubscription_id'

    def _compile(self, context):
        context.assert_end('cliqueclique_subscription_documentsubscription')
        join = sql.Alias(ParentsTable)
        next = sql.Alias(SubscriptionTable)
        joins = [sql.On(join,
                        on=sql.Comp(sql.Column(context.end, 'id'),
                                    sql.Column(join, self.prev_col))),
                 sql.On(next,
                        on=sql.Comp(sql.Column(join, self.next_col),
                                    sql.Column(next, 'id')))]
        return context.new(joins=joins, end=next)

class Parent(Child):
    symbol = '<'
    prev_col = 'from_documentsubscription_id'
    next_col = 'to_documentsubscription_id'

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
        context.assert_end('cliqueclique_subscription_documentsubscription')
        node = sql.Alias(NodeTable)
        joins = [sql.On(node,
                        on=sql.And(sql.Comp(sql.Column(context.end, 'node_id'),
                                            sql.Column(node, 'id')),
                                   sql.Comp(sql.Column(node, 'node_id'),
                                            sql.Const(self.owner))))]
        return context.new(joins=joins, end=node)

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
        context.assert_end('cliqueclique_subscription_documentsubscription')
        doc = sql.Alias(DocumentTable)
        joins = [sql.On(doc,
                        on=sql.And(sql.Comp(sql.Column(context.end, 'document_id'),
                                            sql.Column(doc, 'id')),
                                   sql.Comp(sql.Column(doc, 'document_id'),
                                            sql.Const(self.id))))]
        return context.new(joins=joins, end=doc)

class Parts(Query):
    symbol = ":"
    def _compile(self, context):
        context.assert_end('cliqueclique_subscription_documentsubscription')
        part = sql.Alias(PartTable)
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
        context.assert_end('cliqueclique_document_documentpart')
        part = sql.Alias(PartTable)
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
        context.assert_end('cliqueclique_document_documentpart')
        prop = sql.Alias(PropertyTable)
        joins = [sql.On(prop,
                        on=sql.And(sql.Comp(sql.Column(context.end, 'id'),
                                            sql.Column(prop, 'part_id')),
                                   sql.Comp(sql.Column(prop, 'key'),
                                            sql.Const(self.key)),
                                   sql.Comp(sql.Column(prop, 'value'),
                                            sql.Const(self.value))))]
        return context.new(joins=joins)

class Link(ListQuery):
    symbol = "->"

    def _compile(self, context):
        context.assert_end('cliqueclique_subscription_documentsubscription')

        # Parts structure:
        # Signed->Multipart->Content

        return OrPipe(
            Pipe(Child(), And(Pipe(Parts(), Part(), Part(), Property("part_type", "parent_link"), Property("link_direction", "natural"), *self.subs))),
            Pipe(Child(), And(Pipe(Parts(), Part(), Part(), Property("part_type", "child_link"), Property("link_direction", "reversed"), *self.subs))),

            #Pipe(Child(), And(Pipe(Parts(), Part(), Part(), Property("part_type", "link"), Property("link_direction", "natural"), *self.subs)), Child()),
            #Pipe(Parent(), And(Pipe(Parts(), Part(), Part(), Property("part_type", "link"), Property("link_direction", "reversed"), *self.subs)), Parent())
            )._compile(context)

    def __repr__(self):
        return ":"
