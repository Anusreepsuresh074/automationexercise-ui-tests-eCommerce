# Reproducible test runner: the official Playwright image already has the
# browsers and their system dependencies, pinned to the same version as
# requirements.txt.
FROM mcr.microsoft.com/playwright/python:v1.49.1-noble

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Credentials come from the environment at run time, never baked in:
#   docker run --rm --env-file .env ui-tests -m smoke -n 4
ENTRYPOINT ["pytest"]
