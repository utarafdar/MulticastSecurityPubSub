from Server.Authorization.Authorization import Authorization
from Server.CustomClasses.Topic import Topic


class Initializer:
    @staticmethod
    def initialize_groups():
        topic = Topic("test")
        topic2 = Topic("test")
        group = Authorization.create_group("testGroup", "123", type_of_key_management_protocol=2, type_of_pub_sub_group=4)
        print(group)
        group.add_topic(topic)
        group.add_topic(topic2)
        while True:
            pass