import paho.mqtt.client as paho
import json

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_test_message(client, userdata, msg):
    print(msg.topic)

client = paho.Client()
client.connect("iot.eclipse.org")
print("test")
print(client)
print(client._client_id)
topic_key = dict()
test_flag = 0
"""def on_message(client, userdata, msg):
    print(msg.topic)
    global test_flag
    test_flag = 1
    if msg.topic is b"GCKS/participant1001":
        print("if true")
        topic_key.append(str(msg.payload))
        for topic in topic_key:
            client.subscribe(topic=topic['name'], qos=1)"""
def on_message(client, userdata, msg):
    print(type(msg.topic))
    print(str(msg.payload))
    print (client)
    print("test")
    global test_flag
    test_flag = 1
    print(type(json.loads(msg.payload)))
    #topic_key.append(str(msg.payload))
    #print(topic_key)
    for topic in json.loads(msg.payload):
        print(topic)
    #for topic in topic_key:
        client.subscribe(topic=topic['topic_to_sub'], qos=1)


print(topic_key)
client.on_subscribe = on_subscribe
client.on_message = on_message
client.message_callback_add("GCKS/participant1001", on_test_message)

client.subscribe(topic="GCKS/participant1001", qos=1)

client.loop_forever()
#client.loop_start()
"""print("out")
while test_flag is 0:
    print ("waiting")"""
while len(topic_key) is 0:
    print("waiting")

print(topic_key)

print("out loop")