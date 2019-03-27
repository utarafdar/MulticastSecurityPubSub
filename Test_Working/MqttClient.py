import paho.mqtt.subscribe as subscribe

def print_msg(client, userdata, message):
    print(message.topic, str(message.payload.decode("utf-8")))

# loops forever
subscribe.callback(print_msg, "GCKS/participant1001", hostname="iot.eclipse.org")
