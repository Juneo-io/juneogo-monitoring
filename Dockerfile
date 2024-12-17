# Step 1: Use an Alpine base image
FROM alpine:latest

# Step 2: Install necessary dependencies
RUN apk add --no-cache python3 py3-pip curl

# Step 3: Create a virtual environment and install packages
RUN python3 -m venv /venv && \
    /venv/bin/pip install pyyaml python-dotenv requests

# Step 4: Download and install Prometheus
RUN curl -LO https://github.com/prometheus/prometheus/releases/download/v3.0.1/prometheus-3.0.1.linux-amd64.tar.gz && \
    tar -xzf prometheus-3.0.1.linux-amd64.tar.gz && \
    mv prometheus-3.0.1.linux-amd64/prometheus /usr/local/bin/ && \
    mv prometheus-3.0.1.linux-amd64/promtool /usr/local/bin/ && \
    rm -rf prometheus-3.0.1.linux-amd64*

# Step 5: Set the working directory
WORKDIR /app

# Step 6: Command to generate configuration and start Prometheus
CMD sh -c "/venv/bin/python /app/prometheus/generate_prometheus_config.py && \
    /venv/bin/python /app/prometheus/add_subdomains.py && \
    prometheus --config.file=/app/prometheus/prometheus.yml --storage.tsdb.path=/app/prometheus/data"
