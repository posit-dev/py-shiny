#!/usr/bin/env bash

set -euo pipefail

if [ -n "${PLAYWRIGHT_PORT:-}" ]; then
  container_port="$PLAYWRIGHT_PORT"
  published_port="127.0.0.1:${container_port}:${container_port}"
else
  container_port=$(python3 - <<'PY'
import socket

with socket.socket() as sock:
    sock.bind(("127.0.0.1", 0))
    print(sock.getsockname()[1])
PY
  )
  # An empty host port tells Docker to select an available port.
  published_port="127.0.0.1::${container_port}"
fi

# TCP and UDP port numbers are unsigned 16-bit integers.
if ! [[ "$container_port" =~ ^[0-9]+$ ]] || [ "$container_port" -lt 1 ] || [ "$container_port" -gt 65535 ]; then
  echo "Invalid Playwright server port: $container_port" >&2
  exit 1
fi

docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true

# No --rm: if the server crashes, the container must survive so the
# logs-on-failure step can read it. The command above removes an old container.
# Playwright exits run-server when stdin closes. Keep stdin open in detached
# mode, as required by Playwright's documented Docker setup.
docker run -d \
  --interactive \
  --tty \
  --name "$CONTAINER_NAME" \
  --ipc=host \
  -p "$published_port" \
  --init \
  --workdir /home/pwuser \
  --user pwuser \
  "$IMAGE_REF" \
  /bin/sh -c "npx --no -- playwright run-server --port $container_port --host 0.0.0.0"

host_binding=$(docker port "$CONTAINER_NAME" "$container_port/tcp")
host_port="${host_binding##*:}"
if ! [[ "$host_port" =~ ^[0-9]+$ ]]; then
  echo "Could not resolve the Playwright server host port: $host_binding" >&2
  exit 1
fi

echo "host-port=$host_port" >> "$GITHUB_OUTPUT"
