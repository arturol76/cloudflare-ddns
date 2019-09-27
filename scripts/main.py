#!/usr/bin/env python       
# 
# HOME ASSISTANT
# sensor:
#   - platform: mqtt
#     state_topic: 'ddns/status'
#     name: 'ddns'
#     value_template: '{{ value_json.pub_ip }}'
#     #unit_of_measurement: dB
#     availability_topic: "ddns/LWT"
#     payload_available: "online"
#     payload_not_available: "offline"
#     json_attributes:
#       - pub_ip
#       - ip_changed                         

import argparse                                                                                                       
import logging                                             
import os 
import time

import ddns                                          
import mymqtt          
import json                             

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)03d - [%(funcName)s] %(message)s', datefmt='%d-%b-%y %H:%M:%S')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--email', type=str, required=False, help='overrides env variable DDNS_EMAIL')
    parser.add_argument('-t', '--token', type=str, required=False, help='overrides env variable DDNS_TOKEN')
    parser.add_argument('-d', '--domains', type=str, required=False, help='comma separated list of domain names to update. Overrides env variable DDNS_DOMAINS.')
    parser.add_argument('-tw', '--wait', type=str, required=False, help='seconds to wait before next update. Overrides env variable DDNS_WAIT.')
    parser.add_argument('-v','--verbose', action='store_true', help='verbose debug messages.')
    parser.add_argument('-c','--config', default='./config.json',help='MQTT configuration file')

    args = parser.parse_args()

    if args.verbose is False:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.DEBUG)

    if args.email is not None:
        email=args.email
    else:
        email = os.environ['DDNS_EMAIL']

    if args.token is not None:
        token=args.token
    else:
        token = os.environ['DDNS_TOKEN']

    if args.domains is not None:
        domains=args.domains
    else:
        domains = os.environ['DDNS_DOMAINS']
    domains = [x.strip() for x in domains.split(',')]

    if args.wait is not None:
        wait=int(args.domains)
    else:
        wait = int(os.environ['DDNS_WAIT'])

    #set working dir to script's dir 
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    with open(args.config) as json_data_file:
        cfg = json.load(json_data_file)

    mqtt_cfg = cfg['mqtt']

    cf = ddns.cloudflare(email,token)
    mqtt_client = mymqtt.mqtt(mqtt_cfg)

    while True:
        result = cf.update(domains)
        mqtt_client.send_status(json.dumps(result))
        logging.debug(result)

        logging.debug("Waiting for " + str(wait) + " seconds before next update...")
        time.sleep(wait)