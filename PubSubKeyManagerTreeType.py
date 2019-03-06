from TreeNode import TreeNode, LeafNode
from Participant import Participant
from anytree import Node, findall_by_attr, PreOrderIter
from Topic import Topic
from CustomEnums import PermissionTypesEnum, TypeOfPubSubGroupEnum
from PublishSubscribeTreeKeys import PublishSubscribeTreeKeys
from LKH_Protocol import LKH


def generate_key():
    return 10


class KeyManager:

    @staticmethod
    def setup_topic_trees(topic, participants_permissions=None):
        # check for type of publish subscribe group  and proceed further
        if topic.type_of_pub_sub_group == TypeOfPubSubGroupEnum.ALL_PUBSUB.value:
            # call functions here
            # set publisher, subscriber and common trees based on the group
            KeyManager.__setup_pub_sub_group_trees(topic, participants_permissions, common_tree=True,
                                                   pub_tree=False, sub_tree=False, pub_sub_tree=False)

        elif topic.type_of_pub_sub_group == TypeOfPubSubGroupEnum.SOME_PUBSUB_SOME_PUB.value:
            pub_tree_keys = PublishSubscribeTreeKeys(common_key=True, publisher_public_key=False,
                                                     publisher_private_key=False, subscriber_public_key=True,
                                                     subscriber_private_key=False)
            pub_sub_tree_keys = PublishSubscribeTreeKeys(common_key=True, publisher_public_key=False,
                                                         publisher_private_key=False, subscriber_public_key=True,
                                                         subscriber_private_key=True)
            KeyManager.__setup_pub_sub_group_trees(topic, participants_permissions, common_tree=False,
                                                   pub_tree=True, sub_tree=False, pub_sub_tree=True, pub_tree_keys=pub_tree_keys,
                                                   pub_sub_tree_keys=pub_sub_tree_keys)

        elif topic.type_of_pub_sub_group == TypeOfPubSubGroupEnum.SOME_PUBSUB_SOME_SUB.value:
            pub_sub_tree_keys = PublishSubscribeTreeKeys(common_key=True, publisher_public_key=True,
                                                         publisher_private_key=True, subscriber_public_key=False,
                                                         subscriber_private_key=False)
            sub_tree_keys = PublishSubscribeTreeKeys(common_key=True, publisher_public_key=True,
                                                     publisher_private_key=False, subscriber_public_key=False,
                                                     subscriber_private_key=False)
            KeyManager.__setup_pub_sub_group_trees(topic, participants_permissions, common_tree=False, pub_tree=False,
                                                   sub_tree=True, pub_sub_tree=True, pub_sub_tree_keys=pub_sub_tree_keys,
                                                   sub_tree_keys=sub_tree_keys)

        elif topic.type_of_pub_sub_group == TypeOfPubSubGroupEnum.SOME_PUB_SOME_SUB.value:
            pub_tree_keys = PublishSubscribeTreeKeys(common_key=False, publisher_public_key=True,
                                                     publisher_private_key=True, subscriber_public_key=True,
                                                     subscriber_private_key=False)
            sub_tree_keys = PublishSubscribeTreeKeys(common_key=False, publisher_public_key=True,
                                                     publisher_private_key=False, subscriber_public_key=True,
                                                     subscriber_private_key=True)
            KeyManager.__setup_pub_sub_group_trees(topic, participants_permissions, common_tree=False, pub_tree=True,
                                                   sub_tree=True, pub_tree_keys=pub_tree_keys, pub_sub_tree=False,
                                                   sub_tree_keys=sub_tree_keys)

        elif topic.type_of_pub_sub_group == TypeOfPubSubGroupEnum.SOME_PUBSUB_SOME_PUB_SOME_SUB.value:
            pub_tree_keys = PublishSubscribeTreeKeys(common_key=False, publisher_public_key=True,
                                                     publisher_private_key=True, subscriber_public_key=True,
                                                     subscriber_private_key=False)
            sub_tree_keys = PublishSubscribeTreeKeys(common_key=False, publisher_public_key=True,
                                                     publisher_private_key=False, subscriber_public_key=True,
                                                     subscriber_private_key=True)
            pub_sub_tree_keys = PublishSubscribeTreeKeys(common_key=False, publisher_public_key=True,
                                                         publisher_private_key=True, subscriber_public_key=True,
                                                         subscriber_private_key=True)
            KeyManager.__setup_pub_sub_group_trees(topic, participants_permissions, common_tree=False, pub_tree=True,
                                                   sub_tree=True, pub_tree_keys=pub_tree_keys, pub_sub_tree=True,
                                                   pub_sub_tree_keys=pub_sub_tree_keys, sub_tree_keys=sub_tree_keys)

        elif topic.type_of_pub_sub_group == TypeOfPubSubGroupEnum.MANY_PUB_1_SUB.value:
            # todo -- check this again
            pub_tree_keys = PublishSubscribeTreeKeys(common_key=True, publisher_public_key=False,
                                                     publisher_private_key=False, subscriber_public_key=True,
                                                     subscriber_private_key=False)
            KeyManager.__setup_pub_sub_group_trees(topic, participants_permissions, common_tree=False, pub_tree=True,
                                                   sub_tree=False, pub_tree_keys=pub_tree_keys, pub_sub_tree=False,
                                                   sub_tree_keys=None)

        elif topic.type_of_pub_sub_group == TypeOfPubSubGroupEnum.MANY_SUB_1_PUB.value:
            sub_tree_keys = PublishSubscribeTreeKeys(common_key=True, publisher_public_key=True,
                                                     publisher_private_key=False, subscriber_public_key=False,
                                                     subscriber_private_key=False)
            KeyManager.__setup_pub_sub_group_trees(topic, participants_permissions, common_tree=False, pub_tree=False,
                                                   sub_tree=True, pub_tree_keys=None, pub_sub_tree=False,
                                                   sub_tree_keys=sub_tree_keys)

        else:
            pass  # return error

    # In this method trees are created based on the type publisher-
    # -subscriber group
    @staticmethod
    def __setup_pub_sub_group_trees(topic, participants_permissions=None, pub_tree=None, sub_tree=None, common_tree=None,
                                    pub_tree_keys=None, sub_tree_keys=None, pub_sub_tree=None, pub_sub_tree_keys=None):
        # how to get permissions of individual participant?-receive a map of participant and permissions.
        # set keys in the tree node object
        # not sure below 2 needed yet

        group_key_common = None
        group_key_publishers = dict()  # can test for None instead here (quick check)
        group_key_subscribers = dict()
        group_key_pub_sub = dict()
        publisher_public_key = None
        publisher_private_key = None
        subscriber_public_key = None
        subscriber_private_key = None
        if pub_tree is None and sub_tree is None and common_tree is None and pub_sub_tree is None:
            return "error message"

        if common_tree is True:
            topic_root_node_common = TreeNode('0', root_node=True)
            group_key_common = generate_key()
            topic_root_node_common.set_node_common_key(group_key_common)
            # check thorough
            # topic_root_node_common.node_id = group_key_common
            topic.set_root_tree_common(topic_root_node_common)
            # call function next - not here, recheck

        # generate all the keys
        if pub_tree is True:
            # checking only public key will suffice, because if there is a public key, there will definitely be a
            # private key
            if pub_tree_keys.publisher_public_key is True:
                # generate public and private keys
                # todo -- find an appropriate method to generate ECC public and private keys
                publisher_public_key = generate_key()
                publisher_private_key = generate_key()

            if pub_tree_keys.subscriber_public_key is True:
                # generate public private keys
                subscriber_public_key = generate_key()
                subscriber_private_key = generate_key()

        if sub_tree is True:
            if sub_tree_keys.publisher_public_key is True:
                # generate public and private keys
                # todo -- find an appropriate method to generate ECC public and private keys
                if publisher_public_key is not None:
                    publisher_public_key = generate_key()
                    publisher_private_key = generate_key()

            if sub_tree_keys.subscriber_public_key is True:
                if subscriber_public_key is not None:
                    # generate public private keys
                    subscriber_public_key = generate_key()
                    subscriber_private_key = generate_key()

        if pub_sub_tree is True:
            if pub_sub_tree_keys.publisher_public_key is True:
                # generate public and private keys
                # todo -- find an appropriate method to generate ECC public and private keys
                if publisher_public_key is not None:
                    publisher_public_key = generate_key()
                    publisher_private_key = generate_key()

            if pub_sub_tree_keys.subscriber_public_key is True:
                if subscriber_public_key is not None:
                    # generate public private keys
                    subscriber_public_key = generate_key()
                    subscriber_private_key = generate_key()

        if pub_tree is True:
            topic_root_node_publishers = TreeNode('0', root_node=True)
            if pub_tree_keys.publisher_public_key is True:
                group_key_publishers['publisher_public_key'] = publisher_public_key

            if pub_tree_keys.publisher_private_key is True:
                group_key_publishers['publisher_private_key'] = publisher_private_key

            if pub_tree_keys.subscriber_public_key is True:
                group_key_subscribers['subscriber_public_key'] = subscriber_public_key

            if pub_tree_keys.subscriber_private_key is True:
                group_key_subscribers['subscriber_private_key'] = subscriber_private_key

            if pub_tree_keys.common_key is True:
                group_key_subscribers['common_group_key'] = group_key_common

            topic_root_node_publishers.set_node_publisher_keys(group_key_publishers)
            topic.set_root_tree_publishers(topic_root_node_publishers)  # also try to set the depth and no. children

        if sub_tree is True:
            topic_root_node_subscribers = TreeNode('0', root_node=True)
            if sub_tree_keys.publisher_public_key is True:
                group_key_subscribers['publisher_public_key'] = publisher_public_key

            if sub_tree_keys.publisher_private_key is True:
                group_key_subscribers['publisher_private_key'] = publisher_private_key

            if sub_tree_keys.subscriber_public_key is True:
                group_key_subscribers['subscriber_public_key'] = subscriber_public_key

            if sub_tree_keys.subscriber_private_key is True:
                group_key_subscribers['subscriber_private_key'] = subscriber_private_key

            if sub_tree_keys.common_key is True:
                group_key_subscribers['common_group_key'] = group_key_common

            topic_root_node_subscribers.set_node_subscriber_keys(group_key_subscribers)
            topic.set_root_tree_subscribers(topic_root_node_subscribers)

        if pub_sub_tree is True:
            topic_root_node_pub_sub = TreeNode('0', root_node=True)
            if pub_sub_tree_keys.publisher_public_key is True:
                group_key_pub_sub['publisher_public_key'] = publisher_public_key

            if pub_sub_tree_keys.publisher_private_key is True:
                group_key_pub_sub['publisher_private_key'] = publisher_private_key

            if pub_sub_tree_keys.subscriber_public_key is True:
                group_key_pub_sub['subscriber_public_key'] = subscriber_public_key

            if pub_sub_tree_keys.subscriber_private_key is True:
                group_key_pub_sub['subscriber_private_key'] = subscriber_private_key

            if pub_sub_tree_keys.common_key is True:
                group_key_pub_sub['common_group_key'] = group_key_common

            topic_root_node_pub_sub.set_node_pub_sub_keys(group_key_pub_sub)
            topic.set_root_tree_pub_sub(topic_root_node_pub_sub)

        # handle edge cases single publisher or subscriber key
        if topic.type_of_pub_sub_group is TypeOfPubSubGroupEnum.MANY_SUB_1_PUB.value:
            topic.edge_case_one_publisher_keys = {'common_key': group_key_common,
                                                  'publisher_public_key': publisher_public_key,
                                                  'publisher_private_key': publisher_private_key
                                                  }
        if topic.type_of_pub_sub_group is TypeOfPubSubGroupEnum.MANY_PUB_1_SUB.value:
            topic.edge_case_one_subscriber_keys = {'common_key': group_key_common,
                                                   'subscriber_public_key': subscriber_public_key,
                                                   'subscriber_private_key': subscriber_private_key
                                                   }

        # todo -- handle tree sizes

        # segregate participants and set seperate root trees accordingly
        publish_tree_participants = []
        subscribe_tree_participants = []
        pub_sub_tree_participants = []

        if topic.root_tree_common is not None:
            participants = []
            for participant in participants_permissions:
                participant[0].add_topic(topic, participant[1])
                participants.append(participant[0])
            LKH.generate_tree(topic.root_tree_common, 3, 2, participants)

            # otherwise segregate the participants
        else:
            for participant in participants_permissions:
                if participant[1] is PermissionTypesEnum.PUBLISH.value:
                    participant[0].add_topic(topic, participant[1])
                    publish_tree_participants.append(participant[0])
                if participant[1] is PermissionTypesEnum.SUBSCRIBE.value:
                    participant[0].add_topic(topic, participant[1])
                    subscribe_tree_participants.append(participant[0])
                if participant[1] is PermissionTypesEnum.PUBLISH_AND_SUBSCRIBE.value:
                    participant[0].add_topic(topic, participant[1])
                    pub_sub_tree_participants.append(participant[0])

        if topic.root_tree_publishers is not None:
            LKH.generate_tree(topic.root_tree_publishers, 3, 2, participants=publish_tree_participants)

        if topic.root_tree_subscribers is not None:
            LKH.generate_tree(topic.root_tree_subscribers, 3, 2, participants=subscribe_tree_participants)

        if topic.root_tree_pub_sub is not None:
            LKH.generate_tree(topic.root_tree_pub_sub, 3, 2, participants=pub_sub_tree_participants)


        # call function here to generate the tree
        # set topic and permissions for the participants (do not forget)
        # check participant permissions and create separate lists for all permission types
        # check if pub and sub trees are not none and add participants to the trees accordingly