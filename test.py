from anytree import Node, findall_by_attr
from Participant import Participant
from CustomEnums import PermissionTypesEnum
participants = []
participants = None
participants = 0

class Test:
    def __init__(self, var):
        self.var = var

class test2:
    list_var = list()

print (participants)

f = Node("f")
b = Node("b", parent=f)
c = Node("c", parent=b)
d = Node("d", parent=b)
e = Node("e", parent=f)
h = Node("h", parent=e)
g = Node("g", parent=e)

#print(f.height)

res=findall_by_attr(f, "b")
res1 = res[0]
b.name = "z"
#print (b.name)

participant4 = Participant("12345", "004")
participant5 = Participant("12345", "004")

part_perm = dict()
part_perm[participant4] = PermissionTypesEnum.PUBLISH.value
part_perm[participant5] = PermissionTypesEnum.PUBLISH_AND_SUBSCRIBE.value

del part_perm[participant5]

for part_perm_key, part_perm_value in part_perm.items():
    print(part_perm_key.pairwise_key)
    print(part_perm_key.participant_id)
    print(part_perm_value)

var2 = Test("test")
print(var2.var)

test2.list_var.append(var2)

var3 = test2.list_var[0]
var3.var ="xzy"

print(test2.list_var[0].var)

res=[x for x in test2.list_var if x.var == "xzy"][0]
print(res.var)