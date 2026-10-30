"""Package a portable local app with built frontend and selected weights."""
from pathlib import Path
import json
import zipfile

from demo.prepare import sha, write_json
from demo.publish_models import packages

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demo"


def main():
    packages()
    if not (DEMO / "frontend/dist/index.html").exists():
        raise FileNotFoundError("Build demo/frontend first")
    target = DEMO / "bundle"
    target.mkdir(exist_ok=True)
    files = [ROOT / "Start-Dashboard.cmd"]
    files += [DEMO / x for x in ("__init__.py", "runtime.py", "app.py", "run.py", "setup.ps1", "start.ps1", "requirements.lock", "README.md", "registry.json")]
    for directory in ("data", "vendor", "models", "frontend/dist", "licenses"):
        files.extend(p for p in (DEMO / directory).rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc" and p.name not in ("hub_upload_receipt.json", "upload_manifest.json"))
    output = target / "VN30-Inference-Studio.zip"
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=1) as archive:
        for path in files:
            archive.write(path, "VN30-Inference-Studio/" + path.relative_to(ROOT).as_posix())
    write_json(target / "bundle_manifest.json", dict(zip=output.name, sha256=sha(output), bytes=output.stat().st_size, files={p.relative_to(ROOT).as_posix(): sha(p) for p in files}, laptop_benchmark="omitted_at_user_request"))
    print(output)
    print(round(output.stat().st_size / 2 ** 20, 2), "MiB")


if __name__ == "__main__":
    main()
