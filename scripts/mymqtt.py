import sys
import os

import logging
import json

import paho.mqtt.client as paho_client

class mqtt():
    def __init__(self, mqtt_cfg):
        self.mqtt_lwt_topic = mqtt_cfg['lwt_topic']
        self.mqtt_request_topic = mqtt_cfg['request_topic']
        self.mqtt_response_topic = mqtt_cfg['response_topic']
        self.mqtt_status_topic = mqtt_cfg['status_topic']
        
        self.mqttclient = paho_client.Client(client_id=mqtt_cfg['client_id'])
        self.mqttclient.on_connect = self.on_connect
        self.mqttclient.on_message = self.on_message
        self.mqttclient.username_pw_set(mqtt_cfg['username'], mqtt_cfg['password'])
        self.mqttclient.will_set(self.mqtt_lwt_topic, payload="offline", qos=1, retain=True)
        self.mqttclient.connect(mqtt_cfg['broker'], mqtt_cfg['port'], 60)
        self.mqttclient.loop_start()
        
    def on_connect(self, client, userdate, flag, rc):
        logging.info("[MQTT] Connect RC=" + str(rc))
        client.subscribe(self.mqtt_request_topic, qos=2)
        client.publish(self.mqtt_lwt_topic,"online", qos=1, retain=True)

    #@profile
    def on_message(self, client, userdata, msg):
        logging.debug("[MQTT] message received")
        logging.debug("[MQTT] topic: " + msg.topic)
        logging.debug("[MQTT] payload: " + msg.payload.decode('utf-8'))

        if msg.topic == self.mqtt_request_topic:
            d = msg.payload.decode('utf-8')
            if d == "ping":
                self.send_reponse("alive")    
            elif d == "stop":
                self.send_reponse("ok")       
                client.disconnect()
                exit(0)
            else:
                client.publish(self.mqtt_response_topic,"unknown")

    def send_reponse(self, msg):
        self.mqttclient.publish(self.mqtt_response_topic,msg)

    def send_status(self, msg):
        self.mqttclient.publish(self.mqtt_status_topic,msg)
