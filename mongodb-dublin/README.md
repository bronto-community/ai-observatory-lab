# MongoDB Dublin: AI Observability & Monitoring

Bronto's talk and guided build at **MongoDB Dublin** (Building 2, 1 Ballsbridge, Shelbourne Road, Dublin 4) for
Dublin AI Week, hosted by Give(a)Go, on **Wednesday 7 October 2026**. Event page: <https://luma.com/observability>.

- **Deck:** <https://ai-observability-dublin.vercel.app> (source: [`slides/`](slides))
- **Lab guide:** <https://ai-observatory-lab.vercel.app/dublin> (source: [`../site/app/dublin/page.mdx`](../site/app/dublin/page.mdx))

## Run of show

| Time (Dublin, pm) | What | Deck |
|---|---|---|
| 6:00 | Doors, food, networking | title slide up |
| 6:30 | Welcome and build-session briefing (Give(a)Go) | |
| 6:40 | Harshit Mehta, MongoDB: "AI Observability in Action: MongoDB Atlas OTel Metrics Sink" (talk only) | |
| 6:55 | **Bronto talk**, 20 min | slides 1–11 |
| 7:15 | **Guided build**, 75 min: setup + six steps | slides 12–19 |
| 8:30 | Builds, lessons and questions | slide 20 |
| 8:45 | Food and networking; 9:00 close | slide 21 |

The build delivers what the event page promises:

- **Trace model, agent and tool activity:** step 2, where the agent sends its own traces to the attendee's Bronto.
- **Connect application signals with database metrics:** step 4, Atlas metrics through Bronto's metrics API, plus
  slow-query logs.
- **Investigate a production issue to its root cause:** steps 3, 5 and 6.

## What's here

| Path | What it is |
|---|---|
| [`slides/`](slides) | Slidev deck. `npm ci && npx slidev`; publish with `./deploy.sh` |
| [`agent/`](agent) | The lab's own AI SRE (Strands), one image with `AGENT_STEP=1..6`. Built from the repo root |
| [`storefront/`](storefront) | Builds `bronto-community/storefront-mongo`: Severin's Storefront up to v3.1.0, moved to MongoDB Atlas (v4.0.0), and the v4.1.0 release with the incident |
| [`harness/`](harness) | One EC2 instance running Storefront, its load and an OpenTelemetry Collector that forwards Storefront's telemetry to the shared Bronto demo org. It also relays Atlas's mongod log export: Caddy on 443 (TLS and a relay token) in front of the Collector, which turns each mongod line into one Bronto event with its fields. Atlas sends its metrics to Bronto directly |

## The incident

Storefront's checkout-api and catalog-api store their data in an Atlas M10 cluster with about 1.5M orders. Release
v4.1.0 has three commits, and one of them adds a query on `orders` that no index covers. Every checkout then scans the
collection. Here is what each signal shows:

| Signal | What it shows |
|---|---|
| Traces | A slow `mongodb` child span under `POST /checkout` |
| Atlas metrics | Query targeting and operation latency jump |
| Atlas logs | `Slow query … COLLSCAN` |
| GitHub | The commit, with its misleading message |

Don't share the details with attendees before 8:30. The speaker notes on slides 19–20 have the answer.

### Organiser checklist

**One-off setup**

1. **Atlas:** an M10 cluster called `storefront` and a database user with readWrite on `storefront`.
   - Add the harness's Elastic IP in Network Access.
   - Project → Integrations → OpenTelemetry:
     - **metrics** to `https://ingestion.eu.bronto.io/v1/metrics`;
     - **log export** (`mongod`) to the harness relay, `https://<elastic-ip-with-dashes>.sslip.io/v1/logs`.

     Metrics use the header `x-bronto-api-key` set to the ingestion key. The log export uses `X-Relay-Token` set to the relay token, `RELAY_TOKEN` in the gitignored `harness/.env`.
2. **Storefront repo:**
   - Run `sh storefront/build-history.sh /tmp/storefront-mongo`.
   - Push it to `bronto-community/storefront-mongo` with `git push -u origin main --tags`.
