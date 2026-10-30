"""Review/export-only by default. Explicit --upload publishes the prepared models."""
import argparse
import hashlib
import json
from pathlib import Path

from huggingface_hub import HfApi

DEMO = Path(__file__).resolve().parent
FILES = ["model.safetensors", "config.json", "README.md", "LICENSE", "provenance.json", "inference_spec.json"]


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def packages():
    registry = json.loads((DEMO / "registry.json").read_text())["models"]
    result = []
    for key, spec in registry.items():
        folder = DEMO / spec["local_path"]
        files = {}
        for name in FILES:
            path = folder / name
            files[name] = dict(bytes=path.stat().st_size, sha256=sha(path))
        for name, expected in spec["files"].items():
            if files[name]["sha256"] != expected:
                raise ValueError("Model checksum differs: " + key)
        result.append(dict(id=key, repo_name=key + "-vn30-sft", folder=spec["local_path"], files=files))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--namespace")
    parser.add_argument("--visibility", choices=["public", "private"])
    parser.add_argument("--upload", action="store_true")
    args = parser.parse_args()
    payload = packages()
    write_json(DEMO / "models/upload_manifest.json", dict(mode="review_only", packages=payload))
    if not args.upload:
        for item in payload:
            print(item["repo_name"], round(sum(f["bytes"] for f in item["files"].values()) / 2 ** 20, 2), "MiB", list(item["files"]))
        print("No files uploaded. Review demo/models/upload_manifest.json and the model cards.")
        return
    if not args.namespace or not args.visibility:
        parser.error("--upload requires --namespace and --visibility; no default public publishing")
    if "/" in args.namespace or not args.namespace.strip():
        parser.error("Use a Hugging Face user or organization namespace, not a full repo ID")
    api = HfApi()
    authenticated = api.whoami()["name"]
    if args.namespace == "neikhn" and authenticated != "neikhn":
        raise ValueError("This publishing request requires the neikhn account")
    # Preflight all names before creating/uploading any repo. Do not replace an
    # existing different checkpoint just because its name happens to match.
    for item in payload:
        repo = args.namespace + "/" + item["repo_name"]
        try:
            remote = api.model_info(repo, files_metadata=True)
        except Exception as exc:
            if getattr(getattr(exc, "response", None), "status_code", None) == 404:
                continue
            raise
        if remote.private != (args.visibility == "private"):
            raise ValueError("Existing repo visibility differs: " + repo)
        weights = next((s for s in remote.siblings if s.rfilename == "model.safetensors"), None)
        if weights is not None:
            remote_hash = getattr(weights.lfs, "sha256", None) if weights.lfs else None
            if remote_hash != item["files"]["model.safetensors"]["sha256"]:
                raise ValueError("Existing repo has different weights; review required: " + repo)
    registry_path = DEMO / "registry.json"
    registry = json.loads(registry_path.read_text())
    receipt = dict(namespace=args.namespace, visibility=args.visibility, models={})
    for item in payload:
        repo = args.namespace + "/" + item["repo_name"]
        api.create_repo(repo_id=repo, repo_type="model", private=args.visibility == "private", exist_ok=True)
        info = api.upload_folder(repo_id=repo, folder_path=DEMO / item["folder"], allow_patterns=FILES, commit_message="Add verified exploratory VN30 SFT checkpoint")
        revision = info.oid
        registry["models"][item["id"]].update(hub_repo=repo, hub_revision=revision)
        receipt["models"][item["id"]] = dict(repo=repo, revision=revision)
        write_json(registry_path, registry)
        write_json(DEMO / "models/hub_upload_receipt.json", receipt)
        print(repo, revision)


if __name__ == "__main__":
    main()
