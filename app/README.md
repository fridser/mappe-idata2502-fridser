# app/

The "life shop": a small Flask webapp where you can buy love, happiness and
success. The app is deliberately simple. The interesting part of the project
is the infrastructure around it (see the [main README](../README.md)).

**Stack:** Python 3.15 + Flask, Redis for the counters, Prometheus metrics and
OpenTelemetry traces.

## Routes

| Route             | Method | What it does                                                                 |
| ----------------- | ------ | ---------------------------------------------------------------------------- |
| `/`               | GET    | Shop front page with a visit counter, the build stamp and links to the three products. |
| `/love`           | GET    | Product page for love (5c): a buy button, how many have been bought, and a back button. |
| `/love/buy`       | POST   | Increments the `love` counter in Redis and redirects back to `/love`.        |
| `/happiness`      | GET    | Product page for happiness (50 $).                                           |
| `/happiness/buy`  | POST   | Increments the `happiness` counter and redirects back to `/happiness`.       |
| `/success`        | GET    | Product page for success (1 000 000 $).                                      |
| `/success/buy`    | POST   | Increments the `success` counter and redirects back to `/success`.           |
| `/health`         | GET    | Returns `{"status": "ok", "build": "..."}` for health checks.                |
| `/metrics`        | GET    | Prometheus metrics in the text exposition format.                            |

Without Redis the pages say the counter is unavailable, and the app keeps
running. The `/buy` routes only accept POST, so a GET returns 405.

## Run it

```bash
cd app
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open <http://localhost:5000>. To run it with Redis and the whole
monitoring stack, use `docker compose up -d` from the repository root.

## Tests

```bash
pip install pytest
pytest
```

The tests check that `/health` answers OK and that `/love/buy` rejects GET.
CI runs them on every push.

## Docker

```bash
docker build -t life-shop .
docker run -p 5000:5000 life-shop
```

The [Dockerfile](Dockerfile) is a two-stage build. The final image is based on
`python:3.15-slim`, installs Debian security updates, removes `pip`, and runs
as a non-root system user (`appuser`, uid 10001). The app starts under
`opentelemetry-instrument`, which adds tracing without code changes.

CI publishes the image to `ghcr.io/fridser/mappe-idata2502-fridser`, tagged
`latest` and with the short commit SHA.

## Configuration

Configuration comes from environment variables, so the same image runs
anywhere without being rebuilt.

| Variable                       | Default     | Purpose                                              |
| ------------------------------ | ----------- | ---------------------------------------------------- |
| `REDIS_HOST`                   | `localhost` | Hostname of the Redis server.                        |
| `REDIS_PORT`                   | `6379`      | Redis port.                                          |
| `OTEL_SERVICE_NAME`            | `app`       | Service name on metrics and traces.                  |
| `OTEL_EXPORTER_OTLP_ENDPOINT`  | -           | Where traces are sent (`http://tempo:4318` in compose). |

The compose files set the rest of the `OTEL_*` variables: traces go to Tempo
over OTLP, and `/health` and `/metrics` are excluded from tracing.

## Observability

### Logs

The app writes **structured JSON logs to stdout**, one line per request, with
`timestamp`, `level`, `message`, `method`, `path`, `status`, `request_id` and
`trace_id`. In the stack, Alloy reads them from Docker and ships them to Loki.

`request_id` is taken from the `X-Request-ID` header when the caller sends
one, otherwise generated, and is echoed back in the response headers. It works
as a correlation ID across services. `trace_id` links a log line to its trace
in Tempo.

### Metrics

`/metrics` exposes two metrics, which Prometheus scrapes:

- `http_requests_total`: a counter labelled by `service`, `method`, `path` and `status`
- `http_request_duration_seconds`: a latency histogram labelled by `service`, `method` and `path`

`path` is the route pattern, not the raw URL, to keep the number of label
values low.

### Traces

OpenTelemetry instruments Flask and Redis automatically, so each request
becomes a trace with a span for every Redis call.

Requests to `/health` and `/metrics` are not logged, counted or traced, so
health checks and scrapes don't drown out real traffic.

## Build stamp

The [BUILD](BUILD) file holds a timestamp for when the app was last changed.
The app shows it on `/` and on `/health`, so you can tell which version is
running.
