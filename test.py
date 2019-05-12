from anytree import Node, findall_by_attr
participants = []
participants = None
participants = 0

print (participants)

f = Node("f")
b = Node("b", parent=f)
c = Node("c", parent=b)
d = Node("d", parent=b)
e = Node("e", parent=f)
h = Node("h", parent=e)
g = Node("g", parent=e)

print(f.height)

res=findall_by_attr(f, "b")
res1 = res[0]
b.name = "z"
print (b.name)