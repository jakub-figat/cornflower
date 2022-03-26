#!/usr/bin/env sh

set -e
set -u


rabbitmq_ready() {
  nc -z -i 2 "${RABBITMQ_HOST}" "${RABBITMQ_PORT}"
}

until rabbitmq_ready; do
  echo "RabbitMQ is not available, waiting..."
done

echo "RabbitMQ connection established, continuing..."

exec "$@"