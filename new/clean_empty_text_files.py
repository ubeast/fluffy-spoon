"""
clean_empty_text_files.py
=========================
Scans for empty text files and deletes them.

A file is considered empty if it has zero bytes or contains only whitespace.

By default scans for common text file extensions. You can add your own.

Usage
-----
    # Dry run — shows what would be deleted, deletes nothing
    python clean_empty_text_files.py

    # Delete for real
    python clean_empty_text_files.py --delete

    # Current directory only (no subdirectories)
    python clean_empty_text_files.py --no-recursive

    # Search a specific path
    python clean_empty_text_files.py --path /path/to/search --delete

    # Add extra extensions
    python clean_empty_text_files.py --ext .log .out --delete

    # Only check specific extensions
    python clean_empty_text_files.py --ext .log --delete

From a notebook
---------------
    from clean_empty_text_files import run

    run(".")                                         # dry run, recursive
    run(".", delete=True)                            # delete, recursive
    run(".", recursive=False, delete=True)           # delete, current dir only
    run(".", extensions=[".log", ".txt"], delete=True)  # specific extensions
"""

from pathlib import Path

# Default extensions treated as text files
DEFAULT_EXTENSIONS: list[str] = [
    ".txt", ".md", ".rst", ".csv", ".tsv",
    ".log", ".out", ".err",
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
    ".py", ".js", ".ts", ".html", ".css", ".xml",
    ".sh", ".bat", ".env",
    ".sql",
]


# ── Core logic ────────────────────────────────────────────────────────────────

def is_empty_text_file(path: Path) -> bool:
    """
    Return True if the file has zero bytes or contains only whitespace.

    Parameters
    ----------
    path : Path to a file
    """
    if path.stat().st_size == 0:
        return True
    try:
        return not path.read_text(encoding="utf-8", errors="ignore").strip()
    except OSError:
        return False


def find_empty_text_files(
    path:       "str | Path" = ".",
    recursive:  bool = True,
    extensions: list[str] | None = None,
) -> list[Path]:
    """
    Find empty text files under a directory.

    Parameters
    ----------
    path       : Root directory to search (default: current directory)
    recursive  : If True (default), search all subdirectories.
                 If False, search the current directory only.
    extensions : List of file extensions to check (default: DEFAULT_EXTENSIONS).
                 Pass an explicit list to override, e.g. [".txt", ".log"]

    Returns
    -------
    List of Path objects for empty text files
    """
    root = Path(path).expanduser().resolve()
    exts = {e.lower() if e.startswith(".") else f".{e.lower()}"
            for e in (extensions or DEFAULT_EXTENSIONS)}

    pattern = "**/*" if recursive else "*"
    files   = sorted(
        p for p in root.glob(pattern)
        if p.is_file() and p.suffix.lower() in exts
    )

    depth = "recursively" if recursive else "current directory only"
    print(f"\nSearching {depth} in: {root}")
    print(f"Extensions : {', '.join(sorted(exts))}")
    print(f"Found {len(files)} text file(s)\n")

    empty = []
    for f in files:
        label = f.relative_to(root)
        if is_empty_text_file(f):
            empty.append(f)
            print(f"  EMPTY  {label}")
        else:
            print(f"  OK     {label}")

    print(f"\n{len(empty)} empty / {len(files)} total")
    return empty


def delete_empty_text_files(files: list[Path], dry_run: bool = False) -> None:
    """
    Delete a list of files.

    Parameters
    ----------
    files   : List of Paths to delete (from find_empty_text_files)
    dry_run : If True, print what would be deleted without actually deleting
    """
    if not files:
        print("\nNothing to delete.")
        return

    print()
    deleted = 0
    for f in files:
        if dry_run:
            print(f"  Would delete: {f}")
        else:
            try:
                f.unlink()
                deleted += 1
                print(f"  Deleted: {f}")
            except OSError as e:
                print(f"  ERROR deleting {f.name}: {e}")

    if dry_run:
        print(f"\nDry run — {len(files)} file(s) would be deleted.")
        print("Call with delete=True to actually remove them.")
    else:
        print(f"\nDeleted {deleted} / {len(files)} file(s).")


# ── Main entry point ──────────────────────────────────────────────────────────

def run(
    path:       "str | Path" = ".",
    recursive:  bool = True,
    delete:     bool = False,
    extensions: list[str] | None = None,
) -> list[Path]:
    """
    Find and optionally delete empty text files.

    Parameters
    ----------
    path       : Directory to search (default: current directory)
    recursive  : If True (default), search all subdirectories.
                 If False, search the current directory only.
    delete     : Set True to actually delete. Default is a dry run (safe preview).
    extensions : File extensions to check. Defaults to DEFAULT_EXTENSIONS.
                 Pass an explicit list to override, e.g. [".txt", ".log"]

    Returns
    -------
    List of empty file paths found

    Examples
    --------
    from clean_empty_text_files import run

    run(".")                                           # dry run, recursive
    run(".", recursive=False)                          # dry run, current dir only
    run(".", delete=True)                              # delete, recursive
    run(".", recursive=False, delete=True)             # delete, current dir only
    run(".", extensions=[".log", ".txt"], delete=True) # specific extensions only
    """
    empty = find_empty_text_files(path=path, recursive=recursive, extensions=extensions)
    delete_empty_text_files(empty, dry_run=not delete)
    return empty


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Find and delete empty text files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python clean_empty_text_files.py                           # dry run, recursive
  python clean_empty_text_files.py --delete                  # delete, recursive
  python clean_empty_text_files.py --no-recursive            # dry run, current dir only
  python clean_empty_text_files.py --no-recursive --delete   # delete, current dir only
  python clean_empty_text_files.py --path ~/projects --delete
  python clean_empty_text_files.py --ext .log .out --delete  # specific extensions
        """,
    )
    parser.add_argument("--path",      default=".",  help="Directory to search (default: .)")
    parser.add_argument("--recursive", default=True, action=argparse.BooleanOptionalAction,
                        help="Search subdirectories (default: on). Use --no-recursive to disable.")
    parser.add_argument("--delete",    action="store_true",
                        help="Actually delete (default is dry run)")
    parser.add_argument("--ext",       nargs="+", metavar="EXT", default=None,
                        help="Extensions to check e.g. --ext .txt .log  (default: all common text types)")
    args = parser.parse_args()

    run(path=args.path, recursive=args.recursive, delete=args.delete, extensions=args.ext)
