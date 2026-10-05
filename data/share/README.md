# Shared candidate snapshots

SQLite/ZIP bytes are managed by DVC on the team's Google Drive. Git contains `.dvc` pointers, SHA256 files and receipts under `data/manifests/`.

Google Drive upload and fresh-cache restore verified all 89 data files on 2026-10-06. Git versions the migration pointers and receipts; download the data with DVC. See [DVC setup](../../docs/DVC_Data_Versioning.md) for access and authentication, and [verification receipt](../manifests/dvc_drive_verification.json).

After the remote is populated:

```sh
dvc pull data/share/vn30_vndirect_20261001T151513588605Z_candidate.sqlite.dvc
python scripts/check_shared_data.py
```

Optional ZIP: pull the adjacent `.zip.dvc` pointer and verify with `--format zip`. Raw audit replay uses `dvc pull data/raw.dvc`.

Candidate snapshot: 2,271 rows, 2017-08-24 through 2026-10-01; G1 pending. The newer audit does not replace this snapshot. Read SQLite locally in read-only mode; keep outputs elsewhere. [Data/schema guide](../../docs/Collaborator_Data_Guide.md).
