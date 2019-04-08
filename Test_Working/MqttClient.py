import paho.mqtt.subscribe as subscribe

topic_key = dict()
def print_msg(client, userdata, message):
    print(message.topic, str(message.payload.decode("utf-8")))
    if message.topic is "GCKS/participant1001":
        topic_key.append(str(message.payload.decode("utf-8")))


print(topic_key)
# loops forever
subscribe.callback(print_msg, "GCKS/participant1001", hostname="iot.eclipse.org")
