"""Load a Google Desktop OAuth client into ignored DVC local configuration."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def configure(client_json: Path, remote: str = "team") -> None:
    path = client_json.resolve()
    if path.is_relative_to(ROOT):
        raise ValueError("Keep the OAuth client JSON outside the repository")
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
        installed = document["installed"]
        values = {key: installed[key] for key in ("client_id", "client_secret")}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ValueError("Expected a readable Google Desktop app OAuth JSON") from exc
    if not all(isinstance(value, str) and value.strip() for value in values.values()):
        raise ValueError("Desktop OAuth client ID/secret must be nonempty strings")
    executable = shutil.which("dvc")
    if not executable:
        raise ValueError("Install the isolated DVC tool first")
    for key, value in values.items():
        result = subprocess.run(
            [executable, "remote", "modify", "--local", remote, f"gdrive_{key}", value],
            cwd=ROOT, capture_output=True, text=True,
        )
        if result.returncode:
            # DVC diagnostics may include arguments: never echo credentials.
            raise ValueError("Unable to configure DVC; check the remote name and local permissions")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client-json", required=True, type=Path)
    parser.add_argument("--remote", default="team")
    args = parser.parse_args()
    try:
        configure(args.client_json, args.remote)
    except ValueError as exc:
        parser.exit(1, f"{exc}\n")
    print("Desktop OAuth client configured in ignored .dvc/config.local. Run dvc push/pull to sign in.")


if __name__ == "__main__":
    main()
