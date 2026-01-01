"""Lightweight pluggable model client wrapper.

This client is intentionally generic: configure `MODEL_API_URL` and
`MODEL_API_KEY` via environment variables to point at a GitHub-hosted
model inference endpoint (or any HTTP model endpoint).
"""
from __future__ import annotations

import os
import requests
from typing import Optional, Dict, Any


class GitHubModelClient:
    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None, timeout: int = 30):
        self.api_url = api_url or os.getenv("MODEL_API_URL")
        self.api_key = api_key or os.getenv("MODEL_API_KEY")
        self.timeout = timeout

    def configured(self) -> bool:
        return bool(self.api_url and self.api_key)

    def generate(self, prompt: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Send a prompt to the configured model endpoint and return text output.

        The endpoint contract is intentionally flexible: it will POST JSON
        containing `prompt`; adapt `payload` to match the target endpoint.
        """
        if not self.api_url:
            raise RuntimeError("MODEL_API_URL is not configured")

        payload = {"prompt": prompt}
        if params:
            payload.update(params)

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        resp = requests.post(self.api_url, json=payload, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()

        # Try to extract common fields used by model endpoints
        if isinstance(data, dict):
            for key in ("text", "generated_text", "output", "result"):
                if key in data:
                    return data[key]
            # Some endpoints return choices array
            choices = data.get("choices")
            if isinstance(choices, list) and choices:
                first = choices[0]
                if isinstance(first, dict):
                    return first.get("text") or first.get("message") or str(first)
            return str(data)

        return str(data)

    def generate_github(self, prompt: str, model_path: Optional[str] = None, params: Optional[Dict[str, Any]] = None) -> str:
        """Helper for calling GitHub-hosted model endpoints.

        Usage:
        - Set `MODEL_API_URL` to the full model inference endpoint (recommended),
          or set `MODEL_API_URL` to the GitHub API base and supply `model_path`.
        - Set `MODEL_API_KEY` to a Personal Access Token (PAT) with access to the model.

        The function will set GitHub-appropriate headers (`Accept: application/vnd.github+json`).
        """
        if not self.api_url:
            raise RuntimeError("MODEL_API_URL is not configured")

        # Determine target URL: prefer the configured api_url as full endpoint
        if model_path and (self.api_url.endswith("/") is False):
            # If api_url looks like a base, append model_path
            target = f"{self.api_url.rstrip('/')}/{model_path.lstrip('/')}"
        else:
            target = self.api_url

        payload = {"input": prompt}
        if params:
            payload.update(params)

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        # GitHub recommends specifying API version via header when needed
        headers.setdefault("X-GitHub-Api-Version", "2022-11-28")

        resp = requests.post(target, json=payload, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()

        if isinstance(data, dict):
            for key in ("text", "generated_text", "output", "result"):
                if key in data:
                    return data[key]
            choices = data.get("choices")
            if isinstance(choices, list) and choices:
                first = choices[0]
                if isinstance(first, dict):
                    return first.get("text") or first.get("message") or str(first)
            return str(data)

        return str(data)
