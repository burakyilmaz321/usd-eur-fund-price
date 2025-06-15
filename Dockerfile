# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.10-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Set the working directory to /app
WORKDIR /app

# Copy the working directory contents into the container at /app
COPY . .

# Install locked dependencies
RUN uv sync --locked

# Run app.py when the container launches
CMD exec uv run gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
