import sql
import simplejson

PartTable = sql.Table('cliqueclique_document_documentpart')
SubscriptionTable = sql.Table('cliqueclique_subscription_documentsubscription')
ParentsTable = sql.Table('cliqueclique_subscription_documentsubscription_parents')
NodeTable = sql.Table('cliqueclique_node_localnode')
DocumentTable = sql.Table('cliqueclique_document_document')
PropertyTable = sql.Table('cliqueclique_document_documentproperty')

class Context(object):
    def __init__(self, start, joins, end, wheres = []):
        self.start = start
        self.joins = joins
        self.end = end
        self.wheres = wheres

    def compile(self, id_only = False):
        return sql.Select(
            columns = sql.Column(self.end, ['*', 'id'][id_only]),
            froms = sql.Join(*self.joins),
            wheres = self.wheres and sql.And(*self.wheres) or None)

    def __repr__(self):
        return "%s..%s (%s)" % (self.start.get_name(), self.end.get_name(), str(self.joins))

    def __str__(self):
        return str(self.compile())

    def new(self, start = None, joins = [], end = None, wheres = []):
        return Context(start or self.start, self.joins + joins, end or self.end, self.wheres + wheres)

    def assert_start(self, name):
        if self.start.get_original_name() != name:
            raise AssertionError("Context expected to start with %s but it starts with %s" % (name, self.start.get_original_name()))

    def assert_end(self, name):
        if self.end.get_original_name() != name:
            raise AssertionError("Context expected to end in %s but it ends in %s" % (name, self.end.get_original_name()))

class AnyContext(Context):
    def __init__(self):
        tbl = sql.Alias(SubscriptionTable)
        Context.__init__(self, tbl, [tbl], tbl)

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
        subselects = []
        for sub in self.subs:
            new_start = sql.Alias(context.end)
            new_start_context = Context(new_start, [new_start], new_start)
            subselects.append(sub._compile(new_start_context).new(wheres = [sql.Comp(sql.Column(context.end, 'id'),
                                                                                     sql.Column(new_start, 'id'))]))

        end = None
        for subselect in subselects:
            if end:
                subselect.assert_end(end.get_original_name())
            else:
                end = subselect.end
        
        end = sql.Alias(end)

        return context.new(joins=[sql.On(end,
                                         on = sql.Or(*[sql.Comp(sql.Column(end, 'id'),
                                                                subselect.compile(id_only=True),
                                                                'in')
                                                       for subselect in subselects]))],
                           end = end)

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
        return context.new(joins=joins)

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
        document = sql.Alias(DocumentTable)
        joins = [sql.On(document,
                        on=sql.And(sql.Comp(sql.Column(context.end, 'document_id'),
                                            sql.Column(document, 'id')),
                                   sql.Comp(sql.Column(document, 'document_id'),
                                            sql.Const(self.id))))]
        return context.new(joins=joins)

class IsRead(Query):
    symbol = "read"
    def _compile(self, context):
        context.assert_end('cliqueclique_subscription_documentsubscription')
        return context.new(wheres = [sql.Column(context.end, 'read')])

class IsBookmarked(Query):
    symbol = "bookmarked"
    def _compile(self, context):
        context.assert_end('cliqueclique_subscription_documentsubscription')
        return context.new(wheres = [sql.Column(context.end, 'bookmarked')])

class IsSubscribed(Query):
    symbol = "subscribed"
    def _compile(self, context):
        context.assert_end('cliqueclique_subscription_documentsubscription')
        return context.new(wheres = [sql.Column(context.end, 'local_is_subscribed')])

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

class ChildLink(ListQuery):
    symbol = "->"

    def _compile(self, context):
        context.assert_end('cliqueclique_subscription_documentsubscription')

        # Parts structure:
        # Signed->Multipart->Content

        return OrPipe(
            Pipe(And(Pipe(Parts(), Part(), Part(), Property("part_type", "child_link"), Property("link_direction", "natural"), *self.subs)), Child()),
            Pipe(And(Pipe(Parts(), Part(), Part(), Property("part_type", "parent_link"), Property("link_direction", "reversed"), *self.subs)), Child()),

            Pipe(Child(), And(Pipe(Parts(), Part(), Part(), Property("part_type", "parent_link"), Property("link_direction", "natural"), *self.subs))),
            Pipe(Child(), And(Pipe(Parts(), Part(), Part(), Property("part_type", "child_link"), Property("link_direction", "reversed"), *self.subs))),

            Pipe(Child(), And(Pipe(Parts(), Part(), Part(), Property("part_type", "link"), Property("link_direction", "natural"), *self.subs)), Child()),
            Pipe(Parent(), And(Pipe(Parts(), Part(), Part(), Property("part_type", "link"), Property("link_direction", "reversed"), *self.subs)), Parent())
            )._compile(context)

class ParentLink(ListQuery):
    symbol = "<-"

    def _compile(self, context):
        context.assert_end('cliqueclique_subscription_documentsubscription')

        # Parts structure:
        # Signed->Multipart->Content

        return OrPipe(
            Pipe(And(Pipe(Parts(), Part(), Part(), Property("part_type", "child_link"), Property("link_direction", "reversed"), *self.subs)), Parent()),
            Pipe(And(Pipe(Parts(), Part(), Part(), Property("part_type", "parent_link"), Property("link_direction", "natural"), *self.subs)), Parent()),

            Pipe(Parent(), And(Pipe(Parts(), Part(), Part(), Property("part_type", "parent_link"), Property("link_direction", "reversed"), *self.subs))),
            Pipe(Parent(), And(Pipe(Parts(), Part(), Part(), Property("part_type", "child_link"), Property("link_direction", "natural"), *self.subs))),

            Pipe(Child(), And(Pipe(Parts(), Part(), Part(), Property("part_type", "link"), Property("link_direction", "reversed"), *self.subs)), Child()),
            Pipe(Parent(), And(Pipe(Parts(), Part(), Part(), Property("part_type", "link"), Property("link_direction", "natural"), *self.subs)), Parent())
            )._compile(context)
