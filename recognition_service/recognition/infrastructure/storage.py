from __future__ import annotations

from pathlib import Path

from ..domain.ports import StoragePort


class FileSystemStorageAdapter(StoragePort):
    """Persists binary files on the local filesystem."""

    def __init__(self, media_root: str | Path) -> None:
        self._media_root = Path(media_root)
        self._media_root.mkdir(parents=True, exist_ok=True)

    def save(self, filename: str, content: bytes) -> str:
        destination = self._media_root / filename
        destination.write_bytes(content)
        return str(destination)
