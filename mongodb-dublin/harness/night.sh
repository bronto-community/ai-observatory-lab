#!/bin/sh
# Run the incident on the event's schedule instead of the hourly timers, from a laptop:
#
#   AWS_PROFILE=bronto ./night.sh baseline   # 19:00 Dublin: stop the timers, good release (quiet baseline)
#   AWS_PROFILE=bronto ./night.sh release    # 19:30 Dublin: ship v4.1.0, checkout gets slow
#   AWS_PROFILE=bronto ./night.sh restore    # after 20:45 Dublin: good release, hourly timers back on
#   AWS_PROFILE=bronto ./night.sh status     # which release is live, and the timers
#
# The instance runs on UTC; Dublin in October is Irish Standard Time, UTC+1.
set -eu
REGION=${AWS_REGION:-eu-west-1}
STACK=${STACK:-mongodb-dublin-harness}

case "${1:-}" in
  baseline) cmd='systemctl stop storefront-release.timer storefront-rollback.timer && make -C /opt/lab/demo rollback' ;;
  release)  cmd='make -C /opt/lab/demo release' ;;
  restore)  cmd='make -C /opt/lab/demo rollback && systemctl start storefront-rollback.timer storefront-release.timer' ;;
  status)   cmd='git -C /opt/lab/storefront describe --tags; systemctl list-timers storefront-* --no-pager' ;;
  *) echo "usage: $0 baseline|release|restore|status" >&2; exit 2 ;;
esac

instance=$(aws cloudformation describe-stacks --region "$REGION" --stack-name "$STACK" \
  --query "Stacks[0].Outputs[?OutputKey=='InstanceId'].OutputValue" --output text)
id=$(aws ssm send-command --region "$REGION" --instance-ids "$instance" --document-name AWS-RunShellScript \
  --parameters "commands=[\"$cmd\"]" --query Command.CommandId --output text)
while :; do
  status=$(aws ssm get-command-invocation --region "$REGION" --command-id "$id" --instance-id "$instance" \
    --query Status --output text 2>/dev/null || echo Pending)
  case $status in Pending|InProgress|Delayed) sleep 3 ;; *) break ;; esac
done
aws ssm get-command-invocation --region "$REGION" --command-id "$id" --instance-id "$instance" \
  --query StandardOutputContent --output text | tail -n 8
echo "$1: $status"
[ "$status" = Success ]
