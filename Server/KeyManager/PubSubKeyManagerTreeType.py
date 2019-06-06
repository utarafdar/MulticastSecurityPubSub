from .Protocols.CustomClasses.TreeNode import TreeNode, LeafNode
from Participant import Participant
from anytree import Node, findall_by_attr, PreOrderIter
from Topic import Topic
from Group import Group
from Server.CustomClasses.CustomEnums import PermissionTypesEnum, TypeOfPubSubGroupEnum
from .Protocols.LKH_Protocol import LKH
import random
import nacl.utils
import nacl.secret
import nacl.signing
from nacl.public import PrivateKey, Box


def generate_key():
    return nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)


class PublishSubscribeTreeKeys:

    def __init__(self, common_key, publisher_public_key, publisher_private_key, subscriber_public_key,
                 subscriber_private_key):
        self.common_key = common_key
        self.publisher_public_key = publisher_public_key
        self.publisher_private_key = publisher_private_key
        self.subscriber_public_key = subscriber_public_key
        self.subscriber_private_key = subscriber_private_key


class GroupTreeMapping:

    def __init__(self, group, root_tree_common=None, root_tree_publishers=None, root_tree_subscribers=None, root_tree_pub_sub=None):
        self.group = group
        self.root_tree_common = root_tree_common
        self.root_tree_publishers = root_tree_publishers
        self.root_tree_subscribers = root_tree_subscribers
        self.root_tree_pub_sub = root_tree_pub_sub
        self.edge_case_one_publisher_keys = None
        self.edge_case_one_subscriber_keys = None

    def set_root_tree_common(self, root_node_common):
        self.root_tree_common = Node(self.group.group_name, tree_node=root_node_common)

    def set_root_tree_publishers(self, root_node_publishers):
        self.root_tree_publishers = Node(self.group.group_name, tree_node=root_node_publishers)

    def set_root_tree_subscribers(self, root_node_subscribers):
        self.root_tree_subscribers = Node(self.group.group_name, tree_node=root_node_subscribers)

    def set_root_tree_pub_sub(self, root_node_pub_sub):
        self.root_tree_pub_sub = Node(self.group.group_name, tree_node=root_node_pub_sub)


