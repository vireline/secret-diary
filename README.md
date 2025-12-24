# secret-diary 🔐📓

An **offline-first encrypted notebook**. Notes are stored locally and encrypted with a master password.

## Features (v0.1)
- Create/list/read/search notes
- Tags support
- Local storage (SQLite)
- Encryption using `cryptography` (AES-backed Fernet)

## Install (dev)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -U pip
pip install -e .
```

## Usage
```bash
secret-diary init
secret-diary add --title "Case 001" --tags "osint,field"
secret-diary list
secret-diary read 1
secret-diary search "keyword"
```

## Security note
This is a starter project. Treat it as **personal** encryption, not military-grade opsec.
