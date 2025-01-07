# Node Monitoring

If you wish to monitor your JuneoGo node, it is possible to do so by using the [juneogo-monitoring](https://github.com/Juneo-io/juneogo-monitoring) repository. This repository implements Prometheus and Graphana to monitor, store, and display key JuneoGo node metrics.

It assume also that you have a JuneoGo node running with the required endpoints for Prometheus and JuneoGo metrics.

## Installation instructions

These installation instructions assume that you already have Docker and docker-compose installed on your system. For more information, please refer to their documentation: https://docs.docker.com/get-docker/

First, open the command line on the machine running your node and execute the following command:

```bash
git clone https://github.com/Juneo-io/juneogo-monitoring
```

## Configuring Prometheus

If you use secure metrics endpoints, you need to configure Prometheus to use the correct credentials.

1. Create a `.env` file in the root directory of the project with the following variables:
   ```env
   PROMETHEUS_USERNAME=<your_prometheus_username>
   PROMETHEUS_PASSWORD=<your_prometheus_password>
   ```

- `PROMETHEUS_USERNAME`: The username to access the Prometheus metrics endpoint.
- `PROMETHEUS_PASSWORD`: The password to access the Prometheus metrics endpoint.

Each server need to have the same credentials. If you have different credentials for each server, you need to modify the `prometheus.yml` file.

### Configuring servers.json

To ensure proper monitoring and DNS configuration, you must configure the `servers.json` files. Check the `servers.example.json` file for an example.

Each server entry should include:

- `name`: A name to identify the server.
- `target`: The target address to fetch metrics from.
- `ip`: The IP address for DNS configuration.

Example:

```json
{
  "servers": [
    {
      "name": "server1",
      "target": "server1.mydomain.com",
      "ip": "10.10.10.1"
    },
    {
      "name": "server2",
      "target": "server2.mydomain.com",
      "ip": "10.10.10.2"
    }
  ]
}
```

The target need to expose 2 endpoints:

- `/metrics` for Prometheus metrics.
- `/ext/metrics` for juneogo metrics.

Follow the [juneogo-docker](https://github.com/Juneo-io/juneogo-docker) repository to deploy your JuneoGo node with the required endpoints.

## Configuring Caddy

To be able to access to Grafana with HTTPS, you need to configure Caddy with your domain name.

1. Add The domain name to your DNS configuration with the IP address of the machine running the monitoring.

2. Create a `.env` file in the root directory of the project with the following variables:

   ```env
   CADDY_DOMAIN=<your_domain>
   CADDY_EMAIL=<your_email>
   GF_SERVER_ROOT_URL=<your_domain>
   ```

## Configuring Cloudflare

To automatically manage DNS records for your servers using Cloudflare, follow these steps:

1. Create a `.env` file in the root directory of the project with the following variables:

   ```env
   CLOUDFLARE_READ_TOKEN=<your_cloudflare_read_token>
   CLOUDFLARE_WRITE_TOKEN=<your_cloudflare_write_token>
   ```

2. Ensure your both token have access to all target DNS zones present in your `servers.json` file.

3. Ensure your `servers.json` file is correctly populated with your server details (in Socotra and/or Mainnet).

If you do not provide Cloudflare tokens, DNS will not be managed automatically.

## Configuring Telegram Bot for Notifications

To receive notifications via Telegram, follow these steps:

1. Create a Telegram bot and get the bot token. Refer to the [Telegram documentation](https://core.telegram.org/bots#6-botfather) for instructions.

2. Create a Telegram group and add the bot to the group.

3. Invite the `@getmyid_bot` to the group and get the chat id.

4. Create a `.env` file in the root directory of the project with the following variables:

   ```env
   BOT_TOKEN=<your_telegram_bot_token>
   CHAT_ID_SOCOTRA=<your_telegram_chat_id>
   CHAT_ID_MAINNET=<your_telegram_chat_id>
   ```

   You can use the same chat id for both Socotra and Mainnet, or use different chat ids for each.
   Different chat ids can be useful if you want to receive notifications for Socotra on one group and Mainnet on another.
   If you do not provide Telegram tokens, notifications will not be sent.

## Start Monitoring

```bash
docker-compose up -d
```

If you want to have grafana accessible with port 3000, you need to uncomment the grafana port configuration in the docker-compose.yml file.

Grafana should be accessible with user: `admin` and password: `admin`
