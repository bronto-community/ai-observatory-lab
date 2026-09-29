#!/bin/sh
# Publish the deck to https://observability-for-ai-lab.vercel.app (Vercel team: brontoio).
#
# The deck is built here and uploaded as a static site, because code slides
# import ../agent through a symlink that a Vercel build can't follow, and so
# nothing outside dist/ (like the repo's .env) is ever uploaded.
set -e
cd "$(dirname "$0")"
npm run build
rm -rf .vercel-deploy/assets .vercel-deploy/img .vercel-deploy/lab
find .vercel-deploy -maxdepth 1 -type f ! -name vercel.json -delete 2>/dev/null || true
mkdir -p .vercel-deploy
cp -R dist/. .vercel-deploy/
# The lab guide (../README.md) at /lab
uvx --from markdown python build-lab-page.py .vercel-deploy
# Static upload: no install, no build on Vercel's side.
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
[ -d .vercel ] || vercel link --yes --project observability-for-ai-lab --scope brontoio
vercel deploy --prod --yes --scope brontoio
