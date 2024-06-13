import requests
import json
import argparse

API_URL = 'http://172.16.0.1/api/v1'
Authorization_id = '61646d696e'
Authorization_token = 'fb726083b7918e800bb973c4f99343be'

def api_request(endpoint, method='GET', payload=None):
    url = f"{API_URL}{endpoint}"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"{Authorization_id} {Authorization_token}"
    }

    if method == 'GET':
        response = requests.get(url, headers=headers)
    elif method == 'POST':
        response = requests.post(url, headers=headers, data=json.dumps(payload))
    elif method == 'PUT':
        response = requests.put(url, headers=headers, data=json.dumps(payload))
    elif method == 'DELETE':
        response = requests.delete(url, headers=headers)
    else:
        raise ValueError("Invalid HTTP method specified")

    if response.status_code not in [200, 201, 202, 204]:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

    return response.json()

def configure_wan_ip(new_ip):
    endpoint = '/interface'
    payload = {
        'id': 'wan',
        'type': "staticv4",
        'ipaddr': new_ip,
        'subnet': 24
    }
    response = api_request(endpoint, method='PUT', payload=payload)
    return response

def create_gateway(gateway):
    endpoint = '/routing/gateway'
    response = api_request(endpoint, method='POST', payload=gateway)
    return response

def apply_interface():
    endpoint = '/interface/apply'
    payload = {
        'async': False
    }
    response = api_request(endpoint, method='POST', payload=payload)
    return response

def configure_static_route(route):
    endpoint = '/routing/static_route'
    response = api_request(endpoint, method='POST', payload=route)
    return response

def create_firewall(port, ip_address):
    endpoint = '/firewall/rule'
    payload = {
        'interface': 'wan',
    'type': "pass",
    'ipprotocol': "inet",
        'protocol': 'tcp',
        'src': 'any',
        'srcport': 'any',
        'dst': ip_address,
        'dstport': str(port),
        'descr': f'Allow traffic on port {port} to {ip_address}'
    }
    response = api_request(endpoint, method='POST', payload=payload)
    return response

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Configure firewall rules for specific ports and IP address.')
    parser.add_argument('ip_address', type=str, help='IP address for the destination of the firewall rule')
    args = parser.parse_args()
    
    ip_address = args.ip_address
    ports = [8080, 443, 2222, 2000]
    
    # Create the gateway first to avoid invalid protocol error
    gateway_config = {
        'interface': 'wan',
        'ipprotocol': 'inet',  # Correct protocol for IPv4
        'name': 'staticroute4',
        'gateway': '10.1.10.1',
        'descr': 'static route gateway'
    }
    gateway_response = create_gateway(gateway_config)
    print(f"Gateway configured: {gateway_response}")
    
    for port in ports:
        fw_response = create_firewall(port, ip_address)
        print(f"Firewall rule for port {port} to IP {ip_address} created: {fw_response}")

    # Apply interface changes after all firewall rules are created
    apply_response = apply_interface()
    print(f"Interface changes applied: {apply_response}")
