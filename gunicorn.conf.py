import os

# Render automatically provides $PORT (typically 10000)
# Binding to 0.0.0.0:$PORT is required for Render's reverse proxy to route traffic
port = os.environ.get("PORT", "5000")
bind = f"0.0.0.0:{port}"

# Optimize for cloud free-tier (512MB RAM)
workers = 1
threads = 4
timeout = 120
keepalive = 5

accesslog = "-"
errorlog = "-"
loglevel = "info"
