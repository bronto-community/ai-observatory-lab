#!/bin/sh
# Deploy (or update) the MongoDB Dublin harness.
#
#   BRONTO_INGEST_KEY=... MONGODB_URI=... RELAY_TOKEN=... AWS_PROFILE=bronto ./deploy.sh
#
# Then add the PublicIp output to Atlas → Network Access before the services
# can reach the cluster (bootstrap retries until they can).
set -eu
cd "$(dirname "$0")"
: "${BRONTO_INGEST_KEY:?}" "${MONGODB_URI:?}" "${RELAY_TOKEN:?}"
STACK=${STACK:-mongodb-dublin-harness}
REGION=${AWS_REGION:-eu-west-1}

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
COPYFILE_DISABLE=1 tar -czf "$tmp/harness.tgz" --no-xattrs --exclude .env demo

aws cloudformation deploy --region "$REGION" --stack-name "$STACK" --template-file template.yml \
  --capabilities CAPABILITY_IAM --no-fail-on-empty-changeset --parameter-overrides \
  "BrontoIngestionKey=$BRONTO_INGEST_KEY" "BrontoRegion=${BRONTO_REGION:-eu}" "MongoUri=$MONGODB_URI" "RelayToken=$RELAY_TOKEN"

out() { aws cloudformation describe-stacks --region "$REGION" --stack-name "$STACK" \
  --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue" --output text; }
bucket=$(out HarnessBucket)
aws s3 cp --region "$REGION" "$tmp/harness.tgz" "s3://$bucket/harness.tgz"
aws s3 cp --region "$REGION" bootstrap.sh "s3://$bucket/bootstrap.sh"
echo "Stack $STACK in $REGION: instance $(out InstanceId), public IP $(out PublicIp)"
echo "First boot takes ~20 min (seeding 1.5M orders, image builds). Watch it with:"
echo "  aws ssm start-session --region $REGION --target $(out InstanceId)"
