#!/usr/bin/env bash
set -euo pipefail

docker compose down
git pull
docker compose build
docker compose up -d
