# Workshop Backend

This directory contains an isolated Python backend for executing notebook cells outside GitHub Pages.

## What it does

- exposes a small JSON API for code execution;
- keeps a Python session per `session_id`;
- captures `stdout`, `stderr`, and matplotlib figures;
- reuses the project environment, including `utils`, `src`, notebooks helpers, and `birt-gd` when available.

## Endpoints

- `GET /health`
- `POST /session/init`
- `POST /session/reset`
- `POST /execute`
- `DELETE /session?session_id=...`

## Run locally

```bash
poetry run python -m backend.app
```

By default the backend listens on `0.0.0.0:8765`.

## Useful environment variables

- `WORKSHOP_BACKEND_HOST`
- `WORKSHOP_BACKEND_PORT`
- `WORKSHOP_BACKEND_ALLOW_ORIGIN`

Example:

```bash
WORKSHOP_BACKEND_HOST=0.0.0.0 \
WORKSHOP_BACKEND_PORT=8765 \
WORKSHOP_BACKEND_ALLOW_ORIGIN="https://manuelfjr.github.io" \
poetry run python -m backend.app
```

## Cluster-oriented deployment idea

On a cluster accessed by SSH, a practical first step is:

1. clone the repository on the cluster;
2. create the Poetry environment;
3. start the backend inside `tmux` or `screen`;
4. expose the service through the institution's reverse proxy or an SSH tunnel;
5. point the workshop site to the backend URL.

Example with `tmux`:

```bash
tmux new -s latent-runtime
cd /path/to/latent-ability-ml
poetry install
WORKSHOP_BACKEND_HOST=0.0.0.0 WORKSHOP_BACKEND_PORT=8765 poetry run python -m backend.app
```

Then use your cluster ingress or a reverse proxy to publish the endpoint safely over HTTPS.

## Site integration

### Local development

Start the backend:

```bash
./backend/run_local.sh
```

Start the site with the local backend config:

```bash
RBENV_VERSION=3.2.2 /Users/manuelfjr/.rbenv/versions/3.2.2/bin/jekyll serve --source site --config site/_config.yml,site/_config.local.yml --host 127.0.0.1 --port 4000
```

### Cluster deployment

1. Run the backend on the cluster with `./backend/run_cluster.sh`.
2. Expose it over HTTPS.
3. Copy `site/_config.cluster.example.yml` to a real config file and set the cluster URL.
4. Build or serve Jekyll with that extra config layered on top of `site/_config.yml`.
