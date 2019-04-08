import paho.mqtt.client as paho
from .Registration import Registration
from .KeyManager import TestKeyManagerTopic
from Participant import Participant
import json
import time

# global variables
change_key_topics = list()
topic_decrypt_keys = list()
change_key_ancestors= list()
ancestors_keys = list()
parent_keys = dict()

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(userdata))


def on_testing_initial_topic(client, userdata, msg):
    # authenticate the message -- check if it comes from key manager
    if authenticate_from_keymanager(msg) is True:
        decrypt_message_symmetric(msg, userdata['pairwise_key'])
        # make a global list to store keys or store this data somewhere
        # or make use of userdata
        global topic_decrypt_keys
        global change_key_topics

        print(msg.payload)
        for topic in json.loads(msg.payload):
            client.subscribe(topic=topic['topic_to_sub'], qos=1)
            print("subscribed to "+ topic['topic_to_sub'])
            # also store ancestor keys globally
            # to decode and encode messages accordingly
            change_key_topics.append(topic['topic_to_sub'])
            topic_decrypt_keys.append(topic['enc_key'])

            # add callbacks for key change handling
            client.message_callback_add(topic['topic_to_sub'], on_message_key_change)
        print(topic_decrypt_keys)
        print(change_key_topics)


def on_testing_initial_topic_anc(client, userdata, msg):
    print("ancestors")
    if authenticate_from_keymanager(msg) is True:
        # use decrypted message after implementation
        decrypt_message_symmetric(msg, userdata['pairwise_key'])
        # make a global list to store keys or store this data somewhere
        # or make use of userdata
        global ancestors_keys
        global change_key_ancestors

        for ancestor in json.loads(msg.payload):
            change_key_ancestors.append(ancestor['name'])
            ancestors_keys.append(ancestor['key'])
        print(change_key_ancestors)
        print(ancestors_keys)


# handling key change messages
def on_message_key_change(client, userdata, msg):
    if authenticate_from_keymanager(msg) is True:
        global topic_decrypt_keys
        global change_key_topics
        global ancestors_keys
        global change_key_ancestors
        print(topic_decrypt_keys[change_key_topics.index(str(msg.topic))])
        decrypt_message_symmetric(msg, topic_decrypt_keys[change_key_topics.index(str(msg.topic))])

        # changing decryptkeys of topic
        if change_key_topics.index(str(msg.topic)) is not 0:
            topic_decrypt_keys[change_key_topics.index(str(msg.topic))-1] = str(msg.payload) # use decrypted message later
        print(topic_decrypt_keys)
        # changing ancestor list
        ancestors_keys[change_key_ancestors.index(str(msg.topic).split('__')[2])] = str(msg.payload)
        print(ancestors_keys)



def on_message(client, userdata, msg):
    print("on message call back  -"+str(msg.payload))


# write authentication methods
def authenticate_from_keymanager(mqtt_msg):
    return True


def authenticate_from_clients(mqtt_msg):
    return True


def decrypt_message_symmetric(mqtt_msg, key):
    pass


class ClientTopic:

    def __init__(self, topic, permission):
        # assuming registration process gives the following data done
        # -- think -- send participant id to registration process?

        reg_data = Registration.register(topic)
        self.participant_id = reg_data[1]
        self.pairwise_key = reg_data[0]
        self.permission = permission
        initial_topic_anc = reg_data[3]
        initial_topic = reg_data[2]

        # make pairwise_key global for now, later save on a file or db

        # subscribing to the topic
        # first connect to broker, this should be done before
        # since its test we connect here

        client = paho.Client(userdata={'pairwise_key': self.pairwise_key})
        client.connect("iot.eclipse.org")

        # connection done
        # now subscribe to initial topic
        client.on_subscribe = on_subscribe
        client.on_message = on_message

        client.subscribe(topic=initial_topic, qos=1)
        client.subscribe(topic=initial_topic_anc, qos=1)

        # callbacks for special subscriptions on initial topic
        client.message_callback_add(initial_topic, on_testing_initial_topic)
        client.message_callback_add(initial_topic_anc, on_testing_initial_topic_anc)

        client.loop_start()

        # initialzing trees here
        testKeyManagerTopic = TestKeyManagerTopic("topic1")

        # ideally registration protocol should add clients to GCKS,
        # since this is test we call add client here
        client_participant = Participant(self.pairwise_key, self.participant_id)
        testKeyManagerTopic.add_client(client_participant, self.permission, initial_topic, initial_topic_anc)
        # time.sleep(10)
        # testKeyManagerTopic.add_client(client_participant, self.permission, initial_topic, initial_topic_anc)
        participant4 = Participant("12345", "004")

        time.sleep(10)

        testKeyManagerTopic.add_client(participant4, 3, "testTopic", "testTopicAnc")
        # client.loop_forever()
        while True:
            time.sleep(1)




