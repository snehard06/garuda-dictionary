#!/bin/bash
set -e

# @vercel/static-build runs with system Python 3.9 at /usr, regardless of
# .python-version. We use uv to explicitly install and activate Python 3.12,
# then create an isolated venv so all dependencies resolve correctly.

echo "Installing Python 3.12 via uv..."
uv python install 3.12

echo "Creating virtual environment with Python 3.12..."
uv venv .venv --python 3.12

echo "Installing dependencies into Python 3.12 venv..."
uv pip install -r requirements.txt

echo "Collecting static files..."
uv run python manage.py collectstatic --noinput

# NOTE: 'manage.py migrate' is intentionally NOT run here.
# @vercel/static-build has no network access to Neon PostgreSQL during build.
# Run migrations separately from your local machine with DATABASE_URL set:
#   DATABASE_URL="..." python manage.py migrate --noinput

echo "Build complete!"
