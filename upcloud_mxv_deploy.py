import http.client
import argparse
import json
import base64
import datetime
import time
import socket

API_url = "api.upcloud.com"
API_ver = "1.2"
server_endpoint = "/" + API_ver + "/server"
storage_endpoint = "/" + API_ver + "/storage"

new_server_request_body = {
    "server": {
        "zone": "fi-hel1",
        "plan": "2xCPU-4GB",
        "firewall": "on",
        "title": "MXV 14.0.6",
        "hostname": "localhost",
        "password_delivery":"none",
        "user_data" : "sh -c \"yum install -y unzip; wget https://fileshare.connector73.net/mxv1406-raw/mxv-14.0.6-raw.zip; unzip mxv-14.0.6-raw.zip; dd if=disk1.raw of=/dev/vdb bs=16M oflag=direct;dd if=disk2.raw of=/dev/vdc bs=16M oflag=direct;dd if=disk3.raw of=/dev/vdd bs=16M oflag=direct; shutdown -h now\"",
        "storage_devices": {
            "storage_device": [
                {
                "action": "clone",
                "address": "virtio:0",
                "storage": "01000000-0000-4000-8000-000050010300",
                "title": "Centos from a template",
                "size": 80,
                "tier": "maxiops"
                },
                { 
                "action": "create",
                "address": "virtio:1",
                "title": "DISK1", 
                "size": 10, 
                "tier": "maxiops"
                },
                { 
                "action": "create",
                "address": "virtio:2",
                "title": "DISK2", 
                "size": 10, 
                "tier": "maxiops"
                },
                { 
                "action": "create",
                "address": "virtio:3",
                "title": "DISK3", 
                "size": 25, 
                "tier": "maxiops"
                }
            ]
        },
        "login_user": {
            "username": "upclouduser",
            "create_password":"yes"
        }
    }
}

firewall_rule_list = [
            {
                "action": "accept",
                "destination_port_end": "80",
                "destination_port_start": "80",
                "direction": "in",
                "family": "IPv4",
                "protocol": "tcp"
            },
            {
                "action": "accept",
                "destination_port_end": "443",
                "destination_port_start": "443",
                "direction": "in",
                "family": "IPv4",
                "protocol": "tcp"
            },            
            {
                "action": "accept",
                "direction": "in",
                "family": "IPv4",
                "protocol": "udp",
                "source_address_end": "94.237.127.9",
                "source_address_start": "94.237.127.9",
                "source_port_end": "53",
                "source_port_start": "53"
            },
            {
                "action": "accept",
                "direction": "in",
                "family": "IPv4",
                "protocol": "udp",
                "source_address_end": "94.237.40.9",
                "source_address_start": "94.237.40.9",
                "source_port_end": "53",
                "source_port_start": "53"
            },
            {
                "action": "accept",
                "destination_port_end": "8080",
                "destination_port_start": "8080",
                "direction": "in",
                "family": "IPv4",
                "protocol": "tcp"
            },
            {
                "action": "accept",
                "destination_port_end": "7779",
                "destination_port_start": "7777",
                "direction": "in",
                "family": "IPv4",
                "protocol": "tcp"
            },
            {
                "action": "accept",
                "destination_port_end": "5061",
                "destination_port_start": "5060",
                "direction": "in",
                "family": "IPv4",
                "protocol": "tcp"
            },
            {
                "action": "accept",
                "destination_port_end": "9060",
                "destination_port_start": "9060",
                "direction": "in",
                "family": "IPv4",
                "protocol": "tcp"
            },
            {
                "action": "accept",
                "destination_port_end": "7171",
                "destination_port_start": "7100",
                "direction": "in",
                "family": "IPv4",
                "protocol": "tcp"
            },
            {
                "action": "accept",
                "destination_port_end": "7505",
                "destination_port_start": "7505",
                "direction": "in",
                "family": "IPv4",
                "position": "14",
                "protocol": "tcp"
            },
            {
                "action": "accept",
                "destination_port_end": "5060",
                "destination_port_start": "5060",
                "direction": "in",
                "family": "IPv4",
                "protocol": "udp"
            },
            {
                "action": "accept",
                "destination_port_end": "9060",
                "destination_port_start": "9060",
                "direction": "in",
                "family": "IPv4",
                "protocol": "udp"
            },
            {
                "action": "accept",
                "destination_port_end": "24999",
                "destination_port_start": "20000",
                "direction": "in",
                "family": "IPv4",
                "protocol": "udp"
            },
            {
                "action": "accept",
                "destination_port_end": "3771",
                "destination_port_start": "3771",
                "direction": "in",
                "family": "IPv4",
                "protocol": "udp"
            },
            {
                "action": "accept",
                "direction": "out",
                "family": "IPv4"
            },
            {
                "action": "drop",
                "direction": "in"
            },
            {
                "action": "drop",
                "direction": "out"
            }
        ]