3. **Harness:** run `set -a; . harness/.env; set +a`, then `harness/deploy.sh` with `MONGODB_URI` set.
4. **Shared demo org:** the EU org. Its public "ReadOnly" key has the Lab read (logs + metrics) role, so it covers both MCP and the metrics API.
5. **Agent image:**
   ```bash
   docker buildx build --platform linux/amd64,linux/arm64 -f mongodb-dublin/agent/Dockerfile -t ghcr.io/bronto-community/mongodb-lab-agent --push .
   ```
   Make the package public on GHCR.
6. **Deck and guide:** run `mongodb-dublin/slides/deploy.sh`, and deploy `site/` as usual.

**Pre-event email**

Approved guests get setup guidance before the event. Ask them to arrive with:

- Docker installed
- a Gemini API key
- a Bronto account and its ingestion key
- the `ai-sre-issues` repo and its token
- `docker pull ghcr.io/bronto-community/mongodb-lab-agent` already done

**On the night**

The event's times are Dublin time, Irish Standard Time (UTC+1). The harness runs on **UTC**, so its hourly timers
fire at 19:00 and 19:15 Dublin time (18:00 and 18:15 UTC). Left alone, they would roll the incident back at 20:00
Dublin time, in the middle of step 5. Instead, switch the incident by hand from a laptop with
[`harness/night.sh`](harness/night.sh), which runs the commands on the instance over SSM:

| Dublin (IST) | UTC | Run | Effect |
|---|---|---|---|
| 19:00 | 18:00 | `./night.sh baseline` | Hourly timers off, good release `v4.0.0` live. 19:00–19:30 is the quiet baseline |
| 19:30 | 18:30 | `./night.sh release` | `v4.1.0` ships and checkout gets slow. Leave it running through the build |
| after 20:45 | after 19:45 | `./night.sh restore` | Good release back, hourly timers on again |

Run each from `mongodb-dublin/harness` with `AWS_PROFILE=bronto`, after `aws sso login --profile bronto`.
`./night.sh status` shows which release is live and the timers.

## Provisioned (5 October)

- **Atlas:** org "Stephen's Org", project `mongodb-dublin` (`6ac39bb035b2838e26badbdf`).
  - Cluster `storefront`: M10, AWS eu-west-1, MongoDB 8.0.
  - Database user `storefront`, with readWrite on the `storefront` database.
  - The password is in the gitignored `harness/.env`.
- **Atlas → Bronto metrics:** a custom OTEL metric integration that sends MongoDB and hardware metrics to `https://ingestion.eu.bronto.io/v1/metrics`. The test metric arrived in the shared EU org.
- **Bronto:** ingestion key "mongodb-dublin ingestion (Storefront + Atlas)", which expires 4 November 2026. It's in the gitignored `harness/.env`.
- **GitHub:** `bronto-community/storefront-mongo`, with the built history and tags.
- **Bronto public read-only key** ("ReadOnly", the same key as in Track B): moved from the built-in SearchApi role to a custom API role, **Lab read (logs + metrics)**.
  - Permissions: `logs_read`, `logs_read_pii` and `dashboards_read`.
  - `dashboards_read` is what Bronto checks for `GET /metrics` and `POST /timeseries/search`; Bronto has no metrics permission of its own.
  - MCP still works with it.

## Open questions

- **Atlas log export goes through the harness relay.** Bronto's `/v1/logs` accepts only an exact `application/x-protobuf` or `application/json` Content-Type. Bronto's base endpoint stores a whole OTLP batch as one flattened event, and Atlas's scheduled exports never arrived there anyway: only its tests did.
  - The relay accepts any OTLP encoding and keeps slow queries, warnings and errors.
  - Each record becomes its own event in `mongodb-dublin / atlas-mongod`, with `msg`, `attr.ns`, `attr.planSummary` and `attr.docsExamined` as fields.
  - Configure it through the Admin API (`PUT /groups/{id}/logIntegrations/{id}`, type `OTEL_LOG_EXPORT`). The UI's edit form re-sends the masked header value when it tests.
- The numbers in `slides/components/IncidentTrace.vue` and on the GenAI vocabulary slide are illustrative. Replace them with a real trace after rehearsal.
- Load (`CHECKOUT_RPS`) and seed size (`SEED_ORDERS`): tune them so the bad release costs about 1 s per checkout without saturating the M10.
