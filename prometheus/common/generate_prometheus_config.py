import json
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

CADDY_USER = os.getenv('CADDY_USER')
CADDY_PASSWORD = os.getenv('CADDY_PASSWORD')
PROMETHEUS_CONFIG_DIR = os.getenv('PROMETHEUS_CONFIG_DIR', '/app/prometheus/socotra')

if not CADDY_USER or not CADDY_PASSWORD:
    raise ValueError("CADDY_USER or CADDY_PASSWORD variables are not defined in .env")

# Load servers from servers.json
try:
    servers_json_path = Path(PROMETHEUS_CONFIG_DIR) / 'servers.json'
    with open(servers_json_path, 'r') as f:
        servers = json.load(f)['servers']
except FileNotFoundError:
    raise FileNotFoundError(f"Error: servers.json not found at {servers_json_path}")

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
    'rule_files': ['/app/prometheus/rules.yml']
}

# Define the output path
output_dir = Path(PROMETHEUS_CONFIG_DIR)
output_file = output_dir / 'prometheus.yml'

try:
    # Ensure the parent directory exists
    if output_file.is_dir():
        raise IsADirectoryError(f"The path '{output_file}' exists and is a directory. Please remove or rename it.")

    output_dir.mkdir(parents=True, exist_ok=True)  # Create the directory if it doesn't exist

    # Create or overwrite the prometheus.yml file
    with open (output_file, 'w') as f:
        yaml.dump(config, f, sort_keys=False, default_flow_style=False, allow_unicode=True)
    print(f"{output_file} generated successfully.")
except IsADirectoryError as e:
    print(f"Error: {e}")
    exit(1)
except Exception as e:
    print(f"Error generating prometheus.yml: {e}")
    exit(1)