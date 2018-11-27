
import paho.mqtt.subscribe as subscribe

topics = ['thesis/progress']

m = subscribe.simple(topics, hostname="iot.eclipse.org", retained=False, msg_count=2)
for a in m:
    print(a.topic)
    print(a.payload)