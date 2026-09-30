#!/bin/sh
# Deploy (or update) the always-on Track B harness in the Bronto AWS account.
#
#   AI_SRE_LAB_DIR=~/path/to/ai-sre-lab BRONTO_INGEST_KEY=... AWS_PROFILE=bronto ./deploy.sh
#
# AI_SRE_LAB_DIR is a checkout of bronto-community/ai-sre-lab (internal): its
# demo/ directory and .storefront-shas are packed and uploaded to the stack's
# private bucket. They are never committed to this public repo.
set -eu
cd "$(dirname "$0")"
: "${AI_SRE_LAB_DIR:?point AI_SRE_LAB_DIR at an ai-sre-lab checkout}" "${BRONTO_INGEST_KEY:?}"
STACK=${STACK:-ai-observatory-track-b-harness}
REGION=${AWS_REGION:-eu-west-1}

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
tar -czf "$tmp/harness.tgz" -C "$AI_SRE_LAB_DIR" --exclude '.deploy*' --exclude '.env' demo .storefront-shas

aws cloudformation deploy --region "$REGION" --stack-name "$STACK" --template-file template.yml \
  --capabilities CAPABILITY_IAM --parameter-overrides "BrontoIngestionKey=$BRONTO_INGEST_KEY" --no-fail-on-empty-changeset

bucket=$(aws cloudformation describe-stacks --region "$REGION" --stack-name "$STACK" \
  --query "Stacks[0].Outputs[?OutputKey=='HarnessBucket'].OutputValue" --output text)
aws s3 cp --region "$REGION" "$tmp/harness.tgz" "s3://$bucket/harness.tgz"
aws s3 cp --region "$REGION" bootstrap.sh "s3://$bucket/bootstrap.sh"
instance=$(aws cloudformation describe-stacks --region "$REGION" --stack-name "$STACK" \
  --query "Stacks[0].Outputs[?OutputKey=='InstanceId'].OutputValue" --output text)
echo "Stack $STACK in $REGION: bucket $bucket, instance $instance"
echo "First boot takes ~10 min (images build, then a baseline). Watch it with:"
echo "  aws ssm start-session --region $REGION --target $instance"
