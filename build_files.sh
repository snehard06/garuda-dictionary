#!/bin/bash
set -e

echo "Installing dependencies..."
# Vercel's Python environment is managed by uv (PEP 668).
# Use 'uv pip install --system' to install into the system-managed environment.
uv pip install --system -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput

# NOTE: 'manage.py migrate' is intentionally NOT run here.
# @vercel/static-build runs in a network-restricted build context and cannot
# reach the Neon PostgreSQL database. Run migrations separately via:
#   vercel run python manage.py migrate --noinput
# or once from your local machine with DATABASE_URL set.

echo "Build complete!"
