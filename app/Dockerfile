FROM python:3.15 AS build 
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.15-slim
# Pull in Debian security fixes not yet in the base image (e.g. libzstd1 CVE-2026-124851)
RUN apt-get update \
 && apt-get upgrade -y --no-install-recommends \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=build /install /usr/local 
RUN pip uninstall -y pip
COPY . .
RUN useradd --system --uid 10001 --no-create-home appuser
USER appuser
ENV PYTHONUNBUFFERED=1
CMD ["opentelemetry-instrument", "python", "app.py"]