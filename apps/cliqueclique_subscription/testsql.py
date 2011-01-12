from sql import *

# foo = Alias(Table("foo"))
# fie = Table("fie")
# baz = Alias(Select(
#         columns=List(
#             Column(fie, "bar"),
#         ),
#         froms=List(fie)))

# print Select(
#       columns=List(
#           Column(foo, "bar"),
# 	  Column(foo, "fie"),
# 	  Column(baz, "hehe")
#       ),
#       froms=List(foo, baz),
#       wheres=And(
#           Or(
#               Comp(Column(foo, "hehe"), Const("kafoo"), "="),
#               Comp(Column(foo, "hehe"), Const("kabar"), "=")),
#           Comp(Column(foo, "naja"), Column(baz, "nana"), "="),
#       ))

foo = Table("foo")
bar = Table("bar")

fie = Alias(Select(
        columns=List(
            Column(bar, "bar"),
            ),
        froms=List(bar),
        wheres=And(Comp(Column(bar, "id"), Const(47)),
                   Comp(Column(bar, "xxx"), Const('nana')))
        ))

print Select(
      columns=List(
          Column(foo, "bar"),
      ),
      froms=Join(foo,
                 On(bar,
                    on=And(Comp(Column(foo, "id"), Column(bar, 'foo_id')),
                           Comp(Column(foo, "nana"), Column(bar, 'nana')))),
                 On(fie,
                    on=Comp(Column(bar, "id"), Column(fie, 'bar_id')))),
      wheres=Comp(Column(foo, "hehe"), Const("kafoo"), "=")
      )
