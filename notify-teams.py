#!/usr/bin/env python3 
#
#
# Author: Isaac J. Galvan
# Date: 2018-12-04
#
# https://github.com/isaac-galvan
#

import argparse
import json
import requests
import sys
import socket

def format_link(host, service=None):
    #replace spaces with '+'
    if service:
        service_link = str.replace(service, ' ', '+')
        host_link = str.replace(host, ' ', '+')
        return 'http://%s/nagios/cgi-bin/cmd.cgi?cmd_typ=34&host=%s&service=%s' % (socket.getfqdn(), host_link, service_link)
    else:
        host_link = str.replace(host, ' ', '+')
        return 'http://%s/nagios/cgi-bin/cmd.cgi?cmd_typ=33&host=%s' % (socket.getfqdn(), host_link)

def create_message(url, notification_type, host, service, alert, output, long_message=None):
    ''' creates a dict with for the MessageCard '''
    message = {}

    if service:
        title = '%s: %s/%s is %s' % (notification_type, host, service, alert)
    else:
        title = '%s: %s is %s' % (notification_type, host, alert)

    message['summary'] = title
    message['title'] = title
    message['text'] = output

    if alert == 'WARNING':
        color = 'FFFF00'
    elif alert == 'CRITICAL':
        color = 'FF0000'
    elif alert == 'DOWN':
        color = 'FF0000'
    elif alert == 'UNREACHABLE':
        color = 'FF0000'
    elif alert == 'UNKNOWN':
        color = 'FF7F00'
    else:
        color = '00FF00'

    message['themeColor'] = color

    # if not long_message is None:
    if long_message:
        message['text'] += '\n\n%s' % (long_message)

    service_link = format_link(host, service)

    nagiosAction = {
        '@type': 'OpenUri',
        "name": "Acknowledge",
        "targets": [{
            "os": "default",
            "uri": service_link
        }]
    }
    message['@type'] = 'MessageCard'
    message['@context'] = 'https://schema.org/extensions'
    if (notification_type != 'ACKNOWLEDGEMENT' and notification_type != 'RECOVERY'):
        message['potentialAction'] = [nagiosAction]

    return message

def send_to_teams(url, message_json):
    """ posts the message to the ms teams webhook url """
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url, data=message_json, headers=headers)
    if r.status_code == requests.codes.ok:
        print('success')
        return True
    else:
        print('failure')
        return False

def main(args):

    # verify url
    url = args.get('url')
    if url is None:
        # error no url
        print('error no url')
        exit(2)

    host = args.get('host')
    notification_type = args.get('type')
    service = args.get('service')
    alert = args.get('alert')
    output = args.get('output')
    long_message = args.get('long_message')
    
    message_dict = create_message(url, notification_type, host, service, alert, output, long_message)
    message_json = json.dumps(message_dict)
    
    send_to_teams(url, message_json)

if __name__=='__main__':
    args = {}
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', action='store', help='notification type', required=True)
    parser.add_argument('--host', action='store', help='hostname', required=True)
    parser.add_argument('--service', action='store', help='service description')
    parser.add_argument('--alert', action='store', help='warning, crit, or ok', required=True)
    parser.add_argument('--output', action='store', help='output of the check')
    parser.add_argument('--url', action='store', help='teams connector webhook url', required=True)

    parsedArgs = parser.parse_args()

    args['type'] = parsedArgs.type
    args['host'] = parsedArgs.host
    args['service'] = parsedArgs.service
    args['alert'] = parsedArgs.alert
    args['url'] = parsedArgs.url
    args['output'] = parsedArgs.output

    if not sys.__stdin__.isatty():
        args['long_message'] = sys.__stdin__.read()
        pass
    
    main(args)
