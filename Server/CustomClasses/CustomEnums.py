from enum import Enum


class PermissionTypesEnum(Enum):
    PUBLISH = 1
    SUBSCRIBE = 2
    PUBLISH_AND_SUBSCRIBE = 3


class TypeOfPubSubGroupEnum(Enum):
    ALL_PUBSUB = 1
    SOME_PUBSUB_SOME_PUB = 2
    SOME_PUBSUB_SOME_SUB = 3
    SOME_PUBSUB_SOME_PUB_SOME_SUB = 4
    SOME_PUB_SOME_SUB = 5
    MANY_PUB_1_SUB = 6
    MANY_SUB_1_PUB = 7


class KeyManagementProtocols(Enum):
    GKMP = 1
    LKH = 2