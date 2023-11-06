# Install Promeutheus :

1. Add juneogo to the root :

```
usermod -aG sudo juneogo
```

2. Follow this tutorial:

```
https://docs.avax.network/nodes/maintain/setting-up-node-monitoring
```

2.1) Download the script to a user root (not the base root)

```
wget -nd -m https://raw.githubusercontent.com/ava-labs/avalanche-monitoring/main/grafana/monitoring-installer.sh ;\
chmod 755 monitoring-installer.sh;
```

2.2) Run these 2 commands (after the first one you have to enter the user's password)

```
./monitoring-installer.sh --1
./monitoring-installer.sh --3
```

3. Modify the prometheus config

```
nano etc/prometheus/prometheus.yml
```

Change lines to work with https (if https set)

```
 - job_name: 'avalanchego'
    metrics_path : '/ext/metrics'
    scheme: https
    static_configs:
       - targets: ['your-domain.com:9650']
```

4. Restart the process:

```
sudo systemctl restart prometheus
```

Then go and check that everything is up:

```
http://your-domain.com:9090
```

5. Remove juneogo from root

```
sudo deluser juneogo sudo
```
