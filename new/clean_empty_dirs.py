"""
clean_empty_dirs.py
===================
Scans for empty directories and deletes them.

A directory is considered empty if it contains no files and no subdirectories.
Deletion works bottom-up, so a directory that only contains empty subdirectories
will also be cleaned up in a single pass.

Usage
-----
    # Dry run — shows what would be deleted, deletes nothing
    python clean_empty_dirs.py

    # Delete for real
    python clean_empty_dirs.py --delete

    # Current directory only (no subdirectories)
    python clean_empty_dirs.py --no-recursive

    # Search a specific path
    python clean_empty_dirs.py --path /path/to/search --delete

From a notebook
---------------
    from clean_empty_dirs import run

    run(".")                                    # dry run, recursive
    run(".", delete=True)                       # delete, recursive
    run(".", recursive=False, delete=True)      # delete, current dir only
    run("/path/to/search", delete=True)
"""

from pathlib import Path


# ── Core logic ────────────────────────────────────────────────────────────────

def is_empty_dir(path: Path) -> bool:
    """
    Return True if the directory contains no files and no subdirectories.

    Parameters
    ----------
    path : Path to a directory
    """
    return path.is_dir() and not any(path.iterdir())


def find_empty_dirs(
    path:      "str | Path" = ".",
    recursive: bool = True,
) -> list[Path]:
    """
    Find empty directories under a root path.

    Walks bottom-up so that a directory containing only empty subdirectories
    is itself recognised as empty after its children are identified.

    Parameters
    ----------
    path      : Root directory to search (default: current directory)
    recursive : If True (default), search all subdirectories.
                If False, check only immediate subdirectories.

    Returns
    -------
    List of Path objects for empty directories, deepest first.
    """
    root = Path(path).expanduser().resolve()

    if recursive:
        # walk bottom-up: children before parents so parents can become empty
        candidates = sorted(
            (p for p in root.rglob("*") if p.is_dir()),
            key=lambda p: len(p.parts),
            reverse=True,   # deepest first
        )
    else:
        candidates = [p for p in sorted(root.iterdir()) if p.is_dir()]

    depth = "recursively" if recursive else "current directory only"
    print(f"\nSearching {depth} in: {root}")
    print(f"Found {len(candidates)} subdirector{'ies' if len(candidates) != 1 else 'y'}\n")

    empty = []
    # Re-check emptiness as we go — a dir may become empty after its children
    # are added to the deletion list
    accounted: set[Path] = set()

    for d in candidates:
        # A dir is effectively empty if all its contents are already
        # flagged for deletion
        contents = set(d.iterdir())
        if not contents or contents.issubset(accounted):
            empty.append(d)
            accounted.add(d)
            print(f"  EMPTY  {d.relative_to(root)}")
        else:
            print(f"  OK     {d.relative_to(root)}")

    print(f"\n{len(empty)} empty / {len(candidates)} total")
    return empty


def delete_empty_dirs(directories: list[Path], dry_run: bool = False) -> None:
    """
    Delete a list of empty directories.

    Parameters
    ----------
    directories : List of Paths to delete (from find_empty_dirs)
    dry_run     : If True, print what would be deleted without actually deleting
    """
    if not directories:
        print("\nNothing to delete.")
        return

    print()
    deleted = 0
    for d in directories:
        if dry_run:
            print(f"  Would delete: {d}")
        else:
            try:
                d.rmdir()   # rmdir() only succeeds on truly empty directories
                deleted += 1
                print(f"  Deleted: {d}")
            except OSError as e:
                print(f"  ERROR deleting {d.name}: {e}")

    if dry_run:
        print(f"\nDry run — {len(directories)} director{'ies' if len(directories) != 1 else 'y'} would be deleted.")
        print("Call with delete=True to actually remove them.")
    else:
        print(f"\nDeleted {deleted} / {len(directories)} director{'ies' if len(directories) != 1 else 'y'}.")


# ── Main entry point ──────────────────────────────────────────────────────────

def run(
    path:      "str | Path" = ".",
    recursive: bool = True,
    delete:    bool = False,
) -> list[Path]:
    """
    Find and optionally delete empty directories.

    Parameters
    ----------
    path      : Directory to search (default: current directory)
    recursive : If True (default), search all subdirectories.
                If False, check immediate subdirectories only.
    delete    : Set True to actually delete. Default is a dry run (safe preview).

    Returns
    -------
    List of empty directory paths found

    Examples
    --------
    from clean_empty_dirs import run

    run(".")                               # dry run, recursive (default)
    run(".", recursive=False)              # dry run, immediate subdirs only
    run(".", delete=True)                  # delete, recursive
    run(".", recursive=False, delete=True) # delete, immediate subdirs only
    run("/path/to/search", delete=True)
    """
    empty = find_empty_dirs(path=path, recursive=recursive)
    delete_empty_dirs(empty, dry_run=not delete)
    return empty


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Find and delete empty directories.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python clean_empty_dirs.py                           # dry run, recursive
  python clean_empty_dirs.py --delete                  # delete, recursive
  python clean_empty_dirs.py --no-recursive            # dry run, current dir only
  python clean_empty_dirs.py --no-recursive --delete   # delete, current dir only
  python clean_empty_dirs.py --path ~/projects --delete
        """,
    )
    parser.add_argument("--path",      default=".",  help="Directory to search (default: .)")
    parser.add_argument("--recursive", default=True, action=argparse.BooleanOptionalAction,
                        help="Search subdirectories (default: on). Use --no-recursive to disable.")
    parser.add_argument("--delete",    action="store_true", help="Actually delete (default is dry run)")
    args = parser.parse_args()

    run(path=args.path, recursive=args.recursive, delete=args.delete)
