# Shared VN30 snapshots

This directory is versioned in Git. Clone/pull supplies the same candidate SQLite/ZIP files and checksums to every contributor once the snapshot commit is pushed.

The current snapshot has 2,271 provider rows from 2017-08-24 through 2026-10-01. It is **not an accepted research dataset**; source/calendar acceptance remains pending.

```sh
python scripts/check_shared_data.py
python scripts/check_shared_data.py --format zip
```

Use SQLite read-only. Do not write experiment results into the shared database or commit journal/WAL/SHM files. A new version must have a new filename plus updated checksum/receipt in the same PR. Keep raw working files, weights and large results outside this directory.

See [the data guide](../../docs/Contributor_Data_Guide.md) and [contribution guide](../../CONTRIBUTING.md).