class KeyManager:

    group_tree_mapping_list = list()

    @staticmethod
    def setup_group_trees(group, participants_permissions=None, tree_sizes=None):
        # check for type of publish subscribe group  and proceed further

        # first start mapping group and trees
        group_tree_map = GroupTreeMapping(group)
        if group.type_of_pub_sub_group == TypeOfPubSubGroupEnum.ALL_PUBSUB.value:
            # call functions here
            # set publisher, subscriber and common trees based on the group
            KeyManager.__setup_pub_sub_group_trees(group_tree_map, participants_permissions, tree_sizes, common_tree=True,
                                                   pub_tree=False, sub_tree=False, pub_sub_tree=False)

        elif group.type_of_pub_sub_group == TypeOfPubSubGroupEnum.SOME_PUBSUB_SOME_PUB.value:
            pub_tree_keys = PublishSubscribeTreeKeys(common_key=True, publisher_public_key=False,
                                                     publisher_private_key=False, subscriber_public_key=True,
                                                     subscriber_private_key=False)
            pub_sub_tree_keys = PublishSubscribeTreeKeys(common_key=True, publisher_public_key=False,
                                                         publisher_private_key=False, subscriber_public_key=True,
                                                         subscriber_private_key=True)
            KeyManager.__setup_pub_sub_group_trees(group_tree_map, participants_permissions, tree_sizes, common_tree=False,
                                                   pub_tree=True, sub_tree=False, pub_sub_tree=True, pub_tree_keys=pub_tree_keys,
                                                   pub_sub_tree_keys=pub_sub_tree_keys)

        elif group.type_of_pub_sub_group == TypeOfPubSubGroupEnum.SOME_PUBSUB_SOME_SUB.value:
            pub_sub_tree_keys = PublishSubscribeTreeKeys(common_key=True, publisher_public_key=True,
                                                         publisher_private_key=True, subscriber_public_key=False,
                                                         subscriber_private_key=False)
            sub_tree_keys = PublishSubscribeTreeKeys(common_key=True, publisher_public_key=True,
                                                     publisher_private_key=False, subscriber_public_key=False,
                                                     subscriber_private_key=False)
            KeyManager.__setup_pub_sub_group_trees(group_tree_map, participants_permissions, tree_sizes, common_tree=False, pub_tree=False,
                                                   sub_tree=True, pub_sub_tree=True, pub_sub_tree_keys=pub_sub_tree_keys,
                                                   sub_tree_keys=sub_tree_keys)

        elif group.type_of_pub_sub_group == TypeOfPubSubGroupEnum.SOME_PUB_SOME_SUB.value:
            pub_tree_keys = PublishSubscribeTreeKeys(common_key=False, publisher_public_key=True,
                                                     publisher_private_key=True, subscriber_public_key=True,
                                                     subscriber_private_key=False)
            sub_tree_keys = PublishSubscribeTreeKeys(common_key=False, publisher_public_key=True,
                                                     publisher_private_key=False, subscriber_public_key=True,
                                                     subscriber_private_key=True)
            KeyManager.__setup_pub_sub_group_trees(group_tree_map, participants_permissions, tree_sizes, common_tree=False, pub_tree=True,
                                                   sub_tree=True, pub_tree_keys=pub_tree_keys, pub_sub_tree=False,
                                                   sub_tree_keys=sub_tree_keys)

        elif group.type_of_pub_sub_group == TypeOfPubSubGroupEnum.SOME_PUBSUB_SOME_PUB_SOME_SUB.value:
            pub_tree_keys = PublishSubscribeTreeKeys(common_key=False, publisher_public_key=True,
                                                     publisher_private_key=True, subscriber_public_key=True,
                                                     subscriber_private_key=False)
            sub_tree_keys = PublishSubscribeTreeKeys(common_key=False, publisher_public_key=True,
                                                     publisher_private_key=False, subscriber_public_key=True,
                                                     subscriber_private_key=True)
            pub_sub_tree_keys = PublishSubscribeTreeKeys(common_key=False, publisher_public_key=True,
                                                         publisher_private_key=True, subscriber_public_key=True,
                                                         subscriber_private_key=True)
            KeyManager.__setup_pub_sub_group_trees(group_tree_map, participants_permissions, tree_sizes, common_tree=False, pub_tree=True,
                                                   sub_tree=True, pub_tree_keys=pub_tree_keys, pub_sub_tree=True,
                                                   pub_sub_tree_keys=pub_sub_tree_keys, sub_tree_keys=sub_tree_keys)

        elif group.type_of_pub_sub_group == TypeOfPubSubGroupEnum.MANY_PUB_1_SUB.value:
            # todo -- check this again
            pub_tree_keys = PublishSubscribeTreeKeys(common_key=True, publisher_public_key=False,
                                                     publisher_private_key=False, subscriber_public_key=True,
                                                     subscriber_private_key=False)
            KeyManager.__setup_pub_sub_group_trees(group_tree_map, participants_permissions, tree_sizes, common_tree=False, pub_tree=True,
                                                   sub_tree=False, pub_tree_keys=pub_tree_keys, pub_sub_tree=False,
                                                   sub_tree_keys=None)

        elif group.type_of_pub_sub_group == TypeOfPubSubGroupEnum.MANY_SUB_1_PUB.value:
            sub_tree_keys = PublishSubscribeTreeKeys(common_key=True, publisher_public_key=True,
                                                     publisher_private_key=False, subscriber_public_key=False,
                                                     subscriber_private_key=False)
            KeyManager.__setup_pub_sub_group_trees(group_tree_map, participants_permissions, tree_sizes, common_tree=False, pub_tree=False,
                                                   sub_tree=True, pub_tree_keys=None, pub_sub_tree=False,
                                                   sub_tree_keys=sub_tree_keys)

        else:
            pass  # return error

    # In this method trees are created based on the type publisher-
    # -subscriber group
    @staticmethod
    def __setup_pub_sub_group_trees(group_tree_map, participants_permissions=None, tree_sizes=None, pub_tree=None, sub_tree=None, common_tree=None,
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
            group_root_node_common = TreeNode('0', root_node=True)
            group_key_common = {'common_key': generate_key()}
            group_root_node_common.set_root_node_keys(group_key_common)
            # check thorough
            # topic_root_node_common.node_id = group_key_common
            group_tree_map.set_root_tree_common(group_root_node_common)
            # call function next - not here, recheck

        # generate common group key
        group_key_common = generate_key()
        # generate all the keys
        if pub_sub_tree is True:
            if pub_sub_tree_keys.publisher_public_key is True:
                # generate public and private keys
                if publisher_public_key is None:
                    if group_tree_map.group.type_of_pub_sub_group is TypeOfPubSubGroupEnum.SOME_PUBSUB_SOME_SUB.value:
                        publisher_private_key = nacl.signing.SigningKey.generate()
                        publisher_public_key = publisher_private_key.verify_key
                    else:
                        publisher_private_key = PrivateKey.generate()
                        publisher_public_key = publisher_private_key.public_key

            if pub_sub_tree_keys.subscriber_public_key is True:
                if subscriber_public_key is None:
                    # generate public private keys
                    subscriber_private_key = PrivateKey.generate()
                    subscriber_public_key = subscriber_private_key.public_key

        if pub_tree is True:
            # checking only public key will suffice, because if there is a public key, there will definitely be a
            # private key
            if pub_tree_keys.publisher_public_key is True:
                # generate public and private keys
                #publisher_private_key = nacl.signing.SigningKey.generate()
                #publisher_public_key = publisher_private_key.verify_key
                if publisher_public_key is None:
                    publisher_private_key = PrivateKey.generate()
                    publisher_public_key = publisher_private_key.public_key

            if pub_tree_keys.subscriber_public_key is True:
                # generate public private keys
                if subscriber_public_key is None:
                    subscriber_private_key = PrivateKey.generate()
                    subscriber_public_key = subscriber_private_key.public_key

        if sub_tree is True:
            if sub_tree_keys.publisher_public_key is True:
                # generate public and private keys
                if publisher_public_key is None:
                    #publisher_private_key = nacl.signing.SigningKey.generate()
                    #publisher_public_key = publisher_private_key.verify_key
                    publisher_private_key = PrivateKey.generate()
                    publisher_public_key = publisher_private_key.public_key

            if sub_tree_keys.subscriber_public_key is True:
                if subscriber_public_key is None:
                    # generate public private keys
                    subscriber_private_key = PrivateKey.generate()
                    subscriber_public_key = subscriber_private_key.public_key

        # here when not all are allowed to publish generate signing key


        if pub_tree is True:
            group_root_node_publishers = TreeNode('0', root_node=True)
            if pub_tree_keys.publisher_public_key is True:
                group_key_publishers['publisher_public_key'] = publisher_public_key

            if pub_tree_keys.publisher_private_key is True:
                group_key_publishers['publisher_private_key'] = publisher_private_key

            if pub_tree_keys.subscriber_public_key is True:
                group_key_subscribers['subscriber_public_key'] = subscriber_public_key

            if pub_tree_keys.subscriber_private_key is True:
                group_key_subscribers['subscriber_private_key'] = subscriber_private_key

            if pub_tree_keys.common_key is True:
                group_key_subscribers['common_key'] = group_key_common

            group_root_node_publishers.set_root_node_keys(group_key_publishers)
            group_tree_map.set_root_tree_publishers(group_root_node_publishers)  # also try to set the depth and no. children

        if sub_tree is True:
            group_root_node_subscribers = TreeNode('0', root_node=True)
            if sub_tree_keys.publisher_public_key is True:
                group_key_subscribers['publisher_public_key'] = publisher_public_key

            if sub_tree_keys.publisher_private_key is True:
                group_key_subscribers['publisher_private_key'] = publisher_private_key

            if sub_tree_keys.subscriber_public_key is True:
                group_key_subscribers['subscriber_public_key'] = subscriber_public_key

            if sub_tree_keys.subscriber_private_key is True:
                group_key_subscribers['subscriber_private_key'] = subscriber_private_key

            if sub_tree_keys.common_key is True:
                group_key_subscribers['common_key'] = group_key_common

            group_root_node_subscribers.set_root_node_keys(group_key_subscribers)
            group_tree_map.set_root_tree_subscribers(group_root_node_subscribers)

        if pub_sub_tree is True:
            group_root_node_pub_sub = TreeNode('0', root_node=True)
            if pub_sub_tree_keys.publisher_public_key is True:
                group_key_pub_sub['publisher_public_key'] = publisher_public_key

            if pub_sub_tree_keys.publisher_private_key is True:
                group_key_pub_sub['publisher_private_key'] = publisher_private_key

            if pub_sub_tree_keys.subscriber_public_key is True:
                group_key_pub_sub['subscriber_public_key'] = subscriber_public_key

            if pub_sub_tree_keys.subscriber_private_key is True:
                group_key_pub_sub['subscriber_private_key'] = subscriber_private_key

            if pub_sub_tree_keys.common_key is True:
                group_key_pub_sub['common_key'] = group_key_common

            group_root_node_pub_sub.set_root_node_keys(group_key_pub_sub)
            group_tree_map.set_root_tree_pub_sub(group_root_node_pub_sub)

        # handle edge cases single publisher or subscriber key
        if group_tree_map.group.type_of_pub_sub_group is TypeOfPubSubGroupEnum.MANY_SUB_1_PUB.value:
            group_tree_map.edge_case_one_publisher_keys = {'common_key': group_key_common,
                                                  'publisher_public_key': publisher_public_key,
                                                  'publisher_private_key': publisher_private_key
                                                  }
        if group_tree_map.group.type_of_pub_sub_group is TypeOfPubSubGroupEnum.MANY_PUB_1_SUB.value:
            group_tree_map.edge_case_one_subscriber_keys = {'common_key': group_key_common,
                                                   'subscriber_public_key': subscriber_public_key,
                                                   'subscriber_private_key': subscriber_private_key
                                                   }

        # todo -- handle tree sizes
        # initialising tree sizes
        pub_tree_no_children = None
        sub_tree_no_children = None
        pub_sub_tree_no_children = None
        common_tree_no_children = None
        pub_tree_depth = None
        sub_tree_depth = None
        pub_sub_tree_depth = None
        common_tree_depth = None

        if tree_sizes is not None:
            for tree_size in tree_sizes:
                if tree_size['tree_type'] is 'pub':
                    pub_tree_no_children = tree_size['no_of_children']
                    pub_tree_depth = tree_size['depth']
                if tree_size['tree_type'] is 'sub':
                    sub_tree_no_children = tree_size['no_of_children']
                    sub_tree_depth = tree_size['depth']
                if tree_size['tree_type'] is 'pub_sub':
                    pub_sub_tree_no_children = tree_size['no_of_children']
                    pub_sub_tree_depth = tree_size['depth']
                if tree_size['tree_type'] is 'common':
                    common_tree_no_children = tree_size['no_of_children']
                    common_tree_depth = tree_size['depth']


    # segregate participants and set seperate root trees accordingly
        publish_tree_participants = []
        subscribe_tree_participants = []
        pub_sub_tree_participants = []

        if group_tree_map.root_tree_common is not None:
            participants = []
            # optimization to make tree scalable
            if participants_permissions is None:
                participants = None
            # optimization to make tree scalable
            else:
                for participant in participants_permissions:
                    participant[0].add_group(group_tree_map.group, participant[1])
                    participants.append(participant[0])
                    group_tree_map.group.add_participant(participant[0], participant[1])

            #if common_tree_depth is None or common_tree_no_children is None:
                #return "error: tree size not specified"

            LKH.generate_tree(group_tree_map.root_tree_common, common_tree_depth, common_tree_no_children, participants)

                # otherwise segregate the participants
        else:
            # optimization to make tree scalable
            if participants_permissions is None:
                publish_tree_participants = None
                subscribe_tree_participants = None
                pub_sub_tree_participants = None
            # optimization to make tree scalable
            else:
                for participant in participants_permissions:
                    if participant[1] is PermissionTypesEnum.PUBLISH.value:
                        participant[0].add_group(group_tree_map.group, participant[1])
                        publish_tree_participants.append(participant[0])
                    if participant[1] is PermissionTypesEnum.SUBSCRIBE.value:
                        participant[0].add_group(group_tree_map.group, participant[1])
                        subscribe_tree_participants.append(participant[0])
                    if participant[1] is PermissionTypesEnum.PUBLISH_AND_SUBSCRIBE.value:
                        participant[0].add_group(group_tree_map.group, participant[1])
                        pub_sub_tree_participants.append(participant[0])

                    # add participant to the group data structure
                    group_tree_map.group.add_participant(participant[0], participant[1])

        if group_tree_map.root_tree_publishers is not None:

            # if pub_tree_depth is None or pub_tree_no_children is None:
                # return "error: tree size not specified"

            LKH.generate_tree(group_tree_map.root_tree_publishers, pub_tree_depth, pub_tree_no_children, participants=publish_tree_participants)

        if group_tree_map.root_tree_subscribers is not None:

            # if sub_tree_depth is None or sub_tree_no_children is None:
                # return "error: tree size not specified"

            LKH.generate_tree(group_tree_map.root_tree_subscribers, sub_tree_depth, sub_tree_no_children, participants=subscribe_tree_participants)

        if group_tree_map.root_tree_pub_sub is not None:

            # if pub_sub_tree_depth is None or pub_sub_tree_no_children is None:
                # return "error: tree size not specified"

            LKH.generate_tree(group_tree_map.root_tree_pub_sub, pub_sub_tree_depth, pub_sub_tree_no_children, participants=pub_sub_tree_participants)

        KeyManager.group_tree_mapping_list.append(group_tree_map)
        # call function here to generate the tree
        # set topic and permissions for the participants (do not forget)
        # check participant permissions and create separate lists for all permission types
        # check if pub and sub trees are not none and add participants to the trees accordingly

    @staticmethod
    def add_or_delete_participant(group, participant, participant_permission, add_participant=False,
                                  delete_participant=False):

        # first get the right member from the mapping list
        group_tree_map = [x for x in KeyManager.group_tree_mapping_list if x.group.id == group.id][0]
        # check if add or delete parameter is there
        if add_participant is False and delete_participant is False:
            return "error: set either add or delete"
        if add_participant is True and delete_participant is True:
            return "error: set either add or delete"
        # first check permissions and check if those are valid permissions in that group type
        # get one empty node and add participant
        # big if else based on topic type and permissions type

        # here we set all the required data (keys) to be updated after adding the participant
        trees_data_to_be_updated = []

        if group_tree_map.group.type_of_pub_sub_group is TypeOfPubSubGroupEnum.ALL_PUBSUB.value:
            # set the keys to be changed here
            common_keys_reset = {'common_key': generate_key()}
            trees_data_to_be_updated.append({'tree': group_tree_map.root_tree_common,
                                             'add_participant': add_participant,
                                             'delete_participant': delete_participant,
                                             'changed_root_keys': common_keys_reset})

        elif group_tree_map.group.type_of_pub_sub_group is TypeOfPubSubGroupEnum.SOME_PUBSUB_SOME_SUB.value:
            # todo check .value here
            if participant_permission is PermissionTypesEnum.PUBLISH.value:
                return "error: invalid permissions"
            # first reset all the keys, depending on participant permissions set the tree updates
            common_keys_reset = generate_key()
            # when not all are allowed to publish, public and private key are signing and verifying key
            publisher_private_key_reset = nacl.signing.SigningKey.generate()
            publisher_public_key_reset = publisher_private_key_reset.verify_key
            '''subscriber_private_key_reset = PrivateKey.generate()
            subscriber_public_key_reset = subscriber_private_key_reset.public_key'''
            #publisher_private_key_reset = PrivateKey.generate()
            #publisher_public_key_reset = publisher_private_key_reset.public_key

            subscriber_keys_reset = {'common_key': common_keys_reset,
                                     'publisher_public_key': publisher_public_key_reset}
            '''subscriber_keys_reset = {'subscriber_private_key': subscriber_private_key_reset,
                                     'subscriber_public_key':subscriber_public_key_reset,
                                     'publisher_public_key': publisher_public_key_reset}'''

            pub_sub_keys_reset = {'common_key': common_keys_reset,
                                  'publisher_public_key': publisher_public_key_reset,
                                  'publisher_private_key': publisher_private_key_reset}

            '''pub_sub_keys_reset = {'subscriber_private_key': subscriber_private_key_reset,
                                  'subscriber_public_key':subscriber_public_key_reset,
                                  'publisher_public_key': publisher_public_key_reset,
                                  'publisher_private_key': publisher_private_key_reset}'''

            if participant_permission is PermissionTypesEnum.SUBSCRIBE.value:
                trees_data_to_be_updated.append({'tree': group_tree_map.root_tree_subscribers,
                                                 'add_participant': add_participant,
                                                 'delete_participant': delete_participant,
                                                 'changed_root_keys': subscriber_keys_reset})
                trees_data_to_be_updated.append({'tree': group_tree_map.root_tree_pub_sub,
                                                 'add_participant': False,
                                                 'delete_participant': False,
                                                 'changed_root_keys': pub_sub_keys_reset})

            if participant_permission is PermissionTypesEnum.PUBLISH_AND_SUBSCRIBE.value:
                trees_data_to_be_updated.append({'tree': group_tree_map.root_tree_subscribers,
                                                 'add_participant': False,
                                                 'delete_participant': False,
                                                 'changed_root_keys': subscriber_keys_reset})
                trees_data_to_be_updated.append({'tree': group_tree_map.root_tree_pub_sub,
                                                 'add_participant': add_participant,
                                                 'delete_participant': delete_participant,
                                                 'changed_root_keys': pub_sub_keys_reset})

        elif group_tree_map.group.type_of_pub_sub_group is TypeOfPubSubGroupEnum.SOME_PUBSUB_SOME_PUB.value:
            # common key symmetric
            common_keys_reset = generate_key()

            # generating asymmetric keys for subscribers
            # to remember changes ===here===
            '''subscriber_private_key_reset = PrivateKey.generate()
            subscriber_public_key_reset = subscriber_private_key_reset.public_key'''
            '''publisher_private_key_reset = PrivateKey.generate()
            publisher_public_key_reset = publisher_private_key_reset.public_key'''
            subscriber_private_key_reset = PrivateKey.generate()
            subscriber_public_key_reset = subscriber_private_key_reset.public_key

            pub_sub_keys_reset = {'common_key': common_keys_reset,
                                  'subscriber_public_key': subscriber_public_key_reset,
                                  'subscriber_private_key': subscriber_private_key_reset}

            '''pub_sub_keys_reset = {'publisher_private_key': publisher_private_key_reset,
                                  'publisher_public_key': publisher_public_key_reset,
                                  'subscriber_public_key': subscriber_public_key_reset,
                                  'subscriber_private_key': subscriber_private_key_reset}'''

            publisher_keys_reset = {'subscriber_public_key': subscriber_public_key_reset,
                                    'common_key': common_keys_reset}

            '''publisher_keys_reset = {'subscriber_public_key': subscriber_private_key_reset,
                                    'publisher_private_key': publisher_private_key_reset,
                                    'publisher_public_key': publisher_public_key_reset}'''

            if participant_permission is PermissionTypesEnum.SUBSCRIBE.value:
                return "error: invalid permission"

            if participant_permission is PermissionTypesEnum.PUBLISH_AND_SUBSCRIBE.value:

                trees_data_to_be_updated.append({'tree': group_tree_map.root_tree_pub_sub,
                                                 'add_participant': add_participant,
                                                 'delete_participant': delete_participant,
                                                 'changed_root_keys': pub_sub_keys_reset})
                trees_data_to_be_updated.append({'tree': group_tree_map.root_tree_publishers,
                                                 'add_participant': False,
                                                 'delete_participant': False,
                                                 'changed_root_keys': publisher_keys_reset})

            if participant_permission is PermissionTypesEnum.PUBLISH.value:

                trees_data_to_be_updated.append({'tree': group_tree_map.root_tree_pub_sub,
                                                 'add_participant': False,
                                                 'delete_participant': False,
                                                 'changed_root_keys': pub_sub_keys_reset})
                trees_data_to_be_updated.append({'tree': group_tree_map.root_tree_publishers,
                                                 'add_participant': add_participant,
                                                 'delete_participant': delete_participant,
                                                 'changed_root_keys': publisher_keys_reset})

        elif group_tree_map.group.type_of_pub_sub_group is TypeOfPubSubGroupEnum.SOME_PUBSUB_SOME_PUB_SOME_SUB.value:

            #publisher_private_key_reset = nacl.signing.SigningKey.generate()
            #publisher_public_key_reset = publisher_private_key_reset.verify_key
            publisher_private_key_reset = PrivateKey.generate()
            publisher_public_key_reset = publisher_private_key_reset.public_key

            subscriber_private_key_reset = PrivateKey.generate()
            subscriber_public_key_reset = subscriber_private_key_reset.public_key

            subscriber_keys_reset = {'publisher_public_key': publisher_public_key_reset,
                                     'subscriber_public_key': subscriber_public_key_reset,
                                     'subscriber_private_key': subscriber_private_key_reset}

            pub_sub_keys_reset = {'subscriber_public_key': subscriber_public_key_reset,
                                  'subscriber_private_key': subscriber_private_key_reset,
                                  'publisher_public_key': publisher_public_key_reset,
                                  'publisher_private_key': publisher_private_key_reset}

            publisher_keys_reset = {'publisher_public_key': publisher_public_key_reset,
                                    'publisher_private_key': publisher_private_key_reset,
                                    'subscriber_public_key': subscriber_public_key_reset}

            if participant_permission is PermissionTypesEnum.SUBSCRIBE.value:

                trees_data_to_be_updated.append({'tree': group_tree_map.root_tree_subscribers,
                                                 'add_participant': add_participant,
                                                 'delete_participant': delete_participant,
                                                 'changed_root_keys': subscriber_keys_reset})
                trees_data_to_be_updated.append({'tree': group_tree_map.root_tree_pub_sub,
                                                 'add_participant': False,
                                                 'delete_participant': False,
                                                 'changed_root_keys': pub_sub_keys_reset})
                trees_data_to_be_updated.append({'tree': group_tree_map.root_tree_publishers,
                                                 'add_participant': False,
                                                 'delete_participant': False,
                                                 'changed_root_keys': publisher_keys_reset})

            if participant_permission is PermissionTypesEnum.PUBLISH_AND_SUBSCRIBE.value:

                trees_data_to_be_updated.append({'tree': group_tree_map.root_tree_subscribers,
                                                 'add_participant': False,
                                                 'delete_participant': False,
                                                 'changed_root_keys': subscriber_keys_reset})
                trees_data_to_be_updated.append({'tree': group_tree_map.root_tree_pub_sub,
                                                 'add_participant': add_participant,
                                                 'delete_participant': delete_participant,
                                                 'changed_root_keys': pub_sub_keys_reset})
                trees_data_to_be_updated.append({'tree': group_tree_map.root_tree_publishers,
                                                 'add_participant': False,
                                                 'delete_participant': False,
                                                 'changed_root_keys': publisher_keys_reset})

            if participant_permission is PermissionTypesEnum.PUBLISH.value:

                trees_data_to_be_updated.append({'tree': group_tree_map.root_tree_subscribers,
                                                 'add_participant': False,
                                                 'delete_participant': False,
                                                 'changed_root_keys': subscriber_keys_reset})
                trees_data_to_be_updated.append({'tree': group_tree_map.root_tree_pub_sub,
                                                 'add_participant': False,
                                                 'delete_participant': False,
                                                 'changed_root_keys': pub_sub_keys_reset})
                trees_data_to_be_updated.append({'tree': group_tree_map.root_tree_publishers,
                                                 'add_participant': add_participant,
                                                 'delete_participant': delete_participant,
                                                 'changed_root_keys': publisher_keys_reset})

        elif group_tree_map.group.type_of_pub_sub_group is TypeOfPubSubGroupEnum.SOME_PUB_SOME_SUB.value:

            #publisher_private_key_reset = nacl.signing.SigningKey.generate()
            #publisher_public_key_reset = publisher_private_key_reset.verify_key
            publisher_private_key_reset = PrivateKey.generate()
            publisher_public_key_reset = publisher_private_key_reset.public_key

            subscriber_private_key_reset = PrivateKey.generate()
            subscriber_public_key_reset = subscriber_private_key_reset.public_key

            subscriber_keys_reset = {'publisher_public_key': publisher_public_key_reset,
                                     'subscriber_public_key': subscriber_public_key_reset,
                                     'subscriber_private_key': subscriber_private_key_reset}

            publisher_keys_reset = {'publisher_public_key': publisher_public_key_reset,
                                    'publisher_private_key': publisher_private_key_reset,
                                    'subscriber_public_key': subscriber_public_key_reset}

            if participant_permission is PermissionTypesEnum.SUBSCRIBE.value:
                trees_data_to_be_updated.append({'tree': group_tree_map.root_tree_subscribers,
                                                 'add_participant': add_participant,
                                                 'delete_participant': delete_participant,
                                                 'changed_root_keys': subscriber_keys_reset})

                trees_data_to_be_updated.append({'tree': group_tree_map.root_tree_publishers,
                                                 'add_participant': False,
                                                 'delete_participant': False,
                                                 'changed_root_keys': publisher_keys_reset})

            if participant_permission is PermissionTypesEnum.PUBLISH_AND_SUBSCRIBE.value:
                return "error: invalid permissions"

            if participant_permission is PermissionTypesEnum.PUBLISH.value:
                trees_data_to_be_updated.append({'tree': group_tree_map.root_tree_subscribers,
                                                 'add_participant': False,
                                                 'delete_participant': False,
                                                 'changed_root_keys': subscriber_keys_reset})

                trees_data_to_be_updated.append({'tree': group_tree_map.root_tree_publishers,
                                                 'add_participant': add_participant,
                                                 'delete_participant': delete_participant,
                                                 'changed_root_keys': publisher_keys_reset})

        elif group_tree_map.group.type_of_pub_sub_group is TypeOfPubSubGroupEnum.MANY_PUB_1_SUB.value:

            common_keys_reset = generate_key()
            subscriber_private_key_reset = PrivateKey.generate()
            subscriber_public_key_reset = subscriber_private_key_reset.public_key

            publisher_keys_reset = {'common_key': common_keys_reset,
                                    'subscriber_public_key': subscriber_public_key_reset}

            if participant_permission is PermissionTypesEnum.SUBSCRIBE.value:
                return "handle if the only subscriber leaves"

            if participant_permission is PermissionTypesEnum.PUBLISH_AND_SUBSCRIBE.value:
                return "error: invalid permissions"

            if participant_permission is PermissionTypesEnum.PUBLISH.value:

                trees_data_to_be_updated.append({'tree': group_tree_map.root_tree_publishers,
                                                 'add_participant': add_participant,
                                                 'delete_participant': delete_participant,
                                                 'changed_root_keys': publisher_keys_reset})
            edge_case_subscriber_keys = {'common_key': common_keys_reset,
                                         'publisher_public_key': subscriber_public_key_reset,
                                         'publisher_private_key': subscriber_private_key_reset
                                        }
            group_tree_map.edge_case_one_publisher_keys = edge_case_subscriber_keys.copy()

        elif group_tree_map.group.type_of_pub_sub_group is TypeOfPubSubGroupEnum.MANY_SUB_1_PUB.value:

            common_keys_reset = generate_key()

            #publisher_private_key_reset = nacl.signing.SigningKey.generate()
            #publisher_public_key_reset = publisher_private_key_reset.verify_key
            publisher_private_key_reset = PrivateKey.generate()
            publisher_public_key_reset = publisher_private_key_reset.public_key

            subscriber_keys_reset = {'publisher_public_key': publisher_public_key_reset,
                                     'common_key': common_keys_reset}

            if participant_permission is PermissionTypesEnum.SUBSCRIBE.value:
                trees_data_to_be_updated.append({'tree': group_tree_map.root_tree_subscribers,
                                                 'add_participant': add_participant,
                                                 'delete_participant': delete_participant,
                                                 'changed_root_keys': subscriber_keys_reset})

            if participant_permission is PermissionTypesEnum.PUBLISH_AND_SUBSCRIBE.value:
                return "error: invalid permissions"

            if participant_permission is PermissionTypesEnum.PUBLISH.value:
                return "handle the only publisher leaving"

            # setting keys for edge case // also need to send message encrypted with pairwise key
            edge_case_publisher_keys = {'common_key': common_keys_reset,
                                        'publisher_public_key': publisher_public_key_reset,
                                        'publisher_private_key': publisher_private_key_reset
                                                  }
            group_tree_map.edge_case_one_publisher_keys = edge_case_publisher_keys.copy()

        add_participant_data = dict()
        delete_participant_data = dict()
        update_tree_data = list()

        # print(trees_data_to_be_updated)
        tree_structure_change = False
        for trees_data in trees_data_to_be_updated:
            if trees_data['add_participant'] is True:
                #todo check if duplicate
                participant.add_group(group_tree_map.group, participant_permission)
                group_tree_map.group.add_participant(participant, participant_permission)
                message = LKH.add_participant(trees_data['tree'], participant,
                                              changed_root_keys=trees_data['changed_root_keys'])
                tree_type = ''
                if trees_data['tree'] == group_tree_map.root_tree_publishers:
                    tree_type = 'pub'
                if trees_data['tree'] == group_tree_map.root_tree_subscribers:
                    tree_type = 'sub'
                if trees_data['tree'] == group_tree_map.root_tree_pub_sub:
                    tree_type = 'pub_sub'
                if trees_data['tree'] == group_tree_map.root_tree_common:
                    tree_type = 'common'

                # check if tree structure changed
                if message[3] is True:
                    tree_structure_change = True

                add_participant_data = (message[2], {'tree_type': tree_type})

            if trees_data['delete_participant'] is True:
                participant.delete_group(group_tree_map.group)
                group_tree_map.group.delete_participant(participant)
                message3 = LKH.delete_participant(trees_data['tree'], participant,
                                                  changed_root_keys=trees_data['changed_root_keys'])
                tree_type = ''
                if trees_data['tree'] == group_tree_map.root_tree_publishers:
                    tree_type = 'pub'
                if trees_data['tree'] == group_tree_map.root_tree_subscribers:
                    tree_type = 'sub'
                if trees_data['tree'] == group_tree_map.root_tree_pub_sub:
                    tree_type = 'pub_sub'
                if trees_data['tree'] == group_tree_map.root_tree_common:
                    tree_type = 'common'

                delete_participant_data = (message3[2], {'tree_type': tree_type})

            if trees_data['add_participant'] is False and trees_data['delete_participant'] is False:
                message2 = LKH.update_tree_root_keys(trees_data['tree'],
                                                     changed_root_keys=trees_data['changed_root_keys'])
                tree_type = ''
                if trees_data['tree'] == group_tree_map.root_tree_publishers:
                    tree_type = 'pub'
                if trees_data['tree'] == group_tree_map.root_tree_subscribers:
                    tree_type = 'sub'
                if trees_data['tree'] == group_tree_map.root_tree_pub_sub:
                    tree_type = 'pub_sub'
                if trees_data['tree'] == group_tree_map.root_tree_common:
                    tree_type = 'common'

                update_tree_data.append((message2[1], {'tree_type': tree_type}))

        '''tree_structure_change = False
        
        if message[3] is True:
            tree_structure_change = True'''

        return_message = {'add_participant': add_participant_data,
                          'delete_participant': delete_participant_data,
                          'update_tree': update_tree_data,
                          'tree_structure_change': tree_structure_change}
        # return message3[2],message2[1]
        return return_message