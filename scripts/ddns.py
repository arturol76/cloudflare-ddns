#!/usr/bin/env python                                      

import argparse                                                                                                       
import CloudFlare                                          
import logging                                             
import requests  
import os 
import time

class cloudflare():
    def __init__(self, email, token):
        self.email = email
        self.token = token
        self.prev_ip = "0.0.0.0"

    def getAddress(self, service='http://ip.mrkc.me'):                                                                           
        """                                                    
        Get the apparent public IP of this computer. This does not imply that the
        necessary network configurations are in place to allow public access.

        Raises Exceptions for anything but a 200 response.

        :param service: the url to perform a GET against (should return only an IP)
        :type  service: str
        :returns: this machine's IP as seen by a server on the Internet
        :rtype: str
        """
        logging.debug("Looking up public IP")
        r = requests.get(service)
        r.raise_for_status()
        
        ip = r.text
        
        logging.debug("Found " + ip)

        if ip != self.prev_ip:
            changed = True
            self.prev_ip = ip
        else:
            changed = False

        return ip, changed

    def update(self, names):
        pub_ip, changed = self.getAddress()
                
        ret_obj = dict()
        ret_obj['ip_changed'] = changed
        ret_obj['pub_ip'] = pub_ip
        ret_obj['names'] = []

        for name in names:
            logging.debug("--------------------------------------")
            result = self.update_single(name, pub_ip)
            ret_obj['names'].append(result)

        return(ret_obj)

    def update_single(self, name, pub_ip):
        logging.debug("Updating domain " + name)

        ret_obj = dict();  
        ret_obj['name'] = name
        ret_obj['updated'] = False
        ret_obj['error_happened'] = False
        ret_obj['error_msg'] = ""
        
        # 'AAAA' for IPv6, 'A' for IPv4 (default)
        if ':' in pub_ip:
            ip_address_type = 'AAAA'
        else:
            ip_address_type = 'A'
        logging.debug("Address type " + ip_address_type)

        cf = CloudFlare.CloudFlare(self.email, self.token)
        #zones = cf.zones.get()
        
        #ex: www.arturol76.net --> arturol76.net
        root_name = '.'.join(name.split('.')[-2:])
        logging.debug("root name = " + root_name)

        # query for the zone name and expect only one value back
        try:
            zones = cf.zones.get(params = {'name':root_name,'per_page':1})
        except CloudFlare.CloudFlareAPIError as e:
            msg = '/zones.get {} - api call failed'.format(e)
            logging.error(msg)
            ret_obj['error_happened'] = True
            ret_obj['error_msg'] = e
            return ret_obj
        except Exception as e:
            msg = '/zones.get - {} - api call failed'.format(e)
            logging.error(msg)
            ret_obj['error_happened'] = True
            ret_obj['error_msg'] = e
            return ret_obj

        # extract the zone_id which is needed to process that zone
        if len(zones)>0:
            zone = zones[0]
            logging.debug("Found name=" + zone['name'] + " id=" + zone['id'])
        else:
            msg = 'Zone {} not found!'.format(root_name)
            logging.debug(msg)
            ret_obj['error_happened'] = True
            ret_obj['error_msg'] = msg
            return ret_obj

        
        # zones = cf.zones.get()
        # for zone in zones:
        #     logging.debug("LIST: name=" + zone['name'] + " id=" + zone['id'])

        # # Get the Zone ID
        # logging.debug("Looking up zone id for " + name)        
        # for zone in cf.zones.get():
        #     if '.'.join(name.split('.')[-2:]) in zone['name']:
        #         logging.debug("Found name=" + zone['name'] + " id=" + zone['id'])
        #         break
        #     else:
        #         #raise Exception("Unable to find zone id for " + name)
        #         error_msg = "Unable to find zone id for {}".format(name)
        #         logging.error(error_msg)
        #         ret_obj['error_happened'] = True
        #         ret_onj['error_msg'] = error_msg
        #         return ret_obj        
                
        # Get the DNS record
        logging.debug("Fetching DNS record")
        
        #dns_records = cf.zones.dns_records.get(zone['id'])
        #logging.debug(dns_records)
        
        dns_record = cf.zones.dns_records.get(zone['id'],params={'name': name, 'match': 'all', 'type': ip_address_type})[0]
        logging.debug("Found " + dns_record['id'])
        
        # Check to see if the IP has changed
        if dns_record['content'] != pub_ip:
            logging.info("Performing DSN record update: " + dns_record['content'] + "->" + pub_ip)
            cf.zones.dns_records.put(zone['id'], dns_record['id'],data={'name': name,'type': ip_address_type,'content': pub_ip})
            ret_obj['updated'] = True
        else:
            logging.debug("Old Address:" + dns_record['content'] + " " + "New Address:" + pub_ip)
            logging.info("Address of " + name + " has not changed (" + pub_ip + "). Not updating.")
            ret_obj['updated'] = False

        return ret_obj