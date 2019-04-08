import paho.mqtt.client as paho
from .Registration import Registration
from .KeyManager import TestKeyManagerTopic
from Participant import Participant
import json
import time


def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(userdata))


def on_testing_initial_topic(client, userdata, msg):
    print(msg.payload)
    for topic in json.loads(msg.payload):
        client.subscribe(topic=topic['topic_to_sub'], qos=1)
        print("subscribed to "+ topic['topic_to_sub'])
        # also store ancestor keys globally
        # to decode and encode messages accordingly


def on_testing_initial_topic_anc(client, userdata, msg):
    for topic in json.loads(msg.payload):
        print("save ancestors and keys")


def on_message(client, userdata, msg):
    print("on message call back  -"+str(msg.payload))


class ClientTopic:

    def __init__(self, topic, permission):
        # assuming registration process gives the following data done
        # -- think -- send participant id to registration process?

        reg_data = Registration.register(topic)
        self.participant_id = reg_data[1]
        self.pairwise_key = reg_data[0]
        self.permission = permission
        initial_topic_anc = reg_data[2]
        initial_topic = reg_data[3]

        # subscribing to the topic
        # first connect to broker, this should be done before
        # since its test we connect here

        client = paho.Client()
        client.connect("iot.eclipse.org")

        # connection done
        # now subscribe to initial topic
        client.on_subscribe = on_subscribe
        client.on_message = on_message
        client.message_callback_add(initial_topic, on_testing_initial_topic)
        client.message_callback_add(initial_topic_anc, on_testing_initial_topic_anc)
        client.subscribe(topic=initial_topic, qos=1)

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




