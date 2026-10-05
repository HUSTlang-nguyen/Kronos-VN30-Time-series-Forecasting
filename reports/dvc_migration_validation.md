# DVC migration validation

Reviewed: 2026-10-06. Migration based on `e8527db15a69c5e08fb6ecd5b2417b5870cca9ef`; pointers, receipts, tooling and collaborator documentation are versioned together in the publication commit. This is infrastructure validation, not G1 acceptance.

## Configuration and retained bytes

- Isolated uv tool: DVC 3.67.1, dvc-gdrive 3.0.1, pyOpenSSL 24.2.1. Research `pyproject.toml`/`uv.lock` and CUDA environment unchanged.
- Default remote `team`: `gdrive://1FDP-QGk_-UdcZsjaEuYjXgEu_1Nd62ur`.
- Raw pointer: 87 files, 21,787,567 bytes, DVC MD5 `fecae9449c856a16470d552e40f957f8.dir`.
- SQLite pointer: 589,824 bytes, DVC MD5 `2ee1b6c28f4db44fc7155990232793bc`.
- ZIP pointer: 98,534 bytes, DVC MD5 `510d9663fb63e40c8b2a711666a1bc48`.
- SQLite/ZIP removed from the Git index with `git rm --cached`; local source files remain. Git keeps pointers, existing SHA256 files and unchanged snapshot receipts.
- Both formats remain the 2,271-row candidate through 2026-10-01. Prices, anomaly flags and source bytes were not edited; accepted dataset/calendar/splits remain pending.

## Completed checks

| Check | Result |
|---|---|
| `tmp/ci-data-env/Scripts/python.exe -m pytest -q` | 52 passed; includes ignored credentials/binaries and local-only credential helper behavior |
| `python scripts/check_dvc_roundtrip.py` | Synthetic local remote: upload, empty-cache clone download, two versions, restore v1; SHA256 unchanged |
| Actual-data local roundtrip | All 89 files pushed and restored into an independent empty-cache DVC workspace; every SHA256 matched the source; SQLite/ZIP receipt checks both verified 2,271 candidate rows |
| Google Drive roundtrip (2026-10-06) | `dvc push -r team`: 89 files pushed. Separate workspace with empty cache: 89 files fetched/added; all SHA256 matched, both snapshot receipts verified |
| `python scripts/export_data_requirements.py --check` | Matches uv.lock |
| `docker compose --profile cuda config --quiet` | Pass |
| `dvc status` | Data and pipelines up to date |
| `git diff --check` | Pass |

CI adds `dvc-local` with a synthetic local remote; no Google credentials or real data download are required. This revision has not run on GitHub. Docker image was not rebuilt for this migration.

The actual-data check used a temporary filesystem remote configured with `--local`, then removed that test remote. All source files remained in the original workspace. It validates pointers/cache/bytes locally, not Google permissions or transfer.

## Google Drive verification

Initial `dvc push -r team` failed with `GEN_EMAIL` because pyOpenSSL 22.0.0 and cryptography 50.0.0 were incompatible. Pinning pyOpenSSL 24.2.1 resolved that runtime failure; the next attempt reached Google OAuth. Google blocked the default app. These earlier attempts did not complete an upload.

On 2026-10-06, the user supplied the Desktop client in ignored `.dvc/config.local` and completed Google sign-in. `dvc push -r team` exited 0 with **89 files pushed**. A temporary DVC workspace copied only the pointers/configuration, used its own empty cache, and pulled **89 files** from `team`. Every restored SHA256 matched the original; SQLite and ZIP receipt checks both verified the unchanged 2,271-row candidate with G1 pending. Total logical file size: **22,475,925 bytes**. Local source files were retained; the temporary workspace/credentials copy was removed after verification.

The verification receipt is [data/manifests/dvc_drive_verification.json](../data/manifests/dvc_drive_verification.json), including timestamps, per-file SHA256, pointer hashes and snapshot checks. Pointer line endings were normalized to LF for Git portability without changing their DVC output definitions. The temporary harness required `core.no_scm = true` after copying project configuration; its initial configuration failure did not indicate a Drive transfer failure.

Another collaborator's independent download using their own account/assigned Drive access remains pending. The successful restore used the authenticated uploader's account and does not prove another account's permissions. See [setup and publication order](../docs/DVC_Data_Versioning.md). Old Git history continues to contain previously committed binaries; no history rewrite was performed. No new research gate was accepted.
