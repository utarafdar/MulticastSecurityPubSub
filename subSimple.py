
import paho.mqtt.subscribe as subscribe

topics = ['thesis/progress']

m = subscribe.simple(topics, hostname="iot.eclipse.org", retained=False)  #//msg_count=5
#for a in m:
print(m.topic)
print(m.payload)