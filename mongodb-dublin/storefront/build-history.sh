#!/bin/sh
# Build the git history of bronto-community/storefront-mongo: Severin's
# Storefront up to v3.1.0, the move to MongoDB Atlas (v4.0.0, the good build),
# and the v4.1.0 release (three commits, one of which slows checkout).
#
#   sh build-history.sh /path/to/new/clone
#   cd /path/to/new/clone && git push -u origin main --tags
#
# Prints GOOD_SHA / BAD_SHA for the harness at the end.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
out=${1:?usage: build-history.sh OUT_DIR}

git clone -q https://github.com/ai-sre-lab/storefront.git "$out"
cd "$out"
git checkout -q -B main v3.1.0
git remote set-url origin https://github.com/bronto-community/storefront-mongo.git
git tag -d v3.2.0 >/dev/null

commit() { # author email date message overlay-dir
  cp -R "$here/$5/." .
  git add -A
  GIT_AUTHOR_NAME="$1" GIT_AUTHOR_EMAIL="$2" GIT_AUTHOR_DATE="$3" \
  GIT_COMMITTER_NAME="$1" GIT_COMMITTER_EMAIL="$2" GIT_COMMITTER_DATE="$3" \
    git commit -q -m "$4"
}

commit "Tomas Ek" tomas@storefront.example "2026-09-28T10:20:00+02:00" \
"feat: move catalog and orders to MongoDB Atlas

catalog-api reads the listing from the products collection and
checkout-api writes every confirmed order to orders. Both trace their
database calls (opentelemetry-instrumentation-pymongo), so a slow query
shows up as a child span of the request.

Indexes live in scripts/create_indexes.py." v4.0.0
git tag v4.0.0
good=$(git rev-parse HEAD)

commit "Mira Halvorsen" mira@storefront.example "2026-10-01T11:05:00+02:00" \
"perf(catalog): only fetch the fields the listing renders

The listing only needs the SKU. Project it in the query instead of
pulling whole product documents over the wire." release/1-catalog-projection

commit "Jonas Brandt" jonas@storefront.example "2026-10-01T16:42:00+02:00" \
"feat(checkout): flag returning customers for the loyalty banner

Marketing wants a 'welcome back' banner on the confirmation page. One
count of the customer's previous orders before the charge; orders are
already indexed by customer, so this is cheap." release/2-returning-customer

commit "Mira Halvorsen" mira@storefront.example "2026-10-02T09:30:00+02:00" \
"chore(deps): bump pymongo to 4.15.3

Patch release: connection-pool and retry fixes, no API changes." release/3-pymongo
git tag v4.1.0
bad=$(git rev-parse HEAD)

echo "GOOD_SHA=$good"
echo "BAD_SHA=$bad"
