"""Starter app.

A small Flask app to build on. It is intentionally tiny - the interesting
work is the infrastructure around it, not the app itself.
"""
import json
import logging
import os
import pathlib
import uuid

import redis
from flask import Flask, g, jsonify, request, redirect, url_for

# Configuration comes from environment variables (twelve-factor style).
# Defaults let the app run standalone on your laptop without Redis.
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))


def read_build():
    """Timestamp of the last change to this app, from the BUILD file.

    Shown in the UI and on /health so you can tell at a glance which
    version is running. If the file is missing (e.g. it was not copied
    into the image), say so instead of failing.
    """
    build_file = pathlib.Path(__file__).with_name("BUILD")
    try:
        return build_file.read_text(encoding="utf-8").strip() or "unknown"
    except OSError:
        return "unknown"


BUILD = read_build()

app = Flask(__name__)


class JsonFormatter(logging.Formatter):
    """Emit each log record as one JSON line (structured logging)."""

    def format(self, record):
        entry = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        # Request fields are attached via `extra=` in the log call below.
        for key in ("method", "path", "status", "request_id"):
            if hasattr(record, key):
                entry[key] = getattr(record, key)
        return json.dumps(entry)


# Log to stdout - in a container, that is where logs are collected from.
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger = logging.getLogger("starter-app")
logger.setLevel(logging.INFO)
logger.addHandler(handler)
# Silence Flask's built-in (non-JSON) per-request log lines.
logging.getLogger("werkzeug").setLevel(logging.WARNING)


def get_redis():
    """Return a Redis client, or None if Redis is unreachable."""
    try:
        client = redis.Redis(
            host=REDIS_HOST, port=REDIS_PORT, socket_connect_timeout=1
        )
        client.ping()
        return client
    except redis.exceptions.RedisError:
        return None


@app.before_request
def assign_request_id():
    # Reuse the caller's correlation ID if present, otherwise create one.
    # This lets you follow one request across several services.
    g.request_id = request.headers.get("X-Request-ID", uuid.uuid4().hex[:8])


@app.after_request
def log_request(response):
    response.headers["X-Request-ID"] = g.request_id
    logger.info(
        "request handled",
        extra={
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "request_id": g.request_id,
        },
    )
    return response


@app.route("/")
def index():
    client = get_redis()
    if client is None:
        visits = "Redis not connected - visit counter unavailable."
    else:
        visits = f"You are visitor number {client.incr('visits')}."
    return (
        "<h1>Welcome to the life shop!</h1>"
        f"<p>{visits}</p>"
        f"<p><small>Build: {BUILD}</small></p>"
        f"<p></p>"
        "<ul>"
            f"<li><button type='button' onclick=\"location.href='/love'\">Love</button></li>"
            "<li><button type='button' onclick=\"location.href='/success'\">Success</button></li>"
            "<li><button type='button' onclick=\"location.href='/happiness'\">Happiness</button></li>"
        "</ul>"  
    )

@app.route("/love")
def love():
    client = get_redis()
    if client is None:
        message = "Redis not connected - buy counter unavailable."
    else:
        message = f"You have bought {int(client.get('love') or 0)} love."
    return (
        "<h1>Love</h1>"
        "<p>5c</p>"  
        "<form method='post' action='/love/buy'>"
            "<button type='submit'>Buy</button>"
        "</form>"
        f"<p>{message}</p>"
        "<p>Who knew that love was so cheap?</p>"
        "<button type='button' onclick=\"location.href='/'\">Back</button>"
    )

@app.route("/love/buy", methods=["POST"])
def love_buy():
    client = get_redis()
    if client is not None:
        client.incr("love")
    return redirect(url_for("love"))

@app.route("/success")
def success():
    client = get_redis()
    if client is None:
        message = "Redis not connected - buy counter unavailable."
    else:
        message = f"You have bought {int(client.get('success') or 0)} success."
    return (
        "<h1>Success</h1>"
        "<p>1 000 000 $</p>"  
        "<form method='post' action='/success/buy'>"
            "<button type='submit'>Buy</button>"
        "</form>"
        f"<p>{message}</p>"
        "<p>It's expensive...</p>"
        "<button type='button' onclick=\"location.href='/'\">Back</button>"
    )

@app.route("/success/buy", methods=["POST"])
def success_buy():
    client = get_redis()
    if client is not None:
        client.incr("success")
    return redirect(url_for("success"))

@app.route("/happiness")
def happiness():
    client = get_redis()
    if client is None:
        message = "Redis not connected - buy counter unavailable."
    else:
        message = f"You have bought {int(client.get('happiness') or 0)} happiness."
    return (
        "<h1>Happiness</h1>"
        "<p>50 $</p>"  
        "<form method='post' action='/happiness/buy'>"
            "<button type='submit'>Buy</button>"
        "</form>"
        f"<p>{message}</p>"
        "<p>You really can buy happiness!</p>"
        "<button type='button' onclick=\"location.href='/'\">Back</button>"
    )

@app.route("/happiness/buy", methods=["POST"])
def happiness_buy():
    client = get_redis()
    if client is not None:
        client.incr("happiness")
    return redirect(url_for("happiness"))


@app.route("/health")
def health():
    return jsonify(status="ok", build=BUILD)


@app.route("/hello/<name>")
def hello(name):
    return f"Hello, {name}!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
