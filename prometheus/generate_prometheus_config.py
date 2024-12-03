import json
import os

import yaml
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

CADDY_USER = os.getenv('CADDY_USER')
CADDY_PASSWORD = os.getenv('CADDY_PASSWORD')

if not CADDY_USER or not CADDY_PASSWORD:
    raise ValueError("CADDY_USER or CADDY_PASSWORD variables are not defined in .env")

# Load servers from servers.json
try:
    with open('prometheus/servers.json', 'r') as f:
        servers = json.load(f)['servers']
except FileNotFoundError:
    raise FileNotFoundError("Error: servers.json not found")

# Prometheus configuration template
config = {
    'global': {
        'scrape_interval': '15s'
    },
    'scrape_configs': [
        {
            'job_name': 'prometheus',
            'static_configs': [
                {'targets': ['prometheus:9090']}
            ]
        },
        {
            'job_name': 'juneogo-machine',
            'metrics_path': '/metrics',
            'scheme': 'https',
            'basic_auth': {
                'username': CADDY_USER,
                'password': CADDY_PASSWORD
            },
            'static_configs': [
                {
                    'targets': [f"{server['target']}"],
                    'labels': {'server': server['name']}
                } for server in servers
            ]
        },
        {
            'job_name': 'juneogo',
            'metrics_path': '/ext/metrics',
            'scheme': 'https',
            'basic_auth': {
                'username': CADDY_USER,
                'password': CADDY_PASSWORD
            },
            'static_configs': [
                {
                    'targets': [f"{server['target']}"],
                    'labels': {'server': server['name']}
                } for server in servers
            ]
        }
    ],
    'rule_files': ['/etc/prometheus/rules.yml']
}

# Generate prometheus.yml with proper indentation
try:
    with open('prometheus/prometheus.yml', 'w') as f:
        yaml.dump(config, f, sort_keys=False, default_flow_style=False, allow_unicode=True)
    print("prometheus.yml generated successfully.")
except Exception as e:
    print(f"Error generating prometheus.yml: {e}")
    exit(1)
