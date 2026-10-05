# Repository cleanup and shared-data policy

Current update (2026-10-06): data versioning is migrating to DVC/Google Drive. Git retains pointers/checksums/receipts; SQLite/ZIP bytes are removed from the working index. Drive upload and empty-cache recovery of all 89 files are verified; local data remains available for use. Pointers/receipts and collaborator documentation are included in the Git migration. See [DVC validation](dvc_migration_validation.md). The direct-Git policy described below is historical and superseded by this migration.

Reviewed: 2026-10-05, following the user's request to version `data/share/` and simplify contributor onboarding.

## Changes

- Removed `data/share/` from `.gitignore`. Current SQLite/ZIP snapshots and checksums are eligible for Git tracking; the files have not been automatically committed or pushed.
- Added binary/byte-preserving Git attributes for SQLite/ZIP/checksums. SQLite journal/WAL/SHM remain ignored. `.dockerignore` still excludes snapshot bytes from images; Compose mounts the checkout.
- README/CONTRIBUTING now explicitly cover selecting a task, direct clone vs fork, upstream sync, branch creation, checks, staging selected files, commit/push, PR review and task acceptance.
- Moved the old agent plan from `docs/tmp/` to `docs/archive/`, preserving its exact bytes. Historical draft SHA256: `6e907ad7a70fcce4295e3e6b187aea57538a99491aa873077708cca786e67bc9`.
- Consolidated PowerShell bootstrap into a compatibility entry point that calls the portable Python implementation, removing duplicated repository/revision/checkout logic.
- Removed 13 temporary rendered PNGs under `tmp/` and `tmp/pdfs/`, after verifying the corresponding original PDFs remain under `data/raw/`. Removed 27 Python/pytest cache files and eight empty cache/draft/package directories, including the unused `src/vn30_tsfm/` directory. No raw source prices or study/audit evidence were removed.

The first combined recursive cleanup command was blocked by the execution policy. Cleanup then succeeded through separate archive and exact file/empty-directory operations without recursive deletion.

## Retained intentionally

- Original HTTP captures and original calendar PDFs: needed for evidence and offline replay.
- Source audit scripts, reports, configs and artifacts: selected VNDIRECT does not erase earlier findings or make them disposable.
- `tmp/vnstock-env/`, `requirements/vnstock-audit.txt`: isolated audit runtime and reproducible dependency list.
- `.venv/`, `.vendor/`, model caches: used runtime assets rather than repository clutter.
- ZIP beside SQLite: retained as the existing checksum-bound source of the SQLite conversion and alternative contributor format; both together are under 1 MB.

Current shared snapshots remain candidate data with G1 pending. Git tracking does not grant quality acceptance. Contributor setup Docker limitations from the earlier validation report remain unchanged by cleanup.

## Validation

- 39 tests passed with bytecode and pytest cache creation disabled.
- Both snapshot formats passed integrity checks against their tracked receipts.
- The PowerShell compatibility bootstrap verified the existing pinned Kronos checkout.
- Local documentation links and the archived plan were verified; snapshot paths are no longer ignored, while SQLite runtime files remain ignored.
- Git attributes preserve snapshot/checksum/archive bytes; Compose configuration and `git diff --check` pass.