def connection(timeout=10):
    return http.client.HTTPSConnection(API_url,timeout=timeout)


def auth(username, password):
    userAndPass = base64.b64encode(str.encode(username) + b":" + str.encode(password)).decode("ascii")
    auth_header = {"Authorization" : "Basic %s" % userAndPass}
    return auth_header


def response_error(response, err_code):   
    if response.status != err_code:
        error_data = json.loads(response.read())['error']
        print(response.status, response.reason, error_data['error_code'], error_data['error_message'])
        print('Exiting')
        return True
    else:
        return False


def create_server(auth_header, zone):
    conn = connection()
    content_header = {"Content-type": "application/json"}
    
    body = new_server_request_body
    body['server']['zone'] = zone
    try:
        conn.request("POST", server_endpoint, headers={**content_header,**auth_header}, body=json.dumps(body))
    except Exception as e:
        print("Connection error")
        print(e)
        conn.close()
        exit(1)
    
    response = conn.getresponse()
    if response_error(response, 202):
        conn.close()
        exit(2)
    
    data = json.loads(response.read())
    conn.close()
    return data['server']['uuid']


def get_server_details(auth_header, uuid):
    conn = connection()
    
    try:
        conn.request("GET", server_endpoint + "/" + uuid, headers={**auth_header})
    except Exception as e:
        print("Connection error")
        print(e)
        conn.close()
        exit(1)
    
    response = conn.getresponse()
    if response_error(response, 200):
        conn.close()
        exit(2)
    
    data = json.loads(response.read())
    conn.close()
    return data['server']


def detach_storage(auth_header, conn, uuid, body):
    content_header = {"Content-type": "application/json"}

    try:
        conn.request("POST", server_endpoint + "/" + uuid + "/storage/detach", headers={**content_header,**auth_header}, body=json.dumps(body))
    except Exception as e:
        print("Connection error")
        print(e)
        conn.close()
        exit(1)

    response = conn.getresponse()    
    if response_error(response, 200):
        conn.close()
        exit(2)


def attach_storage(auth_header, conn, uuid, body):
    content_header = {"Content-type": "application/json"}
    
    try:
        conn.request("POST", server_endpoint + "/" + uuid + "/storage/attach", headers={**content_header,**auth_header}, body=json.dumps(body))
    except Exception as e:
        print("Connection error")
        print(e)
        conn.close()
        exit(1)
    
    response = conn.getresponse()    
    if response_error(response, 200):
        conn.close()
        exit(2)


