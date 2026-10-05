import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import configure_dvc_drive as drive


def test_desktop_client_is_local_only_and_failures_do_not_echo_secrets(tmp_path, monkeypatch):
    client = tmp_path / "desktop.json"
    client.write_text(json.dumps({"installed": {"client_id": "fake-client", "client_secret": "fake-secret"}}))
    monkeypatch.setattr(drive.shutil, "which", lambda name: "dvc")
    calls = []

    def run(args, **kwargs):
        calls.append(args)
        return SimpleNamespace(returncode=0 if len(calls) == 1 else 1, stderr="fake-secret")

    monkeypatch.setattr(drive.subprocess, "run", run)
    with pytest.raises(ValueError) as error:
        drive.configure(client)
    assert "fake-secret" not in str(error.value)
    assert len(calls) == 2
    assert all(call[1:5] == ["remote", "modify", "--local", "team"] for call in calls)


def test_client_json_cannot_be_kept_inside_checkout(tmp_path, monkeypatch):
    monkeypatch.setattr(drive, "ROOT", tmp_path)
    with pytest.raises(ValueError, match="outside the repository"):
        drive.configure(tmp_path / "client.json")


def test_web_client_json_is_rejected(tmp_path):
    client = tmp_path / "web.json"
    client.write_text(json.dumps({"web": {"client_id": "fake-client", "client_secret": "fake-secret"}}))
    with pytest.raises(ValueError, match="Desktop app"):
        drive.configure(client)
