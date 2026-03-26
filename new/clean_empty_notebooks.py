"""
clean_empty_notebooks.py
========================
Scans for Jupyter notebooks (.ipynb) and deletes any that are empty.

A notebook is considered empty if:
  - It has no cells at all, OR
  - Every cell has no source content (all cells are blank)

Usage
-----
    # Dry run — shows what would be deleted, deletes nothing
    python clean_empty_notebooks.py

    # Delete for real
    python clean_empty_notebooks.py --delete

    # Search a specific directory
    python clean_empty_notebooks.py --path /path/to/notebooks

    # Recursive (search subdirectories too)
    python clean_empty_notebooks.py --recursive

    # Combine
    python clean_empty_notebooks.py --path ~/projects --recursive --delete

From a notebook
---------------
    from clean_empty_notebooks import find_empty_notebooks, delete_empty_notebooks

    empties = find_empty_notebooks(path=".", recursive=True)
    delete_empty_notebooks(empties)          # actually deletes
    delete_empty_notebooks(empties, dry_run=True)   # preview only
"""

import json
from pathlib import Path
from typing import Optional


# ── Core logic ────────────────────────────────────────────────────────────────

def is_empty_notebook(path: Path) -> bool:
    """
    Return True if the notebook has no cells or all cells have no source.

    Parameters
    ----------
    path : Path to a .ipynb file

    Returns
    -------
    bool
    """
    try:
        nb = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"  WARN  could not read {path}: {e}")
        return False   # don't delete files we can't parse

    cells = nb.get("cells", [])

    # No cells at all → empty
    if not cells:
        return True

    # All cells have empty source → empty
    # source is either a string or a list of strings
    for cell in cells:
        src = cell.get("source", "")
        if isinstance(src, list):
            src = "".join(src)
        if src.strip():
            return False   # found at least one cell with content

    return True


def find_empty_notebooks(
    path: "str | Path" = ".",
    recursive: bool = False,
) -> list[Path]:
    """
    Return a list of empty .ipynb files under the given directory.

    Parameters
    ----------
    path      : Directory to search (default: current directory)
    recursive : If True, search all subdirectories too
    """
    root    = Path(path).expanduser().resolve()
    pattern = "**/*.ipynb" if recursive else "*.ipynb"
    files   = sorted(root.glob(pattern))

    print(f"\nSearching {'recursively ' if recursive else ''}in: {root}")
    print(f"Found {len(files)} notebook(s)\n")

    empty = []
    for nb in files:
        if is_empty_notebook(nb):
            empty.append(nb)
            print(f"  EMPTY  {nb.relative_to(root)}")
        else:
            print(f"  OK     {nb.relative_to(root)}")

    print(f"\n{len(empty)} empty / {len(files)} total")
    return empty


def delete_empty_notebooks(
    notebooks: list[Path],
    dry_run: bool = False,
) -> None:
    """
    Delete a list of notebook files.

    Parameters
    ----------
    notebooks : List of Path objects to delete (from find_empty_notebooks)
    dry_run   : If True, print what would be deleted without deleting anything
    """
    if not notebooks:
        print("\nNothing to delete.")
        return

    action = "Would delete" if dry_run else "Deleting"
    print()
    deleted = 0
    for nb in notebooks:
        print(f"  {action}: {nb}")
        if not dry_run:
            try:
                nb.unlink()
                deleted += 1
            except OSError as e:
                print(f"    ERROR: {e}")

    if dry_run:
        print(f"\nDry run — {len(notebooks)} file(s) would be deleted. Pass dry_run=False to delete.")
    else:
        print(f"\nDeleted {deleted} / {len(notebooks)} file(s).")


# ── Convenience wrapper (notebook-friendly) ───────────────────────────────────

def run(
    path:      "str | Path" = ".",
    recursive: bool = False,
    delete:    bool = False,
) -> list[Path]:
    """
    Find empty notebooks and optionally delete them.

    Parameters
    ----------
    path      : Directory to search
    recursive : Search subdirectories too
    delete    : Actually delete files (default False = dry run)

    Returns
    -------
    List of empty notebook paths found

    Examples
    --------
    from clean_empty_notebooks import run

    # Preview
    run(path=".", recursive=True)

    # Delete for real
    run(path=".", recursive=True, delete=True)
    """
    empty = find_empty_notebooks(path=path, recursive=recursive)
    delete_empty_notebooks(empty, dry_run=not delete)
    return empty

# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Find and delete empty Jupyter notebooks.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python clean_empty_notebooks.py                        # dry run, current dir
  python clean_empty_notebooks.py --delete               # delete, current dir
  python clean_empty_notebooks.py --recursive            # dry run, recursive
  python clean_empty_notebooks.py --path ~/projects --recursive --delete
        """,
    )
    parser.add_argument("--path",      default=".",   help="Directory to search (default: .)")
    parser.add_argument("--recursive", action="store_true", help="Search subdirectories")
    parser.add_argument("--delete",    action="store_true", help="Actually delete (default is dry run)")
    args = parser.parse_args()

    run(path=args.path, recursive=args.recursive, delete=args.delete)