def disk_configuration(auth_header, uuid):
    print("Configuring disks...")
    conn = connection()
    content_header = {"Content-type": "application/json"}

    server_details = get_server_details(auth_header,uuid)
    os_disk, disk1, disk2, disk3 = server_details['storage_devices']['storage_device']
    
    # detach OS disk
    body = {"storage_device": {"address": "virtio:0"}}
    detach_storage(auth_header,conn,uuid,body)
    print("Detached OS disk")
    
    # delete OS disk
    try:
        conn.request("DELETE", storage_endpoint + "/" + os_disk['storage'], headers={**auth_header})
    except Exception as e:
        print("Connection error")
        print(e)
        conn.close()
        exit(1)

    response = conn.getresponse()    
    if response_error(response, 204):
        conn.close()
        exit(2)
    
    print("Deleted OS disk")
    
    # reatach mxv disks
    # detach disk1
    body = {"storage_device": {"address": "virtio:1"}}
    detach_storage(auth_header,conn,uuid,body)  
    print("Detached disk1")
    # attach disk1
    body = {"storage_device": {"type": "disk", "address": "ide:0:0", "storage": disk1['storage'], "boot_disk": "1"}}
    attach_storage(auth_header,conn,uuid,body)  
    print("Attached disk1")

    # detach disk2
    body = {"storage_device": {"address": "virtio:2"}}
    detach_storage(auth_header,conn,uuid,body)  
    print("Detached disk2")
    # attach disk2
    body = {"storage_device": {"type": "disk", "address": "scsi:0:0", "storage": disk2['storage'], "boot_disk": "0"}}
    attach_storage(auth_header,conn,uuid,body)  
    print("Attached disk2")

    # detach disk3
    body = {"storage_device": {"address": "virtio:3"}}
    detach_storage(auth_header,conn,uuid,body)  
    print("Detached disk3")
    # attach disk3
    body = {"storage_device": {"type": "disk", "address": "scsi:0:1", "storage": disk3['storage'], "boot_disk": "0"}}
    attach_storage(auth_header,conn,uuid,body)  
    print("Attached disk3")

    conn.close()


def add_firewall(auth_header, uuid):
    print("Configuring firewall...")
    conn = connection()
    content_header = {"Content-type": "application/json"}
    for rule in firewall_rule_list:
        body = {"firewall_rule": rule}
        try:
            conn.request("POST", server_endpoint + "/" + uuid + "/firewall_rule", headers={**content_header,**auth_header}, body=json.dumps(body))
        except Exception as e:
            print("Connection error")
            print(e)
            conn.close()
            exit(1)

        response = conn.getresponse()    
        if response_error(response, 201):
            conn.close()
            exit(2)

    conn.close()
    

def start_server(auth_header, uuid):
    conn = connection(120)
    try:
        conn.request("POST", server_endpoint + "/" + uuid + "/start", headers={**auth_header})
    except Exception as e:
        print("Connection error")
        print(e)
        conn.close()
        exit(1)

    try:
        response = conn.getresponse()
    except socket.timeout:
        print("Timeout error. Probably server has already started. Check manually.")
        conn.close()
        exit(3)

    if response_error(response, 200):
        conn.close()
        exit(2)

    data = json.loads(response.read())
    print("UUID:", data['server']['uuid'])
    print("Zone:", data['server']['zone'])
    print("IP addresses:")
    ip_addresses = data['server']['ip_addresses']['ip_address']
    for ip in ip_addresses:
        print(ip)
    
    conn.close()


def main(auth_header,zone):
    
    # Creating instance of vm
    before = datetime.datetime.now()
    print("Creating server...Please wait.")
    server_uuid = create_server(auth_header,zone)

    while True:
        if get_server_details(auth_header, server_uuid)['state'] == 'maintenance':
            time.sleep(5)
        else:
            break
    after = datetime.datetime.now()
    print("Time took:", (after - before).seconds, "seconds")

    # Running initialization script
    before = datetime.datetime.now()
    print("Copying MXV disks...Please wait.")

    while True:
        if get_server_details(auth_header, server_uuid)['state'] != 'stopped':
            time.sleep(5)
        else:
            break
    after = datetime.datetime.now()
    print("Time took:", (after - before).seconds, "seconds")

    # Replacing disks
    before = datetime.datetime.now()
    disk_configuration(auth_header,server_uuid)

    # Adding firewall rules
    add_firewall(auth_header, server_uuid)
    # Start machine
    print("Starting server...Please wait.")
    start_server(auth_header,server_uuid)

    print("Finished")
    after = datetime.datetime.now()
    print("Time took:", (after - before).seconds, "seconds")
    exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--zone', dest='zone', default="fi-hel1", choices=["de-fra1","fi-hel1","fi-hel2","nl-ams1","sg-sin1","uk-lon1","us-chi1","us-sjo1"],help='Choose zone for deployment. Default is fi-hel1')
    requiredArg = parser.add_argument_group('required arguments')
    requiredArg.add_argument('--username', dest='user', help='UpCloud API Username', required=True)
    requiredArg.add_argument('--password', dest='secret', help='UpCloud API password', required=True)
    
    args = parser.parse_args()

    main(auth(args.user, args.secret), args.zone)
