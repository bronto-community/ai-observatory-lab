#!/bin/bash
# Runs on the harness instance at first boot, and is safe to re-run over SSM:
#   BUCKET=... SECRET=... bash /root/bootstrap.sh
#
#   /opt/lab/demo/        compose, collector + Atlas log relay, Caddy, load, seed (from S3)
#   /opt/lab/storefront/  clone of bronto-community/storefront-mongo (tags v4.0.0, v4.1.0)
set -euo pipefail
: "${BUCKET:?}" "${SECRET:?}"

dnf install -y -q docker git make
systemctl enable --now docker
plugins=/usr/local/lib/docker/cli-plugins
mkdir -p "$plugins"
if ! docker compose version >/dev/null 2>&1; then
  curl -fsSL -o "$plugins/docker-compose" \
    "https://github.com/docker/compose/releases/download/v2.40.3/docker-compose-linux-aarch64"
  chmod +x "$plugins/docker-compose"
fi
if ! docker buildx version 2>/dev/null | grep -q 'v0\.\(1[7-9]\|[2-9][0-9]\)'; then
  curl -fsSL -o "$plugins/docker-buildx" \
    "https://github.com/docker/buildx/releases/download/v0.29.1/buildx-v0.29.1.linux-arm64"
  chmod +x "$plugins/docker-buildx"
fi

mkdir -p /opt/lab && cd /opt/lab
aws s3 cp --quiet "s3://$BUCKET/harness.tgz" /tmp/harness.tgz
rm -rf demo && tar -xzf /tmp/harness.tgz
if [ ! -d storefront ]; then
  git clone -q https://github.com/bronto-community/storefront-mongo.git storefront
fi
git -C storefront fetch -q --tags origin || true

cd demo
install -m 600 /dev/null .env
aws secretsmanager get-secret-value --secret-id "$SECRET" --query SecretString --output text > .env
# The relay's hostname: <public-ip>.sslip.io, with dashes (an Elastic IP, so it's stable).
imds=$(curl -fsS -X PUT -H "X-aws-ec2-metadata-token-ttl-seconds: 60" http://169.254.169.254/latest/api/token)
ip=$(curl -fsS -H "X-aws-ec2-metadata-token: $imds" http://169.254.169.254/latest/meta-data/public-ipv4)
echo "PUBLIC_HOST=${ip//./-}.sslip.io" >> .env
# Until the Elastic IP is in Atlas's access list, the seed can't connect: keep trying.
for i in $(seq 1 60); do make up && break; echo "waiting for Atlas access ($i)"; sleep 30; done

# The incident, every hour: a quiet baseline from :00, the bad release at :15.
cat > /etc/systemd/system/storefront@.service <<'UNIT'
[Unit]
Description=Storefront harness: make %i
After=docker.service
[Service]
Type=oneshot
WorkingDirectory=/opt/lab/demo
ExecStart=/usr/bin/make %i
UNIT
for action in rollback release; do
  when=$([ "$action" = rollback ] && echo '*-*-* *:00:00' || echo '*-*-* *:15:00')
  cat > "/etc/systemd/system/storefront-$action.timer" <<UNIT
[Unit]
Description=Storefront harness: $action at $when
[Timer]
OnCalendar=$when
Unit=storefront@$action.service
Persistent=false
[Install]
WantedBy=timers.target
UNIT
done
systemctl daemon-reload
systemctl enable --now storefront-rollback.timer storefront-release.timer
systemctl list-timers 'storefront-*' --no-pager
echo "Storefront on Atlas is up; the incident replays hourly at :15."
echo "Atlas log export endpoint: https://${ip//./-}.sslip.io/v1/logs (header X-Relay-Token)"
