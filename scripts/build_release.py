#!/usr/bin/env python3
"""Create a SHA-bound, *non-public* Bridge Squad release candidate from trusted main."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import sys

OWNER = "evilsysadmin/matthias-bridge-squad"
TARGET = "production"
AUDIENCE = "bridgesquad"
SHA = re.compile(r"[a-f0-9]{40}\Z")


class ReleaseError(ValueError):
    pass


def build(source: Path, destination: Path, env: dict[str, str]) -> dict:
    """Packaging alone is NOT a Cloudflare deployment or an Identity bypass."""
    if (env.get("GITHUB_REPOSITORY") != OWNER
            or env.get("GITHUB_REF") != "refs/heads/main"
            or env.get("GITHUB_EVENT_NAME") != "push"):
        raise ReleaseError("Only exact owner main push can produce a release candidate")
    sha = env.get("GITHUB_SHA", "")
    if not SHA.fullmatch(sha):
        raise ReleaseError("Invalid exact source commit")
    if source.is_symlink() or not source.is_file():
        raise ReleaseError("Missing or linked HTML source")
    content = source.read_bytes()
    if not 64 <= len(content) <= 2_000_000:
        raise ReleaseError("Unexpected HTML size")
    try:
        text = content.decode("utf-8")
    except UnicodeError as exc:
        raise ReleaseError("HTML must be UTF-8") from exc
    if not text.lstrip().lower().startswith("<!doctype html>") or "<title>Matthias Bridge Squad" not in text:
        raise ReleaseError("Unexpected Bridge Squad source")
    if destination.is_symlink() or (destination.exists() and any(destination.iterdir())):
        raise ReleaseError("Release destination must be an empty real directory")
    destination.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema": 1,
        "application": "matthias-bridge-squad",
        "environment": TARGET,
        "source_repository": OWNER,
        "source_sha": sha,
        "authentication": {
            "provider": "shadowops-id",
            "audience": AUDIENCE,
            "required": True,
        },
        "files": {
            "index.html": {
                "sha256": hashlib.sha256(content).hexdigest(),
                "bytes": len(content),
            },
        },
    }
    (destination / "index.html").write_bytes(content)
    (destination / "release.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> int:
    try:
        root = Path(__file__).resolve().parents[1]
        manifest = build(root / "index.html", root / "_site", dict(os.environ))
    except (OSError, ReleaseError) as exc:
        print("BRIDGESQUAD_RELEASE_BLOCKED reason=" + type(exc).__name__, file=sys.stderr)
        return 1
    print("BRIDGESQUAD_PRIVATE_CANDIDATE_READY sha=" + manifest["source_sha"]
          + " digest=" + manifest["files"]["index.html"]["sha256"]
          + " authentication=required delivered=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
