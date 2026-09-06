"""Shared input-path rules for the DANDI 000469 analysis."""

from __future__ import annotations

from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]


def data_root(project_dir: Path = PROJECT_DIR) -> Path:
    """Prefer the complete DANDI folder, with an explicit legacy fallback."""
    full_root = project_dir / "raw" / "all" / "000469"
    if full_root.is_dir():
        return full_root
    legacy_root = project_dir / "raw" / "pilot-legacy"
    return legacy_root if legacy_root.is_dir() else project_dir / "raw"


def nwb_files(project_dir: Path = PROJECT_DIR) -> list[Path]:
    """Return all NWB files below the selected data root."""
    return sorted(data_root(project_dir).rglob("*.nwb"))


def find_session(file_name: str, project_dir: Path = PROJECT_DIR) -> Path:
    """Resolve one session by filename and reject ambiguous matches."""
    matches = [path for path in nwb_files(project_dir) if path.name == file_name]
    if not matches:
        raise FileNotFoundError(
            f"NWB session not found below {data_root(project_dir)}: {file_name}"
        )
    if len(matches) > 1:
        locations = ", ".join(str(path) for path in matches)
        raise ValueError(f"NWB session name is ambiguous: {locations}")
    return matches[0]
