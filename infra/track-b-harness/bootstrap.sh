#!/bin/bash
# Runs on the harness instance at first boot (from the stack's user data), and
# is safe to re-run over SSM after updating the tarball:
#   BUCKET=... BRONTO_API_KEY=... bash /root/bootstrap.sh
#
# Layout matches Severin's repo, which the Makefile expects:
#   /opt/lab/demo/            the harness (from S3, not public: it gives the incident away)
#   /opt/lab/.storefront-shas GOOD_SHA / BAD_SHA
#   /opt/lab/storefront/      clone of the public ai-sre-lab/storefront repo
set -euo pipefail
: "${BUCKET:?}" "${BRONTO_API_KEY:?}"

dnf install -y -q docker git make
systemctl enable --now docker

# AL2023's docker package has no compose v2 plugin, and ships an old buildx.
plugins=/usr/local/lib/docker/cli-plugins
mkdir -p "$plugins"
if ! docker compose version >/dev/null 2>&1; then
  curl -fsSL -o "$plugins/docker-compose" \
    "https://github.com/docker/compose/releases/download/v2.40.3/docker-compose-linux-aarch64"
  chmod +x "$plugins/docker-compose"
fi

mkdir -p /opt/lab && cd /opt/lab
aws s3 cp -q "s3://$BUCKET/harness.tgz" /tmp/harness.tgz
rm -rf demo && tar -xzf /tmp/harness.tgz
bash demo/setup-host.sh

# Clone once and keep every object locally: both release commits stay
# deployable even if the public repo is reset later.
if [ ! -d storefront ]; then
  git clone -q https://github.com/ai-sre-lab/storefront.git storefront
fi
git -C storefront fetch -q --tags origin || true

cd demo
install -m 600 /dev/null .env
printf 'BRONTO_API_KEY=%s\n' "$BRONTO_API_KEY" > .env
make up

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
Persistent=false
[Install]
WantedBy=timers.target
UNIT
done
systemctl daemon-reload
systemctl enable --now storefront-rollback.timer storefront-release.timer
systemctl list-timers 'storefront-*' --no-pager
echo "Storefront harness is up; the incident replays hourly at :15."
