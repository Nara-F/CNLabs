FROM python:3.14.6-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends make && rm -rf /var/lib/apt/lists/*
WORKDIR /work
COPY . .
RUN python --version && make build
CMD ["make", "grade"]
