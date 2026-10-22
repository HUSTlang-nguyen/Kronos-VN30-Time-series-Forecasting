# Shared VN30 data

SQLite/ZIP bytes live in the team's DVC Google Drive remote. Git keeps pointers, SHA256 sidecars and receipts under `data/manifests/`.

See [setup and data usage](../../README.md#tải-dữ-liệu-bằng-dvc).

```sh
dvc pull data/share/vn30_vndirect_20261001T151513588605Z_candidate.sqlite.dvc
python scripts/check_shared_data.py
```

Snapshot: 2,271 rows, 2017-08-24 through 2026-10-01. Prices and quality flags are preserved; this is not an automatically cleaned dataset. Read SQLite in read-only mode and write processed outputs elsewhere.
