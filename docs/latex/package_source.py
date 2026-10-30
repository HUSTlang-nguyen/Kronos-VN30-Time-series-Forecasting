"""Package the self-contained LaTeX sources, without research data or runtime."""
from pathlib import Path
import hashlib
import json
from zipfile import ZipFile, ZIP_DEFLATED

HERE = Path(__file__).resolve().parent
names = ["main.tex", "references.bib", "README.md", "compile.ps1", "source_manifest.json"]
files = [HERE / name for name in names]
files += sorted((HERE / "tables").glob("*.tex"))
files += sorted((HERE / "figures").glob("*.pdf"))
output = HERE / "VN30_LaTeX_Source.zip"
with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
    for file in files:
        archive.write(file, file.relative_to(HERE).as_posix())
with ZipFile(output) as archive:
    assert archive.testzip() is None
    for file in files:
        assert archive.read(file.relative_to(HERE).as_posix()) == file.read_bytes()
manifest = {
    "pdf": {"path": "VN30_Report.pdf", "sha256": hashlib.sha256((HERE / "VN30_Report.pdf").read_bytes()).hexdigest()},
    "source_zip": {"path": output.name, "sha256": hashlib.sha256(output.read_bytes()).hexdigest()},
    "source_zip_members": {file.relative_to(HERE).as_posix(): hashlib.sha256(file.read_bytes()).hexdigest() for file in files},
    "compiler": "Tectonic 0.17.0 (XeTeX/BibTeX)",
}
(HERE / "release_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
print(f"Packaged and verified {len(files)} source files: {output.name}")
