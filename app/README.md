# app/

A small Flask web app to build on. It is deliberately simple: the interesting
work is the infrastructure you put around it, not the app itself.

**Stack:** Python + Flask, with optional Redis for a visit counter.

## Routes

| Route           | What it does                                                                                              |
| --------------- | --------------------------------------------------------------------------------------------------------- |
| `/`             | Welcome page with a visit counter and the build stamp. Without Redis it says so - the app still runs.      |
| `/health`       | Returns `{"status": "ok", "build": "..."}` - a machine-readable endpoint for health checks.                |
| `/hello/<name>` | Says hello.                                                                                                |

## Run it

```bash
cd app
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open <http://localhost:5000>. Redis is optional - without it the app
still works, only the visit counter is unavailable.

## Configuration

Configuration comes from environment variables, so the same image can run
anywhere without being rebuilt.

| Variable     | Default     | Purpose                                                     |
| ------------ | ----------- | ------------------------------------------------------------- |
| `REDIS_HOST` | `localhost` | Hostname of the Redis server.                                 |
| `REDIS_PORT` | `6379`      | Redis port.                                                   |

## Build stamp

The `BUILD` file holds a timestamp for when this app was last changed, and
the app shows it on `/` and on `/health`. Compare it against the template to
see whether you are running the current version.

Once you start changing the app yourself, the stamp is yours to do what you
like with - overwrite it during your own build, or drop it.

## Logging

The app writes **structured JSON logs to stdout** - one JSON line per request
with `timestamp`, `level`, `method`, `path`, `status` and `request_id`.

`request_id` is taken from the `X-Request-ID` header when the caller sends
one, otherwise generated, and is echoed back in the response headers. That
makes it a *correlation ID*: one request can be followed through the logs of
several services.

Logging to stdout rather than to a file is what makes `docker logs` and log
collectors work.
