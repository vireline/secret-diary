from __future__ import annotations

import getpass
from pathlib import Path
from datetime import datetime

import typer
from rich.console import Console
from rich.table import Table

from .store import connect
from .crypto import new_salt, fernet_from_password

app = typer.Typer(add_completion=False, no_args_is_help=True)
console = Console()

def home_dir() -> Path:
    # Store DB in a hidden folder in user's home
    d = Path.home() / ".secret-diary"
    d.mkdir(parents=True, exist_ok=True)
    return d

def _get_salt(con) -> bytes:
    row = con.execute("SELECT v FROM meta WHERE k='salt'").fetchone()
    if not row:
        raise typer.BadParameter("Not initialized. Run: secret-diary init")
    return row[0]

def _get_fernet(con):
    password = getpass.getpass("Master password: ")
    salt = _get_salt(con)
    return fernet_from_password(password, salt)

@app.command()
def init():
    """Initialize the local encrypted notebook store."""
    con = connect(home_dir())
    row = con.execute("SELECT 1 FROM meta WHERE k='salt'").fetchone()
    if row:
        console.print("[yellow]Already initialized.[/yellow]")
        return
    salt = new_salt()
    con.execute("INSERT INTO meta(k, v) VALUES('salt', ?)", (salt,))
    con.commit()
    console.print("[green]Initialized.[/green] Your DB lives in ~/.secret-diary/")

@app.command()
def add(
    title: str = typer.Option(..., "--title"),
    tags: str = typer.Option("", "--tags", help="Comma-separated tags"),
):
    """Add a new encrypted note (body opens in your editor)."""
    con = connect(home_dir())
    f = _get_fernet(con)

    body = typer.edit("") or ""
    now = datetime.utcnow().isoformat() + "Z"

    enc_title = f.encrypt(title.encode("utf-8"))
    enc_tags = f.encrypt(tags.encode("utf-8"))
    enc_body = f.encrypt(body.encode("utf-8"))

    con.execute(
        "INSERT INTO notes(title, tags, body, created_at) VALUES(?,?,?,?)",
        (enc_title, enc_tags, enc_body, now),
    )
    con.commit()
    console.print("[green]Saved.[/green]")

@app.command()
def list():
    """List notes (titles decrypted)."""
    con = connect(home_dir())
    f = _get_fernet(con)

    rows = con.execute("SELECT id, title, tags, created_at FROM notes ORDER BY id DESC").fetchall()
    table = Table(title="secret-diary notes")
    table.add_column("ID")
    table.add_column("Title")
    table.add_column("Tags")
    table.add_column("Created")
    for note_id, enc_title, enc_tags, created_at in rows:
        title = f.decrypt(enc_title).decode("utf-8")
        tags = f.decrypt(enc_tags).decode("utf-8")
        table.add_row(str(note_id), title, tags, created_at)
    console.print(table)

@app.command()
def read(note_id: int):
    """Read a note by ID."""
    con = connect(home_dir())
    f = _get_fernet(con)

    row = con.execute("SELECT title, tags, body, created_at FROM notes WHERE id=?", (note_id,)).fetchone()
    if not row:
        raise typer.BadParameter("No such note.")
    enc_title, enc_tags, enc_body, created_at = row
    title = f.decrypt(enc_title).decode("utf-8")
    tags = f.decrypt(enc_tags).decode("utf-8")
    body = f.decrypt(enc_body).decode("utf-8")

    console.rule(f"[bold]{title}[/bold]")
    if tags.strip():
        console.print(f"[cyan]Tags:[/cyan] {tags}")
    console.print(f"[dim]{created_at}[/dim]\n")
    console.print(body)

@app.command()
def search(query: str):
    """Search notes locally (decrypts titles/bodies to search)."""
    con = connect(home_dir())
    f = _get_fernet(con)
    rows = con.execute("SELECT id, title, body FROM notes ORDER BY id DESC").fetchall()

    hits = []
    q = query.lower()
    for note_id, enc_title, enc_body in rows:
        title = f.decrypt(enc_title).decode("utf-8")
        body = f.decrypt(enc_body).decode("utf-8")
        if q in title.lower() or q in body.lower():
            hits.append((note_id, title))

    table = Table(title=f"search: {query}")
    table.add_column("ID")
    table.add_column("Title")
    for note_id, title in hits:
        table.add_row(str(note_id), title)
    console.print(table)

def main():
    app()

if __name__ == "__main__":
    main()
