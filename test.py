from anytree import Node, findall_by_attr
from Participant import Participant
from CustomEnums import PermissionTypesEnum
import math
import json
from collections import namedtuple
participants = []
participants = None
participants = 0

class Test:
    def __init__(self, var):
        self.var = var
        self.dictionary = {"abc": 1, "xyz":2}

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
f.leaves
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

'''res=[x for x in test2.list_var if x.var == "xzy"][0]
print(res.var)
print(math.ceil(math.log2(7) ))'''

print(json.dumps(var2, default=lambda o: o.__dict__))

list = [1,2,3,4]
print(list[1:])

data_sa_json = {
                    'nonce_prefix': 123,
                    'permissions': 123,
                    'pairwise_key': 123,
                    #'ancestor_keys': json.dumps(data_sa.ancestor_keys[1:]),
                    'group_keys': {'publisher_public_key': 123,
                                   'subscriber_public_key': 123,
                                   'publisher_private_key': 123,
                                   'subscriber_private_key': 123}
                    #'rekey_topics': json.dumps(data_sa.rekey_topics_keys),
                    # 'subscriptions': json.dumps(data_sa.subscriptions)
    }
print(json.dumps(data_sa_json))

class a:
    def __init__(self, ab):
        self.ab = ab

class bc(a):
    xzy= None
    def __init__(self, bb):
        self.bb = bb
        bc.xzy = a("abcdfgs")


a = bc("abc")
bc.ab = "asdsad"

print(a.bb)
print(a.ab)
print(bc.xzy.ab)

list_dict = [{"topic_to_sub": "123pub_sub0/3579b257-5fd2-48be-bff5-6e92277adf46__changeParent__0", "enc_key": "7b955c8ae4f835e06ab59463c28d578ee83b4ec8d725fcc7fbebbf31e88cbf79"}, {"topic_to_sub": "123pub_sub0/3579b257-5fd2-48be-bff5-6e92277adf46__changeParent__0", "enc_key": "7b955c8ae4f835e06ab59463c28d578ee83b4ec8d725fcc7fbebbf31e88cbf79"}]

for list in list_dict:
    print(list['topic_to_sub']  )

print(json.loads(b'"38405e86b4770b0758e2ea087935db1d2d7b41e1786bcabf6976a0a2b88ee802"'))
print(list_dict.index({"topic_to_sub": "123pub_sub0/3579b257-5fd2-48be-bff5-6e92277adf46__changeParent__0", "enc_key": "7b955c8ae4f835e06ab59463c28d578ee83b4ec8d725fcc7fbebbf31e88cbf79"}))
text = json.dumps("211adbe701873fb672027db921945ccbbfc8e1fab3b188f8f24c64bb0836b5a6").encode("utf-8", "ignore")
print(json.loads(text.decode("utf-8", "ignore")))
print(bytes.fromhex("5f4c48f1d2b6f8e6f15afe697e1e6e7c56e5e623b54b04ffadf1f8ddba09cc0c"))

string = "abcd"
print(string.encode("utf-8"))

dic1 = {"test": "123",
        "teste2": "345"}
dic2 = {"topic": "xzy"}

dic3 ={"msg": dic1,
       "topic": "xzy"}
print(dic3)

x = "abds"
if not x is  None:
    print("true")

f = Node("f")
b = Node("b", parent=f)
#c = Node("c", parent=b)
#d = Node("d", parent=b)
print(b.root)

