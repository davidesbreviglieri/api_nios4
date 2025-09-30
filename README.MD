# api_nios4 — Python wrapper for Nios4 Web API

A small, single‑file Python library to interact with the **Nios4** backend through the official *Web API*. It provides authentication, record read/write, text and fuzzy search, file management (upload/download), and synchronization helpers.

> **Official Nios4 Web API docs**: https://en.nios4.dev/wep-api

## Table of contents
- [Background](#background)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [Key concepts](#key-concepts)
- [Usage examples](#usage-examples)
  - [Auth & databases](#auth--databases)
  - [Tables & fields](#tables--fields)
  - [Reading records](#reading-records)
  - [Text & fuzzy search](#text--fuzzy-search)
  - [Create/Update/Delete records](#createupdatedelete-records)
  - [File management (upload/download)](#file-management-uploaddownload)
  - [Synchronization](#synchronization)
- [API reference (methods)](#api-reference-methods)
- [Error handling](#error-handling)
- [Best practices](#best-practices)
- [Known limitations](#known-limitations)
- [Security](#security)
- [Contributing](#contributing)
- [License](#license)

## Background
The **Nios4** cloud system relies on two database types:

1. **Synchronization database (D‑One Syncone)**: data flows via D‑One’s sync server and is formatted as JSON strings for storage and exchange among devices. This enables having identical table schemas regardless of their content.
2. **Web version cloud database**: data is stored in its respective fields and tables and consumed directly by the web front‑end.

The **Nios4 Web API** is designed to read and write **directly** against the web database. This wrapper packages the most common HTTP calls and offers helpers for date/TID normalization, searches, and CRUD.

## Features
- **Login** via *token* or *username/password*.
- List **databases**, **users**, **tables**, and **table/field metadata**.
- **Read records** (single by `gguid` or lists with filters/sorting).
- **Fuzzy/semantic search** across multiple fields with configurable threshold.
- **CRUD**: save one record or batches, delete record+details, and **resolve** (recalculate expressions).
- **File handling**: upload/download FILE/IMAGE linked to records.
- **Sync**: trigger synchronization with partial‑sync support.
- Utilities: `tid()`, `normalize_tid()`, `normalize_date()`, `check_value()`, file‑payload creation.

## Requirements
- Python 3.10+
- Dependency: `requests`

```bash
pip install requests
```

## Installation
Drop `api_nios4.py` into your project or package it as an internal module.

```bash
your-project/
  ├─ api_nios4.py
  └─ app.py
```

## Quickstart
```python
from api_nios4 import api_nios4

client = api_nios4(username="user@example.com", password="secret")
if not client.login():
    raise RuntimeError(f"Login failed: {client.error_code} - {client.error_message}")

dbs = client.database_list()
client.dbname = dbs[0]["dbname"]
print(client.table_list())
```

## Key concepts
- **TID** (*Time Identifier*): integer `YYYYMMDDHHMMSS` in UTC.
  - `tid()` → generate current TID.
  - `normalize_tid(int)` → ISO‑8601 `YYYY-MM-DDTHH:MM:SS`.
  - `normalize_date(value)` → convert `datetime`, `date`, `int`, or `YYYY-MM-DD` string to TID (`int`).
- **`check_value(value, format)`**: normalize values for field types (`text`, `decimalnumber`, `integernumber`, `date`).

## Usage examples
### Auth & databases
```python
client = api_nios4(username="user@example.com", password="secret")
assert client.login()

# or with a pre‑existing token
client = api_nios4(token="<TOKEN>")
assert client.login()

dbs = client.database_list()
client.dbname = dbs[0]["dbname"]
```

### Tables & fields
```python
tables = client.table_list()
info = client.table_info("customers")
fields = client.fields_info("customers")
```

### Reading records
```python
row = client.get_record("customers", gguid="550e8400-e29b-41d4-a716-446655440000")

rows = client.find_records(
    tablename="customers",
    fields_search=["name", "surname"],
    value_search="doe",
    search_by={"email": "@acme.com"},
    conditions={"status": ["active", "trial"]},
    order_info=[["created_at", True]]
)
```

### Text & fuzzy search
```python
results = client.fuzzy_records(
    tablename="customers",
    fields_search=["name", "surname", "company"],
    fields_return=["gguid", "name", "surname", "email"],
    query="jon",
    threshold=0.7,
    search_by={"email": "@acme.com"},
)
```

### Create/Update/Delete records
```python
from uuid import uuid4

record = {"gguid": str(uuid4()), "name": "Alice", "surname": "Bianchi"}
client.save_record("customers", record, is_new=True)

record["name"] = "Alice Updated"
client.save_record("customers", record, is_new=False)

client.detail_delete("customers", gguid=record["gguid"])  # delete with linked details
client.detail_resolve("orders", gguid="...")              # force recalculation
```

### File management (upload/download)
```python
gguidfile, body = client.create_data_file("/path/to/report.pdf")

client.upload_file(
    path="/path/to/report.pdf",
    is_image=False,
    gguidrif=gguidfile,
    tablename="documents"
)

client.download_file(
    path="./report.pdf",
    gguidrif=gguidfile,
    tablename="documents"
)
```

### Synchronization
```python
sync_info = client.sync()
if sync_info and sync_info.get("sync", {}).get("partial"):
    print("Partial sync active. Continue from:", sync_info["sync"]["partial_from"])
```

## API reference (methods)
> Most methods optionally accept `dbname` and/or `token` for runtime override.

- **`login(token: str="") -> bool`** — authenticate via token or username/password; updates `token`, `id_user`, `email_user`.
- **`database_list(token: str="") -> Optional[list]`** — list databases for the authenticated user.
- **`users_list(dbname: str="", token: str="") -> Optional[list]`** — users associated to the database (UTA).
- **`table_list(dbname: str="", token: str="") -> Optional[list]`** — list tables in the database.
- **`table_info(tablename: str, ...) -> Optional[dict]`** — table metadata (parameters, expressions, styles).
- **`fields_info(tablename: str, ...) -> Optional[list]`** — fields metadata for the table.
- **`get_record(tablename: str, gguid: str, ...) -> Optional[list]`** — record by `gguid` (as a list containing one dict).
- **`find_records(...) -> Optional[list]`** — query with text search, LIKE/IN filters, sorting.
- **`fuzzy_records(...) -> Optional[list]`** — fuzzy/semantic search with threshold [0.0–1.0].
- **`save_record(...) -> Optional[dict]`** — insert/update or delete a single record; `values` **must** include `gguid`.
- **`save_records(...) -> Optional[dict]`** — batch save multiple records; each dict **must** include `gguid`.
- **`detail_delete(...) -> Optional[dict]`** — delete record and linked details.
- **`detail_resolve(...) -> Optional[dict]`** — force recalculation of expressions/value distributors.
- **`create_data_file(...) -> Tuple[str, str]`** — build `gguidfile` + JSON metadata (`nomefile`).
- **`upload_file(...) -> bool`** — upload file/image to synchronizer (overwrites if same `gguid`).
- **`download_file(...) -> bool`** — download raw file and save to disk.
- **`sync(...) -> Optional[dict]`** — trigger synchronization, with partial‑sync support.

- **Utilities**
  - `tid() -> int`: generate UTC TID `YYYYMMDDHHMMSS`.
  - `normalize_tid(value: int) -> str`: TID → ISO‑8601.
  - `normalize_date(value: Any) -> int`: normalize date/datetime/str to TID.
  - `check_value(value: Any, format: str) -> Any`: normalize values by field type.

## Error handling
Each call resets error state via `reset_error()` and, on failure, sets:
- `self.error_code`
- `self.error_message`

## Best practices
- Manage token properly.
- Set `dbname` before data calls.
- Always check errors.
- Normalize inputs.
- Generate `gguid` client‑side.
- Prefer batch writes.
- Handle large files carefully.
- Implement retry/backoff for partial sync.

## Known limitations
- `save_records` dict vs list handling should be improved.
- `tid()` fix for seconds="60" could be more robust.
- `download_file`/`upload_file` endpoints tied to `app.pocketsell.com/_sync`; may vary.

## Security
- Never commit credentials.
- Always use HTTPS.
- Sanitize logs.

## Contributing
1. Fork.
2. Branch.
3. Add tests/docs.
4. PR.

## License
BSD‑2‑Clause (see source header).
