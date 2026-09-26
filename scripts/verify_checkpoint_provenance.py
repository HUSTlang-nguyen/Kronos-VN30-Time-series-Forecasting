from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml
from huggingface_hub import hf_hub_download


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "manifests" / "checkpoint_provenance.yaml"
OUTPUT = ROOT / "artifacts" / "smoke" / "checkpoint_hash_verification.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_component(name: str, component: dict) -> dict:
    cached_path = Path(
        hf_hub_download(
            repo_id=component["repository"],
            filename=component["weights_file"],
            revision=component["repository_revision"],
        )
    )
    actual_hash = sha256_file(cached_path)
    actual_size = cached_path.stat().st_size
    expected_hash = component["weights_sha256"]
    expected_size = component["weights_size_bytes"]
    passed = actual_hash == expected_hash and actual_size == expected_size
    return {
        "component": name,
        "repository": component["repository"],
        "revision": component["repository_revision"],
        "filename": component["weights_file"],
        "expected_sha256": expected_hash,
        "actual_sha256": actual_hash,
        "expected_size_bytes": expected_size,
        "actual_size_bytes": actual_size,
        "status": "pass" if passed else "fail",
    }


def main() -> int:
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    components = {
        "chronos_2_small": manifest["models"]["chronos_2_small"],
        "kronos_small": manifest["models"]["kronos_small"],
        "kronos_tokenizer_base": manifest["tokenizers"]["kronos_tokenizer_base"],
    }
    results = [verify_component(name, component) for name, component in components.items()]
    payload = {
        "schema_version": 1,
        "manifest": str(MANIFEST.relative_to(ROOT)),
        "status": "pass" if all(result["status"] == "pass" for result in results) else "fail",
        "components": results,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
