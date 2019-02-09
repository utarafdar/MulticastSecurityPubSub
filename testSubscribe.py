import paho.mqtt.subscribe as subscribe

def print_msg(client, userdata, message):
    print(message.topic, str(message.payload.decode("utf-8")))

# loops forever test commit
print("before callback")
subscribe.callback(print_msg, "thesis/progress", hostname="iot.eclipse.org")
print("after callback")