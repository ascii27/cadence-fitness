#!/usr/bin/env bash
# Build the SPA, bundle it into the backend, ship to the exe.dev VM, restart.
#
# Usage: deploy/deploy.sh
# Requires: ssh access to cadence-fitness.exe.xyz, node/npm + uv locally.
set -euo pipefail

VM="cadence-fitness.exe.xyz"
REMOTE_DIR="/home/exedev/cadence"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "==> Building frontend"
npm --prefix "$ROOT/frontend" install --silent
npm --prefix "$ROOT/frontend" run build

echo "==> Bundling SPA into backend/static"
rm -rf "$ROOT/backend/static"
cp -r "$ROOT/frontend/dist" "$ROOT/backend/static"

echo "==> Syncing backend to $VM:$REMOTE_DIR"
ssh -o StrictHostKeyChecking=accept-new "$VM" "mkdir -p $REMOTE_DIR"
rsync -az --delete \
  --exclude '.venv' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '.pytest_cache' \
  --exclude 'cadence.db' \
  --exclude '.env' \
  "$ROOT/backend/" "$VM:$REMOTE_DIR/"

echo "==> Installing systemd unit (if changed) and restarting"
scp "$ROOT/deploy/cadence.service" "$VM:/tmp/cadence.service"
ssh "$VM" "sudo mv /tmp/cadence.service /etc/systemd/system/cadence.service && \
  sudo systemctl daemon-reload && \
  sudo systemctl enable cadence.service >/dev/null 2>&1 || true && \
  cd $REMOTE_DIR && /usr/local/bin/uv sync --quiet && \
  sudo systemctl restart cadence.service"

echo "==> Waiting for health"
sleep 3
curl -fsS "https://$VM/api/health" && echo "  OK"
echo "==> Deployed: https://$VM"
