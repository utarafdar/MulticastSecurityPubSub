import paho.mqtt.client as mqtt  # import the client1
import time
"""
def on_publish(client,userdata,result):             #create function for callback
    print("data published \n")
    print(userdata, result, client)
    pass

def on_message(subscriber, userdata, message):
    print("message received ", str(message.payload.decode("utf-8")))
    print("message topic=", message.topic)
    print("message qos=", message.qos)
    print("message retain flag=", message.retain)

broker_address = "iot.eclipse.org"
print("creating new instance")
subscriber = mqtt.Client("S1")  # create new instance
subscriber.on_publish = on_publish
subscriber.on_message=on_message #attach function to callback
print("connecting to broker")
subscriber.connect(broker_address)  # connect to broker
print("Subscribing to topic", "house/bulbs/bulb1")
subscriber.loop() #start the loop
subscriber.subscribe("testMqttForThesis")
subscriber.publish("testMqttForThesis", "slow")
time.sleep(4) # wait
subscriber.loop_stop() #stop the loop
#subscriber.loop_stop()
"""


def on_publish(client,userdata,result):             #create function for callback
    print("data published \n")
    print(userdata, result, client)
    pass

############
def on_message(client, userdata, message):
    global loopFlag
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)
    loopFlag=0
########################################
#broker_address="192.168.1.184"
broker_address="iot.eclipse.org"
print("creating new instance")
client = mqtt.Client("P1") #create new instance
client.on_message=on_message #attach function to callback
#client.on_publish=on_publish
print("connecting to broker")
client.connect(broker_address) #connect to broker
client.loop_start()#start the loop
print("Subscribing to topic","thesis/progress")
client.subscribe("thesis/progress")
print("Publishing message to topic","thesis/progress")
#client.publish("thesis/progress","OFF")
loopFlag=1
while loopFlag==1:
    time.sleep(4) # wait
    print ("waiting for messsage")
    client.publish("thesis/progress","OFF")


client.loop_stop() #stop the loop

