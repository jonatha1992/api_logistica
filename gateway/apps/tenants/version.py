import os
import re
import subprocess
from functools import lru_cache
from pathlib import Path

from django.http import JsonResponse


@lru_cache(maxsize=1)
def _version_data():
    root = Path(__file__).resolve().parents[4]
    version = os.environ.get("APP_VERSION", "0.1.0")
    for candidate in (root / "VERSION", root / "pyproject.toml"):
        if candidate.is_file():
            text = candidate.read_text(encoding="utf-8")
            match = re.search(r"(?m)^version\s*=\s*[\"']([^\"']+)", text) if candidate.suffix == ".toml" else re.search(r"\S+", text)
            if match:
                version = match.group(1)
                break
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", version):
        version = "0.1.0"
    sha = os.environ.get("GIT_SHA", "")
    if not re.fullmatch(r"[0-9a-fA-F]{7,40}", sha):
        try:
            sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
        except (OSError, subprocess.CalledProcessError):
            sha = "unknown"
    return {"version": version, "sha": sha[:7]}


def version_json(request):
    return JsonResponse(_version_data())
