#!/bin/sh
# Publish the deck to https://ai-observability-dublin.vercel.app (Vercel team: brontoio),
# as a static build so nothing outside dist/ is ever uploaded.
set -e
cd "$(dirname "$0")"
npm run build
rm -rf .vercel-deploy/assets .vercel-deploy/img
find .vercel-deploy -maxdepth 1 -type f ! -name vercel.json -delete 2>/dev/null || true
mkdir -p .vercel-deploy
cp -R dist/. .vercel-deploy/
cat > .vercel-deploy/vercel.json <<'JSON'
{
  "framework": null,
  "installCommand": "",
  "buildCommand": "",
  "outputDirectory": ".",
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
JSON
cd .vercel-deploy
[ -d .vercel ] || vercel link --yes --project ai-observability-dublin --scope brontoio
vercel deploy --prod --yes --scope brontoio
