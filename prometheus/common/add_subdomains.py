import json
import os

import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Token for reading all zones
CLOUDFLARE_READ_TOKEN = os.getenv('CLOUDFLARE_READ_TOKEN')
# Token for editing DNS in a specific zone
CLOUDFLARE_WRITE_TOKEN = os.getenv('CLOUDFLARE_WRITE_TOKEN')
PROMETHEUS_CONFIG_DIR = os.getenv('PROMETHEUS_CONFIG_DIR', '/app/prometheus/socotra')

if not CLOUDFLARE_READ_TOKEN or not CLOUDFLARE_WRITE_TOKEN:
    print("CLOUDFLARE_READ_TOKEN or CLOUDFLARE_WRITE_TOKEN is not defined in .env")
    raise ValueError("CLOUDFLARE_READ_TOKEN or CLOUDFLARE_WRITE_TOKEN is not defined in .env")

# Load servers from servers.json
try:
    servers_json_path = os.path.join(PROMETHEUS_CONFIG_DIR, 'servers.json')
    with open(servers_json_path, 'r') as f:
        servers = json.load(f)['servers']
except FileNotFoundError:
    print(f"Error: servers.json not found at {servers_json_path}")
    raise FileNotFoundError(f"Error: servers.json not found at {servers_json_path}")

# Fetch all zones using the read token
zones_api_endpoint = "https://api.cloudflare.com/client/v4/zones"
headers_read = {
    'Authorization': f'Bearer {CLOUDFLARE_READ_TOKEN}',
    'Content-Type': 'application/json'
}

response = requests.get(zones_api_endpoint, headers=headers_read)

if response.status_code != 200:
    print(f"Failed to fetch zones: {response.text}")
    raise Exception(f"Failed to fetch zones: {response.text}")

zones = response.json().get('result', [])
if not zones:
    print("No zones found in Cloudflare account")
    raise Exception("No zones found in Cloudflare account")

# Map domains to zone IDs
zone_map = {zone['name']: zone['id'] for zone in zones}

# Function to extract domain from target
def extract_domain(target):
    return ".".join(target.split(".")[-2:])

# Fetch all DNS records for each zone
def fetch_all_dns_records(zone_id):
    records = []
    page = 1
    per_page = 100
    while True:
        api_endpoint = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?page={page}&per_page={per_page}"
        response = requests.get(api_endpoint, headers=headers_read)
        if response.status_code == 200:
            data = response.json()
            page_records = data.get('result', [])
            records.extend(page_records)
            if len(page_records) < per_page:
                break
            page += 1
        else:
            print(f"Failed to fetch DNS records for zone {zone_id}: {response.text}")
            break
    return records

# Map to store DNS records for each zone
dns_records_map = {}

for domain, zone_id in zone_map.items():
    dns_records_map[zone_id] = fetch_all_dns_records(zone_id)

# Function to check if DNS record exists locally
def dns_record_exists(zone_id, target, ip):
    records = dns_records_map.get(zone_id, [])
    target_lower = target.lower()
    ip_lower = str(ip).lower()
    return any(record['name'].lower() == target_lower and str(record['content']).lower() == ip_lower for record in records)

# Loop through the servers and add DNS records
headers_write = {
    'Authorization': f'Bearer {CLOUDFLARE_WRITE_TOKEN}',
    'Content-Type': 'application/json'
}

for server in servers:
    
    if not all(key in server for key in ['target', 'ip']):
      print(f"Skipping invalid server entry: {server}")
      continue

    domain = extract_domain(server['target'])
    zone_id = zone_map.get(domain)

    if not zone_id:
        print(f"Skipping {server['name']} - No zone found for domain {domain}")
        continue

    if dns_record_exists(zone_id, server['target'], server['ip']):
        print(f"DNS record for {server['target']} with IP {server['ip']} already exists in zone {domain}")
        continue

    api_endpoint = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    data = {
        'type': 'A',
        'name': server['target'],
        'content': server['ip'],
        'ttl': 120,
        'proxied': True
    }

    response = requests.post(api_endpoint, headers=headers_write, json=data)

    if response.status_code == 200:
        print(f"Successfully added {server['target']} with IP {server['ip']} to zone {domain}")
    else:
        print(f"Failed to add {server['target']} with IP {server['ip']} to zone {domain}: {response.text}")
