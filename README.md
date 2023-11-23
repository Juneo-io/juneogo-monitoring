# Node Monitoring

If you wish to monitor your JuneoGo node, it is possible to do so by using the [juneogo-monitoring](https://github.com/Juneo-io/juneogo-monitoring) repository. This repository implements Prometheus and Graphana to monitor, store, and display key JuneoGo node metrics.

## Installation instructions
These installation instructions assume that you already have Docker and docker-compose installed on your system. For more information, please refer to their documentation: https://docs.docker.com/get-docker/

First, open the command line on the machine running your node and execute the following command:

```bash
git clone https://github.com/Juneo-io/juneogo-monitoring
```

## Configuring Prometheus

If you are running juneogo using [juneogo-docker](https://github.com/Juneo-io/juneogo-docker), you may skip this configuration step and proceed to the Start Monitoring step.

Users who set up their JuneoGo node [manually](https://docs.juneo.com/intro/build/set-up-and-connect-a-node-manually) or with the [install script](https://docs.juneo.com/intro/build/set-up-and-connect-a-node) - it is important to follow this configuration step for all metrics to be monitored.

If you are publicly exposing port `9650` with the juneogo `http-host` configuration flag set to your public ip address (allowing remote RPC calls to your node), you will need to update the `./prometheus/prometheus.yml` file.

Specifically, you will have to update the `"targets"` value for the job_name of `"juneogo"` to your public ip address rather than localhost.

Example:

```yaml
- job_name: "juneogo"
    static_configs:
      - targets: ['XX.XX.XX.XX:9650']
```

If you are not publicly exposting port `9650`, you may skip this step.

## Start Monitoring

```bash
docker-compose up -d
```

Grafana should be accessible through port 3000, use login: admin and password: admin

Prometheus should be accessible through port 9090.
