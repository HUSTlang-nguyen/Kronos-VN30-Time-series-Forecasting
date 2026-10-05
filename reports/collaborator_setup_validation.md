# Collaborator setup validation

## Successful DVC migration CI (2026-10-06)

[Run 37351516675](https://github.com/HUSTlang-nguyen/Kronos-VN30-Time-series-Forecasting/actions/runs/37351516675), commit `f56cfc8c2d2e6ada1995d0d5a8e136c16da00ff0`, passed all four jobs: Windows tests, Ubuntu tests, Docker data build/tests, and the synthetic `dvc-local` upload/download/history check. A fresh local clone of that commit also passed 52 tests and the dependency-lock check, contained no local credentials or SQLite/ZIP bytes, and preserved all receipt-bound DVC pointer hashes. Another collaborator's own-account Drive download remains pending.

## DVC migration checks (2026-10-06)

The migration passes 52 tests and the synthetic local DVC upload/download/history check. Actual-data local upload and fresh-cache restore verified all 89 file SHA256 hashes plus SQLite/ZIP receipts. Google Drive upload and independent empty-cache restoration are also verified using a custom Desktop OAuth client. Pointers/receipts are included in the published migration commit; its CI passed as recorded above. Independent collaborator access remains pending. See [migration validation](dvc_migration_validation.md) and [DVC setup](../docs/DVC_Data_Versioning.md). Historical Git-distributed snapshot instructions below are superseded by DVC.

## Successful remote CI (2026-10-05)

[Run 37282168003](https://github.com/HUSTlang-nguyen/Kronos-VN30-Time-series-Forecasting/actions/runs/37282168003), at commit `6f0d6a7edbdebe08c719ebe74d1a05200bad4762`, completed successfully: Ubuntu and Windows Python 3.11 tests, plus Docker data build and container tests. T009 is accepted for that revision; T007's build/test portion is verified on the GitHub runner. The separate in-container SQLite/ZIP verification commands remain pending, as does T008 GPU verification. Pending/no-remote-run statements below describe the earlier local validation stage. That run predates T010/T012 and the 39-field changes; it does not validate the newly published revision.

## Updated local publication checks (2026-10-05)

The isolated Python 3.11 data environment passes **49 tests**. `export_data_requirements.py --check` confirms the dependency subset still matches `uv.lock`. Both `check_shared_data.py` formats verify the unchanged 2,271-row candidate snapshot. Registered source replay, calendar review replay and 39-case replay pass with the retained raw bytes. No package changes were made to the host CUDA environment. New remote CI must be checked against the pushed HEAD; local success does not imply remote success.

## Original local validation record

Reviewed: 2026-10-05. This report validates collaborator infrastructure, not source acceptance or research results. At this earlier stage, changes were tested in a working tree; no new commit, remote CI run or primary holdout run was claimed.

## Checks completed

| Check | Result |
|---|---|
| Host Python 3.11 unit tests | 39 passed |
| `python scripts/export_data_requirements.py --check` | Generated data dependency subset matches uv.lock |
| `python -S scripts/check_shared_data.py` | SQLite integrity verified, 2,271 rows, G1 pending |
| `python -S scripts/check_shared_data.py --format zip` | ZIP integrity verified, same candidate snapshot |
| `python scripts/bootstrap_kronos.py` | Existing clean checkout verified at pinned 67b630e67f6a18c9e9be918d9b4337c960db1e9a |
| Smoke/provenance `--help` | New `--output` argument available; no model inference required for this check |
| README/collaborator/runbook/checklist local Markdown links | All explicit local links resolve |
| Task registry | 49 unique Task IDs; original research IDs retained |
| `docker compose --profile cuda config --quiet` | Compose configuration valid |
| `docker compose build data` | Successful first build; requirements installed with hashes |

The SQLite/ZIP candidate retains the original capture, all prices/rows and quality flags. Both checks use the trusted hashes in the checkout. `-S` demonstrates the verification helpers need no model dependencies. Unit tests cover tampering, read-only SQLite use, row/anomaly preservation and original-response integrity.

## Docker limitations observed

The data image's first successful build produced config/image ID `sha256:ce89a7b68e8e59b089e0c8e2db1bc82254d4d600bdc677ae994bb900120dc379`. Later documentation/output/concurrency edits are consumed by Compose's source mount but have not yet been validated by a final rebuild. This ID is evidence of that first build, not a frozen final experiment environment.

The CUDA build fetched the locked dependencies, then failed during installation with `failed to receive status: rpc error: code = Unavailable desc = error reading from server: EOF`. Subsequent engine calls returned HTTP 500 or a missing `dockerDesktopLinuxEngine` pipe. Docker Desktop was restarted, but successful runtime recovery has not been established in this report. The root cause is unconfirmed. Disk space and installation resources should be checked; no Docker data/storage settings or unrelated files were removed.

Installation/download concurrency was reduced in Dockerfile to limit build resource use. A successful retry is still required before T008 can pass. CUDA image build, in-container GPU/model smoke and in-container tests are not claimed successful. Host `.venv` remains the existing CUDA environment; no package changes were made there.

## Follow-up on a functioning Docker host

```sh
docker compose build data
docker compose run --rm data
docker compose run --rm data python scripts/export_data_requirements.py --check
docker compose run --rm data python scripts/check_shared_data.py
docker compose run --rm data python scripts/check_shared_data.py --format zip
docker compose --profile cuda build cuda
docker compose --profile cuda run --rm cuda
```

Record outputs, image IDs, device/torch/CUDA versions and the code commit, then update T007/T008 acceptance. GPU smoke/provenance commands are documented in the runbook and should use `artifacts/local/` output paths.

T005 documentation and T006 candidate handoff have local evidence. T007 runtime verification and T008 CUDA verification remain pending. T009 has a configured CI workflow but no remote run URL yet; do not label it passed. Phase 1 G1/calendar/accepted dataset and split outputs remain pending independently of Docker status.

The task update also adds explicit dependencies, outputs and acceptance criteria for every secondary/optional task, preserves the earlier experiment log, and removes the circular dependency where calendar acquisition waited for the source gate that itself needed calendar reconciliation.

## CI failure and dependency correction (2026-10-05)

[collaborator checks run 37280140739](https://github.com/HUSTlang-nguyen/Kronos-VN30-Time-series-Forecasting/actions/runs/37280140739), for commit `bb43229bef28c4251372cdab0bf6a11388c142f2`, failed in the Ubuntu tests and Docker data jobs during pytest collection: `tests/test_vnstock_audit.py` imports `scripts/audit_vnstock_sources.py`, which imports `requests`. The generated data dependency subset omitted this package. The Windows matrix job was cancelled. The Docker data image built successfully in that run; its test command failed.

The export roots now include `requests`; `requirements/data.txt` was regenerated from the existing `uv.lock`, preserving locked versions and distribution hashes. The hash-bound audit script and host CUDA environment were not modified.

Validation in a fresh Python 3.11 environment at `tmp/ci-data-env`, installed only with `uv pip install --python tmp/ci-data-env/Scripts/python.exe --require-hashes -r requirements/data.txt`, passed all 39 tests in 11.75 seconds. The export consistency check and `git diff --check` also passed. This is local verification of the correction; a successful remote CI rerun and final container runtime verification remain pending.
