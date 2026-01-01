Cooking AI Agent (console)
=================================

This is a minimal interactive console application that demonstrates a cooking assistant.

Quick start
------------

- Create a virtualenv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

- Configure an optional model endpoint via environment variables (see `.env.example`).
- Run the app:

```bash
python main.py
```

Notes
-----
- The app supports a pluggable `GitHubModelClient` that posts prompts to a configured HTTP model endpoint. If you don't configure a model, the app falls back to lightweight local heuristics/sample data.
 - The app supports a pluggable `GitHubModelClient` that posts prompts to a configured HTTP model endpoint. If you don't configure a model, the app falls back to lightweight local heuristics/sample data.

Wiring a GitHub-hosted model
----------------------------

1. Set `MODEL_API_URL` to your GitHub-hosted model's full inference endpoint, or to the GitHub API base plus a model path. Example (replace with your actual path):

```
MODEL_API_URL=https://api.github.com/your-org/models/your-model/infer
MODEL_API_KEY=ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

2. The client also exposes `generate_github(prompt, model_path=None)` which will set `Accept: application/vnd.github+json` and include the `Authorization: Bearer` header. If your GitHub-hosted model expects a different JSON shape (for example `{"prompt": ...}`), configure the endpoint to accept the `input` field or adapt the payload in `model_client.py`.

3. Run the app. When `MODEL_API_URL` and `MODEL_API_KEY` are set, the agent will attempt to use the remote model for ingredient extraction; otherwise it uses local heuristics.
