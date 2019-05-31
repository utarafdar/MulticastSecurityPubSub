import paho.mqtt.client as mqtt  # import the client1
import time

def on_publish(client,userdata,result):             #create function for callback
    print("data published \n")
    print(userdata, result, client)
    pass

# broker_address="192.168.1.184"
broker_address = "broker.mqttdashboard.com"  # use external broker
publisher = mqtt.Client("P3")  # create new instance
#publisher.on_publish = on_publish
publisher.connect(broker_address)  # connect to broker
i=0
while i<10:
    publisher.publish("thesis/progress", "cool")  # publish
    print("published cool")
    time.sleep(4)
    i=i+1

### subscribing



