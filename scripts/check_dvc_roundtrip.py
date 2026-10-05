"""Check DVC upload, fresh-clone download and historical checkout on a local remote.

Uses synthetic bytes in temporary directories; never accesses project data or Drive.
Run after installing requirements/dvc.txt in a separate tool environment.
"""
from __future__ import annotations

import hashlib
import shutil
import subprocess
import tempfile
from pathlib import Path


def run(cwd: Path, *args: str) -> str:
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"{args[0]} {args[1:]} failed:\n{result.stdout}\n{result.stderr}")
    return result.stdout.strip()


def main() -> None:
    if not shutil.which("dvc") or not shutil.which("git"):
        raise SystemExit("Install Git and the isolated DVC tool before running this check.")
    with tempfile.TemporaryDirectory(prefix="vn30-dvc-") as directory:
        root = Path(directory)
        publisher, consumer, remote = (root / name for name in ("publisher", "consumer", "store"))
        publisher.mkdir()
        remote.mkdir()
        run(publisher, "git", "init")
        run(publisher, "git", "config", "user.name", "DVC roundtrip check")
        run(publisher, "git", "config", "user.email", "dvc-check@example.invalid")
        run(publisher, "dvc", "init")
        run(publisher, "dvc", "config", "core.analytics", "false")
        run(publisher, "dvc", "config", "cache.type", "copy")
        run(publisher, "dvc", "remote", "add", "-d", "test", str(remote))
        data = publisher / "data" / "fixture.bin"
        data.parent.mkdir()
        versions = (b"VN30 synthetic snapshot v1\x00\r\n", b"VN30 synthetic snapshot v2\xff\n")
        commits = []
        for number, content in enumerate(versions, 1):
            data.write_bytes(content)
            run(publisher, "dvc", "add", "data/fixture.bin")
            run(publisher, "dvc", "push")
            run(publisher, "git", "add", ".dvc", ".dvcignore", "data/.gitignore", "data/fixture.bin.dvc")
            run(publisher, "git", "commit", "-m", f"Snapshot {number}")
            commits.append(run(publisher, "git", "rev-parse", "HEAD"))
        run(root, "git", "clone", "--no-hardlinks", str(publisher), str(consumer))
        if (consumer / "data/fixture.bin").exists() or (consumer / ".dvc/cache").exists():
            raise RuntimeError("Fresh clone unexpectedly includes data/cache bytes")
        # Fetch v1 first: its content cannot be satisfied by a cache or Git checkout.
        for index in (0, 1, 0):
            run(consumer, "git", "switch", "--detach", commits[index])
            run(consumer, "dvc", "pull")
            restored = (consumer / "data/fixture.bin").read_bytes()
            if restored != versions[index]:
                raise RuntimeError(f"Restored version {index + 1} differs from the published bytes")
            print(f"Version {index + 1}: SHA256 {hashlib.sha256(restored).hexdigest()} verified")
    print("DVC local upload/download/history check passed; Google Drive was not tested.")


if __name__ == "__main__":
    main()
