# Runtime Deployment

The workshop site is static on GitHub Pages, but executable cells that need the full Poetry environment (including `birt-gd`) must run on a separate Python service.

## Recommended shape

- Frontend: GitHub Pages
- Runtime API: Render web service running `tools/notebook_runtime_server.py`

## Deploy on Render

1. Push this repository to GitHub.
2. In Render, create a new **Blueprint** deployment from the repository.
3. Render will pick up [`render.yaml`](./render.yaml).
4. After the service is live, copy the public URL.

Expected health check:

```text
https://YOUR-RUNTIME.onrender.com/health
```

It should return JSON with `ok: true`.

## Connect the Pages site to the runtime

In the GitHub repository settings, create an **Actions variable**:

- Name: `RUNTIME_API_URL`
- Value: your runtime URL, for example `https://latent-ability-runtime.onrender.com`

The Pages workflow will inject that URL into the production build so the deployed site can call the runtime API.

## Local development

For local execution, keep using:

```bash
poetry run python tools/notebook_runtime_server.py
```

and in another terminal:

```bash
jekyll serve --source site --config site/_config.yml,site/_config.local.yml --host 127.0.0.1 --port 4000
```
